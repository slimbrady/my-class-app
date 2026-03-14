import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import reveal_slides as rs

# 1. Define your slides in Markdown
slide_content = """
# Genesis 24-41 
---
## Interaction Time!
Move the slider on the right to see how the data points change.
---
## Why this matters?
Because real-time data is more engaging!
"""

# 2. Create side-by-side columns
col1, col2 = st.columns([2, 1]) # Slides get more space

with col1:
    # This renders the "Cinematic" Reveal.js slides
    rs.slides(slide_content, height=500, theme='sky')

with col2:
    st.subheader("Student Interaction")
    # This widget lives outside the slides but is part of the "presentation"
    points = st.slider("Select number of points", 1, 100, 25)
    st.write(f"Displaying {points} random points:")
    st.scatter_chart([i**2 for i in range(points)])

if 'votes' not in st.session_state:
    st.session_state.votes = {"Option A": 0, "Option B": 0, "Option C": 0}

st.title("Class Poll 🗳️")

# Part 1: The Voting Interface (This is what you click, or they click on phones)
st.subheader("Cast your vote:")
cols = st.columns(3)
if cols[0].button("A"):
    st.session_state.votes["Option A"] += 1
if cols[1].button("B"):
    st.session_state.votes["Option B"] += 1
if cols[2].button("C"):
    st.session_state.votes["Option C"] += 1

# Part 2: The Results (This shows on your big screen)
st.subheader("Live Results")
st.bar_chart(st.session_state.votes)

if st.button("Reset Poll"):
    st.session_state.votes = {"Option A": 0, "Option B": 0, "Option C": 0}
    st.rerun()