"""
Phase 2: Binaural rendering
Produces 6 stereo WAV stimuli: 2 datasets × 3 rear elevations.

Coordinate mapping (CIPIC interaural-polar):
  lateral angle = 0°  (az_idx=12) → median plane → front OR rear depends on polar
  polar angle 180°    → directly rear, same horizontal plane
  polar angle <180°   → rear, below horizon
  polar angle >180°   → rear, above horizon

CIPIC elevation grid: el = -45 + i*5.625°
  el_idx=31 → 129.375°  (target rear –51°)
  el_idx=40 → 180.000°  (target rear   0°)
  el_idx=49 → 230.625°  (target rear +51°)
"""

from pathlib import Path
import numpy as np
import scipy.io
import scipy.signal
import soundfile as sf
import os

ROOT         = Path(__file__).parent.parent
DATASET_ROOT = ROOT.parent / "dataset"

# ── paths ─────────────────────────────────────────────────────────────────────
CIPIC_ROOT  = DATASET_ROOT / "cipic-hrtf-database-master/standard_hrir_database"
PROCESSED   = DATASET_ROOT / "my_proc"
OUT_DIR     = ROOT.parent / "outputs/stimuli"
SR          = 44100

DATASETS = {
    "cipic_human":  CIPIC_ROOT / "subject_003/hrir_final.mat",
    "cipic_kemar":  CIPIC_ROOT / "subject_021/hrir_final.mat",
}

# azimuth index 12 → lateral = 0° (median plane, covers both front and rear via polar)
AZ_IDX = 12

# target rear elevations → nearest CIPIC polar-angle index
CONDITIONS = [
    ("rear_neg51", 31, "Rear -51° (polar 129.375°)"),
    ("rear_0",     40, "Rear   0° (polar 180.000°)"),
    ("rear_pos51", 49, "Rear +51° (polar 230.625°)"),
]

# ── test signal: 500 ms pink-ish broadband noise with 5 ms cosine fade ────────
def make_test_signal(duration_s=0.5, sr=44100):
    rng = np.random.default_rng(42)
    n = int(duration_s * sr)
    # white noise
    sig = rng.standard_normal(n)
    # 5 ms fade-in / fade-out to avoid clicks
    fade = int(0.005 * sr)
    window = np.ones(n)
    window[:fade] = 0.5 * (1 - np.cos(np.pi * np.arange(fade) / fade))
    window[-fade:] = 0.5 * (1 - np.cos(np.pi * np.arange(fade, 0, -1) / fade))
    sig *= window
    # normalize
    sig /= np.max(np.abs(sig))
    return sig.astype(np.float32)


def convolve(signal, hrir):
    """OA-FFT convolution; trims to signal length."""
    out = scipy.signal.fftconvolve(signal, hrir)
    return out[:len(signal)].astype(np.float32)


def normalize_stereo(left, right, headroom_db=-3.0):
    peak = max(np.max(np.abs(left)), np.max(np.abs(right)))
    if peak == 0:
        return left, right
    scale = (10 ** (headroom_db / 20)) / peak
    return left * scale, right * scale


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    sources = sorted(PROCESSED.glob("*.wav"))
    if not sources:
        print(f"No files found in {PROCESSED} — run prepare_source.py first.")
        return

    total = 0
    for src_path in sources:
        signal, file_sr = sf.read(src_path, dtype="float32")
        assert file_sr == SR, f"Expected {SR} Hz, got {file_sr} in {src_path.name}"
        print(f"Source: {src_path.name}  [{len(signal)/SR:.1f}s  mono]")

        for dataset_name, mat_path in DATASETS.items():
            mat = scipy.io.loadmat(mat_path)
            hrir_l = mat["hrir_l"]  # (25, 50, 200)
            hrir_r = mat["hrir_r"]

            for cond_name, el_idx, description in CONDITIONS:
                ir_l = hrir_l[AZ_IDX, el_idx, :].astype(np.float64)
                ir_r = hrir_r[AZ_IDX, el_idx, :].astype(np.float64)

                left  = convolve(signal.astype(np.float64), ir_l)
                right = convolve(signal.astype(np.float64), ir_r)
                left, right = normalize_stereo(left, right)

                stereo = np.column_stack([left, right])
                fname = OUT_DIR / f"{src_path.stem}__{dataset_name}_{cond_name}.wav"
                sf.write(fname, stereo, SR, subtype="PCM_16")
                print(f"  ✔ {fname.name}")
                total += 1

        print()

    print(f"Done — {total} stimuli written to '{OUT_DIR}'")


if __name__ == "__main__":
    main()
