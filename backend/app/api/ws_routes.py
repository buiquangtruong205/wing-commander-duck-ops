import base64
import cv2
import numpy as np
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.ai_tracker import tracker
import json

router = APIRouter()

@router.websocket("/ws/tracking")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Receive data from client
            data = await websocket.receive_text()
            
            # Data should be a base64 encoded image frame
            try:
                # Remove header if present (data:image/jpeg;base64,...)
                if "," in data:
                    data = data.split(",")[1]
                
                img_bytes = base64.b64decode(data)
                nparr = np.frombuffer(img_bytes, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if frame is not None:
                    # Process frame
                    result = tracker.process_frame(frame)
                    # Send result back
                    await websocket.send_text(json.dumps(result))
                else:
                    await websocket.send_text(json.dumps({"detected": False, "error": "Invalid frame"}))
            
            except Exception as e:
                await websocket.send_text(json.dumps({"detected": False, "error": str(e)}))
                
    except WebSocketDisconnect:
        print("Client disconnected")
