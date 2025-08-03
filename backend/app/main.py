import asyncio
import math
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "Hello from FastAPI!"}

@app.get("/waveform")
async def compute_wave(
    frequency: float = 440.0,
    amplitude: float = 1.0,
    phase: float = 0.0,
    samples: int = 100,
    frame_size: float = 0.1,
    frame_rate: int = 144
):
    dt_sample = frame_size / samples
    data = []
    for i in range(samples):
        t = phase + i * dt_sample
        x = i * dt_sample
        y = amplitude * math.sin(2 * math.pi * frequency * t)
        data.append([x, y])

    # advance start‐time by one frame’s worth, so waveform scrolls:
    next_phase = phase + (1.0 / frame_rate)
    return {"data": data, "phase": next_phase}

@app.websocket("/ws/waveform")
async def websocket_waveform(ws: WebSocket):
    print("WebSocket connection established")
    await ws.accept()
    phase = 0.0
    frequency = 1.0
    amplitude = 1.0
    samples = 100
    frame_size = 0.1
    frame_rate = 30

    async def recv_settings():
        nonlocal frequency, amplitude, samples, frame_size, frame_rate
        try:
            while True:
                data = await ws.receive_json()
                frequency = float(data.get("frequency", frequency))
                amplitude = float(data.get("amplitude", amplitude))
                samples = int(data.get("samples", samples))
                frame_size = float(data.get("frame_size", frame_size))
                frame_rate = int(data.get("frame_rate", frame_rate))
        except WebSocketDisconnect:
            return

    recv_task = asyncio.create_task(recv_settings())

    try:
        while True:
            payload = await compute_wave(frequency, amplitude, phase, samples, frame_size, frame_rate)
            await ws.send_json({"data": payload["data"]})
            phase = payload["phase"]
            await asyncio.sleep(1/frame_rate)
    except WebSocketDisconnect:
        pass
    finally:
        recv_task.cancel()
        