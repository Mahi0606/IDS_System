"""ML model loading and prediction logic."""
import joblib
import numpy as np
import math
from typing import Dict, Optional, Tuple
from pathlib import Path

from app.config import settings
from app.ml.preprocessing import build_feature_vector_from_flow_dict, FEATURE_COLUMNS


class PredictionResult:
    """Result of a prediction."""
    
    def __init__(
        self,
        is_attack: bool,
        attack_type: str,
        binary_confidence: float,
        class_probabilities: Optional[Dict[str, float]] = None,
        raw_features: Optional[np.ndarray] = None,
    ):
        self.is_attack = is_attack
        self.attack_type = attack_type
        self.binary_confidence = binary_confidence
        self.class_probabilities = class_probabilities or {}
        self.raw_features = raw_features


class MLPredictor:
    """ML model predictor that loads models and makes predictions."""
    
    def __init__(self):
        self.binary_model = None
        self.multiclass_model = None
        self.scaler = None
        self.pca = None
        self.loaded = False
    
    def load_models(self):
        """Load all ML models and preprocessors."""
        # Resolve path relative to project root (parent of backend directory)
        model_dir = Path(__file__).parent.parent.parent.parent / settings.MODEL_DIR
        if not model_dir.exists():
            # Try relative to current working directory
            model_dir = Path(settings.MODEL_DIR)
        
        # Load scaler
        scaler_path = model_dir / "scaler.pkl"
        if not scaler_path.exists():
            raise FileNotFoundError(f"Scaler not found at {scaler_path}")
        self.scaler = joblib.load(scaler_path)
        
        # Load PCA
        pca_path = model_dir / "pca.pkl"
        if not pca_path.exists():
            raise FileNotFoundError(f"PCA not found at {pca_path}")
        self.pca = joblib.load(pca_path)
        
        # Load binary model
        binary_path = model_dir / "binary_svm_model.pkl"
        if not binary_path.exists():
            raise FileNotFoundError(f"Binary model not found at {binary_path}")
        self.binary_model = joblib.load(binary_path)
        
        # Load multiclass model
        multiclass_path = model_dir / "multiclass_rf_model.pkl"
        if not multiclass_path.exists():
            raise FileNotFoundError(f"Multiclass model not found at {multiclass_path}")
        self.multiclass_model = joblib.load(multiclass_path)
        
        self.loaded = True
        print(f"✓ Loaded models: binary={type(self.binary_model).__name__}, "
              f"multiclass={type(self.multiclass_model).__name__}")
    
    def predict(self, flow: Dict) -> PredictionResult:
        """
        Predict attack type from flow dictionary.
        
        Args:
            flow: Dictionary with flow statistics
            
        Returns:
            PredictionResult with prediction details
        """
        if not self.loaded:
            raise RuntimeError("Models not loaded. Call load_models() first.")
        
        # Build feature vector in exact order
        feature_vector = build_feature_vector_from_flow_dict(flow)
        
        # Apply preprocessing pipeline (exactly as in training)
        # 1. StandardScaler
        scaled_features = self.scaler.transform(feature_vector)
        
        # 2. PCA transformation
        pca_features = self.pca.transform(scaled_features)
        
        # 3. Binary classification (attack vs benign)
        binary_pred = self.binary_model.predict(pca_features)[0]

        # Try to get probabilities if the model supports them
        if hasattr(self.binary_model, "predict_proba"):
            binary_proba = self.binary_model.predict_proba(pca_features)[0]
            binary_confidence = float(max(binary_proba))
        else:
            # Fallback: estimate confidence from decision_function if available,
            # otherwise just trust the hard prediction (100% confidence).
            if hasattr(self.binary_model, "decision_function"):
                scores = self.binary_model.decision_function(pca_features)
                # For binary SVM, scores is usually shape (1,)

                if np.ndim(scores) == 1:
                    score = float(scores[0])
                else:
                    # If shape (1,2), use difference
                    score = float(scores[0, 1] - scores[0, 0])

                # Map score to [0,1] with logistic function
                prob_attack = 1.0 / (1.0 + math.exp(-score))
                binary_proba = np.array([1.0 - prob_attack, prob_attack], dtype=float)
                binary_confidence = prob_attack if binary_pred == 1 else 1.0 - prob_attack
            else:
                # Last-resort fallback: no probabilities at all
                if binary_pred == 1:
                    binary_proba = np.array([0.0, 1.0], dtype=float)
                else:
                    binary_proba = np.array([1.0, 0.0], dtype=float)
                binary_confidence = 1.0

        # Decide if binary model thinks this is attack
        binary_attack = (binary_pred == 1)

        # 4. Multiclass classification (run always)
        multiclass_proba = self.multiclass_model.predict_proba(pca_features)[0]
        class_names = self.multiclass_model.classes_

        # Top multiclass prediction
        top_idx = int(np.argmax(multiclass_proba))
        top_label = str(class_names[top_idx])
        top_prob = float(multiclass_proba[top_idx])

        # 5. Fuse decisions:
        #    - Attack if SVM says attack
        #    - OR if multiclass says a non-BENIGN class with high confidence
        multiclass_attack = (top_label != "BENIGN" and top_prob >= 0.6)
        is_attack = bool(binary_attack or multiclass_attack)

        # 6. Build attack_type + class_probabilities
        attack_type = "BENIGN"
        class_probabilities = {}

        if is_attack:
            # We want attack-only probabilities (no BENIGN), normalized to sum to 1
            attack_labels = []
            attack_probs = []

            # Find index of 'BENIGN' if present
            benign_idx = None
            try:
                benign_idx = int(np.where(class_names == "BENIGN")[0][0])
            except Exception:
                pass  # if not found, treat all classes as attacks

            # Collect attack-only labels & probs
            for i, class_name in enumerate(class_names):
                if benign_idx is not None and i == benign_idx:
                    continue  # skip BENIGN
                attack_labels.append(str(class_name))
                attack_probs.append(float(multiclass_proba[i]))

            # Safeguard: avoid divide-by-zero
            total_attack_prob = sum(attack_probs) or 1.0

            # Normalize so attack-only probabilities sum to 1
            attack_probs = [p / total_attack_prob for p in attack_probs]

            # Choose best attack type based on normalized probs
            best_idx = max(range(len(attack_probs)), key=lambda i: attack_probs[i])
            attack_type = attack_labels[best_idx]

            # Final probability dict (only attack classes)
            class_probabilities = {
                label: prob for label, prob in zip(attack_labels, attack_probs)
            }

        else:
            # For benign flows, we only care about benign vs attack from binary model
            class_probabilities["BENIGN"] = float(binary_proba[0])
            class_probabilities["ATTACK"] = float(binary_proba[1])
            attack_type = "BENIGN"


        
        return PredictionResult(
            is_attack=is_attack,
            attack_type=attack_type,
            binary_confidence=binary_confidence,
            class_probabilities=class_probabilities,
            raw_features=feature_vector,
        )
    
    def get_model_info(self) -> Dict:
        """Get information about loaded models."""
        if not self.loaded:
            return {"error": "Models not loaded"}
        
        info = {
            "binary_model": {
                "type": type(self.binary_model).__name__,
                "n_features": self.pca.n_components_ if self.pca else None,
            },
            "multiclass_model": {
                "type": type(self.multiclass_model).__name__,
                "classes": self.multiclass_model.classes_.tolist() if hasattr(self.multiclass_model, 'classes_') else [],
                "n_features": self.pca.n_components_ if self.pca else None,
            },
            "preprocessing": {
                "scaler": type(self.scaler).__name__,
                "pca": {
                    "type": type(self.pca).__name__,
                    "n_components": self.pca.n_components_ if self.pca else None,
                    "explained_variance_ratio": float(sum(self.pca.explained_variance_ratio_)) if self.pca else None,
                },
            },
            "feature_count": len(FEATURE_COLUMNS),
        }
        
        return info


# Global predictor instance (loaded at startup)
predictor = MLPredictor()

