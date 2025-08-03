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
    cycles: int = 1,
    frame_rate: int = 144
):
    single_period = 1.0 / frequency
    total_time = cycles * single_period
    dt = total_time / samples
    data = []

    for i in range(samples):
        t = phase + i * dt
        x = i * dt
        y = amplitude * math.sin(2 * math.pi * frequency * t)
        data.append([x, y])

    next_phase = (phase + 1.0 / frame_rate) % single_period

    return {"data": data, "phase": next_phase}

@app.websocket("/ws/waveform")
async def websocket_waveform(ws: WebSocket):
    print("WebSocket connection established")
    await ws.accept()
    phase = 0.0
    frequency = 1.0
    amplitude = 1.0
    samples = 100
    cycles = 1
    frame_rate = 30

    async def recv_settings():
        nonlocal frequency, amplitude, samples, cycles, frame_rate
        try:
            while True:
                data = await ws.receive_json()
                frequency = float(data.get("frequency", frequency))
                amplitude = float(data.get("amplitude", amplitude))
                samples = int(data.get("samples", samples))
                cycles = int(data.get("cycles", cycles))
                frame_rate = int(data.get("frame_rate", frame_rate))
        except WebSocketDisconnect:
            return

    recv_task = asyncio.create_task(recv_settings())

    try:
        while True:
            payload = await compute_wave(frequency, amplitude, phase, samples, cycles, frame_rate)
            await ws.send_json({"data": payload["data"]})
            phase = payload["phase"]
            await asyncio.sleep(1/frame_rate)
    except WebSocketDisconnect:
        pass
    finally:
        recv_task.cancel()
        