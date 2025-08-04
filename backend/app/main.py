import asyncio
import math
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import numpy as np

from pi.piano import play_pi_sequence_with_harmony

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


@app.get("/api/pi-waveform")
async def pi_waveform(
    digits: int = 50,
    duration: float = 1.0,
    crossfade: float = 0.01,
    key_root: str = "C4",
    harmony_type: str = "third",
    harmony_speed: int = 4,
    octave_doubling: bool = True,
    harmony_movement: str = "chordal"
):
    # 1) Generate the full normalized float-32 waveform
    wave: np.ndarray = play_pi_sequence_with_harmony(
        digits=digits,
        duration=duration,
        crossfade=crossfade,
        key_root=key_root,
        harmony_type=harmony_type,
        harmony_speed=harmony_speed,
        octave_doubling=octave_doubling,
        harmony_movement=harmony_movement,
        return_wave=True
    )
    # 2) Convert to Float32 bytes
    byte_data = wave.astype(np.float32).tobytes()
    # 3) Stream it back as application/octet-stream
    return StreamingResponse(
        iter([byte_data]),
        media_type="application/octet-stream"
    )

@app.websocket("/ws/pi")
async def websocket_pi(ws: WebSocket):
    await ws.accept()
    cfg = await ws.receive_json()
    digits = cfg.get("digits", 50)
    duration = cfg.get("duration", 1.0)
    crossfade = cfg.get("crossfade", 0.01)
    key_root = cfg.get("key_root", "C4")
    harmony_type = cfg.get("harmony_type", "third")
    harmony_speed = cfg.get("harmony_speed", 4)
    octave_doubling = cfg.get("octave_doubling", True)
    harmony_movement = cfg.get("harmony_movement", "chordal")

    # 2) generate the full waveform off the event loop
    combined_wave = await run_in_threadpool(
        play_pi_sequence_with_harmony,
        digits=digits,
        duration=duration,
        crossfade=crossfade,
        key_root=key_root,
        harmony_type=harmony_type,
        harmony_speed=harmony_speed,
        octave_doubling=octave_doubling,
        harmony_movement=harmony_movement,
        return_wave=True
    )

    # 3) stream it back in small real-time chunks
    sample_rate = 44100
    chunk_size = 1024
    total = len(combined_wave)

    try:
        for start in range(0, total, chunk_size):
            chunk = combined_wave[start:start+chunk_size]
            data = [[i/sample_rate, float(v)] for i, v in enumerate(chunk)]
            await ws.send_json({"data": data})
            await asyncio.sleep(chunk_size / sample_rate)

    except WebSocketDisconnect:
        pass
    finally:
        await ws.close()