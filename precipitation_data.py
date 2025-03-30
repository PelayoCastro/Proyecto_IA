import pandas as pd
import numpy as np

# Reproducible configuration
np.random.seed(42)
# TODO: considerar las precipitaciones por intervalo de tiempo
# Precipitation monthly data (mm/month)
monthly_precip = {
    1: 67.8,  # January
    2: 53.7,  # February
    3: 48.3,  # March
    4: 62.0,  # April
    5: 52.0,  # May
    6: 30.7,  # June
    7: 21.0,  # July
    8: 33.5,  # August
    9: 57.2,  # September
    10: 88.3,  # October
    11: 89.7,  # November
    12: 80.7  # December
}

# Conversion factor: 1 mm precipitation → 250 m³ water input
# (Adjustable based on catchment area)
CONVERSION_FACTOR = 250

# Typical hourly pattern (0-23 hours)
hourly_pattern = [
    0.5,  # 0-1 am
    0.3,  # 1-2
    0.2,  # 2-3
    0.1,  # 3-4
    0.05,  # 4-5
    0.025,  # 5-6
    0.15,  # 6-7
    0.4,  # 7-8
    0.8,  # 8-9
    1.2,  # 9-10
    1.0,  # 10-11
    0.8,  # 11-12
    0.6,  # 12-13
    0.5,  # 13-14
    0.4,  # 14-15
    0.3,  # 15-16
    0.2,  # 16-17
    0.3,  # 17-18
    0.5,  # 18-19
    0.8,  # 19-20
    0.7,  # 20-21
    0.5,  # 21-22
    0.3,  # 22-23
    0.5  # 23-24
]

# Normalize the hourly pattern to sum to 1
total_pattern = sum(hourly_pattern)
hourly_pattern = [p / total_pattern for p in hourly_pattern]

# Generate data for the whole year
data = []
for month in range(1, 13):
    days_in_month = 31 if month in [1, 3, 5, 7, 8, 10, 12] else 30
    days_in_month = 28 if month == 2 else days_in_month  # Simplified (not leap year)

    total_month_precip = monthly_precip[month]

    for day in range(1, days_in_month + 1):
        for hour in range(24):
            # Base + randomness (25% deviation)
            base = total_month_precip * hourly_pattern[hour] / days_in_month
            std_dev = 0.25 * base
            precip_mm = max(0, np.random.normal(base, std_dev))

            # Convert to water input (m³)
            water_input = precip_mm * CONVERSION_FACTOR

            data.append({
                'month': month,
                'day': day,
                'hour': hour,
                'precipitation_mm': round(precip_mm, 2),
                'water_input_m3': round(water_input)
            })

# Create DataFrame and save CSV
df = pd.DataFrame(data)
df.to_csv('precipitation.csv', index=False)
print("File 'precipitation.csv' generated successfully.")
