from zynq_tcp_ctrl import ZynqTcpCtrlClient
import numpy as np
import time

#TCP IP configuration
FPGA_IP = "192.168.1.143"

#Memory map regions configuration (defined in https://github.com/RedPitaya/RedPitaya-FPGA/blob/master/dts/memory.dtsi)
MMAP_REGION_ADDR = 0x8000_0000 
MMAP_REGION_SIZE = 0x200_0000

#Example addr & data 
addr = 0x8000_0050
data_tx = np.random.randint(low=-2**15, 
                            high= 2**15, 
                            size=(1000, 8, 80), 
                            dtype=np.int16)


c = ZynqTcpCtrlClient(FPGA_IP)

#Add memory map regions
c.add_mmap_region(MMAP_REGION_ADDR, MMAP_REGION_SIZE)

#Write
t0 = time.time()
c.write(addr, data_tx)
t1 = time.time()
print(f"Wrote {data_tx.nbytes / 1e6} MB in {t1 - t0:.6f} s")

#Read
t0 = time.time()
data_rx = c.read(addr, dtype=data_tx.dtype, size=np.shape(data_tx)) 
t1 = time.time()
print(f"Read {data_rx.nbytes / 1e6} MB in {t1 - t0:.6f} s") 

#Data check
print("Data match:", np.array_equal(data_tx, data_rx))

c.close()