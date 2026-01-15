from zynq_tcp_ctrl import ZynqTcpCtrlClient
import numpy as np
import time

#TCP IP configuration
FPGA_IP = "192.168.1.143"

#Memory map regions configuration
MMAP_REGION_ADDR_LIST = [0x1000000] #Reserved mem addr
MMAP_REGION_SIZE_LIST = [0x100000] #1 MB

#Example addr & data 
addr = 0x1000000
data_tx = np.random.randint(low=-2**15, 
                            high= 2**15, 
                            size=(1000, 2, 8), 
                            dtype=np.int16)



c = ZynqTcpCtrlClient(FPGA_IP, 9001)

#Add memory map regions
for mmap_addr, mmap_size in zip(MMAP_REGION_ADDR_LIST, MMAP_REGION_SIZE_LIST):
    c.add_mmap_region(mmap_addr, mmap_size)

#Write
t0 = time.time()
c.write(addr, data_tx)
t1 = time.time()
print(f"Wrote {data_tx.nbytes * 8/ 1e6} Mb in {t1 - t0:.6f} s")

#Read
t0 = time.time()
data_rx = c.read(addr, dtype=data_tx.dtype, size=np.shape(data_tx)) 
t1 = time.time()
print(f"Read {data_rx.nbytes * 8/ 1e6} Mb in {t1 - t0:.6f} s") 

#Data check
print("Data match:", np.array_equal(data_tx, data_rx))

c.load_bitstream("test.bit")  # Example of loading a bitstream
c.close()