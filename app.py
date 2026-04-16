"""
app.py – Streamlit app for the PList → CSV generator.

Run locally:
    streamlit run app.py
"""

import os

import pandas as pd
import streamlit as st

from plist_parser import FIELDNAMES, parse_plist_text, rows_to_csv_bytes

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="PList → CSV Generator",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Sidebar – options
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("⚙️ Options")
    hard_tupleid_en = st.checkbox(
        "Enable Hard Tuple ID",
        value=False,
        help=(
            "When checked, the 'Hard Tuple ID' column is populated with "
            "the first 8 characters of each Pat's leading identifier field."
        ),
    )
    preview_rows = st.slider(
        "Preview rows",
        min_value=5,
        max_value=100,
        value=20,
        step=5,
        help="Number of rows shown in the interactive preview table.",
    )
    st.divider()
    st.caption(
        "Upload a `.txt` file containing `GlobalPList ..._PLIST` blocks.  "
        "The app parses the blocks and lets you download the result as a CSV."
    )

# ---------------------------------------------------------------------------
# Main area
# ---------------------------------------------------------------------------
st.title("📋 PList → CSV Generator")
st.markdown(
    "Upload a `.txt` file with `GlobalPList ..._PLIST` blocks to generate "
    "a test-input CSV with columns: "
    + ", ".join(f"**{c}**" for c in FIELDNAMES)
    + "."
)

# File uploader
uploaded_file = st.file_uploader(
    "Upload input `.txt` file",
    type=["txt"],
    help=(
        "The file should contain one or more `GlobalPList NAME_PLIST { … }` "
        "blocks with nested `PList` and `Pat` entries."
    ),
)

# Optional filename override (for Plist derivation)
filename_override = st.text_input(
    "Override filename for Plist derivation",
    value="",
    placeholder="Leave blank to use the uploaded file's name",
    help=(
        "The Plist column is derived from tokens 1–2 of the filename split "
        "on '_'.  Override here if the uploaded name differs from the "
        "original INPUT_FILE name."
    ),
)

# ---------------------------------------------------------------------------
# Processing
# ---------------------------------------------------------------------------
if uploaded_file is not None:
    input_filename = filename_override.strip() or uploaded_file.name

    if st.button("⚙️ Generate CSV", type="primary"):
        raw_bytes = uploaded_file.read()
        text = raw_bytes.decode("utf-8", errors="replace")

        with st.spinner("Parsing…"):
            rows, warnings = parse_plist_text(
                text=text,
                input_filename=input_filename,
                hard_tupleid_en=hard_tupleid_en,
            )

        # Warnings
        if warnings:
            with st.expander(f"⚠️ {len(warnings)} warning(s)", expanded=True):
                for w in warnings:
                    st.warning(w)

        if not rows:
            st.error(
                "No rows were generated.  "
                "Check that the file contains `GlobalPList …_PLIST { … }` "
                "blocks with `Pat …;` entries, and review any warnings above."
            )
        else:
            st.success(f"✅ Generated **{len(rows)}** row(s).")

            # Preview table
            df = pd.DataFrame(rows, columns=FIELDNAMES)
            n_preview = min(preview_rows, len(rows))
            st.subheader(f"Preview (first {n_preview} of {len(rows)} rows)")
            st.dataframe(df.head(n_preview), use_container_width=True)

            # Download button
            csv_bytes = rows_to_csv_bytes(rows)
            base_name = os.path.splitext(uploaded_file.name)[0]
            output_name = base_name + "_output.csv"

            st.download_button(
                label="⬇️ Download CSV",
                data=csv_bytes,
                file_name=output_name,
                mime="text/csv",
            )
else:
    st.info("👆 Upload a `.txt` file above to get started.")
