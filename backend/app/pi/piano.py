import numpy as np
import simpleaudio as sa
from mpmath import mp

from pi.sounds import generate_sine_wave, apply_envelope, phase_align_wave

DIGIT_TO_KEY = {
    0: "C4", 1: "D4", 2: "E4", 3: "F4", 4: "G4",
    5: "A4", 6: "B4", 7: "C5", 8: "D5", 9: "E5"
}

def get_pi_waveform(
    digits: int = 100,
    duration: float = 0.5,
    crossfade: float = 0.1,
    key_root: str = "C4",
    harmony: bool = False,
    harmony_type: str = "third",
    harmony_speed: int = 2,
) -> np.ndarray:
    """
    Generate and return the full concatenated waveform (as a NumPy array)
    for the first `digits` of π, with optional harmonization.
    """
    # (Copy the body of play_pi_sequence_continuous up to audio conversion,
    # but instead of playing, just return `combined_wave` as a float array.)
    mp.dps = digits + 2
    pi_digits = str(mp.pi)[2:]
    sample_rate = 44100
    previous_wave = None
    combined_list = []

    for digit in pi_digits[:digits]:
        key = DIGIT_TO_KEY[int(digit)]
        freq = PIANO_KEYS[key]                     # :contentReference[oaicite:3]{index=3}
        wave = generate_sine_wave(freq, duration, sample_rate)  # :contentReference[oaicite:4]{index=4}
        wave = apply_envelope(wave, attack=0.02, decay=0.02)
        wave = phase_align_wave(wave)

        # (optional harmony logic…)

        if previous_wave is not None:
            # crossfade logic…
            combined_list.append(previous_wave)
        previous_wave = wave

    if previous_wave is not None:
        combined_list.append(previous_wave)

    full_wave = np.concatenate(combined_list) if combined_list else np.array([], dtype=float)
    # normalize
    max_amp = np.max(np.abs(full_wave)) or 1
    return full_wave / max_amp

# Generate a library of piano key frequencies
def create_piano_key_library():
    """
    Create a dictionary mapping piano key names to their frequencies.
    Returns:
        dict: A dictionary of piano keys and their corresponding frequencies.
    """
    note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

    piano_keys = {}

    for i in range(88):
        # MIDI note number: Start at A0 = MIDI note 21
        midi_number = i + 21

        # Calculate the frequency for the key
        frequency = 440.0 * 2 ** ((midi_number - 69) / 12.0)  # MIDI 69 is A4

        # Determine the note name and octave
        note_index = midi_number % 12  # Position within the octave
        octave = (midi_number // 12) - 1  # Calculate octave (MIDI 12-23 is octave 0, etc.)
        note_name = f"{note_names[note_index]}{octave}"

        piano_keys[note_name] = round(frequency, 2) 

    return piano_keys

PIANO_KEYS = create_piano_key_library()


def generate_scale(root, scale_type="major", include_octaves=False):
    """
    Generates a scale based on the given root note and type.
    
    Args:
        root (str): Root note (e.g., "C4").
        scale_type (str): Type of scale ("major", "minor").
        include_octaves (bool): If True, include all octaves of the scale.
    
    Returns:
        list: List of note names in the scale.
    """
    major_steps = [2, 2, 1, 2, 2, 2, 1]
    minor_steps = [2, 1, 2, 2, 1, 2, 2]

    # Get the note names and find the index of the root
    note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    root_name, octave = root[:-1], int(root[-1])

    if root_name not in note_names:
        raise ValueError(f"Invalid root note: {root}")

    start_idx = note_names.index(root_name)
    scale_steps = major_steps if scale_type == "major" else minor_steps
    scale = [root]

    current_idx = start_idx
    for step in scale_steps:
        current_idx = (current_idx + step) % 12
        if current_idx < start_idx:
            octave += 1  # Move to next octave
        scale.append(f"{note_names[current_idx]}{octave}")

    if include_octaves:
        scale += [increase_octave(note) for note in scale]  # Add next octave

    return scale

# Define the function to play a single note or a chord
def play_notes(notes, duration=1, volume=0.5, sample_rate=44100):
    """
    Plays a single note or a combination of notes (chord).
    Args:
        notes (list or str): A piano key name (e.g., "C4") or a list of key names.
        duration (float): Duration of the note in seconds.
        volume (float): Volume of the sound (0.0 to 1.0).
        sample_rate (int): Sampling rate for audio playback.
    """
    # Convert note names to frequencies
    if not isinstance(notes, list):
        notes = [notes]

    frequencies = [PIANO_KEYS[note] for note in notes if note in PIANO_KEYS]

    if not frequencies:
        raise ValueError("No valid notes provided or unrecognized note names.")

    # Generate sine waves for each frequency and combine them
    wave = sum(generate_sine_wave(freq, duration, sample_rate, amplitude=volume) for freq in frequencies)

    # Normalize the wave to fit in the range -1.0 to 1.0
    wave = wave / np.max(np.abs(wave))

    # Convert to 16-bit PCM audio format
    audio = (wave * 32767).astype(np.int16)

    # Play the audio using simpleaudio
    play_obj = sa.play_buffer(audio, num_channels=1, bytes_per_sample=2, sample_rate=sample_rate)
    play_obj.wait_done()  # Wait until the audio finishes playing


def play_pi_sequence(digits=100, duration=0.5):
    """
    Plays the first "digits" of π, mapping each digit (0–9) to a piano key.
    Args:
        digits (int): Number of π digits to play.
        duration (float): Duration of each note.
    """
    # Set π precision
    mp.dps = digits + 2  # Digits + "3."
    pi_digits = str(mp.pi)[2:]  # Remove "3."

    print(f"Playing the first {digits} digits of π as notes...")

    # Play each digit as a note
    for digit in pi_digits[:digits]:
        key = DIGIT_TO_KEY[int(digit)]
        print(f"Digit {digit} -> Key {key}")
        play_notes(key, duration=duration)

def play_pi_sequence_continuous(digits=100, duration=0.5, crossfade=0.1):
    """
    Plays the first "digits" of π as a continuous sequence of notes with smooth, phase-aligned transitions.
    Args:
        digits (int): Number of π digits to play.
        duration (float): Duration of each note.
        crossfade (float): Overlapping duration between consecutive notes (for smooth transition).
    """
    mp.dps = digits + 2  # Digits + "3."
    pi_digits = str(mp.pi)[2:]  # Remove "3."

    print(f"Playing the first {digits} digits of π as continuous notes...")

    combined_wave = []  # Use a Python list for waveform collection
    sample_rate = 44100
    previous_wave = None  # Store previous wave for crossfading

    for i, digit in enumerate(pi_digits[:digits]):
        key = DIGIT_TO_KEY.get(int(digit), None)
        if key is None or key not in PIANO_KEYS:
            print(f"Digit {digit} -> Key not found in mapping!")
            continue

        print(f"Digit {digit} -> Key {key}")

        # Generate sine wave
        wave = generate_sine_wave(PIANO_KEYS[key], duration, sample_rate)
        print(f"Generated wave for {key} with length {len(wave)}")

        # Apply smooth attack and decay envelope
        wave = apply_envelope(wave, attack=0.02, decay=0.02)
        print(f"Applied envelope to wave for {key}")

        # Phase-align wave to ensure it starts and ends near zero-crossing
        wave = phase_align_wave(wave, sample_rate)
        print(f"Phase-aligned wave for {key}")

        if previous_wave is not None:
            crossfade_samples = min(len(previous_wave), int(sample_rate * crossfade))

            if crossfade_samples > 0:
                sine_fade = np.sin(np.linspace(0, np.pi / 2, crossfade_samples)) ** 2

                # Blend previous wave end with new wave start
                previous_wave[-crossfade_samples:] = (
                    previous_wave[-crossfade_samples:] * (1 - sine_fade) +
                    wave[:crossfade_samples] * sine_fade
                )
                wave = wave[crossfade_samples:]  # Remove blended section
                print(f"Crossfaded last {crossfade_samples} samples of {key}")

            # Append blended previous wave
            combined_wave.append(previous_wave)

        # Store current wave as previous for the next iteration
        previous_wave = wave

    # Append the final wave
    if previous_wave is not None:
        combined_wave.append(previous_wave)

    # Ensure we have valid waveform data
    if not combined_wave:
        print("No valid waveform generated. Exiting.")
        return

    # Convert list to a NumPy array
    combined_wave = np.concatenate(combined_wave)
    print(f"Final combined wave length: {len(combined_wave)}")

    # Normalize waveform to avoid clipping
    max_amplitude = np.max(np.abs(combined_wave))
    if max_amplitude > 0:
        combined_wave = combined_wave / max_amplitude
    print(f"Waveform normalized. Final length: {len(combined_wave)}")

    # Convert to 16-bit PCM audio format
    audio = (combined_wave * 32767).astype(np.int16)

    # Play the final waveform
    print("Playing audio...")
    play_obj = sa.play_buffer(audio, num_channels=1, bytes_per_sample=2, sample_rate=sample_rate)
    play_obj.wait_done()

def get_harmonized_note(melody_note, scale_notes, harmony_type="third"):
    """
    Returns a harmonized note based on the melody note and scale.
    
    Args:
        melody_note (str): The melody note being played.
        scale_notes (list): List of notes in the scale.
        harmony_type (str): Type of harmony ("third", "fifth", "sixth").
    
    Returns:
        str: The best harmony note.
    """
    try:
        idx = scale_notes.index(melody_note)  # Find the melody note in the scale
    except ValueError:
        print(f"⚠️ Warning: {melody_note} not in scale! Using root.")
        return scale_notes[0]  # Fallback to root note

    harmony_intervals = {
        "third": 2,
        "fifth": 4,
        "sixth": 5
    }

    interval = harmony_intervals.get(harmony_type, 2)  # Default to third
    harmony_idx = (idx + interval) % len(scale_notes)  # Loop within the scale

    return scale_notes[harmony_idx]

def increase_octave(note):
    """
    Increases a note by one octave.
    
    Args:
        note (str): The note to shift up.
    
    Returns:
        str: The same note one octave higher.
    """
    if len(note) < 2 or not note[-1].isdigit():
        return note  # Return unchanged if invalid format

    note_name = note[:-1]  # Extract "C", "D#", etc.
    octave = int(note[-1]) + 1  # Increase octave

    return f"{note_name}{octave}"  # Return shifted note

def fix_wave_length(wave, target_length):
    """
    Adjusts a waveform to match the target length.
    
    Args:
        wave (numpy.array): Input waveform.
        target_length (int): The length to match.
    
    Returns:
        numpy.array: The resized waveform.
    """
    if len(wave) > target_length:
        return wave[:target_length]  # Trim if too long
    elif len(wave) < target_length:
        return np.pad(wave, (0, target_length - len(wave)), mode="constant")  # Pad with silence if too short
    return wave  # Already the correct length

def play_pi_sequence_with_harmony(
    digits: int = 100,
    duration: float = 0.5,
    crossfade: float = 0.05,
    key_root: str = "C4",
    harmony_type: str = "third",
    harmony_speed: int = 2,
    octave_doubling: bool = False,
    harmony_movement: str = "random",
    return_wave: bool = False
) -> np.ndarray | None:
    """
    Plays—or returns—the first `digits` of π as a harmonized piano melody.
    
    Args:
      digits (int): how many π digits to use
      duration (float): seconds per melody note
      crossfade (float): overlap duration between notes
      key_root (str): root note for harmony (e.g. "C4")
      harmony_type (str): "third", "fifth", or "sixth"
      harmony_speed (int): harmony note rate multiplier
      octave_doubling (bool): also play harmony +1 octave
      harmony_movement (str): "random", "intervals", or "chordal"
      return_wave (bool): if True, *do not* play but return waveform array

    Returns:
      np.ndarray: if return_wave=True, the full normalized waveform
      None: if return_wave=False (it plays the audio directly)
    """
    # 1) Prepare π digits
    mp.dps = digits + 2
    pi_digits = str(mp.pi)[2:]  # drop "3."

    print(f"Generating π melody for {digits} digits in key {key_root}…")

    sample_rate = 44100
    combined_segments = []
    prev_wave = None

    # Precompute scale for harmony
    scale_notes = generate_scale(key_root, "major", include_octaves=True)
    melody_dur  = duration
    harmony_dur = melody_dur / harmony_speed
    harmony_idx = 0

    # 2) Build each note + harmony
    for i, ch in enumerate(pi_digits[:digits]):
        digit = int(ch)
        key = DIGIT_TO_KEY.get(digit)
        if not key or key not in PIANO_KEYS:
            print(f"⚠️ Digit {digit} has no mapped key, skipping")
            continue

        print(f"🎵 Note {i+1}/{digits}: {key}")
        # Melody
        mel_wave = generate_sine_wave(PIANO_KEYS[key], melody_dur, sample_rate)
        mel_wave = apply_envelope(mel_wave, attack=0.02, decay=0.02)
        mel_wave = phase_align_wave(mel_wave)

        # Prepare harmony placeholder
        harmony_seq = np.zeros_like(mel_wave)

        # Generate harmony voices
        for h in range(harmony_speed):
            # pick scale index
            if harmony_movement == "random":
                idx = np.random.randint(0, len(scale_notes))
            elif harmony_movement == "intervals":
                idx = (harmony_idx + h*2) % len(scale_notes)
            else:  # chordal or default
                idx = (harmony_idx + h*3) % len(scale_notes)
            note_h = scale_notes[idx]
            print(f"  🎹 Harmony {h+1}: {note_h}")
            h_wave = generate_sine_wave(PIANO_KEYS[note_h], harmony_dur, sample_rate)
            h_wave = apply_envelope(h_wave, attack=0.02, decay=0.02)
            h_wave = phase_align_wave(h_wave)
            # optional octave doubling
            if octave_doubling:
                oct_note = increase_octave(note_h)
                if oct_note in PIANO_KEYS:
                    print(f"    🎶 Octave double: {oct_note}")
                    o_wave = generate_sine_wave(PIANO_KEYS[oct_note], harmony_dur, sample_rate)
                    o_wave = apply_envelope(o_wave, attack=0.02, decay=0.02)
                    o_wave = phase_align_wave(o_wave)
                    o_wave *= 0.6
                    h_wave *= 0.8
                    harmony_seq[:len(o_wave)] += o_wave
            # mix harmony voice
            h_wave *= 0.8
            # place this harmony into the sequence
            start = int(h * len(harmony_seq) / harmony_speed)
            end   = min(len(harmony_seq), start + len(h_wave))
            harmony_seq[start:end] += h_wave[: end-start]

        # advance harmony position
        harmony_idx = (harmony_idx + harmony_speed) % len(scale_notes)

        # blend melody + harmony
        combo = (mel_wave + harmony_seq) / 2.0

        # 3) Crossfade with previous
        if prev_wave is not None:
            xf = min(len(prev_wave), int(sample_rate * crossfade))
            if xf > 0:
                fade = np.sin(np.linspace(0, np.pi/2, xf))**2
                prev_wave[-xf:] = prev_wave[-xf:]*(1-fade) + combo[:xf]*fade
                combo = combo[xf:]
            combined_segments.append(prev_wave)

        prev_wave = combo

    # append last
    if prev_wave is not None:
        combined_segments.append(prev_wave)

    # 4) Concatenate & normalize
    if not combined_segments:
        print("⚠️ No waveform generated.")
        return None
    full_wave = np.concatenate(combined_segments)
    max_a = np.max(np.abs(full_wave)) or 1.0
    full_wave = full_wave / max_a
    print(f"🛠 Built waveform length={len(full_wave)} samples")

    # 5) Return or play
    if return_wave:
        return full_wave

    # otherwise play it
    pcm = (full_wave * 32767).astype(np.int16)
    print("▶️ Playing audio…")
    obj = sa.play_buffer(pcm, num_channels=1, bytes_per_sample=2, sample_rate=sample_rate)
    obj.wait_done()
    return None