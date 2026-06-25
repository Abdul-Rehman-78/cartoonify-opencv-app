# Cartoonify Image

A computer vision application that transforms photographs into cartoon-style images using OpenCV. The app provides live, interactive controls for smoothing, edge detection, color saturation, and posterization, along with one-click style presets (Anime, Comic Book, Disney).

## Group 12

| Name | Roll Number |
|---|---|
| Numan Ahmad Gohar | 2023-CS-521 |
| Abdul Rehman | 2023-CS-578 |
| Shumail Khan | 2023-CS-584 |

## Overview

The original input image goes through a pipeline of classic computer vision operations to produce a cartoon effect:

1. Grayscale conversion
2. Noise reduction (median blur)
3. Edge detection (adaptive thresholding or Canny + dilation)
4. Color smoothing (bilateral filter)
5. Saturation adjustment (HSV color space)
6. Posterization (color quantization)
7. Compositing edges with smoothed color to form the final cartoon

## Features

- Drag-and-drop or camera image upload
- Live sliders for smoothness, edge thickness, saturation, bilateral filter strength, and posterize levels
- Two edge styles: soft (adaptive threshold) and bold (Canny + dilation)
- Style presets: Anime, Comic Book, Disney
- "Surprise me" button to randomize all settings
- Before/after comparison view
- Download output as PNG or JPG

## Tech stack

- **Python** — core language
- **OpenCV (cv2)** — image processing: color conversion, blurring, edge detection, filtering, compositing
- **NumPy** — array-based image data and vectorized math
- **Pillow (PIL)** — image file decoding/encoding for upload and download
- **Streamlit** — web-based UI and live interactivity
- **streamlit-image-comparison** *(optional)* — drag-to-compare before/after slider

## Setup

```bash
pip install streamlit opencv-python-headless numpy pillow streamlit-image-comparison --break-system-packages
```

## Run

```bash
streamlit run cartoonify_app.py
```

This opens the app in your browser. Upload or capture an image, adjust the controls or pick a preset, then download the result.

## Project structure

```
.
├── cartoonify_app.py   # Main Streamlit application
└── README.md           # Project documentation
```

## How it works (technical summary)

| Step | OpenCV function | Purpose |
|---|---|---|
| Grayscale | `cv2.cvtColor` | Reduces image to brightness only, for edge detection |
| Denoise | `cv2.medianBlur` | Removes noise while preserving edges |
| Soft edges | `cv2.adaptiveThreshold` | Locally-adjusted thresholding for thin, hand-drawn outlines |
| Bold edges | `cv2.Canny` + `cv2.dilate` | Gradient-based edges, thickened for a comic-book look |
| Color smoothing | `cv2.bilateralFilter` | Flattens color regions while keeping edges sharp |
| Saturation | `cv2.cvtColor` (HSV) | Scales color intensity independent of brightness/hue |
| Posterize | Custom function (NumPy) | Reduces color levels for flat, graphic color blocks |
| Compositing | `cv2.bitwise_and` | Merges edge mask with smoothed color to form the cartoon |

## Course

Computer Vision — Course Project
