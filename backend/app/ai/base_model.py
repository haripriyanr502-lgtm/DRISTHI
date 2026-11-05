from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import numpy as np

class BaseECGModel(ABC):
    """
    Abstract Base Class for all future DRISTHI AI ECG Analysis Models.
    Ensures modularity: whether CNN, 1D ResNet, Bi-LSTM, or Transformer architecture
    is chosen after IEEE paper evaluation, it will implement this contract.
    """

    @abstractmethod
    def load_model(self, checkpoint_path: Optional[str] = None) -> bool:
        """Loads trained weights / serialized model artifacts."""
        pass

    @abstractmethod
    def predict(
        self, 
        signal: np.ndarray, 
        sampling_rate: float,
        patient_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executes model inference on a preprocessed ECG signal segment.
        Returns structured prediction dictionary.
        """
        pass

    @abstractmethod
    def get_supported_categories(self) -> List[str]:
        """Returns the list of diagnostic / morphological classes supported."""
        pass

    @abstractmethod
    def get_model_metadata(self) -> Dict[str, Any]:
        """Returns model architecture description, version, training dataset, and evaluation metrics."""
        pass
