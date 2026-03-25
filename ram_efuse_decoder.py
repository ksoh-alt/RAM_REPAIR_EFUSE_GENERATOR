import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# MODULE-SPECIFIC REDUNDANCY MAPS
# ---------------------------------------------------------
MODULE_SPECS = {
    "LSM": {
        "lower": {
            # fuse_code : faulty_column_index
            9: 0,
            8: 1,
            7: 2,
            6: 3,
            5: 4,
            4: 5,
            3: 6,
            2: 7,
            1: 8,
            0: 9
        },
        "upper": {
            9: 19,
            8: 18,
            7: 17,
            6: 16,
            5: 15,
            4: 14,
            3: 13,
            2: 12,
            1: 11,
            0: 10
        }
    },

    # ----------------------------
    # SAMPLE MODULE (Replace these)
    # ----------------------------
    "IOSSM": {
        "lower": {i: i for i in range(0, 10)},   # placeholder
        "upper": {i: i+10 for i in range(0, 10)} # placeholder
    },

    # ----------------------------
    # SAMPLE MODULE (Replace these)
    # ----------------------------
    "CSSM": {
        "lower": {9-i: i for i in range(0, 10)},  # placeholder
        "upper": {9-i: i+10 for i in range(0, 10)} # placeholder
    }
}

# ---------------------------------------------------------
# Helper: Auto-detect hex/bin and convert to 32‑bit
# ---------------------------------------------------------
def parse_input(value_str):
    value_str = value_str.strip().lower()

    # Hex input
    if value_str.startswith("0x"):
        try:
            val = int(value_str, 16)
            return format(val, "032b")
        except:
            return None

    # Binary input
    if all(c in "01" for c in value_str):
        try:
            val = int(value_str, 2)
            return format(val, "032b")
        except:
            return None

    return None

# ---------------------------------------------------------
# Main decoder (module-aware)
# ---------------------------------------------------------
def decode_efuse(bits, module):
    spec = MODULE_SPECS[module]

    rsvd = bits[0:4]
    upper_col_code = int(bits[4:11], 2)
    upper_enable = int(bits[11], 2)
    lower_col_code = int(bits[12:19], 2)
    lower_enable = int(bits[19], 2)
    block_id = int(bits[20:32], 2)

    # Reverse lookup using module-specific maps
    lower_fault = spec["lower"].get(lower_col_code, "Invalid")
    upper_fault = spec["upper"].get(upper_col_code, "Invalid")

    return {
        "Module": module,
        "RSVD (31:28)": int(rsvd, 2),

        "Upper Repair Code (raw)": upper_col_code,
        "Upper Redundancy Enable": upper_enable,
        "Upper Faulty Column": upper_fault if upper_enable else "Disabled",

        "Lower Repair Code (raw)": lower_col_code,
        "Lower Redundancy Enable": lower_enable,
        "Lower Faulty Column": lower_fault if lower_enable else "Disabled",

        "RAM BLOCK ID / CJTAG ID": block_id
    }


# ---------------------------------------------------------
# UI
# ---------------------------------------------------------
st.set_page_config(page_title="eFuse Decoder", layout="wide")
st.title("🔥 Multi‑Module eFuse Decoder")

# Module selector
module_list = list(MODULE_SPECS.keys())
selected_module = st.selectbox("Select Module:", module_list)

st.markdown("### Enter a 32‑bit eFuse value (Hex or Binary — auto-detected)")
input_value = st.text_input("Input", placeholder="0xABCDEFFF or 1010101010...")

# History
if "history" not in st.session_state:
    st.session_state.history = []

col1, col2 = st.columns([1, 1])
with col1:
    decode_btn = st.button("Decode")

with col2:
    if st.button("Clear History"):
        st.session_state.history.clear()


# ---------------------------------------------------------
# Decode Logic
# ---------------------------------------------------------
if decode_btn:
    bits = parse_input(input_value)
    if bits is None:
        st.error("❌ Invalid input. Must be HEX (0x...) or Binary.")
    else:
        decoded = decode_efuse(bits, selected_module)
        st.session_state.history.append({"Input": input_value, **decoded})

        st.success("✅ Decode Successful!")
        st.json(decoded)

        # -----------------------------------------------
        # 32-bit Bit-Field Diagram
        # -----------------------------------------------
        st.markdown("## 🧩 32‑bit Bit‑Field Map")

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
                        padding:12px;
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
# History
# ---------------------------------------------------------
st.markdown("## 📜 Decode History")

if len(st.session_state.history) > 0:
    df = pd.DataFrame(st.session_state.history)
    st.dataframe(df, use_container_width=True)
else:
    st.info("No history yet.")

st.caption("Built with ❤️ in Streamlit — Multi‑Module Edition")
