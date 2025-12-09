"""Health check and system status endpoints."""
from fastapi import APIRouter, HTTPException, Query
from app.services.packet_sniffer import PacketSniffer
from app.services.flow_manager import FlowManager
from app.config import settings

router = APIRouter(prefix="/health", tags=["health"])

# Global references (set by main app)
sniffer: PacketSniffer = None
flow_manager: FlowManager = None


@router.get("/")
async def health_check():
    """
    Health check endpoint.
    """
    available_interfaces = []
    try:
        from scapy.all import get_if_list
        available_interfaces = get_if_list()
    except Exception:
        pass
    
    sniffer_stats = {}
    if sniffer:
        sniffer_stats = sniffer.get_stats()
    
    return {
        "status": "healthy",
        "sniffer_running": sniffer._running if sniffer else False,
        "interface": settings.INTERFACE_NAME,
        "available_interfaces": available_interfaces,
        "interface_exists": settings.INTERFACE_NAME in available_interfaces if available_interfaces else None,
        "sniffer_stats": sniffer_stats,
        "active_flows": flow_manager.get_active_flow_count() if flow_manager else 0,
    }


@router.post("/sniffer/start")
async def start_sniffer():
    """
    Start the packet sniffer.
    """
    if not sniffer:
        raise HTTPException(status_code=400, detail="Sniffer not initialized")
    
    if sniffer._running:
        return {"status": "already_running", "message": "Sniffer is already running"}
    
    try:
        # Check if interface exists
        try:
            from scapy.all import get_if_list
            available_interfaces = get_if_list()
            if settings.INTERFACE_NAME not in available_interfaces:
                return {
                    "status": "warning",
                    "message": f"Interface '{settings.INTERFACE_NAME}' not found. Available: {available_interfaces}",
                    "sniffer_running": False
                }
        except Exception as e:
            # If we can't check interfaces, continue anyway
            pass
        
        sniffer.start()
        
        # Give it a moment to start, then check if it's actually running
        import asyncio
        await asyncio.sleep(0.5)
        
        if sniffer._running:
            return {"status": "started", "message": f"Sniffer started on {settings.INTERFACE_NAME}", "sniffer_running": True}
        else:
            return {
                "status": "failed",
                "message": f"Sniffer failed to start. Check interface '{settings.INTERFACE_NAME}' and permissions.",
                "sniffer_running": False
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start sniffer: {str(e)}")


@router.post("/sniffer/stop")
async def stop_sniffer():
    """
    Stop the packet sniffer.
    """
    if not sniffer:
        raise HTTPException(status_code=400, detail="Sniffer not initialized")
    
    if not sniffer._running:
        return {"status": "already_stopped", "message": "Sniffer is already stopped"}
    
    try:
        sniffer.stop()
        return {"status": "stopped", "message": "Sniffer stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop sniffer: {str(e)}")


@router.post("/sniffer/interface")
async def set_interface(interface: str = Query(..., description="Network interface name")):
    """
    Change the network interface for the sniffer.
    Expects interface as query parameter: POST /api/health/sniffer/interface?interface=enp0s1
    """
    if not sniffer:
        raise HTTPException(status_code=400, detail="Sniffer not initialized")
    
    # Check if interface exists
    try:
        from scapy.all import get_if_list
        available_interfaces = get_if_list()
        if interface not in available_interfaces:
            raise HTTPException(
                status_code=400, 
                detail=f"Interface '{interface}' not found. Available: {available_interfaces}"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check interfaces: {str(e)}")
    
    # Stop sniffer if running
    was_running = sniffer._running
    if was_running:
        sniffer.stop()
    
    # Update interface
    sniffer.interface = interface
    
    # Update settings (this won't persist, but will work for current session)
    from app.config import settings
    settings.INTERFACE_NAME = interface
    
    # Restart if it was running
    if was_running:
        try:
            sniffer.start()
            return {
                "status": "updated",
                "message": f"Interface changed to {interface} and sniffer restarted",
                "interface": interface
            }
        except Exception as e:
            return {
                "status": "updated_but_failed_restart",
                "message": f"Interface changed to {interface} but failed to restart: {str(e)}",
                "interface": interface
            }
    else:
        return {
            "status": "updated",
            "message": f"Interface changed to {interface}",
            "interface": interface
        }

