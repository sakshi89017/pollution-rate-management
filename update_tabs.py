# Read the file
with open('global_user_view.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find and update the imports
new_lines = []
skip_next = False
for i, line in enumerate(lines):
    if i == 0:
        # Replace the first 4 import lines
        if 'import streamlit as st' in lines[0]:
            new_imports = """import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx

"""
            new_lines.append(new_imports)
            # Skip the next 3 lines (old imports)
            skip_count = 3
            continue
    
    if i in [1, 2, 3, 4]:
        # Skip old import lines
        continue
    
    new_lines.append(line)

# Join all lines
content = ''.join(new_lines)

# Now fix tabs
content = content.replace(
    'tab1, tab2, tab3, tab4, tab5 = st.tabs(',
    'tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs('
)

# Fix tabs list
old_tabs = '["📊 Overview", "📈 Analytics", "⚠️ Hazardous", "🔍 Country Deep Dive", "🎨 Visualizations"]'
new_tabs = '["📊 Overview", "📈 Analytics", "⚠️ Hazardous", "🔍 Country Deep Dive", "🎨 Visualizations", "🗺️ Map", "🕸️ Network"]'
content = content.replace(old_tabs, new_tabs)

# Write back
with open('global_user_view.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated file successfully")
