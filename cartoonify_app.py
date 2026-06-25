"""
Cartoonify Image - Streamlit app
---------------------------------
Run with:  streamlit run cartoonify_app.py

Requires: streamlit, opencv-python, numpy, pillow
Install:  pip install streamlit opencv-python-headless numpy pillow --break-system-packages

----> Group 12
--> Numan Ahmad 2023-CS-521
--> Abdul Rehman 2023-CS- 578
--> Shumail 2023-CS-584

"""


import io

import cv2
import numpy as np
import streamlit as st
from PIL import Image

st.set_page_config(page_title="Cartoonify", page_icon="🎨", layout="wide")

# ---------- core image processing ----------

def odd(n: int) -> int:
    """OpenCV needs odd kernel/block sizes."""
    return n if n % 2 == 1 else n + 1


def adjust_saturation(image_rgb: np.ndarray, factor: float) -> np.ndarray:
    """factor: 1.0 = unchanged, 0 = grayscale, 2.0 = double saturation."""
    hsv = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2HSV).astype(np.float32)
    hsv[..., 1] = np.clip(hsv[..., 1] * factor, 0, 255)
    hsv = hsv.astype(np.uint8)
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)


def posterize(image_rgb: np.ndarray, levels: int) -> np.ndarray:
    """Reduce the number of color levels per channel (comic-book flat color look)."""
    if levels >= 32:
        return image_rgb
    factor = 255 / (levels - 1)
    return (np.round(image_rgb / factor) * factor).astype(np.uint8)


def get_edges(gray: np.ndarray, smoothness: int, edge_thickness: int, edge_style: str) -> np.ndarray:
    smoothness = odd(smoothness)
    edge_thickness = odd(edge_thickness)
    smooth_gray = cv2.medianBlur(gray, smoothness)

    if edge_style == "soft":
        edges = cv2.adaptiveThreshold(
            smooth_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY, edge_thickness, edge_thickness,
        )
    else:  # "bold" - thicker, darker lines via Canny + dilation
        canny = cv2.Canny(smooth_gray, 60, 150)
        kernel = np.ones((2, 2), np.uint8)
        canny = cv2.dilate(canny, kernel, iterations=1)
        edges = 255 - canny  # white background, black lines, matches mask convention

    return edges


def cartoonify(
    image_rgb: np.ndarray,
    smoothness: int = 5,
    edge_thickness: int = 9,
    saturation: float = 1.0,
    bilateral_strength: int = 9,
    edge_style: str = "soft",
    posterize_levels: int = 32,
) -> np.ndarray:
    gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
    edges = get_edges(gray, smoothness, edge_thickness, edge_style)

    color = cv2.bilateralFilter(image_rgb, bilateral_strength, 250, 250)
    color = posterize(color, posterize_levels)
    color = adjust_saturation(color, saturation)

    cartoon = cv2.bitwise_and(color, color, mask=edges)
    return cartoon


# ---------- presets ----------

PRESETS = {
    "Anime": dict(smoothness=5, edge_thickness=7, saturation=1.4,
                  bilateral_strength=12, edge_style="soft", posterize_levels=32),
    "Comic book": dict(smoothness=7, edge_thickness=9, saturation=1.6,
                        bilateral_strength=9, edge_style="bold", posterize_levels=6),
    "Disney": dict(smoothness=9, edge_thickness=9, saturation=1.1,
                   bilateral_strength=15, edge_style="soft", posterize_levels=16),
}


# ---------- helpers ----------

def load_image(uploaded_file) -> np.ndarray:
    img = Image.open(uploaded_file).convert("RGB")
    return np.array(img)


def to_png_bytes(image_rgb: np.ndarray) -> bytes:
    img = Image.fromarray(image_rgb)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def to_jpg_bytes(image_rgb: np.ndarray) -> bytes:
    img = Image.fromarray(image_rgb)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=92)
    return buf.getvalue()


# ---------- session state defaults ----------

defaults = dict(smoothness=5, edge_thickness=9, saturation=1.0,
                 bilateral_strength=9, edge_style="soft", posterize_levels=32)
for k, v in defaults.items():
    st.session_state.setdefault(k, v)


def apply_preset(name: str):
    for k, v in PRESETS[name].items():
        st.session_state[k] = v


def surprise_me():
    import random
    st.session_state.smoothness = random.choice([3, 5, 7, 9])
    st.session_state.edge_thickness = random.choice([3, 5, 7, 9, 11])
    st.session_state.saturation = round(random.uniform(0.6, 1.8), 1)
    st.session_state.bilateral_strength = random.choice([5, 9, 12, 15])
    st.session_state.edge_style = random.choice(["soft", "bold"])
    st.session_state.posterize_levels = random.choice([4, 6, 8, 16, 32])


# ---------- layout ----------

st.title("🎨 Cartoonify your image")

left, right = st.columns([1, 1.3])

with left:
    uploaded_file = st.file_uploader(
        "Upload an image", type=["png", "jpg", "jpeg"],
        help="Drag and drop or browse for a file"
    )
    camera_file = st.camera_input("Or take a photo")
    source_file = camera_file or uploaded_file

    st.markdown("**Presets**")
    p1, p2, p3 = st.columns(3)
    if p1.button("Anime", use_container_width=True):
        apply_preset("Anime")
    if p2.button("Comic book", use_container_width=True):
        apply_preset("Comic book")
    if p3.button("Disney", use_container_width=True):
        apply_preset("Disney")
    if st.button("🎲 Surprise me", use_container_width=True):
        surprise_me()

    st.markdown("**Controls**")
    st.slider("Smoothness", 1, 15, step=2, key="smoothness")
    st.slider("Edge thickness", 3, 15, step=2, key="edge_thickness")
    st.slider("Color saturation", 0.0, 2.0, step=0.1, key="saturation")
    st.slider("Bilateral filter strength", 3, 20, key="bilateral_strength")
    st.select_slider("Posterize levels (fewer = flatter colors)",
                      options=[4, 6, 8, 16, 32], key="posterize_levels")
    st.radio("Edge style", ["soft", "bold"], key="edge_style", horizontal=True)

with right:
    if source_file is None:
        st.info("Upload or capture an image to get started.")
    else:
        original = load_image(source_file)

        with st.spinner("Cartoonifying..."):
            cartoon = cartoonify(
                original,
                smoothness=st.session_state.smoothness,
                edge_thickness=st.session_state.edge_thickness,
                saturation=st.session_state.saturation,
                bilateral_strength=st.session_state.bilateral_strength,
                edge_style=st.session_state.edge_style,
                posterize_levels=st.session_state.posterize_levels,
            )

        tab1, tab2 = st.tabs(["Before / after", "Side by side"])

        with tab1:
            try:
                from streamlit_image_comparison import image_comparison
                image_comparison(
                    img1=Image.fromarray(original),
                    img2=Image.fromarray(cartoon),
                    label1="Original",
                    label2="Cartoon",
                )
            except ImportError:
                st.caption(
                    "Install `streamlit-image-comparison` for a drag slider "
                    "(`pip install streamlit-image-comparison --break-system-packages`). "
                    "Showing side by side instead."
                )
                c1, c2 = st.columns(2)
                c1.image(original, caption="Original", use_container_width=True)
                c2.image(cartoon, caption="Cartoon", use_container_width=True)

        with tab2:
            c1, c2 = st.columns(2)
            c1.image(original, caption="Original", use_container_width=True)
            c2.image(cartoon, caption="Cartoon", use_container_width=True)

        st.markdown("**Download**")
        d1, d2 = st.columns(2)
        d1.download_button(
            "Download PNG", data=to_png_bytes(cartoon),
            file_name="cartoonified.png", mime="image/png", use_container_width=True,
        )
        d2.download_button(
            "Download JPG", data=to_jpg_bytes(cartoon),
            file_name="cartoonified.jpg", mime="image/jpeg", use_container_width=True,
        )
