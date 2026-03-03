import random
import json
import io
from typing import List, Tuple

import streamlit as st

# -------------------------------
# Utility functions
# -------------------------------
def rand_hex() -> str:
    """Generate a random hex color like #A1B2C3."""
    return "#{:06X}".format(random.randint(0, 0xFFFFFF))

def hex_to_rgb(h: str) -> Tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(r: int, g: int, b: int) -> str:
    return "#{:02X}{:02X}{:02X}".format(r, g, b)

def rel_luminance(rgb: Tuple[int, int, int]) -> float:
    """Relative luminance per WCAG."""
    def chan(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = rgb
    R, G, B = chan(r), chan(g), chan(b)
    return 0.2126 * R + 0.7152 * G + 0.0722 * B

def contrast_ratio(fg_hex: str, bg_hex: str) -> float:
    L1 = rel_luminance(hex_to_rgb(fg_hex))
    L2 = rel_luminance(hex_to_rgb(bg_hex))
    lighter = max(L1, L2)
    darker = min(L1, L2)
    return (lighter + 0.05) / (darker + 0.05)

def best_text_color(bg_hex: str) -> str:
    """Return #000000 or #FFFFFF depending on contrast with background."""
    black = "#000000"
    white = "#FFFFFF"
    c_black = contrast_ratio(black, bg_hex)
    c_white = contrast_ratio(white, bg_hex)
    return black if c_black >= c_white else white

def init_palette(n: int) -> List[dict]:
    return [{"hex": rand_hex(), "locked": False} for _ in range(n)]

def ensure_session_state():
    if "palette" not in st.session_state:
        st.session_state.palette = init_palette(5)
    if "seed" not in st.session_state:
        st.session_state.seed = ""
    if "last_seed" not in st.session_state:
        st.session_state.last_seed = None

# -------------------------------
# UI
# -------------------------------
st.set_page_config(page_title="HEX Code Generator", page_icon="🎨", layout="wide")
st.title("🎨 HEX Code Generator")
st.caption("Generate, lock, tweak, and export color palettes.")

ensure_session_state()

with st.sidebar:
    st.header("Controls")
    # Seed for reproducibility
    seed_input = st.text_input("Random seed (optional)", value=st.session_state.seed, placeholder="e.g., 2026-03-03 or any text/number")
    if seed_input != st.session_state.seed:
        st.session_state.seed = seed_input

    # Palette size
    palette_size = st.slider("Palette size", min_value=1, max_value=12, value=len(st.session_state.palette), step=1)
    if palette_size != len(st.session_state.palette):
        # Resize while preserving existing (locked) entries if possible
        current = st.session_state.palette
        if palette_size > len(current):
            st.session_state.palette = current + init_palette(palette_size - len(current))
        else:
            st.session_state.palette = current[:palette_size]

    st.markdown("---")
    st.subheader("Export")
    # Prepare export data
    export_list = [{"hex": p["hex"], "locked": p["locked"]} for p in st.session_state.palette]
    json_bytes = json.dumps(export_list, indent=2).encode("utf-8")
    csv_str = "hex,locked\n" + "\n".join([f'{p["hex"]},{p["locked"]}' for p in st.session_state.palette])
    csv_bytes = csv_str.encode("utf-8")

    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        st.download_button(
            label="⬇️ JSON",
            data=json_bytes,
            file_name="palette.json",
            mime="application/json",
            use_container_width=True
        )
    with col_exp2:
        st.download_button(
            label="⬇️ CSV",
            data=csv_bytes,
            file_name="palette.csv",
            mime="text/csv",
            use_container_width=True
        )

# Randomize button(s)
col_actions = st.columns([1, 1, 2, 2])
with col_actions[0]:
    if st.button("🎲 Randomize", use_container_width=True):
        # Apply seed if provided
        if st.session_state.seed:
            random.seed(st.session_state.seed)
        else:
            random.seed(None)

        for p in st.session_state.palette:
            if not p["locked"]:
                p["hex"] = rand_hex()
        st.session_state.last_seed = st.session_state.seed

with col_actions[1]:
    if st.button("♻️ Shuffle (unlocked)", use_container_width=True):
        # Shuffle only unlocked colors
        unlocked = [p["hex"] for p in st.session_state.palette if not p["locked"]]
        random.shuffle(unlocked)
        i = 0
        for p in st.session_state.palette:
            if not p["locked"]:
                p["hex"] = unlocked[i]
                i += 1

with col_actions[2]:
    st.write("")
    st.caption("Tip: Lock colors you like, then randomize to fill the rest.")

with col_actions[3]:
    st.write("")
    if st.session_state.last_seed:
        st.caption(f"Last seed used: `{st.session_state.last_seed}`")

st.markdown("---")

# Palette grid
cols = st.columns(min(6, len(st.session_state.palette)) if len(st.session_state.palette) > 0 else 1)

for i, p in enumerate(st.session_state.palette):
    col = cols[i % len(cols)]
    with col:
        bg = p["hex"]
        text = best_text_color(bg)
        contrast_black = contrast_ratio("#000000", bg)
        contrast_white = contrast_ratio("#FFFFFF", bg)
        contrast = max(contrast_black, contrast_white)

        st.markdown(
            f"""
            <div style="
                border-radius: 8px;
                overflow: hidden;
                border: 1px solid #e5e7eb;
                margin-bottom: 8px;
                box-shadow: 0 1px 2px rgba(0,0,0,0.05);
            ">
                <div style="
                    background: {bg};
                    color: {text};
                    height: 100px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: 600;
                    letter-spacing: 0.5px;
                ">
                    {bg}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Color picker to tweak
        new_color = st.color_picker("Pick", value=bg, key=f"picker_{i}", help="Adjust the color", label_visibility="collapsed")
        if new_color != p["hex"]:
            p["hex"] = new_color

        # Lock toggle and copy
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            p["locked"] = st.toggle("🔒 Lock", value=p["locked"], key=f"lock_{i}")
        with c2:
            st.write("")  # alignment spacer
            st.write(f"WCAG contrast: **{contrast:.2f}**")
        with c3:
            st.write("")
            st.code(bg, language=None)  # Displays hex for quick copy
            st.button("Copy HEX", key=f"copy_{i}", help="Double-click to select hex above and copy")

        # RGB preview
        r, g, b = hex_to_rgb(p["hex"])
        st.caption(f"RGB: {r}, {g}, {b}")

st.markdown("---")
st.subheader("About the contrast")
st.write(
    "We compute contrast ratio using WCAG relative luminance. A ratio of **4.5:1** is generally recommended for normal text, "
    "and **3:1** for large text."
)
