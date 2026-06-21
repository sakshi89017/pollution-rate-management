import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
import networkx as nx

st.set_page_config(
    page_title="Global Air Quality Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        * {
            margin: 0;
            padding: 0;
        }
        
        .stApp {
            background: linear-gradient(135deg, #0a1428 0%, #1a2a4a 50%, #0d1f3d 100%);
            color: #e8eef5;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        .stSidebar {
            background: linear-gradient(180deg, #0f1f3f 0%, #1a2f52 100%);
            border-right: 2px solid #2a5a9f;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: rgba(42, 90, 159, 0.1);
            border-radius: 12px;
            padding: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: transparent;
            border-radius: 8px;
            color: #b0bfd9;
            font-weight: 500;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: linear-gradient(135deg, #0e8cf6 0%, #0a6bbf 100%);
            color: white;
        }
        
        .metric-card {
            background: linear-gradient(135deg, #1a3a66 0%, #0f2847 100%);
            border: 2px solid #2a5a9f;
            border-radius: 12px;
            padding: 24px;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .metric-card:hover {
            border-color: #0e8cf6;
            box-shadow: 0 0 20px rgba(14, 140, 246, 0.3);
            transform: translateY(-4px);
        }
        
        .stButton>button {
            background: linear-gradient(135deg, #0e8cf6 0%, #0a6bbf 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .stButton>button:hover {
            box-shadow: 0 0 30px rgba(14, 140, 246, 0.4);
        }
        
        .stSelectbox, .stMultiSelect {
            border-radius: 8px;
        }
        
        h1 {
            color: #fff;
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 8px;
            background: linear-gradient(135deg, #0e8cf6, #00d4ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        h2 {
            color: #b0bfd9;
            font-size: 1.8rem;
            font-weight: 600;
            margin-top: 24px;
            margin-bottom: 16px;
        }
        
        h3 {
            color: #00d4ff;
            font-size: 1.4rem;
            font-weight: 600;
        }
        
        .subtitle {
            color: #8fa3c4;
            font-size: 1.1rem;
            margin-bottom: 24px;
        }
        
        .stDataFrame {
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid #2a5a9f;
        }
        
        div[data-testid="stMetricValue"] {
            font-size: 2rem;
            color: #00d4ff;
            font-weight: 700;
        }
        
        div[data-testid="stMetricLabel"] {
            color: #8fa3c4;
            font-weight: 600;
        }
        
        .alert-box {
            background: linear-gradient(135deg, rgba(14, 140, 246, 0.2), rgba(0, 212, 255, 0.1));
            border-left: 4px solid #0e8cf6;
            border-radius: 8px;
            padding: 16px;
            margin: 16px 0;
            color: #b0bfd9;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Country coordinates mapping
COUNTRY_COORDS = {
    "Afghanistan": [33.9391, 67.7100], "Albania": [41.1533, 20.1683], "Algeria": [28.0339, 1.6596],
    "Argentina": [-38.4161, -63.6167], "Australia": [-25.2744, 133.7751], "Austria": [47.5162, 14.5501],
    "Bangladesh": [23.6850, 90.3563], "Belgium": [50.5039, 4.4699], "Brazil": [-14.2350, -51.9253],
    "Bulgaria": [42.7339, 25.4858], "Canada": [56.1304, -106.3468], "Chile": [-35.6751, -71.5430],
    "China": [35.8617, 104.1954], "Colombia": [4.5709, -74.2973], "Croatia": [45.1000, 15.2000],
    "Czech Republic": [49.8175, 15.4730], "Denmark": [56.2639, 9.5018], "Egypt": [26.8206, 30.8025],
    "Estonia": [58.5953, 25.0136], "Ethiopia": [9.1450, 40.4897], "Finland": [61.9241, 25.7482],
    "France": [46.2276, 2.2137], "Germany": [51.1657, 10.4515], "Greece": [39.0742, 21.8243],
    "Hungary": [47.1625, 19.5033], "India": [20.5937, 78.9629], "Indonesia": [-0.7893, 113.9213],
    "Iran": [32.4279, 53.6880], "Iraq": [33.3128, 44.3615], "Ireland": [53.4129, -8.2439],
    "Israel": [31.0461, 34.8516], "Italy": [41.8719, 12.5674], "Japan": [36.2048, 138.2529],
    "Jordan": [30.5852, 36.2384], "Kazakhstan": [48.0196, 66.9237], "Kenya": [-0.0236, 37.9062],
    "Korea, Republic of": [35.9078, 127.7669], "Kuwait": [29.3117, 47.4818], "Kyrgyzstan": [41.2044, 74.7661],
    "Latvia": [56.8796, 24.6032], "Lebanon": [33.8547, 35.8623], "Lithuania": [55.1694, 23.8812],
    "Luxembourg": [49.8153, 6.1296], "Malaysia": [4.2105, 101.6964], "Mexico": [23.6345, -102.5528],
    "Netherlands": [52.1326, 5.2913], "New Zealand": [-40.9006, 174.8860], "Nigeria": [9.0820, 8.6753],
    "Pakistan": [30.3753, 69.3451], "Peru": [-9.1900, -75.0152], "Philippines": [12.8797, 121.7740],
    "Poland": [51.9194, 19.1451], "Portugal": [39.3999, -8.2245], "Romania": [45.9432, 24.9668],
    "Russian Federation": [61.5240, 105.3188], "Saudi Arabia": [23.8859, 45.0792], "Serbia": [44.0165, 21.0059],
    "Singapore": [1.3521, 103.8198], "Slovakia": [48.6690, 19.6990], "Slovenia": [46.1512, 14.9955],
    "South Africa": [-30.5595, 22.9375], "Spain": [40.4637, -3.7492], "Sweden": [60.1282, 18.6435],
    "Switzerland": [46.8182, 8.2275], "Taiwan": [23.6978, 120.9605], "Thailand": [15.8700, 100.9925],
    "Turkey": [38.9637, 35.2433], "Ukraine": [48.3794, 31.1656], "United Kingdom": [55.3781, -3.4360],
    "United States": [37.0902, -95.7129], "Vietnam": [14.0583, 108.2772], "Yemen": [15.5527, 48.5164],
}

def get_country_coords(country):
    """Get coordinates for a country"""
    return COUNTRY_COORDS.get(country, [20, 0])

def create_network_graph(df, top_countries=10):
    """Create a network graph of countries and top polluted cities"""
    G = nx.Graph()
    
    # Get top countries by pollution
    top_countries_list = df.groupby("country_name")["aqi_value"].mean().nlargest(top_countries).index.tolist()
    top_df = df[df["country_name"].isin(top_countries_list)]
    
    # Add nodes
    for country in top_countries_list:
        avg_aqi = df[df["country_name"] == country]["aqi_value"].mean()
        G.add_node(country, node_type="country", aqi=avg_aqi)
    
    # Add top cities for each country
    for country in top_countries_list:
        top_cities = top_df[top_df["country_name"] == country].nlargest(3, "aqi_value")
        for _, row in top_cities.iterrows():
            city = row["city_name"]
            G.add_node(city, node_type="city", aqi=row["aqi_value"])
            G.add_edge(country, city, weight=row["aqi_value"] / 100)
    
    return G

@st.cache_data
def load_data():
    df = pd.read_csv("./data/global_air_pollution_data.csv")
    df = df.copy()
    df["country_name"] = df["country_name"].fillna("Unknown")
    df["city_name"] = df["city_name"].fillna("Unknown")
    df["aqi_value"] = pd.to_numeric(df["aqi_value"], errors="coerce")
    df["aqi_category"] = df["aqi_category"].astype(str)
    return df


def get_aqi_color(value):
    if value <= 50:
        return "#00b050"
    elif value <= 100:
        return "#ffeb3b"
    elif value <= 150:
        return "#ff9800"
    elif value <= 200:
        return "#ff6b6b"
    else:
        return "#8b0000"


df = load_data()

st.title("🌍 Global Air Quality Dashboard")
st.markdown('<div class="subtitle">Real-time monitoring of air pollution across the globe</div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🎯 Dashboard Controls")
    
    selected_country = st.selectbox(
        "Select Country",
        options=["All"] + sorted(df["country_name"].unique().tolist()),
        key="country_select"
    )
    
    st.markdown("---")
    
    selected_categories = st.multiselect(
        "Filter by AQI Categories",
        options=sorted(df["aqi_category"].unique().tolist()),
        default=sorted(df["aqi_category"].unique().tolist()),
    )
    
    st.markdown("---")
    
    aqi_range = st.slider(
        "AQI Value Range",
        min_value=int(df["aqi_value"].min()),
        max_value=int(df["aqi_value"].max()),
        value=(int(df["aqi_value"].min()), int(df["aqi_value"].max())),
    )
    
    st.markdown("---")
    st.markdown("### 📊 Quick Stats")
    st.metric("🌐 Total Records", f"{len(df):,}")
    st.metric("🗺️ Countries", df["country_name"].nunique())
    st.metric("📈 Avg AQI", f"{df['aqi_value'].mean():.1f}")

filtered_df = df[
    (df["aqi_category"].isin(selected_categories)) &
    (df["aqi_value"] >= aqi_range[0]) &
    (df["aqi_value"] <= aqi_range[1])
]

if selected_country != "All":
    filtered_df = filtered_df[filtered_df["country_name"] == selected_country]

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
    ["📊 Overview", "📈 Analytics", "⚠️ Hazardous", "🔍 Country Deep Dive", "🎨 Visualizations", "🗺️ Map", "🕸️ Network"]
)

with tab1:
    st.markdown("### Global Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Records",
            f"{len(filtered_df):,}",
            delta=f"{len(filtered_df) - len(df)}"
        )
    
    with col2:
        avg_aqi = filtered_df["aqi_value"].mean()
        st.metric(
            "Average AQI",
            f"{avg_aqi:.1f}",
            delta=f"{avg_aqi - df['aqi_value'].mean():.1f}",
            delta_color="inverse"
        )
    
    with col3:
        hazardous = len(filtered_df[filtered_df["aqi_value"] > 300])
        st.metric("🔴 Hazardous Cities", f"{hazardous:,}")
    
    with col4:
        countries = filtered_df["country_name"].nunique()
        st.metric("🗺️ Countries Affected", f"{countries}")
    
    st.markdown("---")
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("### Category Distribution")
        category_data = filtered_df["aqi_category"].value_counts().reset_index()
        category_data.columns = ["Category", "Count"]
        
        chart = alt.Chart(category_data).mark_bar(
            cornerRadiusTopLeft=8,
            cornerRadiusTopRight=8
        ).encode(
            x=alt.X("Count:Q", title="Number of Records"),
            y=alt.Y("Category:N", sort="-x", title="AQI Category"),
            color=alt.Color("Category:N", legend=None),
            tooltip=["Category", "Count"]
        ).properties(height=350).interactive()
        
        st.altair_chart(chart, use_container_width=True)
    
    with col_chart2:
        st.markdown("### Top Affected Countries")
        top_countries = filtered_df["country_name"].value_counts().head(10).reset_index()
        top_countries.columns = ["Country", "Cities"]
        
        chart2 = alt.Chart(top_countries).mark_bar().encode(
            y=alt.Y("Country:N", sort="-x", title="Country"),
            x=alt.X("Cities:Q", title="Number of Cities"),
            color=alt.Color("Cities:Q", scale=alt.Scale(scheme="reds"), legend=None),
            tooltip=["Country", "Cities"]
        ).properties(height=350).interactive()
        
        st.altair_chart(chart2, use_container_width=True)

with tab2:
    st.markdown("### Detailed Analytics")
    
    col_a1, col_a2 = st.columns(2)
    
    with col_a1:
        st.markdown("#### AQI Distribution Histogram")
        hist_data = alt.Chart(filtered_df).mark_bar(
            opacity=0.85,
            color="#0e8cf6"
        ).encode(
            x=alt.X("aqi_value:Q", bin=alt.Bin(maxbins=50), title="AQI Value"),
            y=alt.Y("count():Q", title="Number of Cities"),
            tooltip=["count():Q"]
        ).properties(height=400).interactive()
        
        st.altair_chart(hist_data, use_container_width=True)
    
    with col_a2:
        st.markdown("#### Pollutant Analysis")
        
        co_data = pd.DataFrame({
            "Pollutant": ["CO", "Ozone", "NO2", "PM2.5"],
            "Average Value": [
                filtered_df["co_aqi_value"].mean(),
                filtered_df["ozone_aqi_value"].mean(),
                filtered_df["no2_aqi_value"].mean(),
                filtered_df["pm2.5_aqi_value"].mean(),
            ]
        })
        
        chart3 = alt.Chart(co_data).mark_bar(
            cornerRadiusTopLeft=6,
            cornerRadiusTopRight=6,
            color="#ff6b6b"
        ).encode(
            x=alt.X("Average Value:Q", title="Average Value"),
            y=alt.Y("Pollutant:N", title="Pollutant Type"),
            tooltip=["Pollutant", "Average Value"]
        ).properties(height=400).interactive()
        
        st.altair_chart(chart3, use_container_width=True)

with tab3:
    st.markdown("### ⚠️ Hazardous Locations Analysis")
    
    hazardous_df = filtered_df[filtered_df["aqi_value"] > 300].sort_values("aqi_value", ascending=False)
    
    if len(hazardous_df) > 0:
        st.markdown(f"**Found {len(hazardous_df)} hazardous locations**")
        
        col_h1, col_h2 = st.columns([1, 1])
        
        with col_h1:
            st.markdown("#### Most Critical Cities")
            top_hazard = hazardous_df.head(10)[["city_name", "country_name", "aqi_value", "aqi_category"]]
            st.dataframe(top_hazard, use_container_width=True, hide_index=True)
        
        with col_h2:
            st.markdown("#### Hazardous by Country")
            hazard_country = hazardous_df["country_name"].value_counts().head(10).reset_index()
            hazard_country.columns = ["Country", "Hazardous Cities"]
            
            chart4 = alt.Chart(hazard_country).mark_bar(color="#ff0000").encode(
                x=alt.X("Hazardous Cities:Q"),
                y=alt.Y("Country:N", sort="-x"),
                tooltip=["Country", "Hazardous Cities"]
            ).properties(height=350).interactive()
            
            st.altair_chart(chart4, use_container_width=True)
    else:
        st.markdown('<div class="alert-box">✅ No hazardous locations found in your filtered dataset!</div>', unsafe_allow_html=True)

with tab4:
    st.markdown("### 🔍 Country Deep Dive Analysis")
    
    if selected_country == "All":
        st.markdown('<div class="alert-box">⚠️ Select a specific country from the sidebar to view detailed analysis</div>', unsafe_allow_html=True)
    else:
        country_data = df[df["country_name"] == selected_country]
        
        col_cd1, col_cd2, col_cd3, col_cd4 = st.columns(4)
        
        with col_cd1:
            st.metric("🏙️ Cities", len(country_data))
        
        with col_cd2:
            st.metric("📊 Avg AQI", f"{country_data['aqi_value'].mean():.1f}")
        
        with col_cd3:
            hazard_count = len(country_data[country_data["aqi_value"] > 300])
            st.metric("🔴 Hazardous", hazard_count)
        
        with col_cd4:
            st.metric("📈 Max AQI", f"{country_data['aqi_value'].max():.0f}")
        
        st.markdown("---")
        
        st.markdown("#### All Cities in " + selected_country)
        display_cols = ["city_name", "aqi_value", "aqi_category", "co_aqi_value", "ozone_aqi_value"]
        st.dataframe(
            country_data[display_cols].sort_values("aqi_value", ascending=False),
            use_container_width=True,
            hide_index=True
        )

with tab5:
    st.markdown("### 🎨 Advanced Visualizations")
    
    sub_col1, sub_col2 = st.columns(2)
    
    with sub_col1:
        st.markdown("#### Category Pie Chart")
        pie_data = filtered_df["aqi_category"].value_counts().reset_index()
        pie_data.columns = ["Category", "Count"]
        
        pie_chart = alt.Chart(pie_data).mark_arc().encode(
            theta=alt.Theta("Count:Q"),
            color=alt.Color("Category:N", legend=alt.Legend(title="AQI Category")),
            tooltip=["Category", "Count"]
        ).properties(height=400)
        
        st.altair_chart(pie_chart, use_container_width=True)
    
    with sub_col2:
        st.markdown("#### Scatter: AQI vs Pollutants")
        scatter_data = filtered_df.sample(min(500, len(filtered_df)))
        
        scatter = alt.Chart(scatter_data).mark_circle(size=100, opacity=0.6).encode(
            x=alt.X("co_aqi_value:Q", title="CO AQI"),
            y=alt.Y("aqi_value:Q", title="Overall AQI"),
            color=alt.Color("aqi_category:N", legend=alt.Legend(title="Category")),
            tooltip=["city_name", "aqi_value", "co_aqi_value"]
        ).properties(height=400).interactive()
        
        st.altair_chart(scatter, use_container_width=True)

with tab6:
    st.markdown("### 🗺️ Geographic Heat Map")
    st.markdown("**Interactive map showing air quality levels across countries**")
    
    m = folium.Map(location=[20, 0], zoom_start=3, tiles="CartoDB positron")
    
    country_aqi = filtered_df.groupby("country_name").agg({"aqi_value": "mean", "city_name": "count"}).reset_index()
    country_aqi.columns = ["Country", "Avg AQI", "Cities"]
    country_aqi = country_aqi.sort_values("Avg AQI", ascending=False).head(50)
    
    for _, row in country_aqi.iterrows():
        country = row["Country"]
        avg_aqi = row["Avg AQI"]
        cities = row["Cities"]
        coords = get_country_coords(country)
        
        if avg_aqi <= 50:
            color = "green"
        elif avg_aqi <= 100:
            color = "yellow"
        elif avg_aqi <= 150:
            color = "orange"
        elif avg_aqi <= 200:
            color = "red"
        else:
            color = "darkred"
        
        popup_text = f"<b>{country}</b><br>Avg AQI: {avg_aqi:.1f}<br>Cities: {cities}"
        folium.CircleMarker(
            location=coords, radius=min(20, max(5, avg_aqi / 20)),
            popup=folium.Popup(popup_text, max_width=250),
            color=color, fill=True, fillColor=color, fillOpacity=0.7, weight=2
        ).add_to(m)
    
    st_folium(m, width=1400, height=600)

with tab7:
    st.markdown("### 🕸️ Network Graph Analysis")
    st.markdown("**Relationship network between countries and their most polluted cities**")
    
    G = create_network_graph(filtered_df, top_countries=8)
    
    if len(G) > 0:
        pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
        
        edge_x, edge_y = [], []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        edge_trace = go.Scatter(x=edge_x, y=edge_y, mode='lines', line=dict(width=0.5, color='#8fa3c4'), hoverinfo='none', showlegend=False)
        
        node_x, node_y, node_color, node_size, node_text = [], [], [], [], []
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_info = G.nodes[node]
            aqi = node_info.get('aqi', 0)
            
            if node_info.get('node_type') == 'country':
                node_color.append('#0e8cf6')
                node_size.append(25)
            else:
                node_color.append('#ff6b6b')
                node_size.append(15)
            
            node_text.append(f"{node}<br>AQI: {aqi:.1f}")
        
        node_trace = go.Scatter(x=node_x, y=node_y, mode='markers+text', hoverinfo='text', hovertext=node_text,
            marker=dict(showscale=True, color=node_color, size=node_size, colorscale='YlOrRd', line_width=2, line_color='#1a3a66'),
            showlegend=False)
        
        node_label_x, node_label_y, node_labels = [], [], []
        for node in G.nodes():
            x, y = pos[node]
            node_label_x.append(x)
            node_label_y.append(y)
            node_labels.append(node)
        
        label_trace = go.Scatter(x=node_label_x, y=node_label_y, mode='text', text=node_labels, textposition='top center',
            textfont=dict(size=10, color='#b0bfd9'), hoverinfo='none', showlegend=False)
        
        fig = go.Figure(data=[edge_trace, node_trace, label_trace])
        fig.update_layout(
            title='Network Graph: Countries & Top Polluted Cities', showlegend=False, hovermode='closest',
            margin=dict(b=0, l=0, r=0, t=40), xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='rgba(10, 20, 40, 0.9)', paper_bgcolor='rgba(15, 31, 63, 1)',
            font=dict(color='#b0bfd9'), height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        col_stats1, col_stats2, col_stats3 = st.columns(3)
        with col_stats1:
            st.metric("Total Nodes", len(G.nodes()))
        with col_stats2:
            st.metric("Total Connections", len(G.edges()))
        with col_stats3:
            st.metric("Network Density", f"{nx.density(G):.3f}")

st.markdown("---")
st.markdown(
    '<p style="text-align: center; color: #8fa3c4; margin-top: 40px;">Built with ❤️ using Streamlit, Folium, Plotly & Altair | Real-time Air Quality Monitoring</p>',
    unsafe_allow_html=True
)
