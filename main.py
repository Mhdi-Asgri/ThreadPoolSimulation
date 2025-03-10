import threading
import time
from collections import deque
import json


class Queue:
    def __init__(self, maxsize=0):
        self.queue = deque()
        self.mutex = threading.Lock()
        self.not_empty = threading.Condition(self.mutex)
        self.not_full = threading.Condition(self.mutex)
        self.maxsize = maxsize
        self.unfinished_tasks = 0
        self.all_tasks_done = threading.Condition(self.mutex)

    def put(self, item):
        with self.not_full:
            while self.maxsize > 0 and len(self.queue) >= self.maxsize:
                self.not_full.wait()
            self.queue.append(item)
            self.unfinished_tasks += 1
            self.not_empty.notify()

    def get(self):
        with self.not_empty:
            while not self.queue:
                self.not_empty.wait()
            item = self.queue.popleft()
            self.not_full.notify()
            return item

    def task_done(self):
        with self.all_tasks_done:
            unfinished = self.unfinished_tasks - 1
            if unfinished <= 0:
                if unfinished < 0:
                    raise ValueError("task_done() called too many times")
                self.all_tasks_done.notify_all()
            self.unfinished_tasks = unfinished

    def join(self):
        with self.all_tasks_done:
            while self.unfinished_tasks > 0:
                self.all_tasks_done.wait()

    def empty(self):
        with self.mutex:
            return len(self.queue) == 0


class Task:
    def __init__(self, task_id, arrival_time, execution_time):
        self.task_id = task_id
        self.arrival_time = arrival_time
        self.execution_time = execution_time
        self.completion_time = None


class WorkerThread(threading.Thread):
    def __init__(self, task_queue, log_queue):
        super().__init__()
        self.task_queue = task_queue
        self.log_queue = log_queue
        self.daemon = True

    def run(self):
        while True:
            task = self.task_queue.get()
            if task is None:
                break
            allocation_time = time.strftime("%H:%M:%S", time.localtime())
            self.log_queue.put(
                f"{self.name} allocated to Task {task.task_id} at {allocation_time}"
            )
            start_time = time.strftime("%H:%M:%S", time.localtime())
            time.sleep(task.execution_time)
            task.completion_time = time.strftime("%H:%M:%S", time.localtime())
            self.log_queue.put(
                f"Task {task.task_id} started at {start_time} and completed at {task.completion_time}"
            )
            self.task_queue.task_done()


class ThreadPoolManager:
    def __init__(self, num_threads, queue_size):
        self.num_threads = num_threads
        self.task_queue = Queue(queue_size)
        self.log_queue = Queue()
        self.workers = []
        self.thread_allocations = 0
        self.unused_threads = num_threads
        self.active_threads = 0

        for _ in range(self.num_threads):
            worker = WorkerThread(self.task_queue, self.log_queue)
            worker.start()
            self.workers.append(worker)

    def add_task(self, task):
        self.task_queue.put(task)
        self.log_queue.put(
            f"Task {task.task_id} arrived at {time.strftime('%H:%M:%S')}"
        )
        self.thread_allocations += 1
        self.active_threads += 1
        self.unused_threads = max(0, self.num_threads - self.active_threads)

    def wait_for_completion(self):
        self.task_queue.join()

    def shutdown(self):
        for _ in range(self.num_threads):
            self.task_queue.put(None)
        for worker in self.workers:
            worker.join()

    def generate_report(self, simulation_start_time, simulation_end_time):
        report = []
        total_tasks = 0

        def format_time(seconds):
            return time.strftime("%H:%M:%S", time.gmtime(seconds))

        while not self.log_queue.empty():
            log_entry = self.log_queue.get()
            report.append(log_entry)
            if "completed" in log_entry:
                total_tasks += 1

        report.append("\n=== Simulation Metrics ===")
        report.append(
            f"Total simulation time: {format_time(simulation_end_time - simulation_start_time)}"
        )
        report.append(f"Total tasks completed: {total_tasks}")
        report.append(f"Number of thread allocations: {self.thread_allocations}")
        report.append(f"Number of unused threads: {self.unused_threads}")

        return report


def simulate_thread_pool(num_threads, queue_size, tasks):
    pool_manager = ThreadPoolManager(num_threads=num_threads, queue_size=queue_size)
    simulation_start_time = time.time()

    for task in tasks:
        time.sleep(task.arrival_time)
        pool_manager.add_task(task)

    pool_manager.wait_for_completion()
    pool_manager.shutdown()
    simulation_end_time = time.time()

    try:
        report = pool_manager.generate_report(
            simulation_start_time, simulation_end_time
        )
    except Exception:
        print("pool_manager.generate_report error!")
        report = []

    with open("output.txt", "w") as f:  # output file path
        f.write("=== Simulation Report ===\n")
        for entry in report:
            f.write(entry + "\n")


if __name__ == "__main__":
    file_path = "input3.json"  # input file path
    with open(file_path, "r") as f:
        input_data = json.load(f)

        num_threads = input_data["num_threads"]
        queue_size = input_data["queue_size"]
        tasks_data = input_data["tasks"]
        tasks = [
            Task(task["task_id"], task["arrival_time"], task["execution_time"])
            for task in tasks_data
        ]

        simulate_thread_pool(num_threads, queue_size, tasks)
