#!/usr/bin/env python3

import subprocess
import time
import sys
import psutil
from psutil._common import bytes2human

try:
    import curses
except ImportError:
    sys.exit('platform not supported')

lineno = 0
win = curses.initscr()

def printl(line):
    """A thin wrapper around curses's addstr()."""
    global lineno
    try:
        win.addstr(lineno, 0, line)
    except curses.error:
        lineno = 0
        win.refresh()
        raise
    else:
        lineno += 1

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
    # sleep some time
    time.sleep(interval)
    tot_after = psutil.net_io_counters()
    pnic_after = psutil.net_io_counters(pernic=True)
    return (tot_before, tot_after, pnic_before, pnic_after)

def refresh_window(interval, tot_before, tot_after, pnic_before, pnic_after):
    """Calculate and print network stats."""
    global lineno

    # per-network interface details
    nic_names = list(pnic_after.keys())
    nic_names.sort()

    network_stats = {}

    for name in nic_names:
        # Exclude loopback interface
        if name == 'lo':
            continue

        stats_before = pnic_before[name]
        stats_after = pnic_after[name]

        # Calculate bits per second
        sent_speed_bps = (stats_after.bytes_sent - stats_before.bytes_sent) / interval * 8
        recv_speed_bps = (stats_after.bytes_recv - stats_before.bytes_recv) / interval * 8

        # Convert to human-readable format
        sent_speed_human = convert_bps(sent_speed_bps)
        recv_speed_human = convert_bps(recv_speed_bps)

        # Store in network_stats dictionary
        network_stats[name] = (sent_speed_human, recv_speed_human)

    return network_stats

def setup():
    curses.start_color()
    curses.use_default_colors()
    for i in range(curses.COLORS):
        curses.init_pair(i + 1, i, -1)
    curses.endwin()
    win.nodelay(1)

def tear_down():
    win.keypad(0)
    curses.nocbreak()
    curses.echo()
    curses.endwin()

def get_server_type():
    command = "cat /sys/devices/virtual/dmi/id/product_name"
    result = subprocess.check_output(command, shell=True, encoding='utf-8').strip()
    server_type = result
    return server_type

def get_cpu_type():
    command = "lscpu | grep 'Model name:' | awk -F': ' '{print $2}'"
    result = subprocess.check_output(command, shell=True).decode().strip()
    cpu_type = result
    return cpu_type

def get_cpu_cores():
    command = "lscpu | grep 'Core' | awk -F': ' '{print $2}'"
    result = subprocess.check_output(command, shell=True).decode().strip()
    cpu_cores = result
    return cpu_cores

def get_cpu_sockets():
    command = "lscpu | grep 'Socket' | awk -F': ' '{print $2}'"
    result = subprocess.check_output(command, shell=True).decode().strip()
    cpu_sockets = result
    return cpu_sockets

def get_cpu_average():
    command = "mpstat 1 1 | awk '/^Average:/ {usage=100-$NF} END {print usage}'"
    result = subprocess.check_output(command, shell=True).decode().strip()
    return result

def get_gpu_info():
    command = "nvidia-smi --query-gpu=gpu_name,memory.used,utilization.gpu,memory.total --format=csv,noheader,nounits"
    try:
        result = subprocess.check_output(command, shell=True).decode().strip()
    except subprocess.CalledProcessError:
        return 'None', 0.0, 0.0, 0.0
    else:
        gpu_name, memory_used, gpu_utilization, gpu_memory = result.split(", ")
        memory_used = int(memory_used)
        gpu_memory = int(gpu_memory)
        gpu_memory_gib = round(gpu_memory / 1024, 2)
        memory_used = round(memory_used / 1024, 2)
        return gpu_name, memory_used, gpu_utilization, gpu_memory_gib

def get_memory_info():
    command = "free -h | awk '/^Mem:/ {print $2, $3, $4}'"
    result = subprocess.check_output(command, shell=True).decode().strip()
    total, used, available = result.split()
    return total, used, available

def main():
    setup()
    try:
        server_type = get_server_type()
        cpu_sockets = get_cpu_sockets()
        cpu_cores = get_cpu_cores()
        cpu_type = get_cpu_type()
        gpu_name, memory_used, gpu_utilization, gpu_memory_gib = get_gpu_info()
        
        print(f"\nCisco {server_type} computing node with X440p PCIE node X-Fabric Enabled")
        print(f"\nCPU Type: {cpu_sockets} x {cpu_type} with {cpu_cores} cores each")
        print(f"GPU Type: {gpu_name}\n")
        print(f"\nCPU util   CPU mem used/total\tGPU mem used/total   GPU util   Network tx/rx util")
        
        interval = 1  # Adjust the interval as needed
        while True:
            args = poll(interval)
            network_stats = refresh_window(interval, *args)
            cpu_average = float(get_cpu_average())
            cpu_average = f"{cpu_average:<7.2f}"
            gpu_name, memory_used, gpu_utilization, gpu_memory_gib = get_gpu_info()
            memory_used = float(memory_used)
            memory_used = f"{memory_used:2.2f}"
            gpu_memory_gib = int(gpu_memory_gib)
            gpu_memory_gib = f"{gpu_memory_gib:2}"
            gpu_utilization = int(gpu_utilization)
            gpu_utilization = f"{gpu_utilization:<7}"

            total_memory, used_memory, available_memory = get_memory_info()
            
            # Print all metrics together
            for name, (sent_speed_human, recv_speed_human) in network_stats.items():
                print(f"{cpu_average}%   {used_memory}/{total_memory}\t\t{memory_used}Gi/{gpu_memory_gib}Gi          {gpu_utilization}%   {sent_speed_human}/{recv_speed_human}   ", end="\r", flush=True)
            
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        tear_down()

if __name__ == '__main__':
    main()

