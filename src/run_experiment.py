"""
Phase 3/4: Listening experiment runner
--------------------------------------
Scans outputs/stimuli/ for all rendered WAV files and plays them in
randomised order, collecting elevation responses.
Results are saved to results/<participant_id>.csv.

Controls during each trial:
  1  →  Down  (-30°)
  2  →  Middle (0°)
  3  →  Up    (+30°)
  R  →  Replay current stimulus
  Q  →  Quit (partial results are saved)
"""

import csv
import os
import random
import sys
import time
from pathlib import Path

import pygame

ROOT = Path(__file__).parent.parent

STIMULI_DIR = ROOT / "outputs/stimuli"
RESULTS_DIR = ROOT / "results"

ELEVATION_MAP = {"neg30": ("down", -30), "0": ("middle", 0), "pos30": ("up", 30)}
DATASET_MAP   = {"cipic_human": "CIPIC Human", "cipic_kemar": "CIPIC KEMAR"}


def build_stimuli() -> list[dict]:
    """Scan outputs/stimuli/ and parse metadata from filenames."""
    stimuli = []
    for wav in sorted(STIMULI_DIR.glob("*.wav")):
        # expected: {source}__{dataset}_{condition}.wav
        parts = wav.stem.split("__")
        if len(parts) != 2:
            continue
        source, rest = parts
        for dataset_key, dataset_label in DATASET_MAP.items():
            if rest.startswith(dataset_key + "_rear_"):
                cond = rest[len(dataset_key) + len("_rear_"):]
                if cond in ELEVATION_MAP:
                    elev_label, elev_deg = ELEVATION_MAP[cond]
                    stimuli.append({
                        "path":        wav,
                        "source":      source,
                        "dataset":     dataset_label,
                        "elevation_deg":   elev_deg,
                        "elevation_label": elev_label,
                    })
    return stimuli

RESPONSE_KEYS = {"1": "down", "2": "middle", "3": "up"}

# ── helpers ───────────────────────────────────────────────────────────────────

def clear():
    os.system("clear" if os.name == "posix" else "cls")


def play_wav(path: str):
    pygame.mixer.music.load(path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.05)


def get_keypress(prompt: str) -> str:
    """Read a single character from stdin (cross-platform, no Enter needed)."""
    print(prompt, end="", flush=True)
    try:
        import tty, termios
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
    except (ImportError, termios.error):
        # fallback for environments without tty (Windows, IDE consoles)
        ch = input().strip()[:1]
    print(ch)  # echo
    return ch.lower()

# ── main ──────────────────────────────────────────────────────────────────────

def main():
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

    trials = build_stimuli()
    if not trials:
        print(f"No stimuli found in {STIMULI_DIR} — run render_binaural.py first.")
        return
    random.shuffle(trials)

    clear()
    print("=" * 60)
    print("   HRTF Elevation Localisation Experiment")
    print("=" * 60)
    print()
    print(f"You will hear {len(trials)} sounds played through headphones.")
    print("Each sound comes from BEHIND you at different heights.")
    print()
    print("After each sound, press:")
    print("  1 → Down  (below ear level)")
    print("  2 → Middle (ear level)")
    print("  3 → Up    (above ear level)")
    print()
    print("Press R to replay a sound before answering.")
    print("Press Q at any time to quit and save partial results.")
    print()
    participant_id = input("Enter participant ID (e.g. p01): ").strip()
    if not participant_id:
        participant_id = "unnamed"

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = RESULTS_DIR / f"{participant_id}.csv"

    fieldnames = [
        "participant", "trial", "source", "dataset", "elevation_deg",
        "elevation_label", "response", "correct", "rt_s",
    ]

    with open(csv_path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()

        for i, trial in enumerate(trials, start=1):
            clear()
            print(f"Trial {i} / {len(trials)}")
            print("-" * 40)
            print("Playing sound…  (headphones recommended)")
            print()

            play_wav(trial["path"])

            while True:
                key = get_keypress("Your answer  [1=Down  2=Middle  3=Up  R=Replay  Q=Quit]: ")

                if key == "q":
                    print("\nQuitting — partial results saved.")
                    fh.flush()
                    pygame.mixer.quit()
                    return

                if key == "r":
                    print("Replaying…")
                    play_wav(trial["path"])
                    continue

                if key in RESPONSE_KEYS:
                    break

                print("  Invalid key — please press 1, 2, 3, R, or Q.")

            t_start = time.time()
            response = RESPONSE_KEYS[key]
            rt = round(time.time() - t_start, 3)
            correct = response == trial["elevation_label"]

            writer.writerow({
                "participant":     participant_id,
                "trial":           i,
                "source":          trial["source"],
                "dataset":         trial["dataset"],
                "elevation_deg":   trial["elevation_deg"],
                "elevation_label": trial["elevation_label"],
                "response":        response,
                "correct":         correct,
                "rt_s":            rt,
            })
            fh.flush()

            result_str = "Correct!" if correct else f"Wrong  (was: {trial['elevation_label']})"
            print(f"\n  → {result_str}\n")
            time.sleep(0.8)

    clear()
    print("=" * 60)
    print("   Experiment complete — thank you!")
    print(f"   Results saved to: {csv_path}")
    print("=" * 60)
    pygame.mixer.quit()


if __name__ == "__main__":
    main()
