# Python Script to Monitor CPU and GPU on Ubuntu

This simple script provides a compact view of CPU performance, memory utilization as well as GPU memory and GPU performance

This script will only work if the following commands work on your system:

### Sample Output

```
$ python ai_monitor.py 

Cisco UCSX-210C-M6 computing node with X440p PCIE node X-Fabric Enabled

CPU Type: 2 x Intel(R) Xeon(R) Gold 6348 CPU @ 2.60GHz with 28 cores each
GPU Type: NVIDIA A100-PCIE-40GB


CPU util       CPU mem used/total       GPU mem used/total       GPU util
2%             1.3Gi/503Gi              9.6Gi/40.0Gi             43%
```

### Requirements

This script will only work if the following commands work on your system:

```
lscpu | grep Model
mpstat 1 1
nvidia-smi
free -h
```

### Changing the Name of the Server

To determine the system manufacturer and product name of the system, you can run the following commands:
```
sudo dmidecode -s system-manufacturer
sudo dmidecode -s system-product-name
```

These commands can be incorporated into the script if you like
