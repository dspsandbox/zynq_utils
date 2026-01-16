# ZYNQ Watchdog Service
## Overview
This project creates a watchdog service for Zynq-7000 FPGAs that restarts the FPGA in case it becomes stale (60s timeout).

## Configuration
Open [zynq_watchdog_remote/zynq_watchdog.service](zynq_watchdog_remote/zynq_watchdog.service) and edit line 5 to hold the timeout in seconds (default: 60) and cpu_1x clock frequency in Hz (default: 100000000).


## Remote Installation
* Open terminal window
* Transfer [zynq_watchdog_remote](zynq_watchdog_remote) directory to your ZYNQ FPGA

    ``` 
    scp -r zynq_watchdog_remote <user>@<ip-addr>:
    ```

* SSH into your ZYNQ FPGA 

    ``` 
    ssh <user>@<ip-addr>
    ```
* Run makefile (within SSH session)
    ```
    cd zynq_watchdog_remote
    make all
    ```
* (OPTIONAL) Check service status:
    ```
    systemctl status zynq_watchdog.service
    ```
