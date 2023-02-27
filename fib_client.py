import asyncio
import json
import websockets

async def fibonacci_client():

    while True:
        start = input("Enter starting number of the sequence: ")
        end = input("Enter ending number of the sequence: ")
        try:
            start = int(start)
            end = int(end)
            if start < 0 or end < 0:
                print("Invalid input, numbers must be >= 0")
                continue
        except ValueError:
            print("Invalid input, numbers must be integers")
            continue

        try:
            async with websockets.connect('ws://localhost:8765') as websocket:
                data = {"start": start, "end": end}
                await websocket.send(json.dumps(data))
                ack = await websocket.recv()
                if not("ack" in ack):
                    print(f"Invalid ack from server: {ack}")
                response = await websocket.recv()
                data = json.loads(response)
                if not ("sequence" in data):
                    print("Error response: {}".format(data))
                else:
                    sequence = data["sequence"]
                    # maybe we should check if the values returned are actual integers,
                    # but for the moment we assume the server is well behaved
                    print("Fibonacci sequence: {}".format(sequence))
        except:
            print("Error with the connection to the server")

asyncio.get_event_loop().run_until_complete(fibonacci_client())
