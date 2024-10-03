# Python Script to Monitor LLM Server, CPU, GPU and Network on Ubuntu

This simple script provides a clean compact view of CPU performance, memory utilization, network as well as GPU memory and GPU performance. Great for monitoring your system as you run LLM and other AI/ML workloads. Network monitoring now automatically switches from Kbps/Mbps/Gbps as traffic increases on the tx and rx sides. If you use the plus version it supports multiple GPU and NIC as well as LLM server stats via API.

### Sample Output

```
$ python ai-monitor.py 

Cisco UCSX-410C-M7 computing node with X440p PCIE node X-Fabric Enabled

CPU Type: 4 x Intel(R) Xeon(R) Platinum 8490H with 60 cores each
GPU Type: NVIDIA L4


CPU util   CPU mem used/total	GPU mem used/total   GPU util   Network tx/rx util
0.00   %   6.2Gi/3.9Ti		0.00Gi/22Gi          0      %   4.32 Kbps/1.86 Kbps
```

### Requirements

This script will only work if the following commands work on your system:

```
lscpu | grep Model
mpstat 1 1
nvidia-smi
free -h
```

If you get an error message on psutil then do the following:
```
pip install psutil
```

### Executable Option

If you prefer you can just download the ai-monitor binary (10.7MB) from the Releases section and run it directly on your machine. Note that network bandwidth is currently not in the binary. 

### Testing Network Bandwidth

The AI Monitor now supports resporting tx and rx speed on 1 sec interval. To test this you can send synthetic traffic using iPerf.

```
sudo apt install iperf
iperf -c 5.182.18.49 -u -b 1000M
```

### AI Monitor Plus

If you run AI Monitor Plus, it supports multiple GPU and NIC per host (frontend and backend networking for example). It also has the ability to call the vLLM metrics API (if you are running vLLM) so that you can see the performance of the LLM in tokens/sec along side the workload metrics.

To run AI Monitor Plus with LLM stats you need to specify the api-url in the format http://<IP_address>:<port>/metrics

### Sample Output of AI Monitor Plus

```
$ ./ai-monitor-plus.py --api-url http://64.101.169.102:8000/metrics

Cisco UCSC-C240-M5SX computing node (hostname: ai-11)

CPU: 2 x Intel(R) Xeon(R) Gold 6248R CPU @ 3.00GHz with 24 cores
GPU: 6 x Tesla T4

       Use     Memory Use

 CPU   4.87%   17Gi/1.5Ti

 GPU1  88%     12.8/15.0Gi
 GPU2  81%     12.7/15.0Gi
 GPU3  82%     12.7/15.0Gi
 GPU4  82%     12.7/15.0Gi
 GPU5  83%     12.7/15.0Gi
 GPU6  82%     12.7/15.0Gi

 NIC1 tx: 446.49 Mbps, rx: 469.49 Mbps (eno5)

 LLM: 48.59 tokens/s
```

### Future Features

- Allow flags for NICs that you want to supress
- Help page with examples 