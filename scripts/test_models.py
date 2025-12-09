#!/usr/bin/env python3
"""Test script to verify models can be loaded and make a sample prediction."""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.ml.predictor import predictor
from app.ml.preprocessing import FEATURE_COLUMNS

def test_model_loading():
    """Test that models can be loaded."""
    print("Testing model loading...")
    try:
        predictor.load_models()
        print("✓ Models loaded successfully")
        return True
    except Exception as e:
        print(f"✗ Error loading models: {e}")
        return False

def test_prediction():
    """Test making a sample prediction."""
    print("\nTesting prediction...")
    
    # Create a sample flow dictionary with all required features
    sample_flow = {}
    for col in FEATURE_COLUMNS:
        # Set some default values
        if 'Port' in col:
            sample_flow[col] = 80
        elif 'Duration' in col:
            sample_flow[col] = 1000000
        elif 'Packets' in col or 'Bytes' in col or 'Length' in col:
            sample_flow[col] = 10
        elif 'Mean' in col or 'Std' in col or 'Variance' in col:
            sample_flow[col] = 0.0
        elif 'Flags' in col or 'Count' in col:
            sample_flow[col] = 0
        elif 'Ratio' in col or 'Size' in col:
            sample_flow[col] = 1.0
        elif 's' in col and '/' in col:  # Rate features like "Flow Bytes/s"
            sample_flow[col] = 1000.0
        elif 'IAT' in col:
            sample_flow[col] = 1000.0 if 'Mean' in col or 'Std' in col else 1000
        elif 'Header' in col:
            sample_flow[col] = 20
        elif 'Win' in col or 'seg' in col.lower():
            sample_flow[col] = 65535 if 'Win' in col else 1500
        elif 'Active' in col or 'Idle' in col:
            sample_flow[col] = 1000.0 if 'Mean' in col or 'Std' in col else 1000
        else:
            sample_flow[col] = 0
    
    try:
        result = predictor.predict(sample_flow)
        print(f"✓ Prediction successful")
        print(f"  - Is Attack: {result.is_attack}")
        print(f"  - Attack Type: {result.attack_type}")
        print(f"  - Confidence: {result.binary_confidence:.2%}")
        print(f"  - Class Probabilities: {result.class_probabilities}")
        return True
    except Exception as e:
        print(f"✗ Error making prediction: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("IDS Model Test Script")
    print("=" * 50)
    
    if not test_model_loading():
        sys.exit(1)
    
    if not test_prediction():
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("All tests passed!")
    print("=" * 50)

