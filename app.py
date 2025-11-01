# ============================================================
# 🎨 Interactive 3D-like Blob Poster (Streamlit version)
# ============================================================

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb
from matplotlib.patches import PathPatch
from matplotlib.path import Path
from matplotlib import transforms
import random, math, pandas as pd, os

# ----------------------------
# Blob function
# ----------------------------
def blob(center=(0.5, 0.5), r=0.2, points=200, wobble=0.2):
    angles = np.linspace(0, 2*math.pi, points)
    radii = r * (1 + wobble * (np.random.rand(points)-0.5))
    x = center[0] + radii * np.cos(angles)
    y = center[1] + radii * np.sin(angles)
    return x, y

# ----------------------------
# Palette Manager
# ----------------------------
PALETTE_FILE = "palette.csv"

# 初始化 CSV
if not os.path.exists(PALETTE_FILE):
    df_init = pd.DataFrame([
        {"name":"sky", "r":0.4, "g":0.7, "b":1.0},
        {"name":"sun", "r":1.0, "g":0.8, "b":0.2},
        {"name":"forest", "r":0.2, "g":0.6, "b":0.3}
    ])
    df_init.to_csv(PALETTE_FILE, index=False)

def load_csv_palette():
    df = pd.read_csv(PALETTE_FILE)
    return [(row.r, row.g, row.b) for _, row in df.iterrows()]

def make_palette(k=6, mode="pastel", base_h=0.6):
    if mode == "csv":
        return load_csv_palette()
    cols = []
    for _ in range(k):
        if mode=="pastel":
            h=random.random(); s=random.uniform(0.15,0.35); v=random.uniform(0.9,1.0)
        elif mode=="vivid":
            h=random.random(); s=random.uniform(0.8,1.0); v=random.uniform(0.8,1.0)
        elif mode=="mono":
            h=base_h; s=random.uniform(0.2,0.6); v=random.uniform(0.5,1.0)
        else:
            h=random.random(); s=random.uniform(0.3,1.0); v=random.uniform(0.5,1.0)
        cols.append(tuple(hsv_to_rgb([h,s,v])))
    return cols

# ----------------------------
# Draw poster
# ----------------------------
def draw_poster(n_layers, blob_radius_range, wobble_range, alpha_range, shadow_offset, palette_mode, seed):
    random.seed(seed); np.random.seed(seed)
    palette = make_palette(6, mode=palette_mode)

    fig, ax = plt.subplots(figsize=(6,8))
    ax.axis('off')
    ax.set_facecolor((0.97,0.97,0.97))
    blob_paths = []

    for _ in range(n_layers):
        radius = random.uniform(*blob_radius_range)
        wobble = random.uniform(*wobble_range)
        center = (random.uniform(0.05,0.95), random.uniform(0.05,0.95))
        x, y = blob(center, r=radius, wobble=wobble)
        vertices = np.column_stack([x,y])
        codes = [Path.MOVETO] + [Path.LINETO]*(len(vertices)-1)
        path = Path(vertices, codes)
        color = random.choice(palette)
        alpha = random.uniform(*alpha_range)
        blob_paths.append((path, color, alpha))

    # Draw shadows
    for path, color, alpha in blob_paths:
        shadow = PathPatch(
            path.transformed(transforms.Affine2D().translate(shadow_offset,-shadow_offset)),
            facecolor='black', edgecolor='none', alpha=alpha*0.15, zorder=-2
        )
        ax.add_patch(shadow)

    # Draw blobs
    for path, color, alpha in blob_paths:
        patch = PathPatch(path, facecolor=color, edgecolor='none', alpha=alpha, zorder=-1)
        ax.add_patch(patch)

    ax.text(0.05,0.95,f"Interactive Poster • {palette_mode}", fontsize=12, weight="bold", transform=ax.transAxes)
    st.pyplot(fig)

# ----------------------------
# Streamlit UI
# ----------------------------
st.title("🎨 Generative Blob Poster by He Pengwei")

n_layers = st.slider("Number of Layers", 3, 20, 8)
blob_radius_min, blob_radius_max = st.slider("Blob Radius Range", 0.05, 0.5, (0.1, 0.3))
wobble_min, wobble_max = st.slider("Wobble Range", 0.01, 0.5, (0.05, 0.25))
alpha_min, alpha_max = st.slider("Alpha Range", 0.1, 1.0, (0.3, 0.6))
shadow_offset = st.slider("Shadow Offset", 0.0, 0.1, 0.02)
palette_mode = st.selectbox("Palette Mode", ["pastel","vivid","mono","random","csv"])
seed = st.number_input("Seed", 0, 9999, 0)

if st.button("Generate Poster"):
    draw_poster(
        n_layers=n_layers,
        blob_radius_range=(blob_radius_min, blob_radius_max),
        wobble_range=(wobble_min, wobble_max),
        alpha_range=(alpha_min, alpha_max),
        shadow_offset=shadow_offset,
        palette_mode=palette_mode,
        seed=seed
    )
