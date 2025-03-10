# Thread Pool Simulation

This project implements a multithreaded task scheduling system using a custom queue and worker threads. It reads tasks from a JSON file, simulates their execution with a thread pool, and generates a report with execution details.

## Features
- **Custom Thread-Safe Queue** for managing task execution.
- **Dynamic Thread Allocation** to optimize resource usage.
- **Logging & Reporting** to track task execution details.

## Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/Mhdi-Asgri/ThreadPoolSimulation.git
   cd ThreadPoolSimulation
   ```
2. Ensure you have Python 3 installed.

## Usage
1. Prepare an input JSON file (e.g., `input.json`) with the following format:
   ```json
   {
       "num_threads": 3,
       "queue_size": 5,
       "tasks": [
           {"task_id": 1, "arrival_time": 1, "execution_time": 2},
           {"task_id": 2, "arrival_time": 2, "execution_time": 3}
       ]
   }
   ```
2. Run the simulation:
   ```sh
   python main.py
   ```
3. The output report will be saved in `output.txt`.

## How It Works
1. Tasks arrive based on `arrival_time` and are added to the queue.
2. Worker threads pick up tasks, execute them, and log their completion.
3. The system ensures proper synchronization using threading conditions.
4. After execution, a summary report is generated.

