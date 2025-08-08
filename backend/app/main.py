import asyncio
from contextlib import suppress

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.websockets import WebSocketState
import numpy as np

from waveform.computation import compute_wave, flatten_wave_array
from pi.piano import play_pi_sequence_with_harmony

import logging

app = FastAPI()

COLORS = {
    'DEBUG': '\033[36m',
    'INFO': '\033[32m',
    'WARNING': '\033[33m',
    'ERROR': '\033[31m',
    'CRITICAL': '\033[1;31m'
}
RESET = '\033[0m'

class ColorFormatter(logging.Formatter):
    def format(self, record):
        log_color = COLORS.get(record.levelname, RESET)
        record.levelname = f"{log_color}{record.levelname}{RESET}"
        return super().format(record)

handler = logging.StreamHandler()
handler.setFormatter(ColorFormatter("%(levelname)-8s %(message)s"))

logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/waveform")
async def websocket_waveform(ws: WebSocket):
    await ws.accept()
    generate_wave = False
    phase = 0.0
    frequency = 1.0
    amplitude = 1.0
    samples = 100
    frame_size = 0.1
    frame_rate = 30

    stop = asyncio.Event()

    async def recv_settings():
        nonlocal generate_wave, frequency, amplitude, samples, frame_size, frame_rate
        try:
            while True:
                data = await ws.receive_json()
                generate_wave = bool(data.get("generate_wave", generate_wave))
                frequency = float(data.get("frequency", frequency))
                amplitude = float(data.get("amplitude", amplitude))
                samples = int(data.get("samples", samples))
                frame_size = float(data.get("frame_size", frame_size))
                frame_rate = int(data.get("frame_rate", frame_rate))
        except (WebSocketDisconnect, RuntimeError):
            pass
        finally:
            stop.set()

    async def send_wave():
        nonlocal generate_wave, frequency, amplitude, phase, samples, frame_size
        try:
            while True:
                if ws.application_state != WebSocketState.CONNECTED:
                    break
                if generate_wave:
                    payload = compute_wave(frequency, amplitude, phase, samples, frame_size)
                    phase = phase + (1.0 / frame_rate)
                    await ws.send_bytes(flatten_wave_array(payload))
                else:
                    default_wave = [[0, 0], [1, 0]]
                    await ws.send_bytes(flatten_wave_array(default_wave))
                await asyncio.sleep(1/frame_rate)
        except (WebSocketDisconnect, RuntimeError, asyncio.CancelledError):
            pass
        finally:
            stop.set()
    
    recv_task = asyncio.create_task(recv_settings())
    send_task = asyncio.create_task(send_wave())
    
    try:
        await stop.wait()
    finally:
        for t in (recv_task, send_task):
            t.cancel()
        with suppress(asyncio.CancelledError):
            await recv_task
        with suppress(asyncio.CancelledError):
            await send_task
        with suppress(Exception):
            await ws.close()


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
    print("WebSocket connection established for PI waveform generation.")
    cfg = await ws.receive_json()
    digits = cfg.get("digits", 50)
    duration = cfg.get("duration", 1.0)
    crossfade = cfg.get("crossfade", 0.01)
    key_root = cfg.get("key_root", "C4")
    harmony_type = cfg.get("harmony_type", "third")
    harmony_speed = cfg.get("harmony_speed", 4)
    octave_doubling = cfg.get("octave_doubling", True)
    harmony_movement = cfg.get("harmony_movement", "chordal")

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