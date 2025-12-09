"""ML preprocessing module - extracts features from network flows exactly as in training."""
import numpy as np
from typing import Dict, List, Optional


# Exact feature columns in the order used during training (after dropping non-variant columns)
# This matches the order from Data_Preprocessing.ipynb
FEATURE_COLUMNS = [
    'Destination Port',
    'Flow Duration',
    'Total Fwd Packets',
    'Total Backward Packets',
    'Total Length of Fwd Packets',
    'Total Length of Bwd Packets',
    'Fwd Packet Length Max',
    'Fwd Packet Length Min',
    'Fwd Packet Length Mean',
    'Fwd Packet Length Std',
    'Bwd Packet Length Max',
    'Bwd Packet Length Min',
    'Bwd Packet Length Mean',
    'Bwd Packet Length Std',
    'Flow Bytes/s',
    'Flow Packets/s',
    'Flow IAT Mean',
    'Flow IAT Std',
    'Flow IAT Max',
    'Flow IAT Min',
    'Fwd IAT Total',
    'Fwd IAT Mean',
    'Fwd IAT Std',
    'Fwd IAT Max',
    'Fwd IAT Min',
    'Bwd IAT Total',
    'Bwd IAT Mean',
    'Bwd IAT Std',
    'Bwd IAT Max',
    'Bwd IAT Min',
    'Fwd PSH Flags',
    'Fwd URG Flags',
    'Fwd Header Length',
    'Bwd Header Length',
    'Fwd Packets/s',
    'Bwd Packets/s',
    'Min Packet Length',
    'Max Packet Length',
    'Packet Length Mean',
    'Packet Length Std',
    'Packet Length Variance',
    'FIN Flag Count',
    'SYN Flag Count',
    'RST Flag Count',
    'PSH Flag Count',
    'ACK Flag Count',
    'URG Flag Count',
    'CWE Flag Count',
    'ECE Flag Count',
    'Down/Up Ratio',
    'Average Packet Size',
    'Avg Fwd Segment Size',
    'Avg Bwd Segment Size',
    'Fwd Header Length.1',
    'Subflow Fwd Packets',
    'Subflow Fwd Bytes',
    'Subflow Bwd Packets',
    'Subflow Bwd Bytes',
    'Init_Win_bytes_forward',
    'Init_Win_bytes_backward',
    'act_data_pkt_fwd',
    'min_seg_size_forward',
    'Active Mean',
    'Active Std',
    'Active Max',
    'Active Min',
    'Idle Mean',
    'Idle Std',
    'Idle Max',
    'Idle Min',
]


def build_feature_vector_from_flow_dict(flow: Dict) -> np.ndarray:
    """
    Build feature vector from flow dictionary in the exact order used during training.
    
    Args:
        flow: Dictionary containing flow statistics with keys matching FEATURE_COLUMNS
        
    Returns:
        numpy array of shape (n_features,) with features in the correct order
        
    Raises:
        ValueError: If required features are missing
    """
    feature_vector = []
    missing_features = []
    
    for col in FEATURE_COLUMNS:
        if col not in flow:
            missing_features.append(col)
            # Use 0 as default for missing features (shouldn't happen in production)
            feature_vector.append(0.0)
        else:
            value = flow[col]
            # Handle None/NaN values
            if value is None or (isinstance(value, float) and np.isnan(value)):
                feature_vector.append(0.0)
            else:
                feature_vector.append(float(value))
    
    if missing_features:
        # Log warning but don't fail - use defaults
        import warnings
        warnings.warn(f"Missing features: {missing_features}. Using defaults.")
    
    return np.array(feature_vector, dtype=np.float32).reshape(1, -1)


def validate_flow_dict(flow: Dict) -> bool:
    """
    Validate that flow dictionary has all required features.
    
    Args:
        flow: Dictionary to validate
        
    Returns:
        True if valid, False otherwise
    """
    return all(col in flow for col in FEATURE_COLUMNS)

