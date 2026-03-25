import streamlit as st
import pandas as pd
# ---------------------------------------------------------
# DEVICE-SPECIFIC CJTAGID MAPS
# ---------------------------------------------------------
CJTAG_MAP_SM7 = [
    (1, 12, 32),
    (13, 16, 33),
    (17, 20, 34),
    (21, 24, 35),
    (25, 27, 36),
    (28, 92, 37),
    (93, 96, 38),
    (97, 100, 39),
    (101, 104, 40),
    (105, 107, 41),
    (108, 172, 42),
    (173, 175, 43),
    (176, 240, 44),
    (241, 244, 45),
    (245, 248, 46),
    (249, 252, 47),
    (253, 255, 48),
    (256, 320, 49),
    (321, 332, 50),
    (333, 344, 51),
]
# ---------------------------------------------------------
# MODULE-SPECIFIC REDUNDANCY MAPS
# ---------------------------------------------------------
# ----------------------------
# LSM MODULE - ip756uhdsp11rf_2048x20m4b2wd_cnnnnnnlc
# ----------------------------
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
    # IOSSMCFG MODULE - ip756uhdsp11rf_2048x39m4b2wd_cnnnnnnlc
    # ----------------------------
    "IOSSMCFG": {
        "lower": {
            # fuse_code : faulty_column_index
            18: 0,
            17: 1,
            16: 2,
            15: 3,
            14: 4,
            13: 5,
            12: 6,
            11: 7,
            10: 8,
            9: 9,
            8: 10,
            7: 11,
            6: 12,
            5: 13,
            4: 14,
            3: 15,
            2: 16,
            1: 17,
            0: 18
        },
        "upper": {
            19: 38,
            18: 37,
            17: 36,
            16: 35,
            15: 34,
            14: 33,
            13: 32,
            12: 31,
            11: 30,
            10: 29,
            9: 28,
            8: 27,
            7: 26,
            6: 25,
            5: 24,
            4: 23,
            3: 22,
            2: 21,
            1: 20,
            0: 19
        }
    },

    # ----------------------------
    # IOSSMCAL CH0 MODULE - ip756uhdsp11rf_1024x39m4b1wd_cnnnnnnlc
    # ----------------------------
    "IOSSMCAL CH0": {
        "lower": {
            # fuse_code : faulty_column_index
            18: 0,
            17: 1,
            16: 2,
            15: 3,
            14: 4,
            13: 5,
            12: 6,
            11: 7,
            10: 8,
            9: 9,
            8: 10,
            7: 11,
            6: 12,
            5: 13,
            4: 14,
            3: 15,
            2: 16,
            1: 17,
            0: 18
        },
        "upper": {
            19: 38,
            18: 37,
            17: 36,
            16: 35,
            15: 34,
            14: 33,
            13: 32,
            12: 31,
            11: 30,
            10: 29,
            9: 28,
            8: 27,
            7: 26,
            6: 25,
            5: 24,
            4: 23,
            3: 22,
            2: 21,
            1: 20,
            0: 19
        }
    },

    # ----------------------------
    # IOSSMCAL CH1 MODULE - ip756uhdsp11rf_2048x39m4b2wd_cnnnnnnlc
    # ----------------------------
    "IOSSMCAL CH1": {
        "lower": {
            # fuse_code : faulty_column_index
            18: 0,
            17: 1,
            16: 2,
            15: 3,
            14: 4,
            13: 5,
            12: 6,
            11: 7,
            10: 8,
            9: 9,
            8: 10,
            7: 11,
            6: 12,
            5: 13,
            4: 14,
            3: 15,
            2: 16,
            1: 17,
            0: 18
        },
        "upper": {
            19: 38,
            18: 37,
            17: 36,
            16: 35,
            15: 34,
            14: 33,
            13: 32,
            12: 31,
            11: 30,
            10: 29,
            9: 28,
            8: 27,
            7: 26,
            6: 25,
            5: 24,
            4: 23,
            3: 22,
            2: 21,
            1: 20,
            0: 19
        }
    },

    # ----------------------------
    # CSSM RAM MODULE - ip756uhdsp11rf_2048x39m4b2wd_cnnnnnnlc
    # ----------------------------
    "CSSM RAM": {
        "lower": {
            # fuse_code : faulty_column_index
            18: 0,
            17: 1,
            16: 2,
            15: 3,
            14: 4,
            13: 5,
            12: 6,
            11: 7,
            10: 8,
            9: 9,
            8: 10,
            7: 11,
            6: 12,
            5: 13,
            4: 14,
            3: 15,
            2: 16,
            1: 17,
            0: 18
        },
        "upper": {
            19: 38,
            18: 37,
            17: 36,
            16: 35,
            15: 34,
            14: 33,
            13: 32,
            12: 31,
            11: 30,
            10: 29,
            9: 28,
            8: 27,
            7: 26,
            6: 25,
            5: 24,
            4: 23,
            3: 22,
            2: 21,
            1: 20,
            0: 19
        }
    },

    # ----------------------------
    # CSSM HIP2C MODULE - ip756hs2p11rf_1024x42m1b16wd_cnnnnnnnl
    # ----------------------------
    "CSSM HIP2C": {
        "lower": {
            # fuse_code : faulty_column_index
            19: 19,
            18: 18,
            17: 17,
            16: 16,
            15: 15,
            14: 14,
            13: 13,
            12: 12,
            11: 11,
            10: 10,
            9: 9,
            8: 8,
            7: 7,
            6: 6,
            5: 5,
            4: 4,
            3: 3,
            2: 2,
            1: 1,
            0: 0
        },
        "upper": {
            21: 41,
            20: 40,
            19: 39,
            18: 38,
            17: 37,
            16: 36,
            15: 35,
            14: 34,
            13: 33,
            12: 32,
            11: 31,
            10: 30,
            9: 29,
            8: 28,
            7: 27,
            6: 26,
            5: 25,
            4: 24,
            3: 23,
            2: 22,
            1: 21,
            0: 20
        }
    },

    # ----------------------------
    # CSSM DVP MODULE - ip756hs2p11rf_1024x72m1b16wd_cnnnnsdgh
    # ----------------------------
    "CSSM DVP": {
        "lower": {
            # fuse_code : faulty_column_index
            35: 35,
            34: 34,
            33: 33,
            32: 32,
            31: 31,
            30: 30,
            29: 29,
            28: 28,
            27: 27,
            26: 26,
            25: 25,
            24: 24,
            23: 23,
            22: 22,
            21: 21,
            20: 20,
            19: 19,
            18: 18,
            17: 17,
            16: 16,
            15: 15,
            14: 14,
            13: 13,
            12: 12,
            11: 11,
            10: 10,
            9: 9,
            8: 8,
            7: 7,
            6: 6,
            5: 5,
            4: 4,
            3: 3,
            2: 2,
            1: 1,
            0: 0
        },
        "upper": {
            35: 71,
            34: 70,
            33: 69,
            32: 68,
            31: 67,
            30: 66,
            29: 65,
            28: 64,
            27: 63,
            26: 62,
            25: 61,
            24: 60,
            23: 59,
            22: 58,
            21: 57,
            20: 56,
            19: 55,
            18: 54,
            17: 53,
            16: 52,
            15: 51,
            14: 50,
            13: 49,
            12: 48,
            11: 47,
            10: 46,
            9: 45,
            8: 44,
            7: 43,
            6: 42,
            5: 41,
            4: 40,
            3: 39,
            2: 38,
            1: 37,
            0: 36
        }
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
# Helper: CJTAGID LOOKUP
# ---------------------------------------------------------
def lookup_cjtag(selected_device, ram_block_id):
    if selected_device == "SM7":
        for lo, hi, cid in CJTAG_MAP_SM7:
            if lo <= ram_block_id <= hi:
                return cid
        return "Out of Range"

    # Placeholder for other devices
    if selected_device == "SM4":
        return "Not Implemented"

    if selected_device == "SM1":
        return "Not Implemented"

    return "Unknown Device"

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

        "RAM BLOCK ID": block_id,
        "CJTAGID": lookup_cjtag(selected_device, block_id),
    }


# ---------------------------------------------------------
# UI
# ---------------------------------------------------------
st.set_page_config(page_title="eFuse Decoder", layout="wide")
st.title("🔥 Multi‑Module eFuse Decoder")

# Module selector
device_list = ["SM7"]
selected_device = st.selectbox("Select Device:", device_list)
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
