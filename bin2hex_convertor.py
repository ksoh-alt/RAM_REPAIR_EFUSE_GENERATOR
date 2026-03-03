import re
import io
from typing import Tuple

import streamlit as st

# -------------------------------
# Helpers (formatting & parsing)
# -------------------------------
BIN_RE = re.compile(r"^[01_ \t]+$", re.IGNORECASE)
HEX_RE = re.compile(r"^[0-9a-f_ \t]+$", re.IGNORECASE)

def clean_prefixes(s: str) -> Tuple[str, str]:
    """Return (cleaned_string, detected_base). Detects 0b/0x prefix."""
    s = s.strip()
    if s.lower().startswith("0b"):
        return s[2:], "bin"
    if s.lower().startswith("0x"):
        return s[2:], "hex"
    return s, "unknown"

def strip_separators(s: str) -> str:
    """Remove spaces and underscores commonly used as visual separators."""
    return re.sub(r"[ _\t]", "", s)

def validate_binary(s: str) -> Tuple[bool, str]:
    if s == "":
        return False, "Empty input."
    if not BIN_RE.match(s):
        # find first offending character
        for i, ch in enumerate(s):
            if ch not in ("0", "1", " ", "_", "\t"):
                return False, f"Invalid binary character `{ch}` at position {i+1}."
        return False, "Invalid binary string."
    return True, ""

def validate_hex(s: str) -> Tuple[bool, str]:
    if s == "":
        return False, "Empty input."
    if not HEX_RE.match(s):
        for i, ch in enumerate(s):
            if not (ch.isdigit() or ch.lower() in "abcdef" or ch in (" ", "_", "\t")):
                return False, f"Invalid hex character `{ch}` at position {i+1}."
        return False, "Invalid hexadecimal string."
    return True, ""

def pad_left(s: str, group: int) -> str:
    """Pad on the left so length is a multiple of group (e.g., 4 for nibbles)."""
    rem = len(s) % group
    return s if rem == 0 else "0" * (group - rem) + s

def group_str(s: str, group: int, sep: str = " ") -> str:
    return sep.join(s[i:i+group] for i in range(0, len(s), group))

def to_download_bytes(text: str, filename_hint: str) -> Tuple[bytes, str]:
    return text.encode("utf-8"), filename_hint

# -------------------------------
# Streamlit UI
# -------------------------------
st.set_page_config(page_title="Binary ⇄ Hex Converter", page_icon="🔄", layout="centered")
st.title("🔄 Binary ⇄ Hexadecimal Converter")
st.caption("Clean, validate, and convert in real-time. Supports grouping and prefixes (`0b`, `0x`).")

with st.sidebar:
    st.header("Display Options")
    group_mode = st.selectbox(
        "Grouping",
        [
            "No grouping",
            "Nibbles (4 bits)",
            "Bytes (8 bits)",
            "Words (16 bits)",
            "Double words (32 bits)"
        ],
        index=1
    )
    sep = st.text_input("Separator", value=" ")
    show_prefix = st.checkbox("Show prefixes (0b / 0x) in output", value=True)
    visualize_little_endian = st.checkbox("Visualize little-endian grouping", value=False,
                                          help="Reverse group order for display only. Does not change numeric value.")

    st.markdown("---")
    st.subheader("Batch Mode")
    batch_hint = st.caption("Paste multiple lines to convert them all at once.")

tab_bin_hex, tab_hex_bin, tab_batch = st.tabs(["Binary → Hex", "Hex → Binary", "Batch Convert"])

# Map grouping choice
group_map = {
    "No grouping": 0,
    "Nibbles (4 bits)": 4,
    "Bytes (8 bits)": 8,
    "Words (16 bits)": 16,
    "Double words (32 bits)": 32,
}
group_size = group_map[group_mode]

def maybe_group(s: str, group: int) -> str:
    if group <= 0 or len(s) == 0:
        return s
    # Reverse groups for little-endian visualization
    if visualize_little_endian:
        s = group_str(s, group, sep="")
        parts = [s[i:i+group] for i in range(0, len(s), group)]
        parts.reverse()
        s = "".join(parts)
    return group_str(s, group, sep=sep)

with tab_bin_hex:
    st.subheader("Binary → Hex")

    bin_input = st.text_area("Binary input", placeholder="e.g., 0b1011_0010 1111", height=120)
    cleaned, base = clean_prefixes(bin_input)
    valid, err = validate_binary(cleaned) if cleaned else (False, "")

    if bin_input:
        if not valid:
            st.error(err or "Please enter only 0 and 1 (spaces/underscores allowed).")
        else:
            raw = strip_separators(cleaned)
            # Pad to multiple of 4 for nibble alignment
            padded = pad_left(raw, 4)
            # Convert
            value = int(padded, 2)
            hex_str = f"{value:X}"
            # Keep full-width hex aligned to binary nibble-length
            # e.g., 8 bits -> 2 hex, 12 bits -> 3 hex, etc.
            target_hex_len = (len(padded) + 3) // 4
            hex_str = hex_str.rjust(target_hex_len, "0")

            # Display formats
            grouped_bin = maybe_group(padded, 4 if group_size == 0 else group_size)
            grouped_hex = hex_str
            if group_size > 0:
                # Convert hex grouping matched to chosen grouping (divide by 4)
                hex_group = max(1, group_size // 4)
                # When visualizing little-endian, reverse hex groups too
                hex_chunks = [grouped_hex[i:i+hex_group] for i in range(0, len(grouped_hex), hex_group)]
                if visualize_little_endian:
                    hex_chunks.reverse()
                grouped_hex = sep.join(hex_chunks)

            out_bin = f"0b {grouped_bin}" if show_prefix else grouped_bin
            out_hex = f"0x {grouped_hex}" if show_prefix else grouped_hex

            st.markdown("**Result**")
            c1, c2 = st.columns(2)
            with c1:
                st.text_area("Binary (normalized)", value=out_bin, height=100, label_visibility="visible")
                st.code(out_bin, language=None)
                st.download_button("⬇️ Download Binary", *to_download_bytes(out_bin, "binary.txt"))
            with c2:
                st.text_area("Hexadecimal", value=out_hex, height=100, label_visibility="visible")
                st.code(out_hex, language=None)
                st.download_button("⬇️ Download Hex", *to_download_bytes(out_hex, "hex.txt"))

with tab_hex_bin:
    st.subheader("Hex → Binary")

    hex_input = st.text_area("Hex input", placeholder="e.g., 0xB2_F", height=120)
    cleaned_h, base_h = clean_prefixes(hex_input)
    valid_h, err_h = validate_hex(cleaned_h) if cleaned_h else (False, "")

    if hex_input:
        if not valid_h:
            st.error(err_h or "Please enter only 0–9 and A–F (spaces/underscores allowed).")
        else:
            raw_h = strip_separators(cleaned_h)
            value = int(raw_h, 16)
            bin_str = f"{value:b}"
            # Pad on left to nibble boundary so hex digits map back 1:4
            target_bin_len = len(raw_h) * 4
            bin_str = bin_str.rjust(target_bin_len, "0")

            grouped_bin = bin_str
            if group_size > 0:
                grouped_bin = maybe_group(bin_str, group_size)
            grouped_hex = raw_h.upper()
            if group_size > 0:
                hex_group = max(1, group_size // 4)
                chunks = [grouped_hex[i:i+hex_group] for i in range(0, len(grouped_hex), hex_group)]
                if visualize_little_endian:
                    chunks.reverse()
                grouped_hex = sep.join(chunks)

            out_hex = f"0x {grouped_hex}" if show_prefix else grouped_hex
            out_bin = f"0b {grouped_bin}" if show_prefix else grouped_bin

            st.markdown("**Result**")
            c1, c2 = st.columns(2)
            with c1:
                st.text_area("Hexadecimal (normalized)", value=out_hex, height=100)
                st.code(out_hex, language=None)
                st.download_button("⬇️ Download Hex", *to_download_bytes(out_hex, "hex.txt"))
            with c2:
                st.text_area("Binary", value=out_bin, height=100)
                st.code(out_bin, language=None)
                st.download_button("⬇️ Download Binary", *to_download_bytes(out_bin, "binary.txt"))

with tab_batch:
    st.subheader("Batch Convert")
    st.caption("Paste lines of **binary or hex**. We’ll auto-detect `0b`/`0x` or infer from characters.")
    batch_text = st.text_area("Input (one value per line)", height=200,
                              placeholder="Examples:\n0b1010_1100\n0xDEAD_BEEF\n11110000 00001111\nABCD")

    if st.button("Convert Batch"):
        if not batch_text.strip():
            st.warning("Nothing to convert.")
        else:
            lines = batch_text.splitlines()
            out_lines = []
            for ln in lines:
                original = ln.rstrip("\n")
                if not original.strip():
                    out_lines.append("")
                    continue

                s, base = clean_prefixes(original)
                no_sep = strip_separators(s)

                # Infer base if unknown
                if base == "unknown":
                    if re.fullmatch(r"[01]+", no_sep):
                        base = "bin"
                    elif re.fullmatch(r"[0-9a-fA-F]+", no_sep):
                        base = "hex"
                    else:
                        out_lines.append(f"# ERROR: Could not infer base for line: {original}")
                        continue

                try:
                    if base == "bin":
                        valid, err = validate_binary(s)
                        if not valid:
                            out_lines.append(f"# ERROR: {err}  | line: {original}")
                            continue
                        val = int(no_sep, 2)
                        hex_str = f"{val:X}"
                        # align to nibble
                        hex_len = (len(no_sep) + 3) // 4
                        hex_str = hex_str.rjust(hex_len, "0")
                        # grouping
                        if group_size > 0:
                            nib = max(1, group_size // 4)
                            parts = [hex_str[i:i+nib] for i in range(0, len(hex_str), nib)]
                            if visualize_little_endian:
                                parts.reverse()
                            hex_str = sep.join(parts)
                        prefix = "0x " if show_prefix else ""
                        out_lines.append(f"{prefix}{hex_str}")
                    else:
                        valid, err = validate_hex(s)
                        if not valid:
                            out_lines.append(f"# ERROR: {err}  | line: {original}")
                            continue
                        val = int(no_sep, 16)
                        bin_str = f"{val:b}".rjust(len(no_sep)*4, "0")
                        if group_size > 0:
                            bin_str = maybe_group(bin_str, group_size)
                        prefix = "0b " if show_prefix else ""
                        out_lines.append(f"{prefix}{bin_str}")
                except Exception as ex:
                    out_lines.append(f"# ERROR: {ex}  | line: {original}")

            result_text = "\n".join(out_lines)
            st.text_area("Batch result", value=result_text, height=220)
            st.download_button("⬇️ Download Results", *to_download_bytes(result_text, "batch_results.txt"))

# Footer note
st.markdown("---")
st.caption(
    "Notes: Grouping and little-endian toggle are visual aids. Numeric values remain unchanged. "
    "Hex output uses uppercase for clarity. Spaces/underscores are ignored during parsing."
)
