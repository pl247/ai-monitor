#!/usr/bin/env python3

import subprocess
import time
import sys

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
    cpu_sockets = get_cpu_sockets()
    cpu_cores = get_cpu_cores()
    cpu_type = get_cpu_type()
    gpu_name, memory_used, gpu_utilization, gpu_memory_gib = get_gpu_info()
    print(f"\nCisco UCSX-210C-M7 computing node with X440p PCIE node X-Fabric Enabled")
    print(f"\nCPU Type: {cpu_sockets} x {cpu_type} with {cpu_cores} cores each")
    print(f"GPU Type: {gpu_name}\n")
    print(f"\nCPU util       CPU mem used/total       GPU mem used/total       GPU util")
    while True:
        cpu_average = get_cpu_average()
        gpu_name, memory_used, gpu_utilization, gpu_memory_gib = get_gpu_info()
        total_memory, used_memory, available_memory = get_memory_info()

        print(f"\r {cpu_average}%          {used_memory}/{total_memory}              {memory_used}Gi/{gpu_memory_gib}Gi           {gpu_utilization}%    ", end="", flush=True)
        time.sleep(1)

try:
    main()
except KeyboardInterrupt:
    print(f"\n\nExiting...\n")
    sys.exit()
