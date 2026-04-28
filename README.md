# README

## Project Title
How Do Different HRTF Datasets Affect Rear Spatial Localization?

## Overview
This project studies how different HRTF datasets influence auditory perception in rear sound localization.

HRTF (Head-Related Transfer Function) describes how sound is filtered by the head, ears, and body before reaching the ears. Different datasets are created using different measurement methods, subjects, or dummy heads. These differences may affect how listeners perceive sounds coming from behind.

This project compares several HRTF datasets by rendering binaural audio and testing listener perception.

## Research Question
How do different HRTF datasets (representing different measurement methodologies) affect auditory perception in rear spatial localization?

## Objectives
- Compare 2–3 public HRTF datasets
- Render binaural audio using the same source sound
- Focus on rear sound positions
- Test listener accuracy in localization tasks
- Analyze which dataset performs better

---

## Phase 1: Prepare HRTF Data

### Selected Datasets
- :contentReference[oaicite:0]{index=0} (1 subject)
- :contentReference[oaicite:1]{index=1}
- Optional: :contentReference[oaicite:2]{index=2}

### Tasks
- Download SOFA files
- Load files in MATLAB or Python
- Extract left/right ear impulse responses

### Goal
Successfully read HRTF impulse responses.

---

## Phase 2: Binaural Rendering

Convert mono audio into stereo binaural audio using convolution.

### Process
For each sound direction:

- Left channel = signal * HRTF\_L  
- Right channel = signal * HRTF\_R

### Input Audio
Use short test sounds such as:

- White noise
- Click sound
- Speech sample

### Output
Stereo audio files for:

- Different datasets
- Different rear directions

---

## Phase 3: Experimental Conditions

### Fixed Direction
- Azimuth = 180° (rear)

### Elevation Conditions
- -30°
- 0°
- +30°

### Dataset Conditions
- Dataset A: CIPIC
- Dataset B: KEMAR
- Dataset C: IRCAM (optional)

### Total Stimuli
- 2 datasets × 3 elevations = 6 samples  
or  
- 3 datasets × 3 elevations = 9 samples

---

## Phase 4: Listening Test

### Participants
- Self + 2 to 5 classmates

### Task Option 1 (Recommended)
Identify elevation:

- Up
- Middle
- Down

### Task Option 2
Identify direction:

- Front
- Back

### Data Collection
For each trial record:

- Ground truth location
- Listener response

---

## Phase 5: Analysis

### Metrics

#### Accuracy
Correct responses for each dataset.

#### Confusion Rate
Check common mistakes such as:

- Up heard as middle
- Rear heard as front

### Visualization
- Bar chart for accuracy
- Confusion matrix (optional)

---

## Phase 6: Final Report Structure

1. Introduction  
2. Background (HRTF, spectral cues)  
3. Methodology  
4. Results  
5. Discussion  
6. Conclusion

---

## Tools

### Python Libraries
- numpy
- scipy
- soundfile
- pysofaconventions
- matplotlib

### MATLAB
- SOFA API
- Signal Processing Toolbox

---

## Expected Outcome
Different HRTF datasets may produce different rear localization performance because of differences in:

- Measurement technique
- Ear shape representation
- Subject specificity
- Spectral detail

This project helps understand how dataset choice impacts spatial audio perception.

---

## Author
Individual Project for Colloquy in Music Technology