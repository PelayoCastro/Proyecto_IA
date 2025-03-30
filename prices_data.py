import pandas as pd
import numpy as np

# Reproducible configuration
np.random.seed(42)

# Provided hourly data (€/kWh)
hourly_prices = {
    0: 0.1048,
    1: 0.0869,
    2: 0.0770,
    3: 0.0726,
    4: 0.0777,
    5: 0.0851,
    6: 0.1162,
    7: 0.1546,
    8: 0.0958,
    9: 0.0656,
    10: 0.1304,
    11: 0.1294,
    12: 0.1293,
    13: 0.1269,
    14: 0.0621,
    15: 0.0620,
    16: 0.0626,
    17: 0.0617,
    18: 0.1630,
    19: 0.2739,
    20: 0.2757,
    21: 0.2520,
    22: 0.1782,
    23: 0.1318
}

# Monthly factors (winter and summer with higher prices)
monthly_factors = {
    1: 1.15,  # January
    2: 1.10,  # February
    3: 1.00,  # March
    4: 0.95,  # April
    5: 0.90,  # May
    6: 1.05,  # June
    7: 1.10,  # July
    8: 1.05,  # August
    9: 0.95,  # September
    10: 0.90,  # October
    11: 0.95,  # November
    12: 1.15  # December
}

# Generate data for the whole year
data = []
for month in range(1, 13):
    days_in_month = 31 if month in [1, 3, 5, 7, 8, 10, 12] else 30
    days_in_month = 28 if month == 2 else days_in_month  # Simplified (not leap year)

    month_factor = monthly_factors[month]

    for day in range(1, days_in_month + 1):
        for hour in range(24):
            base_price = hourly_prices[hour] * month_factor

            # Add randomness (25% deviation)
            std_dev = 0.25 * base_price
            final_price = max(0.01, np.random.normal(base_price, std_dev))  # Minimum 0.01€

            data.append({
                'month': month,
                'day': day,
                'hour': hour,
                'base_price_€kWh': round(base_price, 4),
                'final_price_€kWh': round(final_price, 4)
            })

# Create DataFrame and save CSV
df = pd.DataFrame(data)
df.to_csv('electricity_prices.csv', index=False)
print("File 'electricity_prices.csv' generated successfully.")