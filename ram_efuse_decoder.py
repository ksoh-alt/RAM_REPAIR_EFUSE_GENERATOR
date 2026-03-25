import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# RAM Repair Dictionary (fill in your module‑specific rules)
# ---------------------------------------------------------
RAM_REPAIR_DICT = {
    # (upper_repair, upper_en, lower_repair, lower_en): "Meaning"
}


# ---------------------------------------------------------
# Helper: Auto-detect hex/bin and convert to 32‑bit
# ---------------------------------------------------------
def parse_input(value_str):
    value_str = value_str.strip().lower()

    # Hex format
    if value_str.startswith("0x"):
        try:
            val = int(value_str, 16)
            return format(val, "032b")
        except:
            return None

    # Binary format
    if all(c in "01" for c in value_str):
        try:
            val = int(value_str, 2)
            return format(val, "032b")
        except:
            return None

    return None


# ---------------------------------------------------------
# Core eFUSE decode logic
# ---------------------------------------------------------
def decode_efuse(bits):
    # Extract fields
    rsvd = bits[0:4]
    upper_col_repair = bits[4:11]
    upper_en = bits[11]
    lower_col_repair = bits[12:19]
    lower_en = bits[19]
    ram_block_id = bits[20:32]

    # Convert to integers
    upper_col_val = int(upper_col_repair, 2)
    lower_col_val = int(lower_col_repair, 2)
    upper_en_val = int(upper_en, 2)
    lower_en_val = int(lower_en, 2)
    block_id_val = int(ram_block_id, 2)

    key = (upper_col_val, upper_en_val, lower_col_val, lower_en_val)

    return {
        "RSVD (31:28)": int(rsvd, 2),
        "Upper Column Repair": upper_col_val,
        "Upper Redundancy Enable": upper_en_val,
        "Lower Column Repair": lower_col_val,
        "Lower Redundancy Enable": lower_en_val,
        "RAM BLOCK ID / CJTAG ID": block_id_val,
        "Module Repair Meaning": RAM_REPAIR_DICT.get(key, "No entry in dictionary"),
    }


# ---------------------------------------------------------
# UI Layout Formatting
# ---------------------------------------------------------
st.set_page_config(page_title="eFuse Decoder", layout="wide")
st.title("🔥 Enhanced eFuse Decoder Tool")

st.markdown("### Enter a 32-bit eFuse Value (Auto‑detects Hex or Bin)")

# History storage
if "history" not in st.session_state:
    st.session_state.history = []

input_value = st.text_input("HEX or Binary", placeholder="Example: 0xABCDEFFF or 101010...")

col1, col2 = st.columns([1, 1])

with col1:
    decode_btn = st.button("Decode eFuse")

with col2:
    clear_btn = st.button("Clear History")
    if clear_btn:
        st.session_state.history.clear()


# ---------------------------------------------------------
# Decode Logic
# ---------------------------------------------------------
if decode_btn:
    bits = parse_input(input_value)

    if bits is None:
        st.error("❌ Invalid input. Must be HEX (0x...) or Binary.")
    else:
        decoded = decode_efuse(bits)
        st.session_state.history.append({"Input": input_value, **decoded})

        st.success("✅ Decode Successful!")
        st.json(decoded)

        # -----------------------------------------------
        # Visual Bitfield Diagram
        # -----------------------------------------------
        st.markdown("## 🧩 32‑bit Visual Bit‑Field Map")
        
        bit_labels = [
            ("RSVD", bits[0:4]),
            ("Upper Col Repair", bits[4:11]),
            ("Upper EN", bits[11]),
            ("Lower Col Repair", bits[12:19]),
            ("Lower EN", bits[19]),
            ("RAM BLOCK ID", bits[20:32]),
        ]

        cols = st.columns(len(bit_labels))

        for i, (label, b) in enumerate(bit_labels):
            with cols[i]:
                st.markdown(
                    f"""
                    <div style="
                        background-color:#f5f5f5;
                        padding:10px;
                        border-radius:10px;
                        text-align:center;
                        border:1px solid #ddd;">
                        <b>{label}</b><br>
                        <code>{b}</code>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

# ---------------------------------------------------------
# GUI Sliders for Manual Bit Visualization
# ---------------------------------------------------------
st.markdown("## 🎚️ Bit Visualization Sliders")
st.write("Adjust fields and see the real‑time 32‑bit value:")

colA, colB = st.columns(2)

with colA:
    upper_col = st.slider("Upper Column Repair (7 bits)", 0, 127, 0)
    upper_en = st.slider("Upper Enable (1 bit)", 0, 1, 0)

with colB:
    lower_col = st.slider("Lower Column Repair (7 bits)", 0, 127, 0)
    lower_en = st.slider("Lower Enable (1 bit)", 0, 1, 0)

block_id = st.slider("RAM BLOCK ID (12 bits)", 0, 4095, 0)

rsvd = 0

visual_bits = (
    format(rsvd, "04b") +
    format(upper_col, "07b") +
    format(upper_en, "01b") +
    format(lower_col, "07b") +
    format(lower_en, "01b") +
    format(block_id, "012b")
)

st.markdown(f"### 🧮 Generated 32‑bit Value\n`{visual_bits}`")
st.markdown(f"HEX: **0x{format(int(visual_bits, 2), '08X')}**")


# ---------------------------------------------------------
# History Table
# ---------------------------------------------------------
st.markdown("## 📜 Decode History")

if len(st.session_state.history) > 0:
    df = pd.DataFrame(st.session_state.history)
    st.dataframe(df, use_container_width=True)
else:
    st.info("No history yet.")


st.caption("Built with ❤️ in Streamlit — fully enhanced edition.")
