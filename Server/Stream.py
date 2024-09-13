import asyncio
import random
import websockets # type: ignore

async def data_stream(websocket, path):
    while True:
        # Generate random floating-point number
        random_number = round(random.uniform(10, 100), 2)
        
        # Send data to the client
        await websocket.send(str(random_number))
        
        # Simulate real-time by sleeping for 1 second
        await asyncio.sleep(1)

# Start WebSocket server on port 6789
start_server = websockets.serve(data_stream, "localhost", 6789)

# Run the WebSocket server
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
