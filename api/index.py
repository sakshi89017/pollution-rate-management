import os
import pandas as pd
import numpy as np
import joblib
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

# Load data and ML model
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, 'data', 'global_air_pollution_data.csv')
MODEL_PATH = os.path.join(BASE_DIR, 'air_quality_index_prediction_model.sav')

# Coordinate Map
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

df = pd.read_csv(CSV_PATH)
df['country_name'] = df['country_name'].fillna('Unknown')
df['city_name'] = df['city_name'].fillna('Unknown')
df['aqi_value'] = pd.to_numeric(df['aqi_value'], errors='coerce')
df['aqi_category'] = df['aqi_category'].astype(str)

try:
    model = joblib.load(MODEL_PATH)
except Exception as e:
    model = None
    print(f"Error loading prediction model: {e}")

@app.route('/api/meta', methods=['GET'])
def get_meta():
    countries = sorted(df['country_name'].unique().tolist())
    categories = sorted(df['aqi_category'].unique().tolist())
    min_aqi = int(df['aqi_value'].min())
    max_aqi = int(df['aqi_value'].max())
    
    return jsonify({
        "countries": countries,
        "categories": categories,
        "min_aqi": min_aqi,
        "max_aqi": max_aqi,
        "total_records": len(df),
        "total_countries": len(countries),
        "global_avg_aqi": float(df['aqi_value'].mean())
    })

@app.route('/api/query', methods=['POST'])
def query_data():
    req_data = request.get_json() or {}
    
    country = req_data.get('country', 'All')
    categories = req_data.get('categories', [])
    min_aqi = req_data.get('min_aqi', int(df['aqi_value'].min()))
    max_aqi = req_data.get('max_aqi', int(df['aqi_value'].max()))
    
    # Filter dataset
    f_df = df[
        (df['aqi_value'] >= min_aqi) &
        (df['aqi_value'] <= max_aqi)
    ]
    
    if categories:
        f_df = f_df[f_df['aqi_category'].isin(categories)]
        
    if country != 'All':
        f_df = f_df[f_df['country_name'] == country]
        
    # Stats
    total_records = len(f_df)
    avg_aqi = float(f_df['aqi_value'].mean()) if total_records > 0 else 0.0
    hazardous_count = int((f_df['aqi_value'] > 300).sum())
    countries_affected = int(f_df['country_name'].nunique())
    
    # Category Distribution
    cat_counts = f_df['aqi_category'].value_counts().to_dict()
    
    # Top Affected Countries
    top_countries_series = f_df['country_name'].value_counts().head(10)
    top_countries = [{"country": k, "cities": int(v)} for k, v in top_countries_series.items()]
    
    # Pollutant Averages
    pollutants = {
        "CO": float(f_df['co_aqi_value'].mean()) if total_records > 0 else 0.0,
        "Ozone": float(f_df['ozone_aqi_value'].mean()) if total_records > 0 else 0.0,
        "NO2": float(f_df['no2_aqi_value'].mean()) if total_records > 0 else 0.0,
        "PM2.5": float(f_df['pm2.5_aqi_value'].mean()) if total_records > 0 else 0.0
    }
    
    # Hazardous cities info
    haz_df = f_df[f_df['aqi_value'] > 300].sort_values('aqi_value', ascending=False)
    critical_cities = haz_df.head(10)[['city_name', 'country_name', 'aqi_value', 'aqi_category']].to_dict('records')
    haz_by_country_series = haz_df['country_name'].value_counts().head(10)
    haz_by_country = [{"country": k, "cities": int(v)} for k, v in haz_by_country_series.items()]
    
    # Histogram Bins for AQI Values
    hist, bin_edges = np.histogram(f_df['aqi_value'].dropna(), bins=40)
    hist_data = [{"bin_start": float(bin_edges[i]), "bin_end": float(bin_edges[i+1]), "count": int(hist[i])} for i in range(len(hist))]
    
    # Scatter Sample (up to 500 records)
    scatter_df = f_df.sample(min(500, len(f_df))) if len(f_df) > 0 else pd.DataFrame()
    scatter_data = []
    if not scatter_df.empty:
        scatter_data = scatter_df[['city_name', 'aqi_value', 'co_aqi_value', 'aqi_category']].to_dict('records')
        
    # Map points: avg AQI and city count per country for top 50
    map_df = f_df.groupby("country_name").agg({"aqi_value": "mean", "city_name": "count"}).reset_index()
    map_df.columns = ["country", "avg_aqi", "cities"]
    map_df = map_df.sort_values("avg_aqi", ascending=False).head(50)
    map_data = []
    for _, row in map_df.iterrows():
        c_name = row['country']
        coords = COUNTRY_COORDS.get(c_name, [20.0, 0.0])
        map_data.append({
            "country": c_name,
            "avg_aqi": float(row['avg_aqi']),
            "cities": int(row['cities']),
            "coords": coords
        })
        
    # Network Graph
    top_net_countries = f_df.groupby("country_name")["aqi_value"].mean().nlargest(8).index.tolist()
    net_nodes = []
    net_edges = []
    
    # Add country nodes
    for c in top_net_countries:
        c_avg_aqi = float(df[df["country_name"] == c]["aqi_value"].mean())
        net_nodes.append({"id": c, "label": c, "group": "country", "value": c_avg_aqi})
        
        # Get top 3 polluted cities in country
        c_cities = f_df[f_df["country_name"] == c].nlargest(3, "aqi_value")
        for _, row in c_cities.iterrows():
            city = row["city_name"]
            city_id = f"{c}_{city}" # unique key
            net_nodes.append({"id": city_id, "label": city, "group": "city", "value": float(row["aqi_value"])})
            net_edges.append({"from": c, "to": city_id, "weight": float(row["aqi_value"])})
            
    # Country deep dive details (if specific country chosen)
    country_detail = {}
    if country != 'All':
        c_data = df[df['country_name'] == country]
        country_detail = {
            "cities_count": len(c_data),
            "avg_aqi": float(c_data['aqi_value'].mean()),
            "max_aqi": float(c_data['aqi_value'].max()),
            "hazard_count": int((c_data['aqi_value'] > 300).sum()),
            "cities_list": c_data[['city_name', 'aqi_value', 'aqi_category', 'co_aqi_value', 'ozone_aqi_value']].sort_values('aqi_value', ascending=False).to_dict('records')
        }

    return jsonify({
        "stats": {
            "total_records": total_records,
            "avg_aqi": avg_aqi,
            "hazardous_count": hazardous_count,
            "countries_affected": countries_affected
        },
        "category_distribution": cat_counts,
        "top_countries": top_countries,
        "pollutants": pollutants,
        "critical_cities": critical_cities,
        "haz_by_country": haz_by_country,
        "hist_data": hist_data,
        "scatter_data": scatter_data,
        "map_data": map_data,
        "network": {
            "nodes": net_nodes,
            "edges": net_edges
        },
        "country_detail": country_detail
    })

@app.route('/api/predict', methods=['POST'])
def predict_aqi():
    if not model:
        return jsonify({"error": "Prediction model not loaded on server."}), 500
        
    req_data = request.get_json() or {}
    try:
        co = float(req_data.get('co', 0))
        ozone = float(req_data.get('ozone', 0))
        no2 = float(req_data.get('no2', 0))
        pm25 = float(req_data.get('pm2.5', 0))
        
        pred = model.predict([[co, ozone, no2, pm25]])[0]
        
        category_map = {
            1: "Good",
            2: "Moderate",
            3: "Unhealthy",
            4: "Unhealthy for Sensitive Groups",
            5: "Very Unhealthy",
            6: "Hazardous"
        }
        
        category_desc = {
            "Good": "Air quality is satisfactory, and air pollution poses little or no risk.",
            "Moderate": "Air quality is acceptable. However, there may be a risk for some people, particularly those who are unusually sensitive to air pollution.",
            "Unhealthy for Sensitive Groups": "Members of sensitive groups may experience health effects. The general public is less likely to be affected.",
            "Unhealthy": "Some members of the general public may experience health effects; members of sensitive groups may experience more serious health effects.",
            "Very Unhealthy": "Health alert: The risk of health effects is increased for everyone.",
            "Hazardous": "Health warning of emergency conditions: The entire population is more likely to be affected."
        }
        
        pred_label = category_map.get(int(pred), "Unknown")
        description = category_desc.get(pred_label, "No details available.")
        
        return jsonify({
            "category_code": int(pred),
            "category": pred_label,
            "description": description
        })
    except Exception as e:
        return jsonify({"error": f"Invalid inputs: {str(e)}"}), 400

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    if not path:
        path = 'index.html'
    public_dir = os.path.join(BASE_DIR, 'public')
    return send_from_directory(public_dir, path)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
