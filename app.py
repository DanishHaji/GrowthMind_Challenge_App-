import streamlit as st
import pandas as pd
import os
from io import BytesIO
import plotly.express as px # type: ignore
import zipfile

# -------------------- Streamlit Page Configuration --------------------
st.set_page_config(page_title="Data Sweeper Pro", layout="wide")

# -------------------- Sidebar: Theme Selection --------------------
theme = st.sidebar.radio("Select Theme:", ["Dark Mode", "Light Mode"], index=0)

# Apply Theme Using Streamlit Config
if theme == "Dark Mode":
    st.markdown(
        """
        <style>
            body { background-color: #121212; color: #ffffff; }
            .stApp { background-color: #121212; }
            h1, h2, h3, h4, h5, h6, p, label, .stTextInput, .stRadio, .stSelectbox, .stDataFrame, .stMarkdown {
                color: #ffffff !important;
            }
            /* Sidebar styling */
            .stSidebar, .stSidebarContent { background-color: #1e1e1e !important; }
            .stSidebar h1, .stSidebar h2, .stSidebar h3, .stSidebar h4, .stSidebar h5, .stSidebar h6, .stSidebar p, .stSidebar label {
                color: #ffffff !important;
            }
            /* Button styling */
            div.stButton > button {
                background-color: #000000 !important;
                color: #ffffff !important;
                border-radius: 5px;
                border: 1px solid #ffffff;
            }
            div.stButton > button:hover {
                background-color: #333333 !important;
            }
            /* File Conversion Section Styling */
            div.stRadio, div.stDownloadButton {
                color: #000000 !important;
            }
            /* Download Button Styling (Always Black Text) */
            div.stDownloadButton > button {
                background-color: #000000 !important;
                color: #000000 !important;
                border-radius: 5px;
                border: 1px solid #000000;
            }
            div.stDownloadButton > button:hover {
                background-color: #333333 !important; /* Keeps background white */
                color: #ffffff !important; /* Keeps text black */
            }
        </style>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown(
        """
        <style>
            body { background-color: #ffffff; color: #333333; }
            .stApp { background-color: #ffffff; }
            .stTitle, .stHeader, .stText, .stDataFrame { color: #333333; }
        </style>
        """,
        unsafe_allow_html=True
    )

# -------------------- App Title and Description --------------------
st.title("Data Sweeper Pro 🚀")
st.write("Easily clean, transform, visualize, and convert your datasets.")

# -------------------- File Upload Section --------------------
uploaded_files = st.file_uploader(
    "Upload your CSV or Excel files:", type=["csv", "xlsx"], accept_multiple_files=True
)
processed_files = {}

if uploaded_files:
    for file in uploaded_files:
        file_extension = os.path.splitext(file.name)[-1].lower()
        
        # Read File Based on Extension
        if file_extension == ".csv":
            df = pd.read_csv(file)
        elif file_extension == ".xlsx":
            df = pd.read_excel(file)
        else:
            st.error(f"Unsupported file type: {file_extension}")
            continue
        
        # Display File Info
        st.subheader(f"📄 {file.name}")
        st.write(f"**File Size:** {file.size / 1024:.2f} KB")
        st.dataframe(df.head())

        # -------------------- Data Cleaning Section --------------------
        st.subheader("🛠️ Data Cleaning")
        col1, col2 = st.columns(2)

        with col1:
            if st.button(f"Remove Duplicates - {file.name}"):
                df.drop_duplicates(inplace=True)
                st.write("✅ Duplicates removed!")

            if st.button(f"Normalize Numeric Columns - {file.name}"):
                numeric_cols = df.select_dtypes(include=['number']).columns
                df[numeric_cols] = (df[numeric_cols] - df[numeric_cols].min()) / (df[numeric_cols].max() - df[numeric_cols].min())
                st.write("✅ Numeric columns normalized!")

        with col2:
            if st.button(f"Fill Missing Values - {file.name}"):
                numeric_cols = df.select_dtypes(include=['number']).columns
                df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                st.write("✅ Missing values filled with column mean!")

        # -------------------- Data Visualization Section --------------------
        st.subheader("📊 Data Visualization")
        chart_type = st.selectbox(
            "Choose a chart type:", ["Bar Chart", "Histogram", "Pie Chart", "Scatter Plot"], key=file.name
        )

        numeric_columns = df.select_dtypes(include=['number']).columns
        if len(numeric_columns) >= 2:
            x_axis = st.selectbox("X-axis:", numeric_columns, key=f"x_{file.name}")
            y_axis = st.selectbox("Y-axis:", numeric_columns, key=f"y_{file.name}")

            if chart_type == "Bar Chart":
                fig = px.bar(df, x=x_axis, y=y_axis)
            elif chart_type == "Histogram":
                fig = px.histogram(df, x=x_axis)
            elif chart_type == "Pie Chart":
                fig = px.pie(df, names=x_axis, values=y_axis)
            elif chart_type == "Scatter Plot":
                fig = px.scatter(df, x=x_axis, y=y_axis)
            
            st.plotly_chart(fig)

        # -------------------- File Conversion Section --------------------
        st.subheader("🔄 Convert & Download")
        conversion_type = st.radio(
            f"Convert {file.name} to:", ["CSV", "Excel"], key=f"conv_{file.name}"
        )

        buffer = BytesIO()
        if conversion_type == "CSV":
            df.to_csv(buffer, index=False)
            file_name = file.name.replace(file_extension, ".csv")
            mime_type = "text/csv"
        else:
            df.to_excel(buffer, index=False, engine='openpyxl')
            file_name = file.name.replace(file_extension, ".xlsx")
            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        buffer.seek(0)
        processed_files[file_name] = buffer
        st.download_button(f"⬇️ Download {file_name}", buffer, file_name=file_name, mime=mime_type)

# -------------------- Bulk Download (Zip) --------------------
if processed_files:
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        for file_name, file_buffer in processed_files.items():
            zf.writestr(file_name, file_buffer.getvalue())

    zip_buffer.seek(0)
    st.download_button("⬇️ Download All Processed Files", zip_buffer, file_name="processed_files.zip", mime="application/zip")

st.success("🎉 All files processed successfully!")
