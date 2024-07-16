# Python Script to Monitor CPU and GPU on Ubuntu

This simple script provides a clean compact view of CPU performance, memory utilization as well as GPU memory and GPU performance. Great for monitoring your system as you run LLM and other AI/ML workloads.

### Sample Output

```
$ python ai-monitor.py 

Cisco UCSX-210C-M6 computing node with X440p PCIE node X-Fabric Enabled

CPU Type: 2 x Intel(R) Xeon(R) Gold 6348 CPU @ 2.60GHz with 28 cores each
GPU Type: NVIDIA A100-PCIE-40GB


CPU util       CPU mem used/total       GPU mem used/total       GPU util
0.02   %       1.3Gi/503Gi              9.6Gi/40.0Gi             43     %
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

If you prefer you can just download the ai-monitor binary (10.7MB) from the Releases section and run it directly on your machine.

### Testing network Bandwidth

```
sudo apt install iperf
iperf -c 5.182.18.49 -u -b 1000M
```

### Future Enhancements

1. Support multiple GPU per host