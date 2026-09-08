import sys
import time
import webbrowser
import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def log_status(step: int, total_steps: int, message: str):
    """Prints a formatted progress status line in the terminal."""
    print(f"[{step}/{total_steps}] {message}...", flush=True)


def fetch_api_data():
    log_status(1, 5, "Connecting to Open-Meteo REST API")
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 14.5995,
        "longitude": 120.9842,
        "hourly": ["temperature_2m", "direct_radiation"],
        "forecast_days": 3,
        "timezone": "Asia/Manila"
    }
    
    # timeout = 10 to prevent indefinite hanging on network requests
    response = requests.get(url, params=params, timeout=10)
    if response.status_code != 200:
        raise ConnectionError(f"Failed to fetch data from API (Status: {response.status_code})")
        
    time.sleep(0.9)
    log_status(2, 5, "Parsing JSON response into Pandas DataFrame")
    data = response.json()["hourly"]
    time.sleep(0.9)
    
    return pd.DataFrame({
        "Timestamp": pd.to_datetime(data["time"]),
        "Temperature_C": data["temperature_2m"],
        "Solar_Radiation_Wm2": data["direct_radiation"]
    })


def main():
    print("\n--- Starting Data Mining & Visualization Pipeline ---\n")
    
    # Mine Data & Load DF
    df = fetch_api_data()
    
    # Export CSV
    log_status(3, 5, "Exporting mined dataset to 'energy_weather_data.csv'")
    df.to_csv("energy_weather_data.csv", index=False)
    time.sleep(0.9)

    # Build Dual-Axis Graph
    log_status(4, 5, "Building dual Y-axis Plotly interactive figure")
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(
            x=df["Timestamp"], 
            y=df["Temperature_C"], 
            name="Temperature (°C)", 
            line=dict(color="#00b4d8", width=2)
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=df["Timestamp"], 
            y=df["Solar_Radiation_Wm2"], 
            name="Solar Radiation (W/m²)", 
            line=dict(color="#ff4d6d", width=2)
        ),
        secondary_y=True,
    )

    fig.update_layout(
        title="<b>Interactive Hourly Weather & Solar Radiation Monitor</b>",
        template="plotly_dark",
        hovermode="x unified"
    )
    fig.update_yaxes(title_text="<b>Temperature (°C)</b>", secondary_y=False)
    fig.update_yaxes(title_text="<b>Solar Radiation (W/m²)</b>", secondary_y=True)
    time.sleep(0.9)

    # Save HTML & Launch Browser
    html_file = "interactive_visualization.html"
    log_status(5, 5, f"Saving '{html_file}' and launching browser")
    fig.write_html(html_file)
    time.sleep(0.5)
    
    print("\n✔ Pipeline Execution Complete! Opening browser now...\n")
    webbrowser.open(html_file)


if __name__ == "__main__":
    main()