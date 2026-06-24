#!/usr/bin/env python3
"""
Multi-Agent Propulsion & Life Support Script Review Orchestrator
Uses the Gemini API to audit spacecraft source code against:
1) Capillary Equilibrium & Valve Timing
2) Hardware Limits & Radiation Protection
3) Resource Conservation
Synthesizes the audits into a NASA-compliant Flight Readiness Review Report.
"""

import os
import sys
import json
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor

# Default configuration
DEFAULT_MODEL = "gemini-2.5-flash"
API_URL_TEMPLATE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

def call_gemini_api(system_instruction, user_content, model=DEFAULT_MODEL):
    """Makes a direct HTTP POST request to the Gemini API using urllib."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[ERROR] GEMINI_API_KEY environment variable is not set.", file=sys.stderr)
        print("[ERROR] Please run: export GEMINI_API_KEY='your_api_key'", file=sys.stderr)
        print("[INFO] Or run with mock mode: python3 review_system.py --mock", file=sys.stderr)
        sys.exit(1)

    url = API_URL_TEMPLATE.format(model=model, api_key=api_key)
    
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": user_content}
                ]
            }
        ],
        "systemInstruction": {
            "parts": [
                {"text": system_instruction}
            ]
        },
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 4096
        }
    }
    
    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode("utf-8")
            res_json = json.loads(res_body)
            text = res_json["candidates"][0]["content"]["parts"][0]["text"]
            return text
    except urllib.error.HTTPError as e:
        print(f"[ERROR] HTTP request failed with code {e.code}", file=sys.stderr)
        try:
            err_details = e.read().decode("utf-8")
            print(f"[ERROR] API Response Details: {err_details}", file=sys.stderr)
        except Exception:
            pass
        raise e
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred during API call: {e}", file=sys.stderr)
        raise e

# --- PERSONAS & PROMPTS ---

CAPILLARY_AUDITOR_SYSTEM = """You are a Capillary Equilibrium Auditor for NASA spacecraft propulsion systems.
Your job is to analyze python scripts controlling hydro-propulsion or fluid loop modules in microgravity.
Analyze the target code for fluid boundary violations, surface tension, capillary feeding issues, and valve timing.

Pay extreme attention to:
1. Capillary feeding replenishment limit vs draining rate (in microgravity, liquid flow rate to the engine is physically limited by the rate at which capillary action / surface tension wicks/vanes can draw propellant from the main reservoir. If code attempts to drain faster than this limit, vapor bubbles form, causing thruster dry-out or failure).
2. Valve opening intervals and duty cycles (capillary paths need periodic valve closed states to draw fluid. Continuous open states are high risk).
3. Rapid back-to-back valve cycling that can cause liquid water-hammering or cavitation.

Format your response as a clear markdown document. 
Identify issues with severity: [CRITICAL], [MAJOR], or [MINOR] and explain the physics/fluid dynamics reason behind each finding.
"""

HARDWARE_ENV_SYSTEM = """You are a NASA Hardware & Environment Safety Agent.
Your job is to analyze spacecraft control scripts for hardware telemetry boundaries, safety loops, and radiation bit-flip vulnerability (SEUs).

Pay extreme attention to:
1. Missing telemetry checks (temperature, pressure, voltage readings must be validated against safe ranges before executing mechanical or pyrotechnic actions. Never run actuators blind or ignore out-of-bounds telemetry).
2. Lack of safety-critical triggers / shutdowns (if telemetry indicates dangerous temperature or pressure, does the code transition to a safe state?).
3. Radiation-induced Single Event Upsets (SEU) / Bit-flips in RAM (critical state variables like SYSTEM_MODE or valve statuses must be protected. Standard python code must employ software-level safeguards such as Triple Modular Redundancy (TMR) / variable voting, value validation, or checksum verification to prevent a single cosmic ray strike from opening a valve or altering execution modes).

Format your response as a clear markdown document.
Identify issues with severity: [CRITICAL], [MAJOR], or [MINOR] and explain the hardware reliability or radiation risk for each.
"""

RESOURCE_ENGINEER_SYSTEM = """You are a NASA Resource Conservation Engineer.
Your job is to optimize power consumption, propellant usage, and valve life cycles in spacecraft propulsion and thermal scripts.

Pay extreme attention to:
1. Propellant waste (unnecessary gas purging, venting propellant to space without critical need).
2. Power management (inefficient heater profiles, heaters left on 100% continuously rather than duty-cycled or temperature-regulated, high power actuators kept engaged longer than needed).
3. Actuator wear (unnecessary valve cycling that reduces the life cycle margins of the hardware).

Format your response as a clear markdown document.
Identify issues with severity: [CRITICAL], [MAJOR], or [MINOR] and suggest optimization and resource-saving alternatives.
"""

SYNTHESIZER_SYSTEM = """You are the Lead Flight Director and Review Board Chair for a NASA space hydro-propulsion system.
Your job is to intake three audit reports (Capillary Equilibrium, Hardware/Environment, Resource Conservation) on a target code script and synthesize them into a single, cohesive, flight-ready document.

The output document MUST be named "FLIGHT_REVIEW_REPORT.md".
It must adhere to the following NASA review standard structure:
1. Title: NASA Flight Readiness Review (FRR) Report - Space Hydro Propulsion Module
2. Executive Summary: High-level overview of the script, its readiness, and major risks.
3. Flight Readiness Score: An overall numeric score from 0% to 100%.
   - Provide a quantitative breakdown of how the score was calculated (e.g. deductions based on severity of findings: Critical -20 pts, Major -10 pts, Minor -3 pts).
   - If there are CRITICAL findings, the score MUST be below 50%.
4. Consolidated Detailed Findings (grouped by audit category: Capillary & Fluid Dynamics, Hardware & Environmental Protection, Resource Conservation). Clearly preserve the severity markers ([CRITICAL], [MAJOR], [MINOR]).
5. Actions Required for Flight Clearance: A prioritized bulleted task list mapping exactly to the remediation of all critical and major findings.

Your tone should be rigorous, professional, and safety-focused. Make sure the output is pure Markdown.
"""

def generate_mock_report():
    """Generates a high-fidelity simulated NASA Flight Review Report for demonstration purposes."""
    return """# NASA Flight Readiness Review (FRR) Report - Space Hydro Propulsion Module

## Executive Summary
An executive flight readiness audit has been conducted on the unvetted spacecraft propulsion control script `hardware_control.py`. The system controls an active microgravity capillary-fed hydro-propulsion unit. Based on the consolidated findings of the Capillary Equilibrium Auditor, the Hardware & Environment Safety Agent, and the Resource Conservation Engineer, **the script in its current state is UNFIT FOR FLIGHT**. 

Multiple safety-critical violations were identified, including severe capillary flow rate mismatches, lack of software-level Single Event Upset (SEU) protections, completely unvalidated telemetry paths, and inefficient thermal power management. Remediation is required before flight clearance can be granted.

---

## Flight Readiness Score: 37% (FLIGHT SUSPENDED)

### Quantitative Score Breakdown
The initial baseline score is **100%**. Deductions are applied based on finding severity:
- **Critical Findings** (-20 pts each): 2 identified = **-40%**
  - Capillary draw rate deficit (draining faster than capillary replenishment).
  - Lack of radiation bit-flip protection (SEU) on critical state variables.
- **Major Findings** (-10 pts each): 2 identified = **-20%**
  - Unvalidated chamber temperature and pressure telemetry before actuation.
  - Inefficient thermal heater management (100% constant power draw).
- **Minor Findings** (-3 pts each): 1 identified = **-3%**
  - Wasteful gas purge venting cycles.
  
**Final Score Calculation:** 100% - 40% - 20% - 3% = **37%**
*NASA Safety Protocol: Any score below 50% or containing any CRITICAL severity finding results in an automatic Flight Suspension.*

---

## Consolidated Detailed Findings

### 1. Capillary & Fluid Dynamics Audit
* **[CRITICAL] Capillary Draw Rate Deficit**: The script sets `flow_rate_ml_per_sec = 5.0` during the thruster burn, but the hardware capillary limit is defined as `capillary_limit_ml_per_sec = 2.0`. Attempting to extract fluid faster than surface tension and capillary structures can replenish it will result in vapor pocket ingestion, thruster cavitation, and structural dry-out within seconds.
* **[MAJOR] Continuous Valve Actuation**: During a burn, the thrust valve (Valve 3) is kept open continuously for up to 10 seconds without duty-cycled rest intervals. In microgravity capillary-fed systems, valves must be cycled with specific off-intervals to allow capillary forces to re-wet the wick/mesh.
* **[MAJOR] Water-Hammering Risk**: The script commands a secondary micro-adjustment burn (`execute_thrust_burn(1.0)`) immediately following a major burn without any cool-down or pressure stabilization delay, exposing the manifold to severe fluidic water-hammering and transient stress.

### 2. Hardware Safety & Radiation Protection Audit
* **[CRITICAL] Lack of SEU/Bit-Flip Mitigations**: Safety-critical system states (`SYSTEM_MODE` and `VALVE_STATE`) are stored as raw variables without software-level redudancy. A single cosmic ray striking the RAM (Single Event Upset) could corrupt these variables, leading to accidental thruster firing or stuck-open valves.
* **[MAJOR] Unvalidated Telemetry Controls**: Chamber temperature is read but never checked against the safe operating bounds (-10°C to +65°C). Additionally, the pressurization valve (Valve 1) is kept open for 5 seconds without real-time pressure feedback loop checks, risking overpressurization and rupture.

### 3. Resource Conservation Audit
* **[MAJOR] Unregulated Heater Power**: Structural heaters are engaged at 100% power on startup and never adjusted. This is a severe battery/power drain and risks overheating the propulsion system when ambient temperatures are already high.
* **[MINOR] Wasteful Gas Purging**: In `maintain_pressure()`, the purge valve is actuated to vent gas on every single control cycle where pressure is not low, causing unnecessary depletion of the spacecraft's cold gas reserves.

---

## Actions Required for Flight Clearance

1. **[CRITICAL]** Implement a throttling or cycle-burn structure to limit the propellant draw rate to $\le 1.8$ mL/s (incorporating a 10% safety margin below the 2.0 mL/s capillary limit).
2. **[CRITICAL]** Refactor safety-critical state variables (`SYSTEM_MODE` and `VALVE_STATE`) to use Triple Modular Redundancy (TMR) with a software voting mechanism (e.g., three separate variables checked against each other before any physical command).
3. **[MAJOR]** Implement boundary checking on chamber temperature and loop pressure. Add an automatic safety-cutoff state if temperature exits the range of -10°C to +65°C, or if pressure exceeds 60 PSI.
4. **[MAJOR]** Implement a PID or duty-cycled controller for the structural heaters, adjusting heater power based on the actual chamber temperature telemetry rather than running at 100% constant power.
5. **[MINOR]** Modify the pressure regulation logic to only perform purge venting if the pressure exceeds 45 PSI, rather than running a purge on every cycle.
"""

def audit_file(filepath, model, mock_mode=False):
    """Loads target file and runs it through all three auditors, then synthesizes."""
    print(f"[*] Reading target script: {filepath}")
    try:
        with open(filepath, "r") as f:
            code_content = f.read()
    except Exception as e:
        print(f"[ERROR] Failed to read {filepath}: {e}", file=sys.stderr)
        sys.exit(1)

    report_filename = "FLIGHT_REVIEW_REPORT.md"

    if mock_mode:
        print("[*] Running in MOCK Mode (no API keys required)...")
        print("[+] Simulating Capillary Equilibrium Auditor...")
        print("[+] Simulating Hardware & Environment Safety Agent...")
        print("[+] Simulating Resource Conservation Engineer...")
        print("[*] Synthesizing audit findings into FLIGHT_REVIEW_REPORT.md...")
        final_report = generate_mock_report()
        
        try:
            with open(report_filename, "w") as f:
                f.write(final_report)
            print(f"[✓] Success! Flight Review Report saved to {report_filename}")
        except Exception as e:
            print(f"[ERROR] Failed to write report file: {e}", file=sys.stderr)
            sys.exit(1)
            
        print("[✓] Audit Summary Status:\n    Flight Readiness Score: 37% (FLIGHT SUSPENDED)")
        return

    user_content = f"Here is the script source code for review:\n\n```python\n{code_content}\n```"

    tasks = [
        ("Capillary Equilibrium Auditor", CAPILLARY_AUDITOR_SYSTEM, user_content),
        ("Hardware & Environment Safety Agent", HARDWARE_ENV_SYSTEM, user_content),
        ("Resource Conservation Engineer", RESOURCE_ENGINEER_SYSTEM, user_content)
    ]

    results = {}

    print(f"[*] Dispatching audits to Gemini API using model: {model}...")
    
    def run_audit(name, system_instruction, content):
        print(f"[+] Starting: {name}")
        report = call_gemini_api(system_instruction, content, model=model)
        print(f"[✓] Completed: {name}")
        return name, report

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(run_audit, name, sys_inst, content) for name, sys_inst, content in tasks]
        for future in futures:
            name, report = future.result()
            results[name] = report

    synthesis_payload = (
        "=== CAPILLARY EQUILIBRIUM AUDIT REPORT ===\n"
        f"{results['Capillary Equilibrium Auditor']}\n\n"
        "=== HARDWARE & ENVIRONMENT AUDIT REPORT ===\n"
        f"{results['Hardware & Environment Safety Agent']}\n\n"
        "=== RESOURCE CONSERVATION REPORT ===\n"
        f"{results['Resource Conservation Engineer']}\n"
    )

    print("[*] Synthesizing audit findings into FLIGHT_REVIEW_REPORT.md...")
    final_report = call_gemini_api(SYNTHESIZER_SYSTEM, synthesis_payload, model=model)
    
    try:
        with open(report_filename, "w") as f:
            f.write(final_report)
        print(f"[✓] Success! Flight Review Report saved to {report_filename}")
    except Exception as e:
        print(f"[ERROR] Failed to write report file: {e}", file=sys.stderr)
        sys.exit(1)
        
    score_line = "N/A"
    for line in final_report.split("\n"):
        if "readiness score" in line.lower() or "score:" in line.lower() or "readiness rating" in line.lower():
            score_line = line
            break
    print(f"[✓] Audit Summary Status:\n    {score_line}")

def main():
    model = os.environ.get("GEMINI_MODEL", DEFAULT_MODEL)
    
    # Check command line flags
    mock_mode = "--mock" in sys.argv
    
    # Filter out flags to get target file
    args = [arg for arg in sys.argv[1:] if arg != "--mock"]
    
    target_file = "hardware_control.py"
    if args:
        target_file = args[0]

    if not os.path.exists(target_file):
        print(f"[ERROR] Target file '{target_file}' not found.", file=sys.stderr)
        sys.exit(1)

    audit_file(target_file, model, mock_mode=mock_mode)

if __name__ == "__main__":
    main()
