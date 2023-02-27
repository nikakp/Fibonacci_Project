import asyncio
import json
import websockets
import logging
# I would likely change this for a production system: ex location of the log file
logging.basicConfig(filename='fibonacci.log', encoding='utf-8', level=logging.DEBUG)

async def fibonacci(n):
    global cache_hit
    global fib_cache
    
    if n in fib_cache:
        cache_hit = cache_hit + 1
        return fib_cache[n]
    # when we calculate n-1, n-2 will already be in the cache
    if (n-2) in fib_cache:
        cache_hit = cache_hit + 1
        n2_res = fib_cache[n-2]
    else:
        n2_res = await fibonacci(n-2)
        fib_cache[n-2] = n2_res
    
    if (n-1) in fib_cache:
        cache_hit = cache_hit + 1
        n1_res = fib_cache[n-1]
    else:
        n1_res = await fibonacci(n-1)
        fib_cache[n-1] = n1_res



    fib_cache[n] = n1_res + n2_res
    
    return (n1_res + n2_res)


async def fibonacci_sequence(start, end):
    tasks = [fibonacci(n) for n in range(start, end+1, 1)]
    result = await asyncio.gather(*tasks)
    return result

    

async def fibonacci_server(websocket, path):
    async for message in websocket:
        try:
            ack = {"ack": message}
            await websocket.send(json.dumps(ack))
            data = json.loads(message)
            logging.info(f"Message: {message}")
            start = data["start"]
            end = data["end"]
            try:
                s = int(start)
                e = int(end)
                if s < 0 or e < 0:
                    error = {"error": "Invalid request, start: {} end: {}".format(start, end)}
                    logging.error(error)
                    await websocket.send(json.dumps(error))
                    return
            except ValueError:
                error = {"error": "Invalid request invalid numbers were entered, start: {} end: {}".format(start, end)}
                logging.error(error)
                await websocket.send(json.dumps(error))
                return
         
            sequence = await fibonacci_sequence(start, end)
            response = {"sequence": sequence}
            await websocket.send(json.dumps(response))
            logging.info(f"cache hit: {cache_hit}")
            #print("Cache hit: {}".format(cache_hit))
        except:
            error = {"error": "Unable to parse json data from {}".format(message)}
            logging.error(error)
            await websocket.send(json.dumps(error))
            return

fib_cache = {0: 0, 1: 1, 2: 1}
cache_hit = 0
#print("cache_hit: {} ".format(cache_hit))
start_server = websockets.serve(fibonacci_server, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
