# Python Script to Monitor CPU and GPU on Ubuntu

This simple script provides a clean compact view of CPU performance, memory utilization as well as GPU memory and GPU performance. Great for monitoring your system as you run LLM and other AI/ML workloads.

### Sample Output

```
$ python ai-monitor.py 

Cisco UCSX-410C-M7 computing node with X440p PCIE node X-Fabric Enabled

CPU Type: 4 x Intel(R) Xeon(R) Platinum 8490H with 60 cores each
GPU Type: NVIDIA L4


CPU util   CPU mem used/total	GPU mem used/total   GPU util   Network tx/rx util
0.00   %   6.2Gi/3.9Ti		 0.00Gi/22Gi          0      %   4.32 Kbps/1.86 Kbps
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

### Future Enhancements

1. Support multiple GPU per host
2. Add API and webui