from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.all_models import User
from app.schemas.all_schemas import AlertAcknowledgeRequest
from app.services.notification_service import notification_service
from app.api.deps import get_current_user

router = APIRouter(prefix="/caregivers", tags=["Caregiver Dashboard"])

@router.get("/dashboard")
def get_caregiver_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Caregiver portal endpoint providing:
    - Assigned patient vitals & metadata
    - Recent simulated/live alerts
    - Hardware telemetry staging status (ESP32 + AD8232)
    """
    if current_user.role != "caregiver":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to registered Caregiver accounts."
        )

    dashboard_data = notification_service.get_caregiver_dashboard_data(db, current_user.id)
    return {
        "caregiver": {
            "id": current_user.id,
            "name": current_user.full_name or "Caregiver",
            "email": current_user.email
        },
        "assigned_patients": dashboard_data["assigned_patients"],
        "alerts": dashboard_data["alerts"],
        "hardware_integration_notice": dashboard_data["hardware_integration_notice"]
    }

@router.post("/alerts/{alert_id}/acknowledge")
def acknowledge_alert(
    alert_id: int,
    req: AlertAcknowledgeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Allows caregiver to acknowledge an active alert."""
    name = req.caregiver_name or current_user.full_name or "Caregiver"
    alert = notification_service.acknowledge_alert(db, alert_id, caregiver_name=name)
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found.")
    return {
        "success": True,
        "message": f"Alert #{alert_id} acknowledged.",
        "acknowledged_by": alert.acknowledged_by,
        "acknowledged_at": alert.acknowledged_at.isoformat()
    }
