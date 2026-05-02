from pathlib import Path
import scipy.io
import numpy as np
import matplotlib.pyplot as plt

ROOT         = Path(__file__).parent.parent
DATASET_ROOT = ROOT.parent / "dataset"

SUBJECT = "subject_003"
MAT_PATH = DATASET_ROOT / "cipic-hrtf-database-master/standard_hrir_database" / SUBJECT / "hrir_final.mat"

mat = scipy.io.loadmat(MAT_PATH)

hrir_l = mat["hrir_l"]  # (25, 50, 200)
hrir_r = mat["hrir_r"]  # (25, 50, 200)

print("=== CIPIC HRTF Data ===")
print(f"Subject:          {SUBJECT}")
print(f"hrir_l shape:     {hrir_l.shape}  (azimuth x elevation x samples)")
print(f"hrir_r shape:     {hrir_r.shape}")
print(f"Azimuth positions: {hrir_l.shape[0]}")
print(f"Elevation positions: {hrir_l.shape[1]}")
print(f"IR length (samples): {hrir_l.shape[2]}")
print(f"Value range L:    [{hrir_l.min():.4f}, {hrir_l.max():.4f}]")
print(f"Value range R:    [{hrir_r.min():.4f}, {hrir_r.max():.4f}]")

# CIPIC azimuth angles (degrees)
azimuths = [-80, -65, -55, -45, -40, -35, -30, -25, -20, -15,
            -10, -5, 0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 55, 65, 80]

az_idx = 12   # 0 degrees (front-center)
el_idx = 8    # elevation index 8 = roughly 0 degrees

ir_l = hrir_l[az_idx, el_idx, :]
ir_r = hrir_r[az_idx, el_idx, :]

t = np.arange(200) / 44100 * 1000  # milliseconds (CIPIC sample rate = 44100 Hz)

fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
fig.suptitle(f"CIPIC HRTF — {SUBJECT}  |  Azimuth={azimuths[az_idx]}°  Elevation index={el_idx}")

axes[0].plot(t, ir_l, color="steelblue")
axes[0].set_ylabel("Amplitude")
axes[0].set_title("Left Ear HRIR")
axes[0].axhline(0, color="gray", linewidth=0.5)

axes[1].plot(t, ir_r, color="tomato")
axes[1].set_ylabel("Amplitude")
axes[1].set_xlabel("Time (ms)")
axes[1].set_title("Right Ear HRIR")
axes[1].axhline(0, color="gray", linewidth=0.5)

plt.tight_layout()
out_path = ROOT.parent / "outputs/figures/hrtf_verification.png"
plt.savefig(out_path, dpi=150)
print(f"\n✔ Plot saved to {out_path}")
print("✔ HRTF data read successfully — Phase 1 complete!")
