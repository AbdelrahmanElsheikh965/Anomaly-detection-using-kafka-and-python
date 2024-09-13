import asyncio
import time
import math
import random
import websockets # type: ignore


async def data_stream(websocket, path):
    """Simulate a real-time data stream with seasonal patterns, trends, and random noise."""
    t = 0  # Initialize time step
    
    while True:
        # Simulate a regular trend, e.g., a gradual increase over time
        trend = 500 + 0.05 * t
        
        # Simulate seasonal variation using a sine wave - daily cycle (1440 minutes in a day)
        seasonality = 200 * math.sin(2 * math.pi * (t % 1440) / 1440)  
        
        # Add random noise to make it more realistic
        noise = random.uniform(-50, 50)  
        
        # Final transaction value combining trend, seasonality, and noise
        transaction_value = trend + seasonality + noise
        
        # Send the data to the client
        await websocket.send(str(transaction_value))
        
        # Increment time step
        t += 1
        
        # Simulate real-time by sleeping for 1 second
        await asyncio.sleep(1)

# Start WebSocket server on port 6789
start_server = websockets.serve(data_stream, "localhost", 6789)

# Run the WebSocket server
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
