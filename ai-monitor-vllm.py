#!/usr/bin/env python3
# www.github.com/pl247/ai-toolkit-2.0

import subprocess
import time
import sys
import psutil
import curses
import socket
import requests
import re
import argparse  # Import the argparse module

def get_total_generated_tokens(api_url):
    """Fetch total number of generated tokens from vLLM `/metrics`."""
    try:
        response = requests.get(api_url)
        response.raise_for_status()

        pattern = r'^vllm:generation_tokens_total\{model_name="[^"]*"\} ([0-9.e+-]+)'
        match = re.search(pattern, response.text, re.MULTILINE)

        return float(match.group(1)) if match else None

    except requests.RequestException:
        return None

def measure_tokens_per_second(api_url, interval=10):
    """Manually measure tokens per second."""
    tokens_before = get_total_generated_tokens(api_url)
    if tokens_before is None:
        return "N/A [API Down]"

    time.sleep(interval)
    tokens_after = get_total_generated_tokens(api_url)

    if tokens_after is None:
        return "N/A [Metric not found]"

    return (tokens_after - tokens_before) / interval

def convert_bps(bits_per_second):
    """Convert bits per second to Mbps or Gbps based on magnitude."""
    if bits_per_second < 1e6:
        return f"{bits_per_second / 1e3:.2f} Kbps"
    elif bits_per_second < 1e9:
        return f"{bits_per_second / 1e6:.2f} Mbps"
    else:
        return f"{bits_per_second / 1e9:.2f} Gbps"

def poll(interval):
    """Retrieve raw stats within an interval window."""
    tot_before = psutil.net_io_counters()
    pnic_before = psutil.net_io_counters(pernic=True)
    time.sleep(interval)
    tot_after = psutil.net_io_counters()
    pnic_after = psutil.net_io_counters(pernic=True)
    return (tot_before, tot_after, pnic_before, pnic_after)

def refresh_window(interval, tot_before, tot_after, pnic_before, pnic_after):
    """Calculate and print network stats."""
    nic_names = list(pnic_after.keys())
    nic_names.sort()

    network_stats = {}

    for name in nic_names:
        if name == 'lo' or name == 'docker0' or not psutil.net_if_addrs().get(name):
            continue

        stats_before = pnic_before[name]
        stats_after = pnic_after[name]

        sent_speed_bps = (stats_after.bytes_sent - stats_before.bytes_sent) / interval * 8
        recv_speed_bps = (stats_after.bytes_recv - stats_before.bytes_recv) / interval * 8

        sent_speed_human = convert_bps(sent_speed_bps)
        recv_speed_human = convert_bps(recv_speed_bps)

        network_stats[name] = (sent_speed_human, recv_speed_human)

    return network_stats

def get_server_type():
    command = "cat /sys/devices/virtual/dmi/id/product_name"
    result = subprocess.check_output(command, shell=True, encoding='utf-8').strip()
    return result

def get_cpu_type():
    command = "lscpu | grep 'Model name:' | awk -F': ' '{print $2}'"
    result = subprocess.check_output(command, shell=True).decode().strip()
    return result

def get_cpu_cores():
    command = "lscpu | grep 'Core(s) per socket:' | awk -F': ' '{print $2}'"
    result = subprocess.check_output(command, shell=True).decode().strip()
    return result

def get_cpu_sockets():
    command = "lscpu | grep 'Socket(s):' | awk -F': ' '{print $2}'"
    result = subprocess.check_output(command, shell=True).decode().strip()
    return result

def get_cpu_average():
    command = "mpstat 1 1 | awk '/^Average:/ {usage=100-$NF} END {print usage}'"
    result = subprocess.check_output(command, shell=True).decode().strip()
    return result

def get_gpu_info():
    command = "nvidia-smi --query-gpu=gpu_name,memory.used,utilization.gpu,memory.total --format=csv,noheader,nounits"
    try:
        result = subprocess.check_output(command, shell=True).decode().strip()
    except subprocess.CalledProcessError:
        return []

    gpu_info = []
    for line in result.split('\n'):
        gpu_name, memory_used, gpu_utilization, gpu_memory = line.split(", ")
        memory_used = int(memory_used) / 1024
        gpu_memory = int(gpu_memory) / 1024
        gpu_utilization = int(gpu_utilization)
        gpu_info.append((gpu_name, memory_used, gpu_utilization, gpu_memory))

    return gpu_info

def get_memory_info():
    command = "free -h | awk '/^Mem:/ {print $2, $3, $4}'"
    result = subprocess.check_output(command, shell=True).decode().strip()
    total, used, available = result.split()
    return total, used, available

def get_generation_throughput(api_url):
    """Retrieve the average generation throughput from the vLLM API."""
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an error for bad status codes

        # Extract the specific metric from the Prometheus text response
        pattern = r'^vllm:avg_generation_throughput_toks_per_s{.*}\s+([\d\.]+)'
        match = re.search(pattern, response.text, re.MULTILINE)
        if match:
            return float(match.group(1))
        else:
            return "N/A [API down]"  # Return "N/A" if metric not found

    except requests.RequestException:
        return "N/A [API down]"  # Suppress error messages and return "N/A" if the API is down

def main(stdscr, api_url):
    curses.curs_set(0)  # Hide the cursor
    stdscr.nodelay(1)  # Make getch() non-blocking
    stdscr.timeout(1000)  # Refresh every second

    hostname = socket.gethostname()
    server_type = get_server_type()
    cpu_sockets = get_cpu_sockets()
    cpu_cores = get_cpu_cores()
    cpu_type = get_cpu_type()
    gpu_info = get_gpu_info()
    num_gpus = len(gpu_info)

    # Constants for column widths
    COMPONENT_WIDTH = 4
    UTILIZATION_WIDTH = 6
    MEMORY_WIDTH = 20

    # Fixed width strings for consistent alignment
    COMPONENT_FORMAT = f" {{:<{COMPONENT_WIDTH}}}  {{:<{UTILIZATION_WIDTH}}}  {{:<{MEMORY_WIDTH}}}"
    NIC_FORMAT = f" {{:<{COMPONENT_WIDTH}}} {{:<{MEMORY_WIDTH}}} {{:<{MEMORY_WIDTH}}}"

    stdscr.addstr(0, 0, f"Cisco {server_type} computing node (hostname: {hostname})")
    stdscr.addstr(2, 0, f"CPU: {cpu_sockets} x {cpu_type} with {cpu_cores} cores")
    if num_gpus > 0:
        stdscr.addstr(3, 0, f"GPU: {num_gpus} x {gpu_info[0][0]}")
    else:
        stdscr.addstr(3, 0, "No GPU detected")

    stdscr.addstr(5, 0, COMPONENT_FORMAT.format("", "Use", "Memory Use"))

    interval = 1  # Adjust the interval as needed

    try:
        while True:
            args = poll(interval)
            network_stats = refresh_window(interval, *args)
            cpu_average = float(get_cpu_average())
            total_memory, used_memory, available_memory = get_memory_info()

            # Print CPU metrics
            stdscr.addstr(7, 0, COMPONENT_FORMAT.format("CPU", f"{cpu_average:.2f}%", f"{used_memory}/{total_memory}"))

            # Print GPU metrics
            row_offset = 9
            for i, (gpu_name, memory_used, gpu_utilization, gpu_memory) in enumerate(get_gpu_info()):
                stdscr.addstr(row_offset + i, 0, COMPONENT_FORMAT.format(f"GPU{i+1}", f"{gpu_utilization}%", f"{memory_used:.1f}/{gpu_memory:.1f}Gi"))

            # Print NIC metrics
            row_offset += num_gpus + 1
            nic_index = 1
            for name, (sent_speed_human, recv_speed_human) in network_stats.items():
                if any(addr.address for addr in psutil.net_if_addrs().get(name, []) if addr.family == socket.AF_INET):
                    nic_memory = f"tx: {sent_speed_human}, rx: {recv_speed_human}"
                    stdscr.addstr(row_offset, 0, NIC_FORMAT.format(f"NIC{nic_index}", nic_memory, f"({name})"))
                    row_offset += 1
                    nic_index += 1

            # Print Avg Generation Throughput if api_url is specified

# ... (rest of your function remains unchanged)

            if api_url:  # Only modify vLLM metric handling
                tokens_per_second = measure_tokens_per_second(api_url, interval)
                stdscr.addstr(row_offset + 1, 0, f" LLM: {tokens_per_second:.2f} tokens/s [API up]" if isinstance(tokens_per_second, float) else f" LLM: {tokens_per_second}")

    # ... (rest of your function remains unchanged)


            stdscr.clrtoeol()  # Clear to end of line to handle overwriting
            stdscr.refresh()
            time.sleep(interval)

    except KeyboardInterrupt:
        stdscr.clear()  # Clear the screen before exiting
        stdscr.addstr(0, 0, "Exiting gracefully...\n")
        stdscr.refresh()
        time.sleep(2)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="AI Network and GPU Monitoring Tool")
    parser.add_argument('--api-url', type=str, default=None,
                        help='The API URL to retrieve generation throughput from')
    args = parser.parse_args()

    curses.wrapper(lambda stdscr: main(stdscr, args.api_url))  # Pass the api_url to the main function
