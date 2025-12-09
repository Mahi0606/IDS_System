"""API routes for predictions."""
from fastapi import APIRouter, HTTPException
from typing import List

from app.store import prediction_store
from app.schemas.prediction import FlowInput, PredictionResponse, PredictionHistoryItem
from app.ml.predictor import predictor
from datetime import datetime

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.post("/predict-flow", response_model=PredictionResponse)
async def predict_flow(flow_input: FlowInput):
    """
    Predict attack type for a single flow.
    """
    try:
        # Convert input to flow dictionary
        flow_dict = flow_input.to_flow_dict()
        
        # Make prediction
        result = predictor.predict(flow_dict)
        
        # Determine severity
        if result.is_attack:
            if result.binary_confidence > 0.9:
                severity = "high"
            elif result.binary_confidence > 0.7:
                severity = "medium"
            else:
                severity = "low"
        else:
            severity = "none"
        
        # Create event dictionary
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "src_ip": flow_input.src_ip,
            "dst_ip": flow_input.dst_ip,
            "src_port": flow_input.src_port,
            "dst_port": flow_input.dst_port,
            "protocol": flow_input.protocol,
            "is_attack": result.is_attack,
            "attack_type": result.attack_type,
            "binary_confidence": result.binary_confidence,
            "severity": severity,
        }
        
        # Add to in-memory store
        prediction_store.add_event(event)
        
        return PredictionResponse(
            is_attack=result.is_attack,
            attack_type=result.attack_type,
            binary_confidence=result.binary_confidence,
            class_probabilities=result.class_probabilities,
            severity=severity,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@router.get("/history", response_model=List[PredictionHistoryItem])
async def get_history(limit: int = 100):
    """
    Get prediction history from in-memory store.
    """
    events = prediction_store.get_recent(limit)
    
    # Convert events to PredictionHistoryItem format
    history_items = []
    for idx, event in enumerate(events, start=1):
        history_items.append(PredictionHistoryItem(
            id=idx,  # Use index as ID since we don't have DB IDs
            src_ip=event.get("src_ip", ""),
            dst_ip=event.get("dst_ip", ""),
            src_port=event.get("src_port", 0),
            dst_port=event.get("dst_port", 0),
            protocol=event.get("protocol", ""),
            is_attack=event.get("is_attack", False),
            attack_type=event.get("attack_type", "BENIGN"),
            binary_confidence=event.get("binary_confidence", 0.0),
            severity=event.get("severity", "none"),
            created_at=event.get("timestamp", datetime.utcnow().isoformat()),
        ))
    
    return history_items

