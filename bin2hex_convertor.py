import re
from typing import Tuple, Optional, List

import streamlit as st

# -------------------------------
# Base detection & validation
# -------------------------------
BIN_CHARS = set("01")
OCT_CHARS = set("01234567")
DEC_CHARS = set("0123456789")
HEX_CHARS = set("0123456789abcdefABCDEF")

SEP_CHARS = set(" _\t")

def clean_prefixes(s: str) -> Tuple[str, Optional[str], bool]:
    """
    Returns (cleaned_without_prefix, detected_base, is_negative).
    detected_base in {'bin','oct','dec','hex', None}
    Supports optional leading '-' sign and 0b/0o/0x/0d prefixes.
    """
    s = s.strip()
    neg = False
    if s.startswith("-"):
        neg = True
        s = s[1:].lstrip()

    base = None
    sl = s.lower()
    if sl.startswith("0b"):
        base = "bin"; s = s[2:]
    elif sl.startswith("0o"):
        base = "oct"; s = s[2:]
    elif sl.startswith("0x"):
        base = "hex"; s = s[2:]
    elif sl.startswith("0d"):
        base = "dec"; s = s[2:]

    return s.strip(), base, neg

def strip_separators(s: str) -> str:
    return re.sub(r"[ _\t]", "", s)

def validate_digits(s: str, base: str) -> Tuple[bool, str]:
    """
    Validate string s (may include spaces/underscores/tabs) for the given base.
    Works on the already signless, prefixless string.
    """
    if s == "":
        return False, "Empty input."
    # quick bad-char probe for better error
    for i, ch in enumerate(s):
        if ch in SEP_CHARS:
            continue
        if base == "bin" and ch not in BIN_CHARS:
            return False, f"Invalid binary character `{ch}` at position {i+1}."
        if base == "oct" and ch not in OCT_CHARS:
            return False, f"Invalid octal character `{ch}` at position {i+1}."
        if base == "dec" and ch not in DEC_CHARS:
            return False, f"Invalid decimal character `{ch}` at position {i+1}."
        if base == "hex" and ch not in HEX_CHARS:
            return False, f"Invalid hexadecimal character `{ch}` at position {i+1}."
    return True, ""

def infer_base(no_sep: str) -> Optional[str]:
    """Infer base from characters if no prefix and user chose Auto."""
    if no_sep == "":
        return None
    if set(no_sep) <= BIN_CHARS:
        return "bin"
    if set(no_sep) <= OCT_CHARS:
        # Could be decimal too, but if digits are within 0-7 we prefer oct only when prefixed or user says so.
        # We'll treat ambiguous 'OCT-only' as decimal unless a non-decimal-octal digit appears (8/9).
        # To keep it intuitive, we will pick DEC for ambiguous cases like '10', unless user sets base manually.
        return "dec"
    if set(no_sep) <= set("0123456789"):
        return "dec"
    if set(no_sep) <= HEX_CHARS:
        return "hex"
    return None

# -------------------------------
# Formatting helpers
# -------------------------------
def group_str(s: str, group: int, sep: str) -> str:
    if group <= 0:
        return s
    return sep.join(s[i:i+group] for i in range(0, len(s), group))

def reverse_groups_for_visual(s: str, group: int) -> str:
    if group <= 0:
        return s
    parts = [s[i:i+group] for i in range(0, len(s), group)]
    parts.reverse()
    return "".join(parts)

def pad_left_to_multiple(s: str, k: int) -> str:
    if k <= 0 or not s:
        return s
    rem = len(s) % k
    return s if rem == 0 else "0" * (k - rem) + s

def format_binary(value: int, group_bits: int, sep: str, show_prefix: bool,
                  little_endian_visual: bool, pad_to_group: bool) -> str:
    sign = "-" if value < 0 else ""
    n = abs(value)
    s = "0" if n == 0 else f"{n:b}"
    if pad_to_group and group_bits > 0:
        s = pad_left_to_multiple(s, group_bits)
    if little_endian_visual and group_bits > 0:
        s = reverse_groups_for_visual(s, group_bits)
    s = group_str(s, group_bits if group_bits > 0 else 0, sep)
    return f"{sign}{'0b ' if show_prefix else ''}{s}"

def format_octal(value: int, group_digits: int, sep: str, show_prefix: bool,
                 little_endian_visual: bool) -> str:
    sign = "-" if value < 0 else ""
    n = abs(value)
    s = "0" if n == 0 else f"{n:o}"
    if little_endian_visual and group_digits > 0:
        s = reverse_groups_for_visual(s, group_digits)
    s = group_str(s, group_digits if group_digits > 0 else 0, sep)
    return f"{sign}{'0o ' if show_prefix else ''}{s}"

def format_decimal(value: int, thousand_sep: str) -> str:
    sign = "-" if value < 0 else ""
    s = f"{abs(value)}"
    if thousand_sep:
        # insert from the right every 3
        parts = []
        while s:
            parts.append(s[-3:])
            s = s[:-3]
        s = thousand_sep.join(reversed(parts))
    return f"{sign}{s}"

def format_hex(value: int, group_digits: int, sep: str, show_prefix: bool,
               uppercase: bool, little_endian_visual: bool, pad_to_nibble: bool,
               align_to_bits: Optional[int] = None) -> str:
    """
    If align_to_bits is provided (like 8/16/32), left-pad hex to that many bits (n/4 digits).
    """
    sign = "-" if value < 0 else ""
    n = abs(value)
    s = "0" if n == 0 else f"{n:x}"
    if uppercase:
        s = s.upper()
    # Pad to nibble boundary if requested (only affects leading zeros)
    if pad_to_nibble:
        nibs = len(s)
        # already nibble-aligned; this flag mostly mirrors binary pad_to_group behavior
        pass
    # Align to precise bit-width if provided
    if align_to_bits and align_to_bits > 0:
        need_hex_len = (align_to_bits + 3) // 4
        s = s.rjust(need_hex_len, "0")
    if little_endian_visual and group_digits > 0:
        s = reverse_groups_for_visual(s, group_digits)
    s = group_str(s, group_digits if group_digits > 0 else 0, sep)
    return f"{sign}{'0x ' if show_prefix else ''}{s}"

# -------------------------------
# Parsing pipeline
# -------------------------------
def parse_to_int(user_input: str, source_choice: str) -> Tuple[Optional[int], Optional[str]]:
    """
    Return (value, error). source_choice in {"Auto","Binary","Octal","Decimal","Hexadecimal"}.
    """
    s, pref_base, neg = clean_prefixes(user_input)
    if s == "":
        return None, None  # nothing entered

    # Decide base
    base = None
    if source_choice != "Auto":
        base = {"Binary":"bin","Octal":"oct","Decimal":"dec","Hexadecimal":"hex"}[source_choice]
    elif pref_base is not None:
        base = pref_base
    else:
        no_sep = strip_separators(s)
        base = infer_base(no_sep)
        if base is None:
            return None, "Could not infer base. Add a prefix like 0b/0o/0x or choose the base."

    # Validate and convert
    ok, err = validate_digits(s, base)
    if not ok:
        return None, err

    no_sep = strip_separators(s)
    try:
        val = int(no_sep, {"bin":2,"oct":8,"dec":10,"hex":16}[base])
        if neg:
            val = -val
        return val, None
    except Exception as ex:
        return None, f"Failed to parse: {ex}"

# -------------------------------
# Streamlit UI
# -------------------------------
st.set_page_config(page_title="Base Converter (Bin/Oct/Dec/Hex)", page_icon="🧮", layout="centered")
st.title("🧮 Binary · Octal · Decimal · Hex Converter")
st.caption("Auto-detects prefixes (0b, 0o, 0x, 0d) or choose a base. Clean formatting, grouping, and batch mode.")

with st.sidebar:
    st.header("Display Options")

    source_choice = st.selectbox("Source base", ["Auto", "Binary", "Octal", "Decimal", "Hexadecimal"], index=0)

    st.markdown("**Binary formatting**")
    bin_group_bits = st.selectbox("Group bits", [0, 4, 8, 16, 32], index=1, help="0 = no grouping")
    bin_sep = st.text_input("Binary group separator", value=" ")
    bin_pad = st.checkbox("Pad binary left to full group", value=True)

    st.markdown("---")
    st.markdown("**Octal formatting**")
    oct_group_digits = st.selectbox("Group octal digits", [0, 3, 6, 12], index=1)
    oct_sep = st.text_input("Octal group separator", value=" ")

    st.markdown("---")
    st.markdown("**Decimal formatting**")
    dec_sep_choice = st.selectbox("Thousand separator", ["None", "Space ( )", "Underscore (_)", "Comma (,)"], index=0)
    dec_sep_map = {"None":"", "Space ( )":" ", "Underscore (_)":"_", "Comma (,)":","}
    dec_sep = dec_sep_map[dec_sep_choice]

    st.markdown("---")
    st.markdown("**Hex formatting**")
    hex_group_digits = st.selectbox("Group hex digits", [0, 2, 4, 8], index=1, help="2=bytes, 4=words, 8=double words")
    hex_sep = st.text_input("Hex group separator", value=" ")
    hex_upper = st.checkbox("Uppercase hex", value=True)
    hex_align_bits = st.selectbox("Align hex to bit-width", [0, 8, 16, 32, 64], index=0,
                                  help="Left-pad hex to match bit width (0 = no align)")

    st.markdown("---")
    show_prefixes = st.checkbox("Show prefixes (0b/0o/0x)", value=True)
    little_endian_visual = st.checkbox("Visualize little-endian (reverse groups)", value=False,
                                       help="Display only. Numeric value stays the same.")

    st.markdown("---")
    st.caption("Tip: Grouping and endianness toggles are for display only.")

# Main input
st.subheader("Enter a value")
user_input = st.text_area("Value", height=100, placeholder="Examples:\n- 0b1010_1111\n- 0o755\n- 42\n- 0xDEAD_BEEF\n- -255")

value, parse_err = parse_to_int(user_input, source_choice)

if user_input.strip() and parse_err:
    st.error(parse_err)

if value is not None and parse_err is None:
    # Format outputs
    dec_out = format_decimal(value, thousand_sep=dec_sep)

    # Determine bit alignment request for hex
    align_bits = hex_align_bits if isinstance(hex_align_bits, int) and hex_align_bits > 0 else None

    bin_out = format_binary(
        value=value,
        group_bits=bin_group_bits,
        sep=bin_sep,
        show_prefix=show_prefixes,
        little_endian_visual=little_endian_visual,
        pad_to_group=bin_pad
    )
    oct_out = format_octal(
        value=value,
        group_digits=oct_group_digits,
        sep=oct_sep,
        show_prefix=show_prefixes,
        little_endian_visual=little_endian_visual
    )
    hex_out = format_hex(
        value=value,
        group_digits=hex_group_digits,
        sep=hex_sep,
        show_prefix=show_prefixes,
        uppercase=hex_upper,
        little_endian_visual=little_endian_visual,
        pad_to_nibble=True,
        align_to_bits=align_bits
    )

    st.markdown("### Results")
    c1, c2 = st.columns(2)
    with c1:
        st.text_area("Binary", value=bin_out, height=90)
        st.download_button("⬇️ Download Binary", data=bin_out.encode("utf-8"),
                           file_name="binary.txt", mime="text/plain")
        st.text_area("Octal", value=oct_out, height=90)
        st.download_button("⬇️ Download Octal", data=oct_out.encode("utf-8"),
                           file_name="octal.txt", mime="text/plain")
    with c2:
        st.text_area("Decimal", value=dec_out, height=90)
        st.download_button("⬇️ Download Decimal", data=dec_out.encode("utf-8"),
                           file_name="decimal.txt", mime="text/plain")
        st.text_area("Hexadecimal", value=hex_out, height=90)
        st.download_button("⬇️ Download Hex", data=hex_out.encode("utf-8"),
                           file_name="hex.txt", mime="text/plain")

st.markdown("---")
st.subheader("Batch Convert")
st.caption("Paste lines with optional prefixes (0b/0o/0x/0d) or select a source base (Auto recommended).")
batch_text = st.text_area("Input (one value per line)", height=160,
                          placeholder="Examples:\n0b1111_0000\n0o755\n42\n0xDEAD_BEEF\n-0xFF")

if st.button("Convert Batch"):
    lines = batch_text.splitlines()
    out_lines: List[str] = []
    header = "input -> bin | oct | dec | hex"
    out_lines.append(header)
    for ln in lines:
        raw = ln.rstrip("\n")
        if not raw.strip():
            out_lines.append("")
            continue
        v, err = parse_to_int(raw, source_choice)
        if err or v is None:
            out_lines.append(f"# ERROR: {err} | line: {raw}")
            continue

        # Format each per current display options
        b = format_binary(v, bin_group_bits, bin_sep, show_prefixes, little_endian_visual, bin_pad)
        o = format_octal(v, oct_group_digits, oct_sep, show_prefixes, little_endian_visual)
        d = format_decimal(v, dec_sep)
        h = format_hex(v, hex_group_digits, hex_sep, show_prefixes, hex_upper, little_endian_visual, True,
                       align_to_bits=align_bits)

        out_lines.append(f"{raw} -> {b} | {o} | {d} | {h}")

    result_text = "\n".join(out_lines)
    st.text_area("Batch result", value=result_text, height=220)
    st.download_button("⬇️ Download Results", data=result_text.encode("utf-8"),
                       file_name="batch_results.txt", mime="text/plain")

st.markdown("---")
st.caption(
    "Notes:\n"
    "- Ambiguous inputs without a prefix (e.g., `10`) are treated as **decimal** in Auto mode.\n"
    "- Negative numbers are supported. Outputs keep the sign (no two’s-complement encoding).\n"
    "- Little-endian toggle reverses **visual group order only**."
)
