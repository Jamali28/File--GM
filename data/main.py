import streamlit as st
import pandas as pd
from io import BytesIO

# Optional: Ensure xlsxwriter is installed
try:
    import xlsxwriter
except ImportError:
    xlsxwriter = None
    st.error("❌ The 'xlsxwriter' module is not installed. Please install it using `pip install XlsxWriter` to enable Excel file downloads.")

# Set up the Streamlit page configuration
st.set_page_config(page_title="📂 File Cleaner & Converter", layout="wide")
st.title("📂 File Cleaner & Converter")
st.write("Upload your CSV or Excel files to clean and convert them easily ⚡")

# File uploader allowing multiple file uploads
uploaded_files = st.file_uploader("Upload your CSV or Excel files", type=["csv", "xlsx"], accept_multiple_files=True)

# Process each uploaded file
if uploaded_files:
    for uploaded_file in uploaded_files:
        file_extension = uploaded_file.name.split(".")[-1].lower()

        # Read the uploaded file into a DataFrame
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

        # Option to fill missing values
        if st.checkbox(f"Fill Missing Values - {uploaded_file.name}"):
            numeric_columns = df.select_dtypes(include='number').columns
            df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].mean())
            st.success("✅ Missing values filled with column means.")
            st.dataframe(df.head())

        # Option to select specific columns
        selected_columns = st.multiselect(
            f"Select Columns - {uploaded_file.name}",
            options=df.columns,
            default=list(df.columns)
        )
        df_filtered = df[selected_columns]
        st.dataframe(df_filtered.head())

        # Prepare the cleaned data for download
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
            if xlsxwriter is None:
                continue
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
                st.error(f"❌ Error generating Excel file: {e}")
