
from zynq_tcp_ctrl import ZynqTcpCtrlClient
import numpy as np
import time

#TCP IP configuration
FPGA_IP = "192.168.1.143"

#Memory map regions configuration 
MMAP_REGION_ADDR = 0x4120_0000 
MMAP_REGION_SIZE = 0x1000 #4KB

#GPIO address and values for led_on and led_off
gpio_addr = 0x4120_0000
led_on = 0xFF
led_off = 0x00

c = ZynqTcpCtrlClient(FPGA_IP)

#Add memory map regions
c.add_mmap_region(MMAP_REGION_ADDR, MMAP_REGION_SIZE)

#Load bitstream (prebuilt base design of https://github.com/dspsandbox/Pynq-Redpitaya-125)
t0 = time.time()
bitstream_path = "prebuilt/base.bit"
c.load_bitstream(bitstream_path)  
t1 = time.time()
print(f"Loaded bitstream in {t1 - t0:.6f} s")

#Toggle LEDs
print("Toggling LEDs...")
for i in range(10):
    c.write(gpio_addr, led_on)
    time.sleep(0.5)
    c.write(gpio_addr, led_off)
    time.sleep(0.5)
print("Done")

c.close()