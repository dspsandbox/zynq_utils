# ZYNQ TCP CONTROL
## Overview
This project provides TCP-based control utilities for ZYNQ FPGA boards, enabling remote bitstream loading and memory IO.

See examples [led_blink.py](example_redpitaya-125-14/led_blink.py) and [reserved_mem.py](example_redpitaya-125-14/reserved_mem.py)



## Remote Installation
* Open terminal window
* Transfer [zynq_tcp_ctrl_remote](zynq_tcp_ctrl_remote) directory to your ZYNQ FPGA

    ``` 
    scp -r zynq_tcp_ctrl_remote <user>@<ip-addr>:
    ```

* SSH into your ZYNQ FPGA 

    ``` 
    ssh <user>@<ip-addr>
    ```
* Run makefile (within SSH session)
    ```
    cd zynq_tcp_ctrl_remote
    make all
    ```
* (OPTIONAL) Check service status:
    ```
    systemctl status zynq_tcp_ctrl_server.service
    ```


## Local Installation
* Open a terminal window
* Navigate to [zynq_tcp_ctr_local/zynq_tcp_ctrl](zynq_tcp_ctr_local/zynq_tcp_ctrl/)
    ```
    cd zynq_tcp_ctrl_local/zynq_tcp_ctrl/
    ```
* Install on your PC the *zynq_tcp_ctrl* python library
    ```
    pip3 install .
    ```

## Running Example Scripts (Redpitaya-125-14)

* Run the [led_blink.py](example_redpitaya-125-14/led_blink.py) and [reserved_mem.py](example_redpitaya-125-14/reserved_mem.py) examples on your Redpitaya-125-14:
    ```
    cd examples_redpitaya-125-14
    python3 led_blink.py
    python3 reserved_mem.py
    ```


