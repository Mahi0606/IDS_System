"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from datetime import datetime
import json

from app.config import settings
from app.store import prediction_store
from app.ml.predictor import predictor
from app.services.flow_manager import FlowManager
from app.services.packet_sniffer import PacketSniffer
from app.routers import predictions, models, health, stats
from app.routers.health import router as health_router

# WebSocket manager
websocket_connections = set()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    print("=" * 50)
    print("Starting IDS System...")
    print("=" * 50)
    
    # Load ML models
    try:
        predictor.load_models()
        print("✓ Models loaded successfully")
    except Exception as e:
        print(f"✗ Error loading models: {e}")
        raise
    
    # Initialize flow manager
    flow_manager = FlowManager(idle_timeout=settings.FLOW_IDLE_TIMEOUT)
    flow_manager.start()
    print("✓ Flow manager started")
    
    # Initialize packet sniffer (but don't start automatically)
    sniffer = None
    try:
        sniffer = PacketSniffer(
            interface=settings.INTERFACE_NAME,
            flow_manager=flow_manager,
            on_flow_complete=lambda flow: handle_completed_flow(flow),
        )
        # Don't start automatically - user can start via API
        print(f"✓ Packet sniffer initialized (not started - use /api/health/sniffer/start to begin)")
    except Exception as e:
        print(f"⚠ Warning: Could not initialize packet sniffer: {e}")
        print("  You can still use the API for manual predictions.")
    
    # Start background task to process expired and active flows
    async def process_flows():
        while True:
            await asyncio.sleep(5)  # Check every 5 seconds
            
            # Process expired flows (idle > 60 seconds)
            expired_flows = flow_manager.expire_flows()
            if expired_flows:
                print(f"  [Flow Processor] Processing {len(expired_flows)} expired flows")
            for flow in expired_flows:
                handle_completed_flow(flow)
            
            # Also flush active flows that have enough packets or are old enough
            # This ensures flows appear faster (every 5 seconds or after 3 packets)
            flushed_flows = flow_manager.flush_active_flows(min_packets=3, max_age_seconds=5)
            if flushed_flows:
                print(f"  [Flow Processor] Flushing {len(flushed_flows)} active flows")
            for flow in flushed_flows:
                handle_completed_flow(flow)
    
    asyncio.create_task(process_flows())
    
    # Store references
    app.state.flow_manager = flow_manager
    app.state.sniffer = sniffer
    health.sniffer = sniffer
    health.flow_manager = flow_manager
    
    print("=" * 50)
    print("IDS System ready!")
    print("=" * 50)
    
    yield
    
    # Shutdown
    print("\nShutting down IDS System...")
    if sniffer:
        sniffer.stop()
    if flow_manager:
        flow_manager.stop()
    print("✓ Shutdown complete")


def handle_completed_flow(flow):
    """Handle a completed flow: predict and broadcast."""
    try:
        # Convert flow to feature dictionary
        flow_dict = flow.to_feature_dict()
        
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
            "src_ip": flow.src_ip,
            "dst_ip": flow.dst_ip,
            "src_port": flow.src_port,
            "dst_port": flow.dst_port,
            "protocol": flow.protocol,
            "is_attack": result.is_attack,
            "attack_type": result.attack_type,
            "severity": severity,
            "confidence": result.binary_confidence,
            "binary_confidence": result.binary_confidence,  # Also include for history endpoint
        }
        
        # Add to in-memory store
        prediction_store.add_event(event)
        
        # Log successful processing
        print(f"✓ Processed flow: {flow.src_ip}:{flow.src_port} -> {flow.dst_ip}:{flow.dst_port} ({flow.protocol}) - {result.attack_type} (confidence: {result.binary_confidence:.2f})")
        
        # Broadcast to all connected WebSocket clients
        asyncio.create_task(broadcast_websocket(event))
    
    except Exception as e:
        import traceback
        print(f"✗ Error handling completed flow: {e}")
        print(f"  Flow: {flow.src_ip}:{flow.src_port} -> {flow.dst_ip}:{flow.dst_port} ({flow.protocol})")
        traceback.print_exc()


async def broadcast_websocket(event: dict):
    """Broadcast event to all WebSocket connections."""
    if not websocket_connections:
        return  # No clients connected
    
    message = json.dumps(event)
    disconnected = set()
    
    for ws in websocket_connections:
        try:
            await ws.send_text(message)
        except Exception as e:
            print(f"  [WebSocket] Error sending to client: {e}")
            disconnected.add(ws)
    
    # Remove disconnected clients
    websocket_connections.difference_update(disconnected)
    
    if websocket_connections:
        print(f"  [WebSocket] Broadcasted event to {len(websocket_connections)} client(s)")


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(predictions.router, prefix=settings.API_V1_PREFIX)
app.include_router(models.router, prefix=settings.API_V1_PREFIX)
app.include_router(health_router, prefix=settings.API_V1_PREFIX)
app.include_router(stats.router, prefix=settings.API_V1_PREFIX)


# WebSocket endpoint
from fastapi import WebSocket, WebSocketDisconnect

@app.websocket(f"{settings.API_V1_PREFIX}/live")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for live prediction events."""
    await websocket.accept()
    websocket_connections.add(websocket)
    
    try:
        while True:
            # Keep connection alive and wait for client messages (if any)
            data = await websocket.receive_text()
            # Echo back or handle client messages if needed
    except WebSocketDisconnect:
        websocket_connections.discard(websocket)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "IDS System API",
        "version": settings.VERSION,
        "docs": "/docs",
    }

