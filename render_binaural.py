"""
Phase 2: Binaural rendering
Produces 6 stereo WAV stimuli: 2 datasets × 3 rear elevations.

Coordinate mapping (CIPIC interaural-polar):
  lateral angle = 0°  (az_idx=12) → median plane → front OR rear depends on polar
  polar angle 180°    → directly rear, same horizontal plane
  polar angle 150°    → rear, ~30° below horizon
  polar angle 210°    → rear, ~30° above horizon

CIPIC elevation grid: el = -45 + i*5.625°
  el_idx=35 → 151.875°  (target rear –30°)
  el_idx=40 → 180.000°  (target rear   0°)
  el_idx=45 → 208.125°  (target rear +30°)
"""

import numpy as np
import scipy.io
import scipy.signal
import soundfile as sf
import os

# ── paths ─────────────────────────────────────────────────────────────────────
CIPIC_ROOT = "dataset/cipic-hrtf-database-master/standard_hrir_database"
OUT_DIR = "stimuli"
SR = 44100

DATASETS = {
    "cipic_human":  f"{CIPIC_ROOT}/subject_003/hrir_final.mat",
    "cipic_kemar":  f"{CIPIC_ROOT}/subject_021/hrir_final.mat",
}

# azimuth index 12 → lateral = 0° (median plane, covers both front and rear via polar)
AZ_IDX = 12

# target rear elevations → nearest CIPIC polar-angle index
CONDITIONS = [
    ("rear_neg30", 35, "Rear –30° (polar 151.875°)"),
    ("rear_0",     40, "Rear   0° (polar 180.000°)"),
    ("rear_pos30", 45, "Rear +30° (polar 208.125°)"),
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
    os.makedirs(OUT_DIR, exist_ok=True)
    signal = make_test_signal()
    print(f"Test signal: {len(signal)/SR*1000:.0f} ms, {SR} Hz\n")

    for dataset_name, mat_path in DATASETS.items():
        mat = scipy.io.loadmat(mat_path)
        hrir_l = mat["hrir_l"]  # (25, 50, 200)
        hrir_r = mat["hrir_r"]
        print(f"Dataset: {dataset_name}  ({mat_path})")

        for cond_name, el_idx, description in CONDITIONS:
            ir_l = hrir_l[AZ_IDX, el_idx, :].astype(np.float64)
            ir_r = hrir_r[AZ_IDX, el_idx, :].astype(np.float64)

            left  = convolve(signal.astype(np.float64), ir_l)
            right = convolve(signal.astype(np.float64), ir_r)
            left, right = normalize_stereo(left, right)

            stereo = np.column_stack([left, right])
            fname = f"{OUT_DIR}/{dataset_name}_{cond_name}.wav"
            sf.write(fname, stereo, SR, subtype="PCM_16")
            print(f"  ✔ {fname}  [{description}]")

        print()

    print(f"Done — {len(DATASETS) * len(CONDITIONS)} stimuli written to '{OUT_DIR}/'")
    print("\nFile summary:")
    for f in sorted(os.listdir(OUT_DIR)):
        path = os.path.join(OUT_DIR, f)
        info = sf.info(path)
        print(f"  {f}  {info.duration*1000:.0f} ms  {info.channels}ch  {info.samplerate} Hz")


if __name__ == "__main__":
    main()
