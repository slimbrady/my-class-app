import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 1. Page Configuration for a modern "Wide" feel
st.set_page_config(page_title="Creative Dashboard", layout="wide")

# 2. Sidebar for user inputs and navigation
with st.sidebar:
    st.title("Settings")
    st.markdown("---")
    # Interactive widgets in the sidebar
    chart_type = st.selectbox("Choose a Chart Style", ["Scatter Plot", "Bar Chart"])
    theme_color = st.color_picker("Pick a Highlight Color", "#00f900")
    data_points = st.slider("Select Data Density", 10, 500, 100)
    
    st.info("The sidebar keeps your presentation clean and organized!")

# 3. Main Header
st.title("🎨 Creative Interactive Presentation")
st.write("This is a sleek UI built entirely in Python using [Streamlit](https://streamlit.io/).")

# 4. Generate some random data for visuals
df = pd.DataFrame({
    'x': np.random.randn(data_points),
    'y': np.random.randn(data_points),
    'category': np.random.choice(['Group A', 'Group B', 'Group C'], data_points)
})

# 5. Create Columns for side-by-side layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Live Visualization")
    # Using Plotly for "eye-pleasing" interactive graphics
    if chart_type == "Scatter Plot":
        fig = px.scatter(df, x='x', y='y', color='category', 
                         color_discrete_sequence=[theme_color, "#636EFA", "#EF553B"],
                         template="plotly_dark")
    else:
        fig = px.bar(df.groupby('category').count().reset_index(), 
                     x='category', y='x', color='category',
                     template="plotly_dark")
    
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Data Summary")
    st.markdown("The data updates **instantly** when you change settings in the sidebar.")
    st.dataframe(df.describe(), use_container_width=True)
    
    # Adding a fun interactive trigger
    if st.button("Celebrate Success! 🎉"):
        st.balloons()

# 6. Adding an Expander for technical details
with st.expander("See Raw Data"):
    st.write(df)
