import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_theme(style="darkgrid")
import requests
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go

# Plotly template
pio.templates.default = "plotly_white"

# Title
st.title("Air Quality Index Analysis!!")

# Read data
data = pd.read_csv("air_quality_data.csv")

# Convert 'date' column to datetime format at the beginning
data['date'] = pd.to_datetime(data['date'], errors='coerce')

# Show raw data
st.subheader("Air Quality Data of Month January")
st.dataframe(data)

# AQI Breakpoints (example: for PM2.5; same logic used for others)
aqi_breakpoints = [
    (0, 12.0, 50), (12.1, 35.4, 100), (35.5, 55.4, 150),
    (55.5, 150.4, 200), (150.5, 250.4, 300), (250.5, 350.4, 400),
    (350.5, 500.4, 500)
]

# AQI calculation logic
def calculate_aqi(pollutant_name, concentration):
    for low, high, aqi in aqi_breakpoints:
        if low <= concentration <= high:
            return aqi
    return None

def calculate_overall_aqi(row):
    aqi_values = []
    pollutants = ['co', 'no', 'no2', 'o3', 'so2', 'pm2_5', 'pm10', 'nh3']
    for pollutant in pollutants:
        if pd.notnull(row[pollutant]):
            aqi = calculate_aqi(pollutant, row[pollutant])
            if aqi is not None:
                aqi_values.append(aqi)
    return max(aqi_values) if aqi_values else None

# Apply AQI calculation
data['AQI'] = data.apply(calculate_overall_aqi, axis=1)

# AQI Categories
aqi_categories = [
    (0, 50, 'Good'), (51, 100, 'Moderate'), (101, 150, 'Unhealthy for Sensitive Groups'),
    (151, 200, 'Unhealthy'), (201, 300, 'Very Unhealthy'), (301, 500, 'Hazardous')
]

def categorize_aqi(aqi_value):
    for low, high, category in aqi_categories:
        if low <= aqi_value <= high:
            return category
    return "Unknown"

# Add AQI category column
data['AQI Category'] = data['AQI'].apply(categorize_aqi)

# Optional preview
if st.checkbox("Show Data with AQI & Category"):
    st.write(data[['date', 'AQI', 'AQI Category'] + ['co', 'no', 'no2', 'o3', 'so2', 'pm2_5', 'pm10', 'nh3']].head())

# Time Series Plot of Pollutants
st.subheader("Time Series Plot of Pollutants")
fig = go.Figure()
pollutants = ['co', 'no', 'no2', 'o3', 'so2', 'pm2_5', 'pm10', 'nh3']
for pollutant in pollutants:
    if pollutant in data.columns:
        fig.add_trace(go.Scatter(x=data['date'], y=data[pollutant], mode='lines', name=pollutant))
fig.update_layout(title='Time Series of Air Pollutants',
                  xaxis_title='Date', yaxis_title='Concentration (µg/m³)')
st.plotly_chart(fig)

# AQI Time Series Plot
st.subheader("Time Series Plot of AQI")
fig_aqi = go.Figure()
fig_aqi.add_trace(go.Scatter(x=data['date'], y=data['AQI'], mode='lines', name='AQI', line=dict(color='firebrick')))
fig_aqi.update_layout(title='Time Series of AQI',
                      xaxis_title='Date', yaxis_title='AQI Value')
st.plotly_chart(fig_aqi)

# Select Month for AQI Bar Chart
st.subheader("AQI Bar Chart by Month")
selected_month = st.selectbox(
    "Select month:", 
    range(1, 13), 
    format_func=lambda x: pd.to_datetime(str(x), format="%m").strftime("%B")
)

# Filter by selected month
filtered_data = data[data['date'].dt.month == selected_month]
filtered_data = filtered_data.dropna(subset=['AQI'])  # Ensure AQI is available

# Plot bar chart if data exists
if not filtered_data.empty:
    st.subheader(f"AQI Bar Chart for {pd.to_datetime(str(selected_month), format='%m').strftime('%B')}")
    fig_bar = px.bar(filtered_data, x="date", y="AQI", 
                     title=f"AQI of Delhi in {pd.to_datetime(str(selected_month), format='%m').strftime('%B')}")
    fig_bar.update_xaxes(title="Date")
    fig_bar.update_yaxes(title="AQI")
    st.plotly_chart(fig_bar)
else:
    st.warning("No AQI data available for the selected month.")
# AQI Category Distribution Over Time (Histogram)
st.subheader("AQI Category Distribution Over Time")
fig = px.histogram(
    data,
    x="date",
    color="AQI Category",
    title="AQI Category Distribution Over Time"
)
fig.update_xaxes(title="Date")
fig.update_yaxes(title="Count")
st.plotly_chart(fig)
# Donut Chart of Pollutant Concentrations
st.subheader("Overall Pollutant Concentrations in Delhi")

# Define pollutants and their colors
pollutants = ["co", "no", "no2", "o3", "so2", "pm2_5", "pm10", "nh3"]
pollutant_colors = px.colors.qualitative.Plotly

# Calculate the sum of pollutant concentrations
total_concentrations = data[pollutants].sum()

# Create a DataFrame for the concentrations
concentration_data = pd.DataFrame({
    "Pollutant": pollutants,
    "Concentration": total_concentrations.values
})

# Create a donut plot
fig_donut = px.pie(
    concentration_data,
    names="Pollutant",
    values="Concentration",
    title="Pollutant Concentrations in Delhi",
    hole=0.4,
    color_discrete_sequence=pollutant_colors
)

# Customize donut chart
fig_donut.update_traces(textinfo="percent+label")
fig_donut.update_layout(legend_title="Pollutant")

# Show the donut plot
st.plotly_chart(fig_donut)
# Correlation Between Pollutants
st.subheader("Correlation Between Pollutants")

# Compute correlation matrix for pollutants
correlation_matrix = data[pollutants].corr()

# Create a heatmap using Plotly
fig_corr = px.imshow(
    correlation_matrix,
    x=pollutants,
    y=pollutants,
    title="Correlation Between Pollutants",
    color_continuous_scale="RdBu_r",
    text_auto=True
)

# Show the heatmap
st.plotly_chart(fig_corr)
# Hourly AQI Trends
st.subheader("Hourly Average AQI Trends")

# Extract the hour from the date
data['Hour'] = data['date'].dt.hour

# Calculate hourly average AQI
hourly_avg_aqi = data.groupby('Hour')['AQI'].mean().reset_index()

# Create a line plot
fig_hourly = px.line(
    hourly_avg_aqi,
    x='Hour',
    y='AQI',
    title='Hourly Average AQI Trends in Delhi',
    markers=True
)
fig_hourly.update_xaxes(title="Hour of the Day", tickmode='linear', dtick=1)
fig_hourly.update_yaxes(title="Average AQI")

# Display the plot
st.plotly_chart(fig_hourly)
# Average AQI by Day of the Week
st.subheader("Average AQI by Day of the Week")

# Extract day of the week
data['Day_of_Week'] = data['date'].dt.day_name()

# Compute average AQI per day of the week, in correct order
average_aqi_by_day = (
    data.groupby('Day_of_Week')['AQI']
    .mean()
    .reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    .reset_index()
)

# Plot bar chart
fig_day = px.bar(
    average_aqi_by_day,
    x='Day_of_Week',
    y='AQI',
    title='Average AQI by Day of the Week',
    color='Day_of_Week'
)

# Customize axes
fig_day.update_xaxes(title="Day of the Week")
fig_day.update_yaxes(title="Average AQI")

# Display in Streamlit
st.plotly_chart(fig_day)
