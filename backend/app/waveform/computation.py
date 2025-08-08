import math

import numpy as np

def compute_wave(
    frequency: float = 440.0,
    amplitude: float = 1.0,
    phase: float = 0.0,
    samples: int = 100,
    frame_size: float = 0.1
):
    data = []
    dt_sample = frame_size / samples
    for i in range(samples):
        t = phase + i * dt_sample
        x = i * dt_sample
        y = amplitude * math.sin(2 * math.pi * frequency * t)
        data.append([x, y])

    return data

def flatten_wave_array(wave) -> bytes:
    return bytes(np.array(wave, dtype=np.float32).tobytes())