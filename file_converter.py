import streamlit as st
import pandas as pd
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Advanced File Converter",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        margin-top: 1em;
    }
    .stDataFrame {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 1rem;
    }
    .stSuccess {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.title("🔄 Advanced File Converter")
st.markdown("""
    <div style='background-color: #f8f9fa; padding: 1rem; border-radius: 5px; margin-bottom: 2rem;'>
        <h3>Features:</h3>
        <ul>
            <li>Convert between CSV and Excel formats</li>
            <li>Clean and preprocess your data</li>
            <li>Interactive visualizations</li>
            <li>Advanced data analysis</li>
        </ul>
    </div>
""", unsafe_allow_html=True)

# File uploader with better styling
st.markdown("### 📁 Upload Your Files")
files = st.file_uploader(
    "Drag and drop your CSV or Excel files here",
    type=["csv", "xlsx"],
    accept_multiple_files=True
)

if files:
    for file in files:
        try:
            # File information
            file_size = file.size / (1024 * 1024)  # Convert to MB
            st.markdown(f"""
                <div style='background-color: #e9ecef; padding: 1rem; border-radius: 5px; margin-bottom: 1rem;'>
                    <h4>📄 {file.name}</h4>
                    <p>Size: {file_size:.2f} MB</p>
                </div>
            """, unsafe_allow_html=True)

            # Progress indicator
            with st.spinner('Loading file...'):
                ext = file.name.split(".")[-1]
                df = pd.read_csv(file) if ext == "csv" else pd.read_excel(file)

            # Data preview with tabs
            tab1, tab2, tab3 = st.tabs(["Preview", "Data Info", "Visualization"])
            
            with tab1:
                st.dataframe(df.head(), use_container_width=True)
            
            with tab2:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("#### Data Shape")
                    st.write(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")
                with col2:
                    st.markdown("#### Missing Values")
                    missing_values = df.isnull().sum()
                    st.write(missing_values[missing_values > 0])
            
            with tab3:
                if not df.select_dtypes(include="number").empty:
                    numeric_cols = df.select_dtypes(include="number").columns
                    if len(numeric_cols) >= 2:
                        chart_type = st.selectbox(
                            "Select Chart Type",
                            ["Bar Chart", "Line Chart", "Scatter Plot"],
                            key=f"chart_{file.name}"
                        )
                        col1, col2 = st.columns(2)
                        with col1:
                            x_col = st.selectbox("Select X-axis", numeric_cols, key=f"x_{file.name}")
                        with col2:
                            y_col = st.selectbox("Select Y-axis", numeric_cols, key=f"y_{file.name}")
                        
                        if chart_type == "Bar Chart":
                            fig = px.bar(df, x=x_col, y=y_col)
                        elif chart_type == "Line Chart":
                            fig = px.line(df, x=x_col, y=y_col)
                        else:
                            fig = px.scatter(df, x=x_col, y=y_col)
                        
                        st.plotly_chart(fig, use_container_width=True)

            # Data cleaning options
            st.markdown("### 🧹 Data Cleaning Options")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.checkbox(f"Remove Duplicates - {file.name}"):
                    original_rows = len(df)
                    df = df.drop_duplicates()
                    removed_rows = original_rows - len(df)
                    st.success(f"Removed {removed_rows} duplicate rows")
                    st.dataframe(df.head(), use_container_width=True)

            with col2:
                if st.checkbox(f"Fill Missing Values - {file.name}"):
                    df.fillna(df.select_dtypes(include=["number"]).mean(), inplace=True)
                    st.success("Missing values filled with mean")
                    st.dataframe(df.head(), use_container_width=True)

            # Column selection
            st.markdown("### 📊 Select Columns")
            selected_columns = st.multiselect(
                f"Select columns to keep - {file.name}",
                df.columns,
                default=df.columns
            )
            df = df[selected_columns]

            # Export options
            st.markdown("### 💾 Export Options")
            format_choice = st.radio(
                f"Convert {file.name} to:",
                ["CSV", "Excel"],
                key=file.name,
                horizontal=True
            )

            if st.button(f"Download {file.name} as {format_choice}", key=f"download_{file.name}"):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                if format_choice == "CSV":
                    csv_data = df.to_csv(index=False)
                    st.download_button(
                        label="Click to Download CSV",
                        data=csv_data,
                        file_name=f"{file.name.split('.')[0]}_{timestamp}.csv",
                        mime="text/csv"
                    )
                else:
                    excel_buffer = BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                        df.to_excel(writer, index=False, sheet_name='Sheet1')
                    excel_buffer.seek(0)
                    st.download_button(
                        label="Click to Download Excel",
                        data=excel_buffer,
                        file_name=f"{file.name.split('.')[0]}_{timestamp}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

        except Exception as e:
            st.error(f"Error processing {file.name}: {str(e)}")
            st.info("Please check if the file format is correct and try again.")
