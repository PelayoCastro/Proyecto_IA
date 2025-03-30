import numpy as np
import pandas as pd
from typing import List, Dict, Any
from dataclasses import dataclass
from power_station import PowerStation


@dataclass
class PowerStationConfig:
    max_water_level: float
    initial_water_level: float
    loss_coefficient: float


class PowerStationSystem:
    def __init__(self,
                 config_path: str = 'data/power_stations_config.csv',
                 precipitation_path: str = 'data/precipitation.csv',
                 price_path: str = 'data/electricity_prices.csv'):
        """
        Initialize the hydroelectric system by loading data from CSV files.

        Args:
            config_path: Path to power station configuration CSV
            precipitation_path: Path to precipitation data CSV in hours
            price_path: Path to electricity price data CSV in hours
        """
        # Load power station configurations
        try:
            config_df = pd.read_csv(config_path)
            if len(config_df) != 7:
                raise ValueError("Exactly 7 power stations required")

            self.power_stations = [
                PowerStation(
                    max_water_level=row['max_water_level_m3'],
                    initial_water_level=row['initial_water_level_m3'],
                    loss_coefficient=row['loss_coefficient'],
                    station_id=row['station_id'],
                    is_first=(row['station_id'] == 0))
                for _, row in config_df.iterrows()
            ]

            # System configuration
            self.distances = config_df['previous_distance_km'].tolist()[1:]
            self.route_losses = config_df['route_loss'].tolist()[1:]
            self.delays = config_df['delay_intervals'].tolist()[1:]

            # Load time series data
            self.precip_data = self._load_time_series(precipitation_path)
            self.price_data = self._load_time_series(price_path)
            print(self.precip_data)
            print(self.price_data)

        except FileNotFoundError as e:
            raise FileNotFoundError(f"Missing data file: {e.filename}") from e
        except KeyError as e:
            raise ValueError(f"Missing required column in CSV: {e}") from e

        # System state
        self.current_time = 0  # 15-minute intervals
        self.historic_data = {
            'outflows': [[] for _ in range(7)],
            'energy': [[] for _ in range(7)],
            'revenue': [[] for _ in range(7)]
        }
        self.past_outflows = []
        # past_outflows = [
        #   [ outfow[station0, period1], ..., outfow[station6, period1] ],
        #   [ outfow[station0, period2], ..., outfow[station6, period2] ],
        #   [ outfow[station0, period3], ..., outfow[station6, period3] ],
        #   [ outfow[station0, period4], ..., outfow[station6, period4] ],
        #   ...
        # ]
        self._init_delay_buffers()

    @staticmethod
    def _load_time_series(path: str) -> pd.DataFrame:
        """Load and preprocess time series data to create 15-minute intervals."""
        df = pd.read_csv(path)

        # Repeat each row 4 times efficiently using numpy's repeat function
        expanded_df = df.loc[np.repeat(df.index.values, 4)].reset_index(drop=True)

        return expanded_df

    def _init_delay_buffers(self):
        """Initialize delay buffers between stations."""
        self.buffers = []
        for delay in self.delays:
            self.buffers.append({
                'data': np.zeros(delay),
                'ptr': 0
            })

    def get_current_conditions(self) -> tuple[float, float]:
        """Get current precipitation and price values."""
        try:
            precip = self.precip_data.iloc[self.current_time]['water_input_m3']
            price = self.price_data.iloc[self.current_time]['final_price_€kWh']
            return float(precip), float(price)
        except IndexError:
            raise RuntimeError("Time series data doesn't cover simulation period")

    def simulate_step(self):
        """Run one 15-minute simulation step."""
        self.past_outflows.append([])
        water_inflow, price = self.get_current_conditions()
        for i, station in enumerate(self.power_stations):
            # First station uses precipitation, others use delayed flow
            if i == 0:
                inflow = water_inflow
                station.inflow = inflow
            else:
                delay = self.delays[i - 1]
                if self.current_time - delay < 0:
                    inflow = 0
                else:
                    inflow = self.past_outflows[self.current_time - delay][i - 1]
                station.inflow = inflow

            # Fixed flow based on max capacity
            outflow = station.max_water_level / 100
            station.set_outflow(outflow)
            self.past_outflows[-1].append(outflow)
            # print(f"{self.current_time} Station {i}: {station.inflow} inflow, {station.outflow} outflow, {station.water_level} level")

            # Update water level
            station.update_water_level()

            # Generate electricity and record
            energy = station.generate_electricity(price)
            self.historic_data['outflows'][i].append(station.outflow)
            self.historic_data['energy'][i].append(energy)
            self.historic_data['revenue'][i].append(energy * price)

        # print()
        self.current_time += 1

    def get_system_state(self) -> List[Dict]:
        """Get current state of all stations."""
        return [station.get_state() for station in self.power_stations]

    def get_total_energy(self) -> float:
        """Get total energy generated across all stations (kWh)."""
        return sum(station.total_generated for station in self.power_stations)

    def get_total_revenue(self) -> float:
        """Get total revenue across all stations (€)."""
        return sum(station.total_revenue for station in self.power_stations)

    def set_gate_openings(self, openings: List[float]):
        """Set gate openings for all stations (0-1 values)."""
        if len(openings) != len(self.power_stations):
            raise ValueError("Need exactly 7 opening values")
        for station, opening in zip(self.power_stations, openings):
            station.set_gate_opening(opening)