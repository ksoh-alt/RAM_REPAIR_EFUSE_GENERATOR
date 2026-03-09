import streamlit as st
import pandas as pd
import re
from typing import Any, Dict, List, Tuple, Optional

# -------------------------------------------------------------
# Page config
# -------------------------------------------------------------
st.set_page_config(
    page_title="Ram Repair Efuse Generator",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------------------------------------------
# Sidebar navigation
# -------------------------------------------------------------

st.sidebar.title("📚 Sections")
sections = [
    "EFUSE Generator",
    "LVLIB Reader",
]

# Attempt to read query param for section (supports both new and legacy APIs)
current_section = None
try:
    # Newer API (Streamlit >= 1.30): st.query_params
    qp = st.query_params
    if "section" in qp:
        current_section = qp.get("section")
except Exception:
    try:
        # Legacy experimental API
        qp = st.experimental_get_query_params()
        if "section" in qp:
            current_section = qp.get("section")[0]
    except Exception:
        pass

section = st.sidebar.selectbox("Jump to", sections, index=(sections.index(current_section) if current_section in sections else 0))

# Keep the URL in sync with selection
try:
    st.query_params["section"] = section
except Exception:
    try:
        st.experimental_set_query_params(section=section)
    except Exception:
        pass

st.sidebar.write("---")
st.sidebar.caption("This app helps generate efuse hex code for Array Ram Repair Simulation.")

# -------------------------------------------------------------
# SECTION: EFUSE Generator
# -------------------------------------------------------------
if section == "EFUSE Generator":
    st.title("EFUSE Generator")
    #st.header("Use this apps to generate ARRAY Ram Efuse Hex for repair simulation")
    st.subheader("Upload the RAMID Table")
    uploaded = st.file_uploader("Upload a CSV", type=["csv"])
    if uploaded is not None:
        df = pd.read_csv(uploaded)
        #st.dataframe(df)
  
    st.subheader("Memory IPs")
    sb = st.selectbox("Select one", ["LSMMBIST", "IOSSMMBIST", "CSSMMBIST"], index=1)
    #st.write("IP(s):", sb)

    if sb == "LSMMBIST":
        st.subheader("LSMMBIST")
        st.subheader("RAMID")

        if uploaded is None:
            st.info("Please upload a CSV first.")
        else:
            # 1) Filter to MemType == 'LSM'
            if "MemType" not in df.columns or "CJTAGID" not in df.columns:
                st.error("The CSV must contain 'MemType' and 'CJTAGID' columns.")
            else:
                # Normalize columns to be safe
                df["MemType"] = df["MemType"].astype("string").str.strip()
                df["CJTAGID"] = df["CJTAGID"].astype("string").str.strip()
    
                df_lsm = df[df["MemType"] == "LSM"]
    
                if df_lsm.empty:
                    st.warning("No rows found with MemType == 'LSM'.")
                else:
                    # 2) Build unique CJTAGID list (drop NaN/empty)
                    cjtagid_lsm = (
                        df_lsm["CJTAGID"]
                        .replace("", pd.NA)
                        .dropna()
                        .drop_duplicates()
                        .tolist()
                    )
    
                    if not cjtagid_lsm:
                        st.warning("No valid CJTAGID found under MemType == 'LSM'.")
                    else:
                        # Optional: sort for nicer UX
                        cjtagid_lsm = sorted(cjtagid_lsm, key=lambda x: x.casefold())
    
                        # 3) Safe default index
                        default_index = 0  # use 0 to avoid IndexError when only one value exists
    
                        sb_cjtagidlsm = st.selectbox(
                            "Select CJTAGID",
                            cjtagid_lsm,
                            index=default_index,
                            key="select_cjtagid_lsm"
                        )
    
                        # 4) Apply correct filter: MemType == 'LSM' AND CJTAGID == selected
                        df_lsm_cjtagid = df_lsm[df_lsm["CJTAGID"] == sb_cjtagidlsm]
    
                        # (Optional) If you want to be extra safe case-insensitively:
                        # df_lsm_cjtagid = df_lsm[df_lsm["CJTAGID"].str.casefold() == sb_cjtagidlsm.casefold()]
    
                        st.subheader("Filtered Rows")
                        st.dataframe(df_lsm_cjtagid, use_container_width=True)
    
                        # Optional: show count
                        st.caption(f"Matched rows: {len(df_lsm_cjtagid)}")


    elif sb == "IOSSMMBIST":
        st.subheader("IOSSMBIST")
        iossm_choice = st.radio("Pick one", ["IOSSMCFG", "IOSSMCAL Serial Channel 0", "IOSSMCAL Serial Channel 1"], index=0)
        st.subheader("RAMID")
        #if uploaded is not None:
         #   if iossm_choice == "IOSSMCFG":
          #      df_iossm = df[df["MemType"] == "IOSSMCFG"]
           # else: 
            #    df_iossm = df[df["MemType"] == "IOSSMCAL"]
        if uploaded is None:
            st.info("Please upload a CSV first.")
        else:
            # 1) Filter to MemType == 'LSM'
            if "MemType" not in df.columns or "CJTAGID" not in df.columns:
                st.error("The CSV must contain 'MemType' and 'CJTAGID' columns.")
            else:
                # Normalize columns to be safe
                df["MemType"] = df["MemType"].astype("string").str.strip()
                df["CJTAGID"] = df["CJTAGID"].astype("string").str.strip()
                if iossm_choice == "IOSSMCFG" :
                    df_iossm = df[df["MemType"] == "IOSSMCFG"]
                else:
                    df_iossm = df[df["MemType"] == "IOSSMCAL"]
                    
                if df_iossm.empty:
                    st.warning("No rows found with MemType == 'LSM'.")
                else:
                    # 2) Build unique CJTAGID list (drop NaN/empty)
                    cjtagid_iossm = (
                        df_iossm["CJTAGID"]
                        .replace("", pd.NA)
                        .dropna()
                        .drop_duplicates()
                        .tolist()
                    )
    
                    if not cjtagid_iossm:
                        st.warning("No valid CJTAGID found under MemType == 'IOSSM'.")
                    else:
                        # Optional: sort for nicer UX
                        cjtagid_iossm = sorted(cjtagid_iossm, key=lambda x: x.casefold())
    
                        # 3) Safe default index
                        default_index = 0  # use 0 to avoid IndexError when only one value exists
    
                        sb_cjtagidiossm = st.selectbox(
                            "Select CJTAGID",
                            cjtagid_iossm,
                            index=default_index,
                            key="select_cjtagid_lsm"
                        )
    
                        # 4) Apply correct filter: MemType == 'LSM' AND CJTAGID == selected
                        df_iossm_cjtagid = df_iossm[df_iossm["CJTAGID"] == sb_cjtagidiossm]
    
                        # (Optional) If you want to be extra safe case-insensitively:
                        # df_lsm_cjtagid = df_lsm[df_lsm["CJTAGID"].str.casefold() == sb_cjtagidlsm.casefold()]
    
                        st.subheader("Filtered Rows")
                        st.dataframe(df_iossm_cjtagid, use_container_width=True)
    
                        # Optional: show count
                        st.caption(f"Matched rows: {len(df_iossm_cjtagid)}")
        
    elif sb == "CSSMMBIST":
        st.subheader("CSSMMBIST")
        cssm_choice = st.radio("Pick one", ["CSSM HIP2C", "CSSM CNT", "CSSM DVP"], index=0)
        st.subheader("RAMID")
        if uploaded is None:
            st.info("Please upload a CSV first.")
        else:
            # 1) Filter to MemType == 'LSM'
            if "MemType" not in df.columns or "CJTAGID" not in df.columns:
                st.error("The CSV must contain 'MemType' and 'CJTAGID' columns.")
            else:
                # Normalize columns to be safe
                df["MemType"] = df["MemType"].astype("string").str.strip()
                df["CJTAGID"] = df["CJTAGID"].astype("string").str.strip()
    
                df_cssm = df[df["MemType"] == "CSSM"]
    
                if df_cssm.empty:
                    st.warning("No rows found with MemType == 'CSSM'.")
                else:
                    # 2) Build unique CJTAGID list (drop NaN/empty)
                    cjtagid_cssm = (
                        df_cssm["CJTAGID"]
                        .replace("", pd.NA)
                        .dropna()
                        .drop_duplicates()
                        .tolist()
                    )
    
                    if not cjtagid_cssm:
                        st.warning("No valid CJTAGID found under MemType == 'CSSM'.")
                    else:
                        # Optional: sort for nicer UX
                        cjtagid_cssm = sorted(cjtagid_cssm, key=lambda x: x.casefold())
    
                        # 3) Safe default index
                        default_index = 0  # use 0 to avoid IndexError when only one value exists
    
                        sb_cjtagidcssm = st.selectbox(
                            "Select CJTAGID",
                            cjtagid_cssm,
                            index=default_index,
                            key="select_cjtagid_cssm"
                        )
    
                        # 4) Apply correct filter: MemType == 'LSM' AND CJTAGID == selected
                        df_cssm_cjtagid = df_cssm[df_cssm["CJTAGID"] == sb_cjtagidcssm]
    
                        # (Optional) If you want to be extra safe case-insensitively:
                        # df_lsm_cjtagid = df_lsm[df_lsm["CJTAGID"].str.casefold() == sb_cjtagidlsm.casefold()]
    
                        st.subheader("Filtered Rows")
                        st.dataframe(df_cssm_cjtagid, use_container_width=True)
    
                        # Optional: show count
                        st.caption(f"Matched rows: {len(df_cssm_cjtagid)}")


# -------------------------------------------------------------
# SECTION: LVLIB Reader
# -------------------------------------------------------------
if section == "LVLIB Reader":
    st.title("LVLIB Reader")
    #st.header("Use this apps to generate ARRAY Ram Efuse Hex for repair simulation")
    

    # --------- Parsing ---------
    
    # Block start: e.g., "Name {" or "Name (ID) {", optional comment after "{"
    BLOCK_START = re.compile(r'^(\w+)(?:\s*\(([^)]*)\))?\s*\{\s*(?://.*)?$')
    
    # Key-value: e.g., "Key : Value; // optional comment"
    KEY_VALUE = re.compile(r'^\s*([\w\d_]+)\s*:\s*(.+?);(?:\s*//.*)?$')
    
    # Block end: "}" with optional comment
    BLOCK_END = re.compile(r'^\}\s*(?://.*)?$')
    
    def parse_summary_file_from_string(text: str) -> Dict[str, Any]:
        """
        Parse custom 'Name { ... }' / 'Name (ID) { ... }' format into a nested dict.
        Repeated non-ID blocks become lists.
        ID'ed blocks become dicts keyed by the ID; if the same ID repeats, become lists.
        Repeated keys inside a block become lists.
        Lines like 'key: value; // comment' supported.
        """
        root: Dict[str, Any] = {}
        stack: List[Dict[str, Any]] = [root]
    
        for raw in text.splitlines():
            line = raw.strip()
            if not line or line.startswith('//'):
                continue
    
            # 1) Block start
            m = BLOCK_START.match(line)
            if m:
                name = m.group(1)
                block_id = (m.group(2) or '').strip() or None
                parent = stack[-1]
    
                if block_id is not None:
                    # ID'ed block -> dict of id -> block
                    parent.setdefault(name, {})
                    container = parent[name]
                    if not isinstance(container, dict):
                        # edge case: previously became list (shouldn't happen with IDs)
                        container = {}
                        parent[name] = container
                    if block_id in container:
                        existing = container[block_id]
                        if isinstance(existing, list):
                            new_block: Dict[str, Any] = {}
                            existing.append(new_block)
                        else:
                            new_block = {}
                            container[block_id] = [existing, new_block]
                    else:
                        new_block = {}
                        container[block_id] = new_block
                    stack.append(new_block)
                else:
                    # Non-ID block -> may repeat, turn into list
                    if name in parent:
                        if isinstance(parent[name], list):
                            new_block = {}
                            parent[name].append(new_block)
                        else:
                            new_block = {}
                            parent[name] = [parent[name], new_block]
                    else:
                        new_block = {}
                        parent[name] = new_block
                    stack.append(parent[name][-1] if isinstance(parent[name], list) else parent[name])
                continue
    
            # 2) Block end
            if BLOCK_END.match(line):
                if len(stack) > 1:
                    stack.pop()
                continue
    
            # 3) Key-value line
            kv = KEY_VALUE.match(line)
            if kv:
                k, v = kv.group(1).strip(), kv.group(2).strip()
                curr = stack[-1]
                if k in curr:
                    if not isinstance(curr[k], list):
                        curr[k] = [curr[k]]
                    curr[k].append(v)
                else:
                    curr[k] = v
                continue
    
            # 4) Ignore lines that don't match any pattern
    
        return root
    
    # --------- Flattening ---------
    
    def _to_list(x) -> List[Any]:
        if x is None:
            return []
        return x if isinstance(x, list) else [x]
    
    def _coerce_float_maybe(x):
        try:
            return float(str(x))
        except Exception:
            return pd.NA
    
    def flatten_summary_to_df(summary: Dict[str, Any]) -> pd.DataFrame:
        """
        Produces one row per MemoryCollar under each BistPort, with context columns and
        the Step indices where that memory appears.
        """
        rows: List[Dict[str, Any]] = []
    
        regions = summary.get('DataForPhysicalRegion', {})
        if isinstance(regions, list):
            # Rare: treat as list without IDs
            regions_iter = [(None, r) for r in regions]
        elif isinstance(regions, dict):
            regions_iter = regions.items()
        else:
            regions_iter = []
    
        for region_id, region in regions_iter:
            region_type = region.get('Type')
            region_module = region.get('ModuleName')
    
            tap = region.get('TapController')
            tap_blocks = tap if isinstance(tap, list) else ([tap] if isinstance(tap, dict) else [])
    
            for tap_block in tap_blocks:
                tap_inst = tap_block.get('Instance')
                tap_mod  = tap_block.get('ModuleName')
    
                # BistPort can be dict of id -> block OR list (rare)
                bist = tap_block.get('BistPort')
                if isinstance(bist, dict):
                    bist_items = list(bist.items())
                elif isinstance(bist, list):
                    bist_items = [(None, b) for b in bist]
                else:
                    bist_items = []
    
                for bp_id, bp in bist_items:
                    ctrl_type = bp.get('ControllerType')
                    bp_inst   = bp.get('Instance')
                    bp_mod    = bp.get('ModuleName')
                    clk_conn  = bp.get('BistClkConnection')
                    clk_freq  = _coerce_float_maybe(bp.get('BistClkFrequency'))
                    ref_clk   = bp.get('ReferenceClock')
                    ref_freq  = _coerce_float_maybe(bp.get('ReferenceClockFrequency'))
    
                    # Build MemoryID -> [step indices] mapping from Step blocks
                    mem_to_steps: Dict[str, List[str]] = {}
                    steps = bp.get('Step', {})
                    if isinstance(steps, dict):
                        for step_id, step_obj in steps.items():
                            step_blocks = step_obj if isinstance(step_obj, list) else [step_obj]
                            for sblk in step_blocks:
                                mems = _to_list(sblk.get('MemoryInstance'))
                                for mem in mems:
                                    if mem is None:
                                        continue
                                    sid = str(step_id).strip()
                                    mem_to_steps.setdefault(mem, [])
                                    if sid not in mem_to_steps[mem]:
                                        mem_to_steps[mem].append(sid)
    
                    # Iterate MemoryCollar(ID) entries
                    collars = bp.get('MemoryCollar', {})
                    if isinstance(collars, dict):
                        for mem_id, mc in collars.items():
                            mc_blocks = mc if isinstance(mc, list) else [mc]
                            for mc_block in mc_blocks:
                                steps_list = mem_to_steps.get(mem_id, [])
                                rows.append({
                                    'RegionID': region_id,
                                    'RegionType': region_type,
                                    'RegionModuleName': region_module,
                                    'TapController_Instance': tap_inst,
                                    'TapController_ModuleName': tap_mod,
                                    'BistPort_ID': bp_id,
                                    'ControllerType': ctrl_type,
                                    'BistPort_Instance': bp_inst,
                                    'BistPort_ModuleName': bp_mod,
                                    'BistClkConnection': clk_conn,
                                    'BistClkFrequency_MHz': clk_freq,
                                    'ReferenceClock': ref_clk,
                                    'ReferenceClockFrequency_MHz': ref_freq,
                                    'MemoryID': mem_id,
                                    'CollarModuleName': mc_block.get('CollarModuleName'),
                                    'MemoryModule': mc_block.get('MemoryModule'),
                                    'MemoryInstance': mc_block.get('MemoryInstance'),
                                    'CollarInstance': mc_block.get('CollarInstance'),
                                    'StepIDs': ','.join(sorted(steps_list, key=lambda s: (float(s) if s.replace(".","",1).isdigit() else s))),
                                    'StepCount': len(steps_list),
                                })
                    else:
                        # If no MemoryCollar, still output MemoryIDs from steps (optional)
                        for mem_id, steps_list in mem_to_steps.items():
                            rows.append({
                                'RegionID': region_id,
                                'RegionType': region_type,
                                'RegionModuleName': region_module,
                                'TapController_Instance': tap_inst,
                                'TapController_ModuleName': tap_mod,
                                'BistPort_ID': bp_id,
                                'ControllerType': ctrl_type,
                                'BistPort_Instance': bp_inst,
                                'BistPort_ModuleName': bp_mod,
                                'BistClkConnection': clk_conn,
                                'BistClkFrequency_MHz': clk_freq,
                                'ReferenceClock': ref_clk,
                                'ReferenceClockFrequency_MHz': ref_freq,
                                'MemoryID': mem_id,
                                'CollarModuleName': pd.NA,
                                'MemoryModule': pd.NA,
                                'MemoryInstance': pd.NA,
                                'CollarInstance': pd.NA,
                                'StepIDs': ','.join(sorted(steps_list)),
                                'StepCount': len(steps_list),
                            })
    
        df = pd.DataFrame(rows)
        # Optional: column order
        preferred_cols = [
            'RegionID','RegionType','RegionModuleName',
            'TapController_Instance','TapController_ModuleName',
            'BistPort_ID','ControllerType','BistPort_Instance','BistPort_ModuleName',
            'BistClkConnection','BistClkFrequency_MHz','ReferenceClock','ReferenceClockFrequency_MHz',
            'MemoryID','CollarModuleName','MemoryModule','MemoryInstance','CollarInstance',
            'StepIDs','StepCount'
        ]
        return df[preferred_cols] if not df.empty else df

        # (Paste the two functions: parse_summary_file_from_string, flatten_summary_to_df)
        st.subheader("Upload the Summary File")
        uploaded = st.file_uploader("Upload summary .summary", type=["summary"])
        
        if uploaded:
            raw = uploaded.read()
            text = None
            for enc in ("utf-8-sig", "utf-8", "latin-1"):
                try:
                    text = raw.decode(enc)
                    break
                except Exception:
                    continue
            if text is None:
                st.error("Failed to decode file. Try UTF-8 encoding.")
                st.stop()
        
            with st.spinner("Parsing..."):
                summary = parse_summary_file_from_string(text)
        
            with st.spinner("Flattening..."):
                df = flatten_summary_to_df(summary)
        
            if df.empty:
                st.warning("Parsed successfully, but no rows found (no MemoryCollar blocks?).")
            else:
                st.success(f"Flattened rows: {len(df)}")
                st.dataframe(df, use_container_width=True)
        
                # Export
                col1, col2 = st.columns(2)
                with col1:
                    csv = df.to_csv(index=False).encode("utf-8")
                    st.download_button("⬇️ Download CSV", csv, "flattened.csv", "text/csv")
                with col2:
                    try:
                        xlsx = df.to_excel(index=False, engine="openpyxl")
                    except Exception:
                        # Streamlit cloud sometimes lacks openpyxl; fallback to CSV only
                        pass
    
