"""
prepare_source.py
Convert audio files in data/source_audio/raw/ to mono, 15-second WAV stimuli
with 0.5 s cosine fade-in and fade-out, saved to data/source_audio/processed/.

Usage:
    python src/prepare_source.py
"""

from pathlib import Path
import numpy as np
import scipy.signal
import soundfile as sf

ROOT      = Path(__file__).parent.parent
SRC_DIR   = ROOT / "assets/raw"
OUT_DIR   = ROOT / "assets/processed"
SR        = 44100
DURATION  = 15.0
FADE      = 0.5

AUDIO_EXTS = {".wav", ".mp3", ".aiff", ".flac", ".ogg"}


def prepare(path: Path, target_sr=SR, duration_s=DURATION, fade_s=FADE) -> np.ndarray:
    sig, sr = sf.read(path, always_2d=True)
    sig = sig.mean(axis=1)  # to mono
    if sr != target_sr:
        sig = scipy.signal.resample(sig, int(len(sig) * target_sr / sr))

    # trim leading silence (threshold: -60 dBFS)
    threshold = 10 ** (-60 / 20)
    onset = np.argmax(np.abs(sig) > threshold)
    sig = sig[onset:]

    target_n = int(duration_s * target_sr)
    if len(sig) >= target_n:
        sig = sig[:target_n]
    else:
        repeats = int(np.ceil(target_n / len(sig)))
        sig = np.tile(sig, repeats)[:target_n]

    fade_n = int(fade_s * target_sr)
    ramp = 0.5 * (1 - np.cos(np.pi * np.arange(fade_n) / fade_n))
    sig[:fade_n]  *= ramp
    sig[-fade_n:] *= ramp[::-1]

    sig /= np.max(np.abs(sig))
    return sig.astype(np.float32)


def pick_files() -> list[Path]:
    candidates = [f for f in sorted(SRC_DIR.iterdir()) if f.suffix.lower() in AUDIO_EXTS]
    if not candidates:
        print(f"No audio files found in {SRC_DIR}")
        return []

    print("Files in raw/:")
    for i, f in enumerate(candidates, 1):
        print(f"  [{i}] {f.name}")
    print("  [0] Process all")

    raw = input("\nEnter number(s) separated by spaces: ").strip()
    if raw == "0":
        return candidates

    chosen = []
    for token in raw.split():
        try:
            idx = int(token) - 1
            if 0 <= idx < len(candidates):
                chosen.append(candidates[idx])
            else:
                print(f"  Skipping invalid number: {token}")
        except ValueError:
            print(f"  Skipping invalid input: {token}")
    return chosen


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    files = pick_files()
    if not files:
        return

    for src in files:
        print(f"  Processing {src.name} ...", end=" ", flush=True)
        sig = prepare(src)
        out_path = OUT_DIR / (src.stem + ".wav")
        sf.write(out_path, sig, SR, subtype="PCM_16")
        print(f"-> {out_path.name}  [{len(sig)/SR:.1f}s  mono  {SR}Hz]")

    print(f"\nDone — {len(files)} file(s) processed.")


if __name__ == "__main__":
    main()
