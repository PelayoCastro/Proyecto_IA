import numpy as np
from typing import Dict


class PowerStation:
    def __init__(self,
                 max_water_level: float,
                 initial_water_level: float,
                 loss_coefficient: float,
                 station_id: int,
                 is_first: bool = False):
        """
        Initialize a hydroelectric power station.
        """
        self.max_water_level = max_water_level
        self.water_level = initial_water_level
        self.loss_coefficient = loss_coefficient
        self.station_id = station_id
        self.is_first = is_first

        # Flow variables (m³ per 15-minute interval)
        self.inflow = 0.0
        self.outflow = 0.0
        self.gate_opening = 1.0  # Gate opening (0-1)

        # Statistics
        self.total_generated = 0.0  # Total energy generated (kWh)
        self.total_revenue = 0.0  # Total revenue (€)

    def update_water_level(self, water_input_m3: float = None):
        """Update the water level in the reservoir."""
        evaporation_loss = self.water_level * (1 - self.loss_coefficient)
        if self.is_first and water_input_m3 is not None:
            self.inflow = water_input_m3
            self.water_level += self.inflow - self.outflow - evaporation_loss
        else:
            self.water_level += self.inflow - self.outflow - evaporation_loss

        self.water_level = np.clip(self.water_level, 0, self.max_water_level)

    def generate_electricity(self, current_price: float) -> float:
        """Simulate electricity generation."""
        conversion_factor = 0.023  # 0.023 kWh per m³ of turbinate water
        energy_generated = self.outflow * conversion_factor
        revenue = energy_generated * current_price

        self.total_generated += energy_generated
        self.total_revenue += revenue

        return energy_generated

    def set_outflow(self, outflow: float):
        """Set the amount of water leaving the station."""
        max_possible_outflow = min(self.water_level, outflow)
        self.outflow = self.gate_opening * max_possible_outflow

    def set_gate_opening(self, opening: float):
        """Set the gate opening level."""
        self.gate_opening = np.clip(opening, 0, 1)

    def get_state(self) -> Dict:
        """Return the current state of the station."""
        return {
            'station_id': self.station_id,
            'water_level': self.water_level,
            'max_water_level': self.max_water_level,
            'inflow': self.inflow,
            'outflow': self.outflow,
            'gate_opening': self.gate_opening,
            'total_generated': self.total_generated,
            'total_revenue': self.total_revenue
        }