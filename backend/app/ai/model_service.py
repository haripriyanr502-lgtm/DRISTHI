from typing import Optional, Dict, Any
import numpy as np
from app.ai.base_model import BaseECGModel
from app.ai.simulated_demo import SimulatedDemoECGModel

class AIServiceManager:
    """
    Central AI Service Manager.
    Separates model-loading and inference from the web framework and database.
    Allows easy hot-swapping or future plug-in of real trained PyTorch/TensorFlow models.
    """

    def __init__(self):
        # Default to research demonstration mode
        self._active_model: BaseECGModel = SimulatedDemoECGModel()
        self._is_production_model_connected: bool = False

    def get_model_status(self) -> Dict[str, Any]:
        """Returns the readiness status of the AI inference subsystem."""
        metadata = self._active_model.get_model_metadata()
        return {
            "model_connected": self._is_production_model_connected,
            "status_description": (
                "Connected (Production Model)" if self._is_production_model_connected 
                else "Running in Research Demonstration Mode (Algorithm Selection in Progress)"
            ),
            "metadata": metadata
        }

    def register_production_model(self, model: BaseECGModel):
        """Enables connecting a trained neural network algorithm."""
        self._active_model = model
        self._is_production_model_connected = True

    def run_inference(
        self, 
        signal: np.ndarray, 
        sampling_rate: float = 250.0,
        patient_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executes analysis on conditioned signal using the active model pipeline.
        """
        return self._active_model.predict(signal, sampling_rate, patient_metadata)

ai_service = AIServiceManager()
