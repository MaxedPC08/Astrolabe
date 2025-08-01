## Info about the cameras

Thne global server has its own websocket at port 50000. It will always be hosted, even if cameras are not connected. The global server is used to send commands to the cameras and receive information from them.

```
{
    "functiopn": "command_name",
    "arg1": value1,
    "arg2": value2,
    ...,
    "argN": valueN
}
```

---

### **`hardware_info`**

**Description:** Returns detailed information about the current hardware system.

**Returns:**
* **`temperature`** (float): The temperature of the CPU.
* **`cpu_usage`** (float): The current percentage of CPU utilization.
* **`memory_usage`** (float): The current percentage of memory utilization.
* **`disk_usage`** (float): The current percentage of disk space usage.
* **`system`** (string, optional): The name of the operating system.
* **`node_name`** (string, optional): The name of the machine on the network.
* **`release`** (string, optional): The OS release version.
* **`version`** (string, optional): The specific OS version currently running.
* **`machine`** (string, optional): The architecture of the CPU.
* **`processor`** (float): More detailed information about the processor.

---

### **`connection_info`**

**Description:** Returns information about the current connections, including cameras and other open websockets.

**Returns:**
* **`connections`** (dictionary): A dictionary containing information about all active connections.