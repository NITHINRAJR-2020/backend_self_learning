# Project 2: Live job progress (sections 10 and 14)

# Client sends {"type": "start", "seconds": 10}. The server runs a blocking “job” in a thread and streams {"type": "progress", "percent": 30} updates back while the job runs.
# Hint: the worker thread must not touch the WebSocket directly. Think about run_coroutine_threadsafe or an asyncio.Queue.
# Also handle the client disconnecting mid-job.

from fastapi import FastAPI , WebSocket

app = FastAPI()

import time

def blocking_job(seconds: int, on_progress) -> str:
    for i in range(1, 101):
        time.sleep(seconds / 100)       # pretend to do real work
        on_progress(i)                  # report progress from inside the job
    return f"finished a {seconds}s job"

@app.websocket('/ws')
async def wsendpoint(websocket:WebSocket):
    websocket.accept()
    try:
        async for mess in websocket.iter_text():
            
    except:
