from zynq_tcp_ctrl import ZynqTcpCtrlClient

c = ZynqTcpCtrlClient("192.168.1.143", 9001)
c.add_mmap_region(0x1000000, 4096)
c.write(0x1000000, b"by")
d = c.read(0x1000000, dtype=bytes, length=5  )  # b'hello'
print(d)

c.close()