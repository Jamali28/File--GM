import streamlit as st
import pandas as pd
from io import BytesIO

# Try to import xlsxwriter (optional dependency for Excel export)
try:
    import xlsxwriter
    HAS_XLSXWRITER = True
except ImportError:
    HAS_XLSXWRITER = False

# Set up the Streamlit page
st.set_page_config(page_title="📂 File Cleaner & Converter", layout="wide")
st.title("📂 File Cleaner & Converter")
st.write("Upload your CSV or Excel files to clean and convert them easily ⚡")

# Show warning if xlsxwriter is not installed
if not HAS_XLSXWRITER:
    st.warning("⚠️ The 'xlsxwriter' module is not installed. Excel downloads will be disabled. Run `pip install xlsxwriter` to enable this feature.")

# File uploader
uploaded_files = st.file_uploader("Upload your CSV or Excel files", type=["csv", "xlsx"], accept_multiple_files=True)

# Process files
if uploaded_files:
    for uploaded_file in uploaded_files:
        file_extension = uploaded_file.name.split(".")[-1].lower()

        try:
            # Load file into DataFrame
            if file_extension == "csv":
                df = pd.read_csv(uploaded_file)
            elif file_extension == "xlsx":
                df = pd.read_excel(uploaded_file)
            else:
                st.error(f"❌ Unsupported file type: {file_extension}")
                continue
        except Exception as e:
            st.error(f"❌ Error reading {uploaded_file.name}: {e}")
            continue

        st.subheader(f"🔍 Preview - {uploaded_file.name}")
        st.dataframe(df.head())

        # Fill missing values
        if st.checkbox(f"Fill Missing Values - {uploaded_file.name}"):
            numeric_cols = df.select_dtypes(include='number').columns
            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
            st.success("✅ Missing values filled with column means.")
            st.dataframe(df.head())

        # Column selection
        selected_columns = st.multiselect(
            f"Select Columns - {uploaded_file.name}",
            options=df.columns.tolist(),
            default=df.columns.tolist()
        )

        df_filtered = df[selected_columns]
        st.dataframe(df_filtered.head())

        # Download button
        buffer = BytesIO()

        if file_extension == "csv":
            df_filtered.to_csv(buffer, index=False)
            buffer.seek(0)
            st.download_button(
                label=f"⬇ Download Cleaned CSV - {uploaded_file.name}",
                data=buffer,
                file_name=f"cleaned_{uploaded_file.name}",
                mime="text/csv"
            )

        elif file_extension == "xlsx":
            if not HAS_XLSXWRITER:
                st.warning(f"⚠️ Skipping Excel export for {uploaded_file.name} (xlsxwriter not installed).")
                continue
            try:
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df_filtered.to_excel(writer, index=False, sheet_name='CleanedData')
                buffer.seek(0)
                st.download_button(
                    label=f"⬇ Download Cleaned Excel - {uploaded_file.name}",
                    data=buffer,
                    file_name=f"cleaned_{uploaded_file.name}",
