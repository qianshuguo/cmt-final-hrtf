# How Do Different HRTF Datasets Affect Rear Spatial Localization?

Individual project for Colloquy in Music Technology.

## Overview

This project compares two subjects from the CIPIC HRTF database — a human participant (subject 003) and a KEMAR dummy head (subject 021) — to assess how dataset choice affects listeners' ability to identify the elevation of sounds coming from behind them.

Source audio is convolved with CIPIC HRIRs at three rear elevations, then played back in a blind randomized listening test. Responses are recorded as CSV for offline analysis.

## Research Question

How does the choice of HRTF dataset (human vs. KEMAR dummy head) affect auditory elevation perception for rear sound sources?

---

## Repository Structure

```
.
├── src/
│   ├── prepare_source.py     # Step 1 – preprocess raw audio
│   ├── explore_hrtf.py       # (optional) visualize CIPIC HRIRs
│   ├── render_binaural.py    # Step 2 – convolve audio with HRTFs
│   └── run_experiment.py     # Step 3 – run listening test
├── ../dataset/
│   ├── my_raw/               # place raw audio files here (external, not in repo)
│   ├── my_proc/              # output of prepare_source.py (external, not in repo)
│   └── cipic-hrtf-database-master/
│       └── standard_hrir_database/   # CIPIC .mat files (external, not in repo)
├── ../outputs/
│   ├── stimuli/              # rendered binaural WAV files (external, not in repo)
│   └── figures/              # HRIR verification plots (external, not in repo)
├── ../results/               # per-participant CSV files (external, not in repo)
└── env/
    ├── requirements.txt
    └── environment.yml
```

---

## Experimental Design

### HRTF Datasets

| Condition | CIPIC Subject | Description |
|-----------|---------------|-------------|
| A | subject_003 | Human participant |
| B | subject_021 | KEMAR dummy head |

### Stimulus Conditions

- **Azimuth:** lateral = 0° (median plane, rear positions)
- **Elevation (CIPIC polar angle):**
  - Rear −51° → polar index 31 (≈129.375°)
  - Rear   0° → polar index 40 (180.000°)
  - Rear +51° → polar index 49 (≈230.625°)

Each source audio file produces **6 stimuli** (2 datasets × 3 elevations).

### Listening Task

Participants hear each stimulus over headphones and identify the perceived elevation:

| Key | Response |
|-----|----------|
| `1` | Up (above ear level) |
| `2` | Middle (ear level) |
| `3` | Down (below ear level) |
| `R` | Replay |
| `Q` | Quit (partial results saved) |

Trials are randomized per participant. Reaction time is recorded from playback start.

---

## Usage

### 1. Install dependencies

```bash
pip install -r env/requirements.txt
# or
conda env create -f env/environment.yml
```

### 2. Prepare source audio

Place audio files (`.wav`, `.mp3`, `.aiff`, `.flac`, `.ogg`) in `../dataset/my_raw/`, then run:

```bash
python src/prepare_source.py
```

This converts each file to **mono, 44 100 Hz, 15 s** with:
- Leading silence trimmed (threshold: −60 dBFS)
- 0.5 s cosine fade-in and fade-out
- Peak normalization

Output goes to `../dataset/my_proc/`.

### 3. Render binaural stimuli

```bash
python src/render_binaural.py
```

Convolves each processed source with HRIRs from both CIPIC subjects at all three rear elevations. Output WAVs are written to `outputs/stimuli/` using the naming convention:

```
{source}__{dataset}_{condition}.wav
# e.g. electric_guitar__cipic_human_rear_neg51.wav
```

### 4. Run the listening experiment

```bash
python src/run_experiment.py
```

Enter a participant ID when prompted (e.g. `p01`). Results are saved to `results/<participant_id>.csv` with the following columns:

| Column | Description |
|--------|-------------|
| `participant` | Participant ID |
| `trial` | Trial number |
| `source` | Source audio filename stem |
| `dataset` | CIPIC Human or CIPIC KEMAR |
| `elevation_deg` | Ground-truth elevation (−51, 0, +51) |
| `elevation_label` | Ground-truth label (down / middle / up) |
| `response` | Participant response |
| `correct` | Boolean |
| `rt_s` | Reaction time in seconds |

### 5. (Optional) Explore HRTF data

```bash
python src/explore_hrtf.py
```

Prints HRIR metadata and saves a verification plot to `outputs/figures/hrtf_verification.png`.

---

## Dependencies

| Package | Purpose |
|---------|---------|
| numpy / scipy | Signal processing, FFT convolution |
| soundfile | WAV read / write |
| pygame | Audio playback in listening test |
| pandas / seaborn | Results analysis and plotting |
| matplotlib | HRIR visualization |

CIPIC `.mat` files are loaded directly with `scipy.io.loadmat` — no additional SOFA library required.

---

## Expected Outcome

Human and KEMAR HRTFs encode elevation cues differently due to differences in pinna shape and measurement conditions. The experiment tests whether these differences translate to measurable changes in listeners' elevation identification accuracy for rear sound sources.
