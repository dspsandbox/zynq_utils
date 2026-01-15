# ZYNQ TCP CONTROL

## Remote Installation
###  
* Open terminal window
* Transfer [remote](remote) directory to ZYNQ FPGA

    ``` 
    scp -r remote <user>@<ip-addr>:
    ```

* SSH into ZYNQ FPGA 

    ``` 
    ssh <user>@<ip-addr>
    ```
* Run makefile (within SSH session)
    ```
    cd remote
    make all
    ```
* (OPTIONAL) Check service status:
    ```
    systemctl status zynq_tcp_ctrl_server.service
    ```


## Local Installation
* Open a terminal window
* Navigate to [local/zynq_tcp_ctrl](local/zynq_tcp_ctrl/)
    ```
    cd local/zynq_tcp_ctrl/
    ```
* Install on your PC the *zynq_tcp_ctrl* python library
    ```
    pip3 install .
    ```

## Example Script

* Run [local/example/example_zynq_tcp_ctrl.py](local/example/example_zynq_tcp_ctrl.py):
    ```
    python3 local/example/example_zynq_tcp_ctrl.py
    ```


