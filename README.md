# 🔧 RAM Repair eFuse Generator

A collection of Streamlit tools for semiconductor test-flow analysis and eFuse generation.

---

## Apps

| File | Description |
|---|---|
| `efuse_generator.py` | eFuse hex generator and Summary File Reader |
| `app.py` | **PList → CSV Generator** (parse `GlobalPList` blocks into a test-input CSV) |
| `streamlit_app.py` | Streamlit beginner guide / demo |

---

## PList → CSV Generator (`app.py`)

Parses `.txt` files that contain `GlobalPList …_PLIST { … }` blocks and generates
a test-input CSV with columns:

> `TestStep` · `Module` · `Zip` · `Plist` · `GlobalPlist` · `TestName` · `VMPREFIX` · `vrev` · `mode` · `vectype` · `Optional Switches` · `Hard Tuple ID`

### Run locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch the PList → CSV app
streamlit run app.py

# Or launch the eFuse Generator
streamlit run efuse_generator.py
```

### Usage

1. Upload a `.txt` file containing `GlobalPList` blocks.
2. (Optional) Override the filename used to derive the `Plist` column.
3. (Optional) Enable **Hard Tuple ID** in the sidebar.
4. Click **Generate CSV** to parse the file.
5. Review the preview table, then download the CSV.

---

## Parser module (`plist_parser.py`)

The parsing logic is factored into a reusable module that can be imported independently:

```python
from plist_parser import parse_plist_text, rows_to_csv_bytes

rows, warnings = parse_plist_text(
    text=open("my_input.txt").read(),
    input_filename="my_input.txt",
    hard_tupleid_en=False,
)

csv_bytes = rows_to_csv_bytes(rows)
open("output.csv", "wb").write(csv_bytes)
```

---

## Running tests

```bash
pytest tests/
```

