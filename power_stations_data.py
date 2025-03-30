import pandas as pd

data = {
    'station_id': [0, 1, 2, 3, 4, 5, 6],
    'name': [
        'Upper River Station',
        'Green Valley Station',
        'White Rock Station',
        'Blue Lake Station',
        'Great Falls Station',
        'The Storms Station',
        'Final Reservoir Station'
    ],
    'max_water_level_m3': [
        2_500_000,  # 2.5 million m³
        1_800_000,
        1_200_000,
        1_500_000,
        2_000_000,
        1_600_000,
        2_200_000
    ],
    'initial_water_level_m3': [
        1_500_000,  # 60% capacity
        900_000,    # 50% capacity
        600_000,
        750_000,
        1_000_000,
        800_000,
        1_100_000
    ],
    'loss_coefficient': [
        0.999998,  # Daily loss of 0.0002% of the water stored in the reservoir
        0.999997,
        0.999996,
        0.999991,
        0.999989,
        0.999997,
        0.999995    # Lower stations typically have more evaporation
    ],
    'previous_distance_km': [
        0,    # First station has no previous
        15,   # Distance from Station 0 to 1
        20,   # Distance from Station 1 to 2
        10,
        25,
        18,
        12
    ],
    'route_loss': [
        0,     # Doesn't apply to first station
        0.95,  # 5% loss en route
        0.93,
        0.97,
        0.94,
        0.96,
        0.95
    ],  # TODO: Factor de conversión intervalos-tiempo. Conectado con la precipitación.
    'delay_intervals': [
        0,  # Doesn't apply
        2,  # 30 minutes (2 intervals of 15 min)
        3,  # 45 minutes
        1,  # 15 minutes
        4,  # 1 hour
        2,
        3
    ]
}

df = pd.DataFrame(data)
df.to_csv('power_stations_config.csv', index=False)
print("CSV file generated successfully: 'power_stations_config.csv'")
