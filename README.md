# Cafe-Queue-Simulation-Optimization

A queuing theory project using Python and Power BI to analyze customer wait times in a cafe environment. 

By replacing standard First-Come, First-Served (FCFS) queue logic with a Shortest Processing Time (SPT) rule and an 8-minute wait limit, average customer wait times were reduced by 10.7% (2.1 minutes per order).

## Overview & Results

* Reduced average wait time from 19.6 minutes to 17.5 minutes across peak arrival windows.
* Used an 8-minute wait threshold override to prevent larger orders from being stuck in line indefinitely.
* Built a Power BI dashboard to compare FCFS vs. Optimized metrics, customer order breakdown, and peak queue dynamics.

## System Workflow

1. `Cafe_Queue_Simulator.xlsx` contains order logs, timestamps, and item prep times.
2. `simulation.py` runs both FCFS and SPT logic and outputs wait times.
3. `Simulation_Results.xlsx` exports the processed data into Power BI for dashboarding.

## Dashboard Preview

* Preview: Cafe Queue Preview.png

## How to Run

1. Install required packages:
   ```bash
   pip install pandas openpyxl
