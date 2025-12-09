"""API routes for statistics."""
from fastapi import APIRouter
from app.store import prediction_store

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/")
async def get_stats():
    """
    Get statistics computed from in-memory event store.
    """
    stats = prediction_store.get_stats()
    # Add total count for frontend compatibility
    stats["totalFlows"] = stats.get("total_flows", 0)
    stats["totalAttacks"] = stats.get("total_attacks", 0)
    stats["attackRatio"] = stats.get("attack_ratio", 0)
    stats["mostFrequentAttack"] = stats.get("most_frequent_attack", "N/A")
    return stats

