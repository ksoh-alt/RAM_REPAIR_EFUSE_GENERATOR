"""
tests/test_parser_v2.py
-----------------------
Unit tests for plist_parser V2 functions:
    parse_plist_text_v2() and rows_to_csv_bytes_v2().

Key differences from V1:
  - TestStep is a user-provided string (not auto-incrementing)
  - mode/vectype come from parameters, not Pat fields
  - TestName always ends with `.stil`
  - Loop logic outputs patopt[LoopStart]/patopt[LoopEnd] style switches
  - 20-column CSV schema with 8 additional placeholder columns
"""

import pytest
from plist_parser import (
    FIELDNAMES_V2,
    HARD_TUPLE_ID_LENGTH,
    parse_plist_text_v2,
    rows_to_csv_bytes_v2,
)


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

class TestBasicPatV2:
    def test_returns_one_row(self):
        rows, warns = parse_plist_text_v2(BASIC_INPUT, BASIC_FILENAME)
        assert len(rows) == 1

    def test_no_warnings(self):
        _, warns = parse_plist_text_v2(BASIC_INPUT, BASIC_FILENAME)
        assert warns == []

    def test_module(self):
        rows, _ = parse_plist_text_v2(BASIC_INPUT, BASIC_FILENAME)
        assert rows[0]["Module"] == "MOD"

    def test_zip(self):
        rows, _ = parse_plist_text_v2(BASIC_INPUT, BASIC_FILENAME)
        assert rows[0]["Zip"] == "W_WAFER_F.ZIP"

    def test_plist_derived_from_filename(self):
        rows, _ = parse_plist_text_v2(BASIC_INPUT, BASIC_FILENAME)
        assert rows[0]["Plist"] == "MOD_WAFER.plist"

    def test_global_plist(self):
        rows, _ = parse_plist_text_v2(BASIC_INPUT, BASIC_FILENAME)
        assert rows[0]["GlobalPlist"] == "CHIP"

    def test_teststep_is_user_string(self):
        """V2: TestStep is a user-provided string, not auto-incrementing."""
        rows, _ = parse_plist_text_v2(BASIC_INPUT, BASIC_FILENAME)
        assert rows[0]["TestStep"] == "FT"

    def test_teststep_custom_value(self):
        rows, _ = parse_plist_text_v2(BASIC_INPUT, BASIC_FILENAME, test_step="WAFER")
        assert rows[0]["TestStep"] == "WAFER"

    def test_vrev(self):
        rows, _ = parse_plist_text_v2(BASIC_INPUT, BASIC_FILENAME)
        assert rows[0]["vrev"] == "vrev0123"

    def test_mode_from_parameter(self):
        """V2: mode comes from the parameter, not the Pat name."""
        rows, _ = parse_plist_text_v2(BASIC_INPUT, BASIC_FILENAME)
        assert rows[0]["mode"] == "jecahpshec"

    def test_mode_custom_value(self):
        rows, _ = parse_plist_text_v2(BASIC_INPUT, BASIC_FILENAME, mode="custom_mode")
        assert rows[0]["mode"] == "custom_mode"

    def test_vectype_from_parameter(self):
        """V2: vectype comes from the parameter, not the Pat name."""
        rows, _ = parse_plist_text_v2(BASIC_INPUT, BASIC_FILENAME)
        assert rows[0]["vectype"] == "hvm100"

    def test_vectype_custom_value(self):
        rows, _ = parse_plist_text_v2(BASIC_INPUT, BASIC_FILENAME, vectype="custom_vec")
        assert rows[0]["vectype"] == "custom_vec"

    def test_test_name_has_stil_suffix(self):
        """V2: TestName always ends with .stil."""
        rows, _ = parse_plist_text_v2(BASIC_INPUT, BASIC_FILENAME)
        assert rows[0]["TestName"].endswith(".stil")
        assert rows[0]["TestName"] == "W_WAFER_0123_mode_vtype.stil"

    def test_vmprefix_empty_by_default(self):
        rows, _ = parse_plist_text_v2(BASIC_INPUT, BASIC_FILENAME)
        assert rows[0]["VMPREFIX"] == ""

    def test_optional_switches_empty_by_default(self):
        rows, _ = parse_plist_text_v2(BASIC_INPUT, BASIC_FILENAME)
        assert rows[0]["Optional Switches"] == ""

    def test_hard_tuple_id_empty_when_disabled(self):
        rows, _ = parse_plist_text_v2(BASIC_INPUT, BASIC_FILENAME, hard_tupleid_en=False)
        assert rows[0]["Hard Tuple ID"] == ""


# ---------------------------------------------------------------------------
# Placeholder columns exist (even if blank)
# ---------------------------------------------------------------------------

class TestPlaceholderColumns:
    def test_opt_out_empty(self):
        rows, _ = parse_plist_text_v2(BASIC_INPUT, BASIC_FILENAME)
        assert rows[0]["Opt-out"] == ""

    def test_sof_filename_empty(self):
        rows, _ = parse_plist_text_v2(BASIC_INPUT, BASIC_FILENAME)
        assert rows[0]["SOF FileName"] == ""

    def test_sof2vec_option_empty(self):
        rows, _ = parse_plist_text_v2(BASIC_INPUT, BASIC_FILENAME)
        assert rows[0]["Sof2Vec Option"] == ""

    def test_hdbi_vrev_empty(self):
        rows, _ = parse_plist_text_v2(BASIC_INPUT, BASIC_FILENAME)
        assert rows[0]["HDBI_vrev"] == ""

    def test_hdbi_mode_empty(self):
        rows, _ = parse_plist_text_v2(BASIC_INPUT, BASIC_FILENAME)
        assert rows[0]["HDBI_mode"] == ""

    def test_hdbi_vectype_empty(self):
        rows, _ = parse_plist_text_v2(BASIC_INPUT, BASIC_FILENAME)
        assert rows[0]["HDBI_vectype"] == ""

    def test_hdbi_optional_switches_empty(self):
        rows, _ = parse_plist_text_v2(BASIC_INPUT, BASIC_FILENAME)
        assert rows[0]["HDBI_Optional Switches"] == ""

    def test_hdbi_hard_tuple_id_empty(self):
        rows, _ = parse_plist_text_v2(BASIC_INPUT, BASIC_FILENAME)
        assert rows[0]["HDBI_Hard Tuple ID"] == ""

    def test_all_20_columns_present(self):
        rows, _ = parse_plist_text_v2(BASIC_INPUT, BASIC_FILENAME)
        for col in FIELDNAMES_V2:
            assert col in rows[0], f"Missing column: {col}"


# ---------------------------------------------------------------------------
# Nested PList lines affecting VMPREFIX
# ---------------------------------------------------------------------------

class TestNestedPlistVMPREFIXV2:
    NESTED_TEXT = (
        "GlobalPList MOD_WAFER_CHIP_PLIST {\n"
        "    PList NEST1\n"
        "    PList NEST2\n"
        f"    Pat {BASIC_PAT};\n"
        "}\n"
    )

    def test_vmprefix_joined(self):
        rows, _ = parse_plist_text_v2(self.NESTED_TEXT, BASIC_FILENAME)
        assert rows[0]["VMPREFIX"] == "NEST1 NEST2"

    def test_nested_plists_cleared_after_pat(self):
        text = (
            "GlobalPList MOD_WAFER_CHIP_PLIST {\n"
            "    PList NEST1\n"
            f"    Pat {BASIC_PAT};\n"
            f"    Pat {BASIC_PAT};\n"
            "}\n"
        )
        rows, _ = parse_plist_text_v2(text, BASIC_FILENAME)
        assert len(rows) == 2
        assert rows[0]["VMPREFIX"] == "NEST1"
        assert rows[1]["VMPREFIX"] == ""


# ---------------------------------------------------------------------------
# V2 Loop handling – patopt style
# ---------------------------------------------------------------------------

class TestLoopStartV2:
    def test_loop_start_patopt(self):
        text = _single_block(f"{BASIC_PAT}[LoopStart]")
        rows, _ = parse_plist_text_v2(text, BASIC_FILENAME)
        assert rows[0]["Optional Switches"] == "patopt[LoopStart]"

    def test_loop_start_tag_removed_from_test_name(self):
        text = _single_block(f"{BASIC_PAT}[LoopStart]")
        rows, _ = parse_plist_text_v2(text, BASIC_FILENAME)
        assert "[LoopStart]" not in rows[0]["TestName"]
        assert rows[0]["TestName"].endswith(".stil")

    def test_loop_repeat_patopt(self):
        text = _single_block(f"{BASIC_PAT}[LoopRepeat]")
        rows, _ = parse_plist_text_v2(text, BASIC_FILENAME)
        assert rows[0]["Optional Switches"] == "patopt[LoopStart] [LoopRepeat]"

    def test_loop_repeat_with_count(self):
        text = _single_block(f"{BASIC_PAT}[LoopRepeat:3]")
        rows, _ = parse_plist_text_v2(text, BASIC_FILENAME)
        assert rows[0]["Optional Switches"] == "patopt[LoopStart] [LoopRepeat 3]"

    def test_loop_repeat_tag_removed_from_test_name(self):
        text = _single_block(f"{BASIC_PAT}[LoopRepeat:3]")
        rows, _ = parse_plist_text_v2(text, BASIC_FILENAME)
        assert "[LoopRepeat" not in rows[0]["TestName"]
        assert rows[0]["TestName"].endswith(".stil")


class TestLoopEndV2:
    def test_loop_end_patopt(self):
        text = _single_block(f"{BASIC_PAT}[LoopEnd]")
        rows, _ = parse_plist_text_v2(text, BASIC_FILENAME)
        assert rows[0]["Optional Switches"] == "patopt[LoopEnd]"

    def test_loop_end_tag_removed_from_test_name(self):
        text = _single_block(f"{BASIC_PAT}[LoopEnd]")
        rows, _ = parse_plist_text_v2(text, BASIC_FILENAME)
        assert "[LoopEnd]" not in rows[0]["TestName"]
        assert rows[0]["TestName"].endswith(".stil")


# ---------------------------------------------------------------------------
# Hard Tuple ID (V2)
# ---------------------------------------------------------------------------

class TestHardTupleIDV2:
    def test_enabled_returns_first_8_chars(self):
        rows, _ = parse_plist_text_v2(BASIC_INPUT, BASIC_FILENAME, hard_tupleid_en=True)
        assert rows[0]["Hard Tuple ID"] == "HARDID01"
        assert len(rows[0]["Hard Tuple ID"]) == HARD_TUPLE_ID_LENGTH

    def test_disabled_returns_empty(self):
        rows, _ = parse_plist_text_v2(BASIC_INPUT, BASIC_FILENAME, hard_tupleid_en=False)
        assert rows[0]["Hard Tuple ID"] == ""


# ---------------------------------------------------------------------------
# TestStep is the same for all rows (not incrementing)
# ---------------------------------------------------------------------------

class TestTestStepNotIncrementingV2:
    def test_all_rows_same_teststep(self):
        text = (
            "GlobalPList MOD_WAFER_CHIP_PLIST {\n"
            f"    Pat {BASIC_PAT};\n"
            f"    Pat {BASIC_PAT};\n"
            f"    Pat {BASIC_PAT};\n"
            "}\n"
        )
        rows, _ = parse_plist_text_v2(text, BASIC_FILENAME, test_step="FT")
        assert all(r["TestStep"] == "FT" for r in rows)


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCasesV2:
    def test_no_w_token_skipped_with_warning(self):
        text = "GlobalPList MOD_WAFER_CHIP_PLIST {\n    Pat NOID_NMOD_X_CHIP_0123;\n}\n"
        rows, warns = parse_plist_text_v2(text, BASIC_FILENAME)
        assert rows == []
        assert any("W" in w or "skipping" in w for w in warns)

    def test_empty_input_no_rows(self):
        rows, _ = parse_plist_text_v2("", BASIC_FILENAME)
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
        rows, _ = parse_plist_text_v2(text, BASIC_FILENAME)
        assert len(rows) == 2
        assert rows[0]["Module"] == "MOD"
        assert rows[1]["Module"] == "MOD2"


# ---------------------------------------------------------------------------
# rows_to_csv_bytes_v2
# ---------------------------------------------------------------------------

class TestRowsToCsvBytesV2:
    def test_returns_bytes(self):
        rows, _ = parse_plist_text_v2(BASIC_INPUT, BASIC_FILENAME)
        result = rows_to_csv_bytes_v2(rows)
        assert isinstance(result, bytes)

    def test_header_has_20_columns(self):
        csv_bytes = rows_to_csv_bytes_v2([])
        header_line = csv_bytes.decode("utf-8").strip()
        assert header_line == ",".join(FIELDNAMES_V2)

    def test_data_row_count(self):
        rows, _ = parse_plist_text_v2(BASIC_INPUT, BASIC_FILENAME)
        lines = rows_to_csv_bytes_v2(rows).decode("utf-8").splitlines()
        # 1 header + 1 data row
        assert len(lines) == 2

    def test_fieldnames_v2_has_20_columns(self):
        assert len(FIELDNAMES_V2) == 20

    def test_fieldnames_v2_order(self):
        expected = [
            "Opt-out", "TestStep", "Module", "TestName",
            "SOF FileName", "Sof2Vec Option", "Zip", "VMPREFIX",
            "Plist", "GlobalPlist", "vrev", "mode", "vectype",
            "Optional Switches", "Hard Tuple ID",
            "HDBI_vrev", "HDBI_mode", "HDBI_vectype",
            "HDBI_Optional Switches", "HDBI_Hard Tuple ID",
        ]
        assert FIELDNAMES_V2 == expected
