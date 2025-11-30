# Summerlands – De ultieme tartan-generator (2025)
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO
import json

# === Laad kleuren & tartans ===
@st.cache_data
def load_data():
    with open("colors.json") as f:
        colors = json.load(f)
    with open("tartans.json") as f:
        tartans = json.load(f)
    return colors, tartans

COLORS, TARTANS = load_data()

def parse_threadcount(tc: str):
    parts = [p.strip() for p in tc.replace(",", " ").split() if p.strip()]
    pattern = []
    for part in parts:
        part = part.upper()
        color = None
        num_str = part
        for c in sorted(COLORS.keys(), key=len, reverse=True):
            if part.startswith(c):
                color = c
                num_str = part[len(c):]
                break
        if color and color in COLORS:
            count = 1.0 if not num_str else float(num_str)
            pattern.append((color, count))
    return pattern

def build_sett(pattern):
    f_counts = [c for _, c in pattern]
    f_colors  = [col for col, _ in pattern]
    return f_counts + f_counts[::-1][1:], f_colors + f_colors[::-1][1:]

def create_tartan(pattern, size=900, scale=1):
    sett_counts, sett_colors = build_sett(pattern)
    widths = [max(1, int(round(c * scale))) for c in sett_counts]
    total_w = sum(widths)
    tartan = np.zeros((total_w, total_w, 3), dtype=np.uint8)
    pos = 0
    for w, col in zip(widths, sett_colors):
        tartan[:, pos:pos+w] = COLORS[col]
        pos += w
    weft = tartan.copy().transpose(1, 0, 2)
    result = np.minimum(tartan + weft, 255).astype(np.uint8)
    pil_img = Image.fromarray(result)
    final = pil_img.resize((size, size), Image.NEAREST)
    return np.array(final)

st.set_page_config(page_title="Summerlands – Tartan Mirror", layout="centered")
st.title("Summerlands – 531 Schotse Tartans")

selected = st.selectbox(
    "Zoek een tartan (typ naam)",
    options=[""] + sorted(TARTANS.keys()),
    format_func=lambda x: "– Kies een tartan –" if not x else x
)

tc = TARTANS.get(selected, "") if selected else st.text_input("Of handmatig", "G1 K6 B3 R1")

col1, col2 = st.columns([3, 1])
with col2:
    scale = st.slider("Schaal", 1, 100, 1)

if tc.strip():
    pattern = parse_threadcount(tc)
    if pattern:
        img = create_tartan(pattern, size=900, scale=scale)
        st.image(img, use_column_width=True)
        buf = BytesIO()
        plt.imsave(buf, img, format="png")
        buf.seek(0)
        st.download_button("Download", buf,
                           file_name=f"Summerlands_{selected.replace(' ', '_') if selected else 'custom'}.png",
                           mime="image/png")

st.caption("Summerlands – door jou gebouwd. Voor altijd.")
