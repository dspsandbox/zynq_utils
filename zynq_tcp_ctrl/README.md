# ZYNQ TCP CONTROL

## INSTALLATION
### REMOTE 
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


### Local 
* Open a terminal window
* Navigate to 
* Install on your PC the [zynq_tcp_ctrl](local/zynq_tcp_ctrl) library by opening 
