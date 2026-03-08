import streamlit as st

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
  
    st.subheader("Memory IPs")
    sb = st.selectbox("Select one", ["LSMMBIST", "IOSSMMBIST", "CSSMMBIST"], index=1)
    st.write("IP(s):", sb)


    if sb == "LSMMBIST":
        st.subheader("LSMMBIST")

    elif sb == "IOSSMMBIST":
        st.subheader("IOSSMBIST")
        iossm_choice = st.radio("Pick one", ["IOSSMCFG", "IOSSMCAL Serial Channel 0", "IOSSMCAL Serial Channel 1"], index=0)

    elif sb == "CSSMMBIST":
        st.subheader("CSSMMBIST")
        cssm_choice = st.radio("Pick one", ["CSSM HIP2C", "CSSM CNT", "CSSM DVP"], index=0)
        
