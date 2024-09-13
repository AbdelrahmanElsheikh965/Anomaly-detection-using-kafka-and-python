import asyncio
import websockets # type: ignore

async def receive_data():
    uri = "ws://localhost:6789"
    
    async with websockets.connect(uri) as websocket:
        while True:
            data = await websocket.recv()
            print(f"Received: {data}")

# Run the client
asyncio.get_event_loop().run_until_complete(receive_data())
