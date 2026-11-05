from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.all_models import User, PatientProfile, CaregiverPatientAssignment
from app.schemas.all_schemas import UserRegisterRequest, UserLoginRequest, UserResponse, TokenResponse
from app.services.auth_service import auth_service
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse)
def register(req: UserRegisterRequest, db: Session = Depends(get_db)):
    # Verify doctor login is not allowed per strict development rules
    if req.role not in ["patient", "caregiver"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be either 'patient' or 'caregiver'."
        )

    # Check existing email
    existing_user = db.query(User).filter(User.email == req.email.lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address is already registered."
        )

    hashed_pw = auth_service.hash_password(req.password)
    user = User(
        email=req.email.lower(),
        hashed_password=hashed_pw,
        role=req.role,
        full_name=req.full_name or req.email.split("@")[0].capitalize(),
        phone_number=req.phone_number
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    assigned_pid = req.patient_id
    if req.role == "patient":
        # Link or create patient profile
        pid = req.patient_id or f"PT-{1000 + user.id}"
        assigned_pid = pid
        profile = db.query(PatientProfile).filter(PatientProfile.patient_id == pid).first()
        if not profile:
            profile = PatientProfile(
                patient_id=pid,
                user_id=user.id,
                age=35,
                gender="Not specified"
            )
            db.add(profile)
        else:
            profile.user_id = user.id
        db.commit()
    elif req.role == "caregiver":
        # Assign to patient if provided, or default to first patient
        if req.patient_id:
            profile = db.query(PatientProfile).filter(PatientProfile.patient_id == req.patient_id).first()
            if not profile:
                profile = PatientProfile(patient_id=req.patient_id, age=45)
                db.add(profile)
                db.commit()
            assignment = CaregiverPatientAssignment(
                caregiver_id=user.id,
                patient_id=req.patient_id,
                relationship_to_patient="Primary Caregiver"
            )
            db.add(assignment)
            db.commit()

    token = auth_service.create_access_token({"sub": str(user.id), "role": user.role, "email": user.email})
    user_resp = UserResponse(
        id=user.id,
        email=user.email,
        role=user.role,
        full_name=user.full_name,
        phone_number=user.phone_number,
        patient_id=assigned_pid,
        is_active=user.is_active,
        created_at=user.created_at
    )
    return TokenResponse(access_token=token, token_type="bearer", user=user_resp)

@router.post("/login", response_model=TokenResponse)
def login(req: UserLoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email.lower()).first()
    if not user or not auth_service.verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password."
        )

    assigned_pid = None
    if user.patient_profile:
        assigned_pid = user.patient_profile.patient_id
    elif user.caregiver_assignments:
        assigned_pid = user.caregiver_assignments[0].patient_id

    token = auth_service.create_access_token({"sub": str(user.id), "role": user.role, "email": user.email})
    user_resp = UserResponse(
        id=user.id,
        email=user.email,
        role=user.role,
        full_name=user.full_name,
        phone_number=user.phone_number,
        patient_id=assigned_pid,
        is_active=user.is_active,
        created_at=user.created_at
    )
    return TokenResponse(access_token=token, token_type="bearer", user=user_resp)

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    assigned_pid = None
    if user.patient_profile:
        assigned_pid = user.patient_profile.patient_id
    elif user.caregiver_assignments:
        assigned_pid = user.caregiver_assignments[0].patient_id

    return UserResponse(
        id=user.id,
        email=user.email,
        role=user.role,
        full_name=user.full_name,
        phone_number=user.phone_number,
        patient_id=assigned_pid,
        is_active=user.is_active,
        created_at=user.created_at
    )
