"""
services/chat_ws.py

Manager de conexiones WebSocket para el chat por emergencia.
Agrupa clientes por id_emergency (una "sala" por emergencia).
"""

from typing import Dict, List
from fastapi import WebSocket


class ChatConnectionManager:
    def __init__(self):
        # { id_emergency: [WebSocket, ...] }
        self.rooms: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, id_emergency: int):
        await websocket.accept()
        self.rooms.setdefault(id_emergency, []).append(websocket)

    def disconnect(self, websocket: WebSocket, id_emergency: int):
        room = self.rooms.get(id_emergency, [])
        if websocket in room:
            room.remove(websocket)
        if not room:
            self.rooms.pop(id_emergency, None)

    async def broadcast(self, payload: dict, id_emergency: int):
        """Envía a todos los conectados en la sala, descarta conexiones muertas."""
        dead: List[WebSocket] = []
        for ws in self.rooms.get(id_emergency, []):
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws, id_emergency)


# Singleton — se importa desde el router
chat_manager = ChatConnectionManager()