import simpy
import pandas as pd
import logging
import os
from power_station_system import PowerStationSystem
from tabulate import tabulate
import power_stations_data
import precipitation_data
import prices_data

'''
Results must be stored in every step and the sum of the values (except for price) must be shown every day. 
'''

# TODO: establecer intervalos de una hora y duración de 1 año. Añadir un factor de conversión que pase de valor por mes
#   a valor por hora
# TODO: tener en cuenta los retardos

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='simulation.log'
)


def generate_data_files(data_dir: str):
    """Generate/overwrite the required CSV files for the simulation"""
    os.makedirs(data_dir, exist_ok=True)

    # Regenerate power stations file
    power_stations_data.df.to_csv(
        f'{data_dir}/power_stations_config.csv',
        index=False
    )
    logging.info("Power stations file regenerated")

    # Regenerate precipitation file
    precipitation_data.df.to_csv(
        f'{data_dir}/precipitation.csv',
        index=False
    )
    logging.info("Precipitation file regenerated")

    # Regenerate prices file
    prices_data.df.to_csv(
        f'{data_dir}/electricity_prices.csv',
        index=False
    )
    logging.info("Prices file regenerated")


class HydroSimEnvironment:
    def __init__(self, data_dir: str = 'data'):
        """Initialize the environment and regenerate all data"""
        # Generate CSV files (always overwriting)
        generate_data_files(data_dir)

        self.system = PowerStationSystem(
            config_path=f'{data_dir}/power_stations_config.csv',
            precipitation_path=f'{data_dir}/precipitation.csv',
            price_path=f'{data_dir}/electricity_prices.csv'
        )
        self.sim_duration = 35_040  # 1 year in 15 minutes intervals = 35_040
        self.current_step = 0
        self.results = []

    def run_simulation(self):
        """Run the complete simulation."""
        env = simpy.Environment()
        env.process(self.simulation_process(env))
        env.run(until=self.sim_duration)
        self.save_results()
        logging.info("Simulation completed")

    def simulation_process(self, env):
        """Main simulation process."""
        while self.current_step < self.sim_duration:
            self.system.simulate_step()
            self.record_step_results()

            # Show status every day (96 steps = 1 day)
            if self.current_step % 96 == 0:
                self._print_status_table()

            self.current_step += 1
            yield env.timeout(1)
            # Weekly summary
            if self.current_step % 672 == 0:  # 168 steps in one week
                week_num = self.current_step // 672
                logging.info(f"Processed week {week_num} of 52")

    def record_step_results(self):
        """Record the results of the current step."""
        step_data = {
            'step': self.current_step,
            'total_energy': self.system.get_total_energy(),
            'total_revenue': self.system.get_total_revenue(),
            'station_states': [station.get_state() for station in self.system.power_stations]
        }
        self.results.append(step_data)

    def save_results(self):
        """Save results to CSV files."""
        import os

        # Create 'results' folder if it doesn't exist
        os.makedirs('results', exist_ok=True)

        # Save summary
        summary_df = pd.DataFrame([{
            'step': r['step'],
            'total_energy': r['total_energy'],
            'total_revenue': r['total_revenue']
        } for r in self.results])
        summary_df.to_csv('results/summary.csv', index=False)

        # Save data per station
        for station_id in range(len(self.system.power_stations)):
            station_data = []
            for step in self.results:
                state = step['station_states'][station_id]
                station_data.append({
                    'step': step['step'],
                    **state
                })
            pd.DataFrame(station_data).to_csv(f'results/station_{station_id}.csv', index=False)

    def _print_status_table(self):
        """Print the current state of all stations in table format."""
        # Prepare headers with all station names
        headers = [""] + [f"Station {i + 1}" for i in range(len(self.system.power_stations))]

        data = []

        # Get states of all stations
        states = [station.get_state() for station in self.system.power_stations]

        # Get current conditions (electricity price)
        _, current_price = self.system.get_current_conditions()

        # Calculate evaporation loss for each station
        losses = [
            station.water_level * (1 - station.loss_coefficient)
            for station in self.system.power_stations
        ]

        # Build table rows
        data.append(["Current water level (m³)"] + [f"{state['water_level']:,.2f}" for state in states])
        data.append(["Water inflow (m³)"] + [f"{state['inflow']:,.2f}" for state in states])
        data.append(["Water outflow (m³)"] + [f"{state['outflow']:,.2f}" for state in states])
        data.append(["Evaporation and filtration loss (m³)"] + [f"{loss:,.2f}" for loss in losses])

        # New requested rows
        data.append(["Turbined water (m³)"] + [f"{state['outflow']:,.2f}" for state in states])
        data.append(["Electricity price (€/kWh)"] + [f"{current_price:,.4f}"] + [""] * (
                    len(self.system.power_stations) - 1))
        data.append(["Generated revenue (€)"] + [f"{state['total_revenue']:,.2f}" for state in states])

        # Print table
        print(f"\nSystem status - Time {self.current_step}")
        print(tabulate(data, headers=headers, tablefmt="grid", stralign="right"))


if __name__ == "__main__":
    try:
        print("Starting simulation - Regenerating data files...")
        sim_env = HydroSimEnvironment(data_dir='data')
        sim_env.run_simulation()
        print("Simulation completed. Results saved in /results")
    except Exception as e:
        logging.error(f"Simulation error: {str(e)}")
        raise Exception
