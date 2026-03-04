# streamlit_beginner_guide.py
# -------------------------------------------------------------
# Streamlit Beginner Guide: A single-file tour of common widgets
# and patterns you will use in most apps.
#
# How to run:
#   1) pip install streamlit pandas numpy
#   2) streamlit run streamlit_beginner_guide.py
# -------------------------------------------------------------

import io
import time
import math
import json
import wave
from io import BytesIO
from dataclasses import dataclass

import numpy as np
import pandas as pd
import streamlit as st

# -------------------------------------------------------------
# Page config
# -------------------------------------------------------------
st.set_page_config(
    page_title="Streamlit Beginner Guide",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------------------------------------------
# Helper: generate a small sine-wave WAV in-memory for st.audio
# -------------------------------------------------------------

def generate_sine_wav(duration_s: float = 1.0, freq_hz: int = 440, sample_rate: int = 16000) -> bytes:
    t = np.linspace(0, duration_s, int(sample_rate * duration_s), endpoint=False)
    wave_data = 0.25 * np.sin(2 * np.pi * freq_hz * t)  # 25% volume
    # Convert to 16-bit PCM
    pcm = (wave_data * 32767).astype(np.int16)
    buf = BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(pcm.tobytes())
    return buf.getvalue()

# -------------------------------------------------------------
# Caching examples
# -------------------------------------------------------------

@st.cache_data(show_spinner=False)
def cached_slow_sum(n: int) -> int:
    """Pretend this is expensive; cache the result for each n."""
    time.sleep(0.8)
    return sum(range(n + 1))

@st.cache_resource(show_spinner=False)
def get_expensive_resource():
    """Simulate an expensive resource (e.g., DB connection, model)."""
    time.sleep(0.5)
    return {"resource": "ready", "created_at": time.time()}

# -------------------------------------------------------------
# Sidebar navigation
# -------------------------------------------------------------

st.sidebar.title("📚 Sections")
sections = [
    "Basics",
    "Input Widgets",
    "Layout & Containers",
    "Data Display",
    "Charts",
    "Status & Feedback",
    "Forms & State",
    "Media",
    "Caching & Performance",
    "Advanced"
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
st.sidebar.caption("This app showcases many core Streamlit features in a single file.")

# -------------------------------------------------------------
# SECTION: Basics
# -------------------------------------------------------------
if section == "Basics":
    st.title("Streamlit Beginner Guide")
    st.header("Basics: Text, Markdown, Math, Code, and Help")
    st.subheader("1) Text elements")

    st.write("`st.write` can display text, numbers, dicts, DataFrames, and more.")
    st.text("This is st.text — monospaced, no markdown.")
    st.markdown("**Markdown** works with _formatting_, lists, and more.\n\n- Bullet 1\n- Bullet 2\n\n> Quote block\n\nInline code: `x = 1`.")
    st.caption("This is a small caption for additional hints.")
    st.code("""
# Code blocks with syntax highlighting
import math
print(math.sqrt(49))
""", language="python")

    st.subheader("2) Math with LaTeX")
    st.latex(r"""
    P(X = k) = {n \choose k} p^k (1-p)^{n-k}
    """)

    st.subheader("3) Displaying Python objects")
    sample_dict = {"a": 1, "b": 2}
    st.write("Write dict:", sample_dict)
    st.json({"message": "Hello, JSON!", "items": [1, 2, 3]})

    st.divider()
    st.subheader("4) Built-in help")
    st.write("Use `st.help(thing)` to see API help in the app.")
    st.help(st.slider)

# -------------------------------------------------------------
# SECTION: Input Widgets
# -------------------------------------------------------------
elif section == "Input Widgets":
    st.header("Input Widgets")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Buttons & Toggles")
        if st.button("Click me"):
            st.success("Button clicked!")
        st.checkbox("I agree to the terms", key="agree")
        choice = st.radio("Pick one", ["Option A", "Option B", "Option C"], index=0)
        st.write("You chose:", choice)
        st.toggle("Enable feature flag", key="feature_toggle")

        st.subheader("Selects")
        sb = st.selectbox("Select one", ["Apple", "Banana", "Cherry"], index=1)
        ms = st.multiselect("Select many", ["Python", "R", "Julia", "C++"], default=["Python", "Julia"])
        st.write("Selectbox:", sb)
        st.write("Multiselect:", ms)

    with col2:
        st.subheader("Inputs & Sliders")
        txt = st.text_input("Your name", placeholder="Type here...")
        ta = st.text_area("Short bio", height=100)
        num = st.number_input("Pick a number", min_value=0, max_value=100, value=10, step=5)
        date_val = st.date_input("Pick a date")
        time_val = st.time_input("Pick a time")
        color = st.color_picker("Favorite color", "#00f900")
        rng = st.slider("Range slider", min_value=0, max_value=100, value=(20, 80))
        ssel = st.select_slider("Select slider", options=["low", "medium", "high"], value="medium")
        st.write({"name": txt, "bio": ta, "num": num, "date": str(date_val), "time": str(time_val), "color": color, "range": rng, "level": ssel})

    st.subheader("File & Camera")
    uploaded = st.file_uploader("Upload a CSV", type=["csv"])
    if uploaded is not None:
        df = pd.read_csv(uploaded)
        st.dataframe(df)

    try:
        pic = st.camera_input("Take a picture (works in supported browsers)")
        if pic is not None:
            st.success("Got a photo!")
            st.image(pic)
    except Exception:
        st.info("Camera input not supported in this environment.")

    st.subheader("Download")
    csv_bytes = pd.DataFrame({"x": [1, 2, 3], "y": [10, 20, 30]}).to_csv(index=False).encode("utf-8")
    st.download_button("Download sample CSV", data=csv_bytes, file_name="sample.csv", mime="text/csv")

# -------------------------------------------------------------
# SECTION: Layout & Containers
# -------------------------------------------------------------
elif section == "Layout & Containers":
    st.header("Layout & Containers")
    st.write("Use columns, tabs, expanders, containers, and sidebar to organize your UI.")

    st.subheader("Columns")
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        st.write("Left column")
    with c2:
        st.write("Wider middle column")
    with c3:
        st.write("Right column")

    st.subheader("Tabs")
    t1, t2 = st.tabs(["Tab A", "Tab B"])
    with t1:
        st.write("Content for Tab A")
    with t2:
        st.write("Content for Tab B")

    st.subheader("Expandable sections")
    with st.expander("Click to expand"):
        st.write("Hidden details go here.")

    st.subheader("Containers & Placeholders")
    container = st.container(border=True)
    container.write("This is inside a bordered container.")
    placeholder = st.empty()
    if st.button("Update placeholder"):
        placeholder.info("The placeholder was updated!")

    st.sidebar.subheader("Sidebar controls example")
    side_val = st.sidebar.slider("Sidebar slider", 0, 100, 50)
    st.write("Sidebar slider value:", side_val)

# -------------------------------------------------------------
# SECTION: Data Display
# -------------------------------------------------------------
elif section == "Data Display":
    st.header("Data Display")
    df = pd.DataFrame({
        "city": ["Penang", "KL", "JB", "Ipoh"],
        "temp_c": [30.1, 31.5, 29.0, 28.7],
        "humid": [70, 68, 75, 72],
    })

    st.subheader("DataFrame (interactive)")
    st.dataframe(df, use_container_width=True)

    st.subheader("Table (static)")
    st.table(df)

    st.subheader("Data Editor (editable)")
    edited = st.data_editor(df, num_rows="dynamic")
    st.write("Edited DataFrame:")
    st.write(edited)

    st.subheader("Metrics")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Revenue", "$12.3k", "+3.2%")
    with c2:
        st.metric("Users", "1,024", "+12")
    with c3:
        st.metric("Churn", "4.5%", "-0.2%")

# -------------------------------------------------------------
# SECTION: Charts
# -------------------------------------------------------------
elif section == "Charts":
    st.header("Charts")

    chart_df = pd.DataFrame({
        "x": np.arange(0, 100),
        "y1": np.random.randn(100).cumsum(),
        "y2": np.random.randn(100).cumsum(),
    })

    st.subheader("Built-in charts")
    st.line_chart(chart_df.set_index("x"), use_container_width=True)
    st.area_chart(chart_df.set_index("x"), use_container_width=True)
    st.bar_chart(chart_df.set_index("x")["y1"], use_container_width=True)

    st.subheader("Map (optional)")
    try:
        map_df = pd.DataFrame({"lat": [5.336], "lon": [100.306]})  # Penang-ish
        st.map(map_df, zoom=10)
    except Exception:
        st.info("Map display requires pydeck support; skipping here.")

# -------------------------------------------------------------
# SECTION: Status & Feedback
# -------------------------------------------------------------
elif section == "Status & Feedback":
    st.header("Status & Feedback")

    st.success("Success message")
    st.info("Info message")
    st.warning("Warning message")
    st.error("Error message")

    try:
        st.toast("This is a toast notification (if supported)")
    except Exception:
        st.caption("Toast not supported in this version.")

    st.subheader("Exception display")
    try:
        1 / 0
    except Exception as e:
        st.exception(e)

    st.subheader("Progress & Spinner")
    progress = st.progress(0, text="Working...")
    for i in range(0, 101, 10):
        time.sleep(0.05)
        progress.progress(i, text=f"Working... {i}%")
    progress.empty()

    with st.spinner("Simulating a slow task..."):
        time.sleep(0.5)
    st.success("Done!")

    colb1, colb2 = st.columns(2)
    with colb1:
        if st.button("Celebrate 🎈"):
            st.balloons()
    with colb2:
        if st.button("Let it snow ❄️"):
            st.snow()

# -------------------------------------------------------------
# SECTION: Forms & State
# -------------------------------------------------------------
elif section == "Forms & State":
    st.header("Forms & State")

    st.subheader("Forms")
    with st.form("contact_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        msg = st.text_area("Message")
        submitted = st.form_submit_button("Submit")
    if submitted:
        st.success(f"Thanks, {name}! We'll reach out to {email}.")
        st.write({"name": name, "email": email, "message": msg})

    st.subheader("Session State")
    if "counter" not in st.session_state:
        st.session_state.counter = 0

    colc1, colc2 = st.columns(2)
    with colc1:
        if st.button("Increment"):
            st.session_state.counter += 1
    with colc2:
        if st.button("Reset"):
            st.session_state.counter = 0

    st.write("Counter value:", st.session_state.counter)

    st.write("All session state:")
    st.write(st.session_state)

# -------------------------------------------------------------
# SECTION: Media
# -------------------------------------------------------------
elif section == "Media":
    st.header("Media")

    st.subheader("Images")
    img_array = (np.random.rand(200, 300, 3) * 255).astype(np.uint8)
    st.image(img_array, caption="Random image", use_column_width=True)

    st.subheader("Audio")
    audio_bytes = generate_sine_wav(duration_s=1.0, freq_hz=523)  # C5
    st.audio(audio_bytes, format="audio/wav")

    st.subheader("Video (YouTube)")
    st.video("https://www.youtube.com/watch?v=VqgUkExPvLY")  # Public explanatory video

# -------------------------------------------------------------
# SECTION: Caching & Performance
# -------------------------------------------------------------
elif section == "Caching & Performance":
    st.header("Caching & Performance")

    st.subheader("@st.cache_data for pure functions")
    n = st.slider("Compute sum(0..n)", 0, 100000, 50000, step=5000)
    start = time.time()
    total = cached_slow_sum(n)
    elapsed = (time.time() - start) * 1000
    st.write(f"Result: **{total}** (computed in {elapsed:.1f} ms; cached on repeat)")

    st.subheader("@st.cache_resource for expensive singletons")
    res = get_expensive_resource()
    st.write("Resource:", res)

# -------------------------------------------------------------
# SECTION: Advanced
# -------------------------------------------------------------
elif section == "Advanced":
    st.header("Advanced")

    st.subheader("Query parameters (URL state)")
    st.write("The current section is synchronized to the URL query param `?section=...`. You can share links to open the app in a specific section.")

    st.subheader("Theming & Config")
    st.write(
        "Theme is controlled via **.streamlit/config.toml** (not in-app). Try switching between light/dark in the app menu."
    )

    st.subheader("Debug info")
    st.write({
        "Streamlit version": st.__version__,
        "Python": f"{np.__name__} {np.__version__}",
    })

    st.subheader("Tips")
    st.markdown(
        """
- Use **`st.cache_data`** for pure computations; **`st.cache_resource`** for singletons like DB connections.
- Keep layouts simple—favor built-in charts and widgets first.
- Use **forms** to group inputs that should submit together.
- Use **session_state** to remember values between reruns.
- Break larger apps into multiple pages (see `pages/` directory pattern).
        """
    )
