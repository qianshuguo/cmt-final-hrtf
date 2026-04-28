"""
Phase 3/4: Listening experiment runner
--------------------------------------
Plays 6 binaural stimuli in randomised order and collects elevation
responses.  Results are saved to results/<participant_id>.csv.

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

# ── stimuli metadata ──────────────────────────────────────────────────────────
STIMULI_DIR = ROOT / "outputs/stimuli"
RESULTS_DIR = ROOT / "results"

# (filename_stem, dataset_label, elevation_deg, elevation_label)
STIMULI = [
    ("cipic_human_rear_neg30", "CIPIC Human", -30, "down"),
    ("cipic_human_rear_0",     "CIPIC Human",   0, "middle"),
    ("cipic_human_rear_pos30", "CIPIC Human",  30, "up"),
    ("cipic_kemar_rear_neg30", "CIPIC KEMAR",  -30, "down"),
    ("cipic_kemar_rear_0",     "CIPIC KEMAR",    0, "middle"),
    ("cipic_kemar_rear_pos30", "CIPIC KEMAR",   30, "up"),
]

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

    clear()
    print("=" * 60)
    print("   HRTF Elevation Localisation Experiment")
    print("=" * 60)
    print()
    print("You will hear 6 short sounds played through headphones.")
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
    csv_path = os.path.join(RESULTS_DIR, f"{participant_id}.csv")

    # shuffle trials
    trials = list(STIMULI)
    random.shuffle(trials)

    fieldnames = [
        "participant", "trial", "dataset", "elevation_deg",
        "elevation_label", "response", "correct", "rt_s",
    ]

    with open(csv_path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()

        for i, (stem, dataset, elev_deg, elev_label) in enumerate(trials, start=1):
            wav_path = os.path.join(STIMULI_DIR, f"{stem}.wav")

            clear()
            print(f"Trial {i} / {len(trials)}")
            print("-" * 40)
            print("Playing sound…  (headphones recommended)")
            print()

            play_wav(wav_path)

            while True:
                key = get_keypress("Your answer  [1=Down  2=Middle  3=Up  R=Replay  Q=Quit]: ")

                if key == "q":
                    print("\nQuitting — partial results saved.")
                    fh.flush()
                    pygame.mixer.quit()
                    return

                if key == "r":
                    print("Replaying…")
                    play_wav(wav_path)
                    continue

                if key in RESPONSE_KEYS:
                    break

                print("  Invalid key — please press 1, 2, 3, R, or Q.")

            t_start = time.time()
            response = RESPONSE_KEYS[key]
            rt = round(time.time() - t_start, 3)
            correct = response == elev_label

            writer.writerow({
                "participant":    participant_id,
                "trial":          i,
                "dataset":        dataset,
                "elevation_deg":  elev_deg,
                "elevation_label": elev_label,
                "response":       response,
                "correct":        correct,
                "rt_s":           rt,
            })
            fh.flush()

            result_str = "Correct!" if correct else f"Wrong  (was: {elev_label})"
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
