import streamlit as st
import pandas as pd
from io import BytesIO

# Try to import xlsxwriter
try:
    import xlsxwriter
except ImportError:
    xlsxwriter = None
    st.warning("⚠️ XlsxWriter not installed. Excel download will be disabled.")

# Streamlit page config
st.set_page_config(page_title="📂 File Cleaner & Converter", layout="wide")
st.title("📂 File Cleaner & Converter")
st.write("Upload your CSV or Excel files to clean and convert them easily ⚡")

# Upload files
uploaded_files = st.file_uploader(
    "Upload your CSV or Excel files", type=["csv", "xlsx"], accept_multiple_files=True
)

# If files uploaded
if uploaded_files:
    for uploaded_file in uploaded_files:
        file_extension = uploaded_file.name.split(".")[-1].lower()

        # Read file into DataFrame
        try:
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
            numeric_columns = df.select_dtypes(include="number").columns
            df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].mean())
            st.success("✅ Missing values filled with column means.")
            st.dataframe(df.head())

        # Select columns
        selected_columns = st.multiselect(
            f"Select Columns - {uploaded_file.name}",
            options=df.columns,
            default=list(df.columns)
        )

        df_filtered = df[selected_columns]

        # Prepare to download
        buffer = BytesIO()

        if file_extension == "csv":
            df_filtered.to_csv(buffer, index=False)
            buffer.seek(0)
            st.download_button(
                label=f"✅ Download Cleaned CSV - {uploaded_file.name}",
                data=buffer,
                file_name=f"cleaned_{uploaded_file.name}",
                mime="text/csv"
            )

        elif file_extension == "xlsx":
            if xlsxwriter:
                try:
                    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                        df_filtered.to_excel(writer, index=False, sheet_name='CleanedData')
                    buffer.seek(0)
                    st.download_button(
                        label=f"⬇ Download Cleaned Excel - {uploaded_file.name}",
                        data=buffer,
                        file_name=f"cleaned_{uploaded_file.name}",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                except Exception as e:
                    st.error(f"❌ Error writing Excel: {e}")
            else:
                st.warning("⚠️ Excel download skipped (xlsxwriter not installed).")
 