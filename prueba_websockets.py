import asyncio
import websockets

async def test_ws():
    uri = "wss://darjujuy.duckdns.org/emergencies/im_on_alert/"
    token = input("Ingresa token: ")  # tu JWT

    async with websockets.connect(uri) as websocket:
        # Enviar el token como primer mensaje
        await websocket.send(token)

        # Escuchar mensajes periódicos
        while True:
            respuesta = await websocket.recv()
            print("Servidor respondió:", respuesta)

asyncio.run(test_ws())
