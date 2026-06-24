#!/usr/bin/env python3
"""
Propulsion and Life Support Fluid Loop Control System (Simulated)
Target: Spacecraft Hydro-Propulsion Module
WARNING: Unvetted code. Do not run in flight hardware.
"""

import time
import random

# Global System State (Vulnerable to radiation bit-flips / SEU - no TMR or ECC)
SYSTEM_MODE = 1  # 1 = Idle, 2 = Pressurizing, 3 = Firing, 4 = Venting
VALVE_STATE = 0  # Bitmask of open/closed valves

# Hardware Registers / Interfaces (Simulated)
class HardwareInterface:
    def __init__(self):
        self.reservoir_volume_ml = 1000.0  # Max capacity
        self.capillary_limit_ml_per_sec = 2.0  # Capillary flow replenishment limit
        self.current_fill_ml = 800.0
        
    def read_pressure_psi(self):
        # Normal operating pressure should be 15 - 45 PSI. Peak limit is 60 PSI.
        return random.uniform(10.0, 75.0)

    def read_chamber_temp_c(self):
        # Safe operating temperature is -10C to +65C
        return random.uniform(-40.0, 110.0)

    def set_valve(self, valve_id, state):
        global VALVE_STATE
        if state == 1:
            VALVE_STATE |= (1 << valve_id)
            print(f"[HW] Valve {valve_id} opened.")
        else:
            VALVE_STATE &= ~(1 << valve_id)
            print(f"[HW] Valve {valve_id} closed.")

    def run_heater(self, power_percent):
        # Structural heaters to prevent freezing of aqueous propellant
        print(f"[HW] Heater power set to {power_percent}%.")

    def fire_thruster_electromagnet(self, duration_ms):
        print(f"[HW] Electromagnet thruster actuated for {duration_ms} ms.")

hw = HardwareInterface()

def initialize_system():
    print("Initializing hydro-propulsion loop...")
    # Issue: Constant high-draw heater set to 100% on start and never adjusted based on actual temperature telemetry
    hw.run_heater(100) 
    
    # Open safety isolator valve
    hw.set_valve(0, 1)
    time.sleep(0.1)

def maintain_pressure():
    """Reads chamber pressure and regulates it."""
    # Issue: Reads telemetry but does not validate if pressure exceeds limits (e.g. > 60 PSI)
    # before performing actions, risking structural rupture.
    pressure = hw.read_pressure_psi()
    print(f"Current Loop Pressure: {pressure:.2f} PSI")
    
    if pressure < 20.0:
        # Repressurizing
        print("Pressure low. Opening pressurization valve.")
        hw.set_valve(1, 1)
        # Issue: No time limit on valve opening - can overpressurize if left open
        time.sleep(5.0) 
        hw.set_valve(1, 0)
    else:
        # Already high pressure, but we open pressure regulator valve anyway to vent gas to space
        # Issue: Resource waste. Vents gas without checking if pressure is dangerously high.
        print("Performing routine purge venting...")
        hw.set_valve(2, 1)
        time.sleep(2.0)
        hw.set_valve(2, 0)

def execute_thrust_burn(burn_duration_sec):
    """Executes thruster burn using microgravity capillary feed."""
    global SYSTEM_MODE
    SYSTEM_MODE = 3
    
    print(f"Beginning burn of duration {burn_duration_sec}s...")
    
    # Capillary feeding relies on surface tension to draw fluid into the chamber.
    # Liquid flow replenishment rate is limited. 
    # Issue: Draining fluid too fast (e.g. 5.0 ml/s flow rate) compared to the capillary limit (2.0 ml/s)
    # results in bubble ingestion and thruster dry-out.
    flow_rate_ml_per_sec = 5.0 
    
    # Actuate thrust valve (Valve 3)
    hw.set_valve(3, 1)
    
    start_time = time.time()
    while time.time() - start_time < burn_duration_sec:
        # Update fluid levels
        hw.current_fill_ml -= flow_rate_ml_per_sec
        print(f"Propellant Remaining: {hw.current_fill_ml:.1f} ml")
        
        # Actuate thrust electromagnet continuously
        hw.fire_thruster_electromagnet(100)
        
        # Issue: Valve is kept open continuously without duty cycle intervals.
        # Capillary systems require periodic valve shutoffs (intervals) to allow capillary forces
        # to re-wet the wick/mesh and pull more fluid from the reservoir.
        time.sleep(0.1)
        
    hw.set_valve(3, 0)
    SYSTEM_MODE = 1
    print("Burn complete.")

def main_loop():
    initialize_system()
    
    # Run loop
    for cycle in range(3):
        print(f"\n--- Control Cycle {cycle + 1} ---")
        
        # Check telemetry (Issue: Reads chamber temperature but does not check if it exceeds thermal limits)
        temp = hw.read_chamber_temp_c()
        print(f"Chamber Temperature: {temp:.2f} C")
        
        maintain_pressure()
        
        # Execute thrust sequence
        execute_thrust_burn(10.0)
        
        # Issue: Rapid back-to-back valve cycling without cool-down periods causes fluidic water-hammering.
        print("Preparing secondary micro-adjustment burn...")
        execute_thrust_burn(1.0)
        
        time.sleep(1.0)

if __name__ == "__main__":
    main_loop()
