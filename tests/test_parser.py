"""
tests/test_parser.py
--------------------
Unit tests for plist_parser.parse_plist_text() and rows_to_csv_bytes().

Key scenarios:
  - Basic GlobalPList block with one Pat
  - Nested PList lines affecting VMPREFIX
  - LoopStart / LoopRepeat Optional Switches and tag removal
  - LoopEnd Optional Switches and tag removal
  - Hard Tuple ID enabled / disabled
  - Sequential TestStep values across multiple Pats
  - Pat without 'W' token is skipped with a warning
  - rows_to_csv_bytes column order
"""

import pytest
from plist_parser import FIELDNAMES, HARD_TUPLE_ID_LENGTH, MAX_VREV_DIGITS, parse_plist_text, rows_to_csv_bytes


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _single_block(pat_name: str, block_suffix: str = "MOD_WAFER_CHIP") -> str:
    """Return minimal GlobalPList text with one Pat."""
    return (
        f"GlobalPList {block_suffix}_PLIST {{\n"
        f"    Pat {pat_name};\n"
        f"}}\n"
    )


BASIC_PAT = "HARDID01_MOD_W_WAFER_0123_mode_vtype"
BASIC_INPUT = _single_block(BASIC_PAT)
BASIC_FILENAME = "PREFIX_MOD_WAFER.txt"


# ---------------------------------------------------------------------------
# Basic GlobalPList block with one Pat
# ---------------------------------------------------------------------------

class TestBasicPat:
    def test_returns_one_row(self):
        rows, warns = parse_plist_text(BASIC_INPUT, BASIC_FILENAME)
        assert len(rows) == 1

    def test_no_warnings(self):
        _, warns = parse_plist_text(BASIC_INPUT, BASIC_FILENAME)
        assert warns == []

    def test_module(self):
        rows, _ = parse_plist_text(BASIC_INPUT, BASIC_FILENAME)
        assert rows[0]["Module"] == "MOD"

    def test_zip(self):
        rows, _ = parse_plist_text(BASIC_INPUT, BASIC_FILENAME)
        assert rows[0]["Zip"] == "W_WAFER_F.ZIP"

    def test_plist_derived_from_filename(self):
        rows, _ = parse_plist_text(BASIC_INPUT, BASIC_FILENAME)
        # tokens: PREFIX, MOD, WAFER → join[1:3] = "MOD_WAFER.plist"
        assert rows[0]["Plist"] == "MOD_WAFER.plist"

    def test_global_plist(self):
        rows, _ = parse_plist_text(BASIC_INPUT, BASIC_FILENAME)
        assert rows[0]["GlobalPlist"] == "CHIP"

    def test_teststep_starts_at_one(self):
        rows, _ = parse_plist_text(BASIC_INPUT, BASIC_FILENAME)
        assert rows[0]["TestStep"] == 1

    def test_vrev(self):
        rows, _ = parse_plist_text(BASIC_INPUT, BASIC_FILENAME)
        # fields[4] = "0123" → "vrev0123"
        assert rows[0]["vrev"] == "vrev0123"

    def test_mode(self):
        rows, _ = parse_plist_text(BASIC_INPUT, BASIC_FILENAME)
        # w_index=2, mode = fields[w_index+3] = fields[5] = "mode"
        assert rows[0]["mode"] == "mode"

    def test_vectype(self):
        rows, _ = parse_plist_text(BASIC_INPUT, BASIC_FILENAME)
        # w_index=2, vectype = fields[w_index+4] = fields[6] = "vtype"
        assert rows[0]["vectype"] == "vtype"

    def test_test_name(self):
        rows, _ = parse_plist_text(BASIC_INPUT, BASIC_FILENAME)
        assert rows[0]["TestName"] == "W_WAFER_0123_mode_vtype"

    def test_vmprefix_empty_by_default(self):
        rows, _ = parse_plist_text(BASIC_INPUT, BASIC_FILENAME)
        assert rows[0]["VMPREFIX"] == ""

    def test_optional_switches_empty_by_default(self):
        rows, _ = parse_plist_text(BASIC_INPUT, BASIC_FILENAME)
        assert rows[0]["Optional Switches"] == ""

    def test_hard_tuple_id_empty_when_disabled(self):
        rows, _ = parse_plist_text(BASIC_INPUT, BASIC_FILENAME, hard_tupleid_en=False)
        assert rows[0]["Hard Tuple ID"] == ""


# ---------------------------------------------------------------------------
# Nested PList lines affecting VMPREFIX
# ---------------------------------------------------------------------------

class TestNestedPlistVMPREFIX:
    NESTED_TEXT = (
        "GlobalPList MOD_WAFER_CHIP_PLIST {\n"
        "    PList NEST1\n"
        "    PList NEST2\n"
        f"    Pat {BASIC_PAT};\n"
        "}\n"
    )

    def test_vmprefix_joined(self):
        rows, _ = parse_plist_text(self.NESTED_TEXT, BASIC_FILENAME)
        assert rows[0]["VMPREFIX"] == "NEST1 NEST2"

    def test_nested_plists_cleared_after_pat(self):
        """Second Pat should have empty VMPREFIX because nested_plists was cleared."""
        text = (
            "GlobalPList MOD_WAFER_CHIP_PLIST {\n"
            "    PList NEST1\n"
            f"    Pat {BASIC_PAT};\n"
            f"    Pat {BASIC_PAT};\n"
            "}\n"
        )
        rows, _ = parse_plist_text(text, BASIC_FILENAME)
        assert len(rows) == 2
        assert rows[0]["VMPREFIX"] == "NEST1"
        assert rows[1]["VMPREFIX"] == ""


# ---------------------------------------------------------------------------
# LoopStart / LoopRepeat behaviour
# ---------------------------------------------------------------------------

class TestLoopStart:
    def test_loop_start_sets_init_only(self):
        text = _single_block(f"{BASIC_PAT}[LoopStart]")
        rows, _ = parse_plist_text(text, BASIC_FILENAME)
        assert rows[0]["Optional Switches"] == "-init_only"

    def test_loop_start_tag_removed_from_test_name(self):
        text = _single_block(f"{BASIC_PAT}[LoopStart]")
        rows, _ = parse_plist_text(text, BASIC_FILENAME)
        assert "[LoopStart]" not in rows[0]["TestName"]

    def test_loop_repeat_sets_init_only(self):
        text = _single_block(f"{BASIC_PAT}[LoopRepeat]")
        rows, _ = parse_plist_text(text, BASIC_FILENAME)
        assert rows[0]["Optional Switches"] == "-init_only"

    def test_loop_repeat_tag_removed_from_test_name(self):
        text = _single_block(f"{BASIC_PAT}[LoopRepeat]")
        rows, _ = parse_plist_text(text, BASIC_FILENAME)
        assert "[LoopRepeat]" not in rows[0]["TestName"]

    def test_loop_start_with_suffix_text(self):
        """Tags like [LoopStart:3] should also be matched."""
        text = _single_block(f"{BASIC_PAT}[LoopStart:3]")
        rows, _ = parse_plist_text(text, BASIC_FILENAME)
        assert rows[0]["Optional Switches"] == "-init_only"
        assert "[LoopStart:3]" not in rows[0]["TestName"]


# ---------------------------------------------------------------------------
# LoopEnd behaviour
# ---------------------------------------------------------------------------

class TestLoopEnd:
    def test_loop_end_no_switch(self):
        text = _single_block(f"{BASIC_PAT}[LoopEnd]")
        rows, _ = parse_plist_text(text, BASIC_FILENAME)
        assert rows[0]["Optional Switches"] == ""

    def test_loop_end_tag_removed_from_test_name(self):
        text = _single_block(f"{BASIC_PAT}[LoopEnd]")
        rows, _ = parse_plist_text(text, BASIC_FILENAME)
        assert "[LoopEnd]" not in rows[0]["TestName"]


# ---------------------------------------------------------------------------
# Hard Tuple ID
# ---------------------------------------------------------------------------

class TestHardTupleID:
    def test_enabled_returns_first_8_chars(self):
        rows, _ = parse_plist_text(BASIC_INPUT, BASIC_FILENAME, hard_tupleid_en=True)
        # fields[0] = "HARDID01" (exactly HARD_TUPLE_ID_LENGTH chars)
        assert rows[0]["Hard Tuple ID"] == "HARDID01"
        assert len(rows[0]["Hard Tuple ID"]) == HARD_TUPLE_ID_LENGTH

    def test_enabled_truncates_to_8(self):
        long_id = "LONGIDENTIFIER"
        text = _single_block(f"{long_id}_MOD_W_WAFER_0123_mode_vtype")
        rows, _ = parse_plist_text(text, BASIC_FILENAME, hard_tupleid_en=True)
        assert rows[0]["Hard Tuple ID"] == long_id[:HARD_TUPLE_ID_LENGTH]

    def test_disabled_returns_empty(self):
        rows, _ = parse_plist_text(BASIC_INPUT, BASIC_FILENAME, hard_tupleid_en=False)
        assert rows[0]["Hard Tuple ID"] == ""


# ---------------------------------------------------------------------------
# Multiple Pats – sequential TestStep
# ---------------------------------------------------------------------------

class TestSequentialTestStep:
    def test_three_pats_sequential(self):
        text = (
            "GlobalPList MOD_WAFER_CHIP_PLIST {\n"
            f"    Pat {BASIC_PAT};\n"
            f"    Pat {BASIC_PAT};\n"
            f"    Pat {BASIC_PAT};\n"
            "}\n"
        )
        rows, _ = parse_plist_text(text, BASIC_FILENAME)
        assert [r["TestStep"] for r in rows] == [1, 2, 3]


# ---------------------------------------------------------------------------
# Edge cases / error handling
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_no_w_token_skipped_with_warning(self):
        text = "GlobalPList MOD_WAFER_CHIP_PLIST {\n    Pat NOID_NMOD_X_CHIP_0123;\n}\n"
        rows, warns = parse_plist_text(text, BASIC_FILENAME)
        assert rows == []
        assert any("W" in w or "skipping" in w for w in warns)

    def test_empty_input_no_rows(self):
        rows, _ = parse_plist_text("", BASIC_FILENAME)
        assert rows == []

    def test_multiple_blocks(self):
        text = (
            "GlobalPList MOD_WAFER_CHIP_PLIST {\n"
            f"    Pat {BASIC_PAT};\n"
            "}\n"
            "GlobalPList MOD2_WAFER2_CHIP2_PLIST {\n"
            f"    Pat {BASIC_PAT};\n"
            "}\n"
        )
        rows, _ = parse_plist_text(text, BASIC_FILENAME)
        assert len(rows) == 2
        assert rows[0]["Module"] == "MOD"
        assert rows[1]["Module"] == "MOD2"

    def test_teststep_continues_across_blocks(self):
        text = (
            "GlobalPList MOD_WAFER_CHIP_PLIST {\n"
            f"    Pat {BASIC_PAT};\n"
            "}\n"
            "GlobalPList MOD2_WAFER2_CHIP2_PLIST {\n"
            f"    Pat {BASIC_PAT};\n"
            "}\n"
        )
        rows, _ = parse_plist_text(text, BASIC_FILENAME)
        assert rows[0]["TestStep"] == 1
        assert rows[1]["TestStep"] == 2

    def test_filename_plist_derivation_two_tokens(self):
        rows, warns = parse_plist_text(BASIC_INPUT, "PREFIX_MOD.txt")
        assert rows[0]["Plist"] == "MOD.plist"
        assert any("2" in w or "token" in w.lower() for w in warns)

    def test_filename_plist_derivation_no_underscore(self):
        rows, warns = parse_plist_text(BASIC_INPUT, "filename.txt")
        assert rows[0]["Plist"] == "filename.plist"
        assert any("delimiter" in w.lower() or "no '_'" in w for w in warns)


# ---------------------------------------------------------------------------
# rows_to_csv_bytes
# ---------------------------------------------------------------------------

class TestRowsToCsvBytes:
    def test_returns_bytes(self):
        rows, _ = parse_plist_text(BASIC_INPUT, BASIC_FILENAME)
        result = rows_to_csv_bytes(rows)
        assert isinstance(result, bytes)

    def test_header_column_order(self):
        csv_bytes = rows_to_csv_bytes([])
        header_line = csv_bytes.decode("utf-8").strip()
        assert header_line == ",".join(FIELDNAMES)

    def test_data_row_count(self):
        rows, _ = parse_plist_text(BASIC_INPUT, BASIC_FILENAME)
        lines = rows_to_csv_bytes(rows).decode("utf-8").splitlines()
        # 1 header + 1 data row
        assert len(lines) == 2

    def test_fieldnames_order_matches_constant(self):
        """FIELDNAMES list must match the original DictWriter column order."""
        expected = [
            "TestStep", "Module", "Zip", "Plist", "GlobalPlist",
            "TestName", "VMPREFIX", "vrev", "mode", "vectype",
            "Optional Switches", "Hard Tuple ID",
        ]
        assert FIELDNAMES == expected
