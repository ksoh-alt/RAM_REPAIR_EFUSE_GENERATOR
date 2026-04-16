"""
plist_parser.py
---------------
Reusable parsing logic for GlobalPList test-input files.

Exposes:
    parse_plist_text(text, input_filename, hard_tupleid_en) -> (rows, warnings)
    rows_to_csv_bytes(rows) -> bytes
    FIELDNAMES  – ordered list of CSV column names
"""

import re
import csv
import io
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# CSV column order (must match original DictWriter fieldnames exactly)
# ---------------------------------------------------------------------------
FIELDNAMES: List[str] = [
    "TestStep",
    "Module",
    "Zip",
    "Plist",
    "GlobalPlist",
    "TestName",
    "VMPREFIX",
    "vrev",
    "mode",
    "vectype",
    "Optional Switches",
    "Hard Tuple ID",
]

# ---------------------------------------------------------------------------
# Compiled regular expressions
# ---------------------------------------------------------------------------
_GLOBAL_PLIST_RE = re.compile(r"^GlobalPList\s+(\S+)_PLIST", re.IGNORECASE)
_NESTED_PLIST_RE = re.compile(r"^\s*PList\s+(\S+)")
_PAT_RE = re.compile(r"^\s*Pat\s+(\S+?);")
_LOOP_START_RE = re.compile(r"\[LoopStart[^\]]*\]|\(LoopStart[^)]*\)", re.IGNORECASE)
_LOOP_REPEAT_RE = re.compile(r"\[LoopRepeat[^\]]*\]|\(LoopRepeat[^)]*\)", re.IGNORECASE)
_LOOP_END_RE = re.compile(r"\[LoopEnd[^\]]*\]|\(LoopEnd[^)]*\)", re.IGNORECASE)
_BRACKET_TAG_RE = re.compile(r"\[[^\]]*\]|\([^)]*\)")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse_plist_text(
    text: str,
    input_filename: str,
    hard_tupleid_en: bool = False,
) -> Tuple[List[Dict], List[str]]:
    """Parse GlobalPList block text and return ``(rows, warnings)``.

    Args:
        text:             Full content of the input ``.txt`` file.
        input_filename:   Name of the uploaded file (used to derive the
                          ``Plist`` column value via ``tokens[1:3]``).
        hard_tupleid_en:  When ``True``, populate the ``Hard Tuple ID``
                          column with the first 8 characters of each Pat's
                          first underscore-delimited field.

    Returns:
        A 2-tuple ``(rows, warnings)`` where *rows* is a list of dicts
        (one per Pat entry) and *warnings* is a list of human-readable
        warning strings about skipped or malformed entries.
    """
    rows: List[Dict] = []
    warn_msgs: List[str] = []

    # Derive plist from the input filename.
    # Original logic: INPUT_FILE.split("_")[1:3] joined with "_" + ".plist"
    # Strip the file extension first so it doesn't bleed into the last token.
    base_name = input_filename.rsplit(".", 1)[0]
    fname_tokens = base_name.split("_")
    if len(fname_tokens) >= 3:
        plist = "_".join(fname_tokens[1:3]) + ".plist"
    elif len(fname_tokens) == 2:
        plist = fname_tokens[1] + ".plist"
        warn_msgs.append(
            f"Filename '{input_filename}' has only 2 '_'-delimited tokens; "
            f"Plist derived as '{plist}'."
        )
    else:
        plist = base_name + ".plist"
        warn_msgs.append(
            f"Filename '{input_filename}' has no '_' delimiter; "
            f"Plist set to '{plist}'."
        )

    current_block: Optional[Tuple[str, str, str]] = None  # (module, zip, global_plist)
    nested_plists: List[str] = []
    in_block: bool = False
    brace_depth: int = 0
    test_step: int = 1

    for lineno, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()

        # ------------------------------------------------------------------
        # Detect the start of a GlobalPList block
        # ------------------------------------------------------------------
        m = _GLOBAL_PLIST_RE.match(line)
        if m:
            block_name = m.group(1)  # e.g. "MOD_WAFER_CHIP" (without _PLIST)
            parts = block_name.split("_")
            module = parts[0] if parts else ""
            zip_val = ("W_" + parts[1] + "_F.ZIP") if len(parts) > 1 else ""
            global_plist = "_".join(parts[2:]) if len(parts) > 2 else ""
            current_block = (module, zip_val, global_plist)
            nested_plists = []
            in_block = True
            # Count any braces that appear on the same line as GlobalPList
            brace_depth = line.count("{") - line.count("}")
            if brace_depth < 0:
                brace_depth = 0
            continue

        if not in_block or current_block is None:
            continue

        # ------------------------------------------------------------------
        # Track brace depth to detect end of the GlobalPList block
        # ------------------------------------------------------------------
        brace_depth += line.count("{") - line.count("}")
        if brace_depth <= 0:
            in_block = False
            current_block = None
            nested_plists = []
            brace_depth = 0
            continue

        # ------------------------------------------------------------------
        # Nested PList line  (accumulate for VMPREFIX)
        # ------------------------------------------------------------------
        pm = _NESTED_PLIST_RE.match(line)
        if pm:
            # Strip any trailing "{" that may be attached to the name
            plist_name = pm.group(1).rstrip("{").strip()
            if plist_name:
                nested_plists.append(plist_name)
            continue

        # ------------------------------------------------------------------
        # Pat entry
        # ------------------------------------------------------------------
        patm = _PAT_RE.match(line)
        if patm:
            pat_name = patm.group(1)
            row, pat_warns = _process_pat(
                pat_name=pat_name,
                block_info=current_block,
                plist=plist,
                nested_plists=list(nested_plists),
                hard_tupleid_en=hard_tupleid_en,
                test_step=test_step,
                lineno=lineno,
            )
            warn_msgs.extend(pat_warns)
            if row is not None:
                rows.append(row)
                test_step += 1
            # Clear nested plists after every Pat (whether valid or not)
            nested_plists.clear()

    return rows, warn_msgs


def rows_to_csv_bytes(rows: List[Dict]) -> bytes:
    """Convert a list of row dicts to UTF-8 encoded CSV bytes.

    Column order follows ``FIELDNAMES`` exactly, matching the original
    ``csv.DictWriter`` field order.

    Args:
        rows:  List of row dicts produced by :func:`parse_plist_text`.

    Returns:
        UTF-8 encoded bytes including the header row.
    """
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=FIELDNAMES, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue().encode("utf-8")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _process_pat(
    pat_name: str,
    block_info: Tuple[str, str, str],
    plist: str,
    nested_plists: List[str],
    hard_tupleid_en: bool,
    test_step: int,
    lineno: int,
) -> Tuple[Optional[Dict], List[str]]:
    """Process a single Pat entry and return ``(row_dict, warnings)``.

    The Pat name is split on ``_``.  The index of the ``"W"`` token
    anchors relative derivations; absolute index ``4`` gives the vrev
    source, indices ``w_index+3`` and ``w_index+4`` give mode/vectype.
    Loop markers (``[LoopStart]``, ``[LoopRepeat]``, ``[LoopEnd]``) in
    the last field set Optional Switches and are cleaned from TestName.
    """
    module, zip_val, global_plist = block_info
    warn_msgs: List[str] = []

    fields = pat_name.split("_")

    # Find the "W" token
    try:
        w_index = fields.index("W")
    except ValueError:
        warn_msgs.append(
            f"Line {lineno}: No 'W' token found in Pat name '{pat_name}'; skipping."
        )
        return None, warn_msgs

    # vrev – absolute index 4
    if len(fields) > 4:
        vrev = "vrev" + str(fields[4])[:4]
    else:
        vrev = ""
        warn_msgs.append(
            f"Line {lineno}: Pat '{pat_name}' has fewer than 5 fields; "
            "vrev will be empty."
        )

    # mode and vectype – relative to w_index
    mode = fields[w_index + 3] if len(fields) > w_index + 3 else ""
    vectype = fields[w_index + 4] if len(fields) > w_index + 4 else ""

    # Build test_name parts from w_index onward; detect and clean loop tags
    test_name_parts: List[str] = list(fields[w_index:])
    optional_switches = ""

    if test_name_parts:
        last = test_name_parts[-1]
        if _LOOP_START_RE.search(last) or _LOOP_REPEAT_RE.search(last):
            optional_switches = "-init_only"
            cleaned = _BRACKET_TAG_RE.sub("", last).strip("_").strip()
            test_name_parts[-1] = cleaned
        elif _LOOP_END_RE.search(last):
            optional_switches = ""
            cleaned = _BRACKET_TAG_RE.sub("", last).strip("_").strip()
            test_name_parts[-1] = cleaned

        # Drop any trailing empty parts produced by cleaning
        while test_name_parts and not test_name_parts[-1]:
            test_name_parts.pop()

    test_name = "_".join(test_name_parts)

    # VMPREFIX – space-joined names of all preceding nested PList entries
    vmprefix = " ".join(nested_plists)

    # Hard Tuple ID – first 8 chars of the first field (when enabled)
    hard_tuple_id = fields[0][:8] if hard_tupleid_en and fields else ""

    row: Dict = {
        "TestStep": test_step,
        "Module": module,
        "Zip": zip_val,
        "Plist": plist,
        "GlobalPlist": global_plist,
        "TestName": test_name,
        "VMPREFIX": vmprefix,
        "vrev": vrev,
        "mode": mode,
        "vectype": vectype,
        "Optional Switches": optional_switches,
        "Hard Tuple ID": hard_tuple_id,
    }

    return row, warn_msgs
