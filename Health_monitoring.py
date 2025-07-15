import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_theme(style="darkgrid")

# Sidebar
st.sidebar.header("Health Monitor Control Panel")
with st.sidebar.expander("🔐 User Login (Demo)"):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if username and password:
        st.sidebar.success(f"Welcome, Dr. {username.capitalize()}!")

uploaded_file = st.sidebar.file_uploader("Upload your patient data", type=['csv'])

if uploaded_file is not None:
    health_data = pd.read_csv(uploaded_file)
else:
    health_data = pd.read_csv('patient_health_data_1.csv')

activity_filter = st.sidebar.multiselect(
    "Filter by Activity Level", 
    options=health_data['ActivityLevel'].unique(), 
    default=health_data['ActivityLevel'].unique()
)
health_data = health_data[health_data['ActivityLevel'].isin(activity_filter)]

st.title("🩻 Health Monitoring Dashboard")
st.caption("Analyze patient vitals & detect health trends effectively.")

st.subheader("📋 Raw Patient Data")
st.dataframe(health_data)

st.write("Missing values in each column:")
st.write(health_data.isnull().sum())

st.write("Filling null values using mean or mode:")
health_data['Age'] = health_data['Age'].fillna(health_data['Age'].mean())
health_data['HeartRate'] = health_data['HeartRate'].fillna(health_data['HeartRate'].mean())
health_data['BodyTemperature'] = health_data['BodyTemperature'].fillna(health_data['BodyTemperature'].mean())
health_data['SleepQuality'] = health_data['SleepQuality'].fillna('Fair')
health_data['StressLevel'] = health_data['StressLevel'].fillna('Moderate')

st.write("Cleaned Data Sample:")
st.write(health_data.head())

st.markdown("### 🩺 Key Health Stats")
col1, col2, col3 = st.columns(3)
col1.metric("Avg Heart Rate", f"{health_data['HeartRate'].mean():.1f} bpm")
col2.metric("Avg Temp", f"{health_data['BodyTemperature'].mean():.1f} °F")
col3.metric("Oxygen Saturation", f"{health_data['OxygenSaturation'].mean():.1f} %")

st.write("Summary Statistics:")
st.write(health_data.describe())

st.write("### Distributions of Numerical Features")
fig, axes = plt.subplots(3, 2, figsize=(14, 18))
sns.histplot(health_data['Age'], bins=20, kde=True, ax=axes[0, 0])
axes[0, 0].set_title('Age Distribution')
sns.histplot(health_data['HeartRate'], bins=20, kde=True, ax=axes[0, 1])
axes[0, 1].set_title('Heart Rate Distribution')
sns.histplot(health_data['RespiratoryRate'], bins=20, kde=True, ax=axes[1, 0])
axes[1, 0].set_title('Respiratory Rate Distribution')
sns.histplot(health_data['BodyTemperature'], bins=20, kde=True, ax=axes[1, 1])
axes[1, 1].set_title('Body Temperature Distribution')
sns.histplot(health_data['OxygenSaturation'], bins=10, kde=True, ax=axes[2, 0])
axes[2, 0].set_title('Oxygen Saturation Distribution')
fig.delaxes(axes[2, 1])
plt.tight_layout()
st.pyplot(fig)

st.write("### Gender Distribution and Correlation Matrix")
gender_counts = health_data['Gender'].value_counts()
correlation_matrix = health_data[['Age', 'HeartRate', 'RespiratoryRate', 'BodyTemperature', 'OxygenSaturation']].corr()
fig, axes = plt.subplots(1, 2, figsize=(12, 6))
gender_counts.plot(kind='pie', ax=axes[0], autopct='%1.1f%%', startangle=90, colors=['#ff9999', '#66b3ff', '#99ff99'])
axes[0].set_ylabel('')
axes[0].set_title('Gender Distribution')
sns.heatmap(correlation_matrix, annot=True, fmt=".2f", cmap='coolwarm', ax=axes[1])
axes[1].set_title('Correlation Matrix')
plt.tight_layout()
st.pyplot(fig)

st.write("### Heart Rate by Activity Level")
fig = plt.figure(figsize=(10, 6))
sns.boxplot(x='ActivityLevel', y='HeartRate', data=health_data)
plt.title('Heart Rate by Activity Level')
st.pyplot(fig)

st.write("### Blood Pressure Analysis")
bp_split = health_data['BloodPressure'].dropna().str.extract(r'(\d+)[\/\- ]+(\d+)')
health_data['SystolicBP'] = pd.to_numeric(bp_split[0], errors='coerce')
health_data['DiastolicBP'] = pd.to_numeric(bp_split[1], errors='coerce')
fig = plt.figure(figsize=(12, 6))
sns.histplot(health_data['SystolicBP'], color="skyblue", label="Systolic", kde=True)
sns.histplot(health_data['DiastolicBP'], color="red", label="Diastolic", kde=True)
plt.title('Blood Pressure Distribution')
plt.legend()
st.pyplot(fig)

st.write("### Health Metrics by Gender")
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
sns.boxplot(x='Gender', y='HeartRate', data=health_data, ax=axes[0])
axes[0].set_title('Heart Rate by Gender')
sns.boxplot(x='Gender', y='OxygenSaturation', data=health_data, ax=axes[1])
axes[1].set_title('Oxygen Saturation by Gender')
plt.tight_layout()
st.pyplot(fig)

st.write("### Sleep Quality and Stress Level Impact on Health Metrics")
sleep_quality_order = ['Excellent', 'Good', 'Fair', 'Poor']
stress_level_order = ['Low', 'Moderate', 'High']
health_data['SleepQuality'] = health_data['SleepQuality'].str.capitalize()
health_data['StressLevel'] = health_data['StressLevel'].str.capitalize()
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
sns.boxplot(x='SleepQuality', y='HeartRate', data=health_data, order=sleep_quality_order, ax=axes[0, 0])
axes[0, 0].set_title('Heart Rate by Sleep Quality')
sns.boxplot(x='StressLevel', y='HeartRate', data=health_data, order=stress_level_order, ax=axes[0, 1])
axes[0, 1].set_title('Heart Rate by Stress Level')
sns.boxplot(x='SleepQuality', y='OxygenSaturation', data=health_data, order=sleep_quality_order, ax=axes[1, 0])
axes[1, 0].set_title('Oxygen Saturation by Sleep Quality')
sns.boxplot(x='StressLevel', y='OxygenSaturation', data=health_data, order=stress_level_order, ax=axes[1, 1])
axes[1, 1].set_title('Oxygen Saturation by Stress Level')
plt.tight_layout()
st.pyplot(fig)

st.write("### Activity Level vs Respiratory Rate & Body Temperature")
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
sns.boxplot(x='ActivityLevel', y='RespiratoryRate', data=health_data, ax=axes[0])
axes[0].set_title('Respiratory Rate by Activity Level')
sns.boxplot(x='ActivityLevel', y='BodyTemperature', data=health_data, ax=axes[1])
axes[1].set_title('Body Temperature by Activity Level')
plt.tight_layout()
st.pyplot(fig)

def age_group(age):
    if age <= 35:
        return 'Young'
    elif age <= 55:
        return 'Middle-aged'
    else:
        return 'Senior'

def bp_category(systolic, diastolic):
    if pd.isna(systolic) or pd.isna(diastolic):
        return 'Unknown'
    if systolic < 120 and diastolic < 80:
        return 'Normal'
    elif 120 <= systolic < 140 or 80 <= diastolic < 90:
        return 'Elevated'
    elif 140 <= systolic < 160 or 90 <= diastolic < 100:
        return 'Hypertension Stage 1'
    else:
        return 'Hypertension Stage 2'

def hr_category(hr):
    if pd.isna(hr):
        return 'Unknown'
    if hr < 60:
        return 'Low'
    elif hr <= 100:
        return 'Normal'
    else:
        return 'High'

def oxy_category(oxy):
    if pd.isna(oxy):
        return 'Unknown'
    if oxy < 94:
        return 'Low'
    else:
        return 'Normal'

health_data['AgeGroup'] = health_data['Age'].apply(age_group)
health_data['BPCategory'] = health_data.apply(lambda x: bp_category(x['SystolicBP'], x['DiastolicBP']), axis=1)
health_data['HRCategory'] = health_data['HeartRate'].apply(hr_category)
health_data['OxyCategory'] = health_data['OxygenSaturation'].apply(oxy_category)

st.write("### Categorized Health Metrics (Sample)")
st.dataframe(health_data[['Age', 'AgeGroup', 'SystolicBP', 'DiastolicBP', 'BPCategory', 'HeartRate', 'HRCategory', 'OxygenSaturation', 'OxyCategory']].head(10))

st.write("### 🚨 High-Risk Patients")
alert_data = health_data[(health_data['HRCategory'] == 'High') | (health_data['OxyCategory'] == 'Low') | (health_data['BPCategory'].str.contains('Hypertension'))]
if alert_data.empty:
    st.success("No patients currently in critical health zones.")
else:
    st.dataframe(alert_data[['Age', 'Gender', 'HeartRate', 'HRCategory', 'OxygenSaturation', 'OxyCategory', 'BPCategory']])

csv = health_data.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download Cleaned Data", csv, "cleaned_patient_data.csv", "text/csv")
