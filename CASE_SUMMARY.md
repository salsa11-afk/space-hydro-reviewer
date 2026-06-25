# Space Hydro Reviewer: Automated Multi Agent Aerospace Code Auditor

###   1. The Problem We Targeted
In deep space, autonomous life support systems like hydroponic capillary watering systems are mission critical. A single timing anomaly, unvalidated sensor telemetry hook, or buffer overflow in a fluid control script can lead to catastrophic valve flooding or resource exhaustion. Because standard compilers only look for syntactic typos, they have zero understanding of physical, environmental, or aerospace safety constraints. The Space Hydro Reviewer solves this by establishing a physics aware, automated AI safety board that evaluates unvetted code against real aerospace and hardware limitations before deployment.

---

###   2. Architectural Decisions & Orchestration Strategy
To maximize auditing depth, our system utilizes an **orchestrated multi-agent pipeline** built in Python (`review_system.py`). Rather than asking a single LLM instance for a generic review, the orchestrator opens the target file (`hardware_control.py`), packages the payload, and parallel-streams the code to three highly specialized sub agent personas running concurrently:
1. **Capillary Equilibrium Auditor:** Scans for fluid velocity limits, valve constraints, and boundary physics.
2. **Hardware & Environment Safety Agent:** Audits for cosmic radiation bit flip vulnerabilities and hardware exceptions.
3. **Resource Conservation Engineer:** Analyzes power configurations and maximizes execution efficiency.

The orchestrator dynamically aggregates these parallel streams, calculates a standardized mathematical **Flight Readiness Score**, and auto synthesizes a NASA compliant markdown document (`FLIGHT_REVIEW_REPORT.md`) outlining flaws and providing refactored, safe code blocks.

---

###   3. Google Technology Used & Why
Our entire intelligence engine is powered natively by the **Google Gemini API** (utilizing the `gemini-2.5-flash` model via the Python Google Generative AI SDK) and built within the cloud integrated **Antigravity IDE** framework. 
* **Why Gemini API:** Building a true multi agent safety system requires low latency, advanced reasoning over dense code strings, and native support for system instructions to enforce strict engineering personas. Gemini handled three concurrent execution paths effortlessly.
* **Why Antigravity:** The specialized cloud environment allowed for seamless workspace alignment, streamlined workspace tracking, and reliable execution of our automated orchestration pipeline.

---

###   4. Future Improvements (With More Time)
Given more time to scale this prototype, our roadmap includes:
* **Live API Feedback Loops:** Upgrading from the simulated `--mock` framework to automated live Gemini API payload evaluation loops.
* **Abstract Syntax Tree (AST) Coupling:** Integrating Python's native `ast` library to pinpoint the precise line numbers of flaws before handing the snippets to the Gemini agents.
* **CI/CD Integration GitHub Actions:** Automating this script to trigger instantly on every single GitHub `git push`, completely blocking any code deployment if the Flight Readiness Score falls below an 80% safety threshold.
