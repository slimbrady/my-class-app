

{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 2,
   "id": "d4ec482a",
   "metadata": {},
   "outputs": [
    {
     "ename": "ModuleNotFoundError",
     "evalue": "No module named 'streamlit'",
     "output_type": "error",
     "traceback": [
      "\u001b[0;31m---------------------------------------------------------------------------\u001b[0m",
      "\u001b[0;31mModuleNotFoundError\u001b[0m                       Traceback (most recent call last)",
      "Cell \u001b[0;32mIn[2], line 1\u001b[0m\n\u001b[0;32m----> 1\u001b[0m \u001b[38;5;28;01mimport\u001b[39;00m\u001b[38;5;250m \u001b[39m\u001b[38;5;21;01mstreamlit\u001b[39;00m\u001b[38;5;250m \u001b[39m\u001b[38;5;28;01mas\u001b[39;00m\u001b[38;5;250m \u001b[39m\u001b[38;5;21;01mst\u001b[39;00m\n\u001b[1;32m      2\u001b[0m \u001b[38;5;28;01mimport\u001b[39;00m\u001b[38;5;250m \u001b[39m\u001b[38;5;21;01mpandas\u001b[39;00m\u001b[38;5;250m \u001b[39m\u001b[38;5;28;01mas\u001b[39;00m\u001b[38;5;250m \u001b[39m\u001b[38;5;21;01mpd\u001b[39;00m\n\u001b[1;32m      3\u001b[0m \u001b[38;5;28;01mimport\u001b[39;00m\u001b[38;5;250m \u001b[39m\u001b[38;5;21;01mnumpy\u001b[39;00m\u001b[38;5;250m \u001b[39m\u001b[38;5;28;01mas\u001b[39;00m\u001b[38;5;250m \u001b[39m\u001b[38;5;21;01mnp\u001b[39;00m\n",
      "\u001b[0;31mModuleNotFoundError\u001b[0m: No module named 'streamlit'"
     ]
    }
   ],
   "source": [
    "import streamlit as st\n",
    "import pandas as pd\n",
    "import numpy as np\n",
    "import plotly.express as px\n",
    "\n",
    "# 1. Page Configuration for a modern \"Wide\" feel\n",
    "st.set_page_config(page_title=\"Creative Dashboard\", layout=\"wide\")\n",
    "\n",
    "# 2. Sidebar for user inputs and navigation\n",
    "with st.sidebar:\n",
    "    st.title(\"Settings\")\n",
    "    st.markdown(\"---\")\n",
    "    # Interactive widgets in the sidebar\n",
    "    chart_type = st.selectbox(\"Choose a Chart Style\", [\"Scatter Plot\", \"Bar Chart\"])\n",
    "    theme_color = st.color_picker(\"Pick a Highlight Color\", \"#00f900\")\n",
    "    data_points = st.slider(\"Select Data Density\", 10, 500, 100)\n",
    "    \n",
    "    st.info(\"The sidebar keeps your presentation clean and organized!\")\n",
    "\n",
    "# 3. Main Header\n",
    "st.title(\"🎨 Creative Interactive Presentation\")\n",
    "st.write(\"This is a sleek UI built entirely in Python using [Streamlit](https://streamlit.io/).\")\n",
    "\n",
    "# 4. Generate some random data for visuals\n",
    "df = pd.DataFrame({\n",
    "    'x': np.random.randn(data_points),\n",
    "    'y': np.random.randn(data_points),\n",
    "    'category': np.random.choice(['Group A', 'Group B', 'Group C'], data_points)\n",
    "})\n",
    "\n",
    "# 5. Create Columns for side-by-side layout\n",
    "col1, col2 = st.columns([2, 1])\n",
    "\n",
    "with col1:\n",
    "    st.subheader(\"Live Visualization\")\n",
    "    # Using Plotly for \"eye-pleasing\" interactive graphics\n",
    "    if chart_type == \"Scatter Plot\":\n",
    "        fig = px.scatter(df, x='x', y='y', color='category', \n",
    "                         color_discrete_sequence=[theme_color, \"#636EFA\", \"#EF553B\"],\n",
    "                         template=\"plotly_dark\")\n",
    "    else:\n",
    "        fig = px.bar(df.groupby('category').count().reset_index(), \n",
    "                     x='category', y='x', color='category',\n",
    "                     template=\"plotly_dark\")\n",
    "    \n",
    "    st.plotly_chart(fig, use_container_width=True)\n",
    "\n",
    "with col2:\n",
    "    st.subheader(\"Data Summary\")\n",
    "    st.markdown(\"The data updates **instantly** when you change settings in the sidebar.\")\n",
    "    st.dataframe(df.describe(), use_container_width=True)\n",
    "    \n",
    "    # Adding a fun interactive trigger\n",
    "    if st.button(\"Celebrate Success! 🎉\"):\n",
    "        st.balloons()\n",
    "\n",
    "# 6. Adding an Expander for technical details\n",
    "with st.expander(\"See Raw Data\"):\n",
    "    st.write(df)"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "envname",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.9.6"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}


