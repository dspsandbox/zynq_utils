#!/usr/bin/env python3
import mmap

def read_mem(addr):
    f = open("/dev/mem", "r+b")
    m = mmap.mmap(fileno=f.fileno(), length=mmap.PAGESIZE, offset=(int(addr / mmap.PAGESIZE)*mmap.PAGESIZE))
    m.seek(addr % mmap.PAGESIZE)
    val = m.read(4)
    f.close()
    m.close()
    return int.from_bytes(val, "little")


def write_mem(addr, val):
    f = open("/dev/mem", "w+b")
    m = mmap.mmap(fileno=f.fileno(), length=mmap.PAGESIZE, offset=(int(addr / mmap.PAGESIZE)*mmap.PAGESIZE))
    m.seek(addr % mmap.PAGESIZE)
    m.write(val.to_bytes(4, "little"))
    f.close()
    m.close()
    return 


def config_watchdog(timeout, clk_freq):
    
    addr_dict = {"mode" : 0xF8005000, "control" : 0xF8005004, "restart": 0xF8005008, "status": 0xF800500C}
    

    
    ZKEY = 0xABC
    IRQLN = 3 
    RSTLN = 4
    IRQEN = 0    
    RSTEN = int(timeout >= 0)
    WDEN =  int(timeout >= 0)
    MODE_VAL = (ZKEY << 12) | (IRQLN << 7) | (RSTLN << 4) | (IRQEN << 2) | (RSTEN << 1) | WDEN
    MODE_ADDR = addr_dict["mode"]
    
    CKEY = 0x248
    CRV = max(int(timeout * clk_freq / (4096 * 0x1000)), 0)
    CLKSEL = 3 
    CONTROL_VAL = (CKEY << 14) | (CRV << 2) | CLKSEL
    CONTROL_ADDR = addr_dict["control"]
    
    KEY_VAL = 0x1999
    RESTART_VAL = KEY_VAL
    RESTART_ADDR = addr_dict["restart"]
    
    
    if(((read_mem(MODE_ADDR) & 0xfff) != (MODE_VAL & 0xfff)) or ((read_mem(CONTROL_ADDR) & 0xffff) != (CONTROL_VAL & 0xffff))):
        write_mem(MODE_ADDR, MODE_VAL & 0xfffffc)
        write_mem(CONTROL_ADDR, CONTROL_VAL)
        write_mem(MODE_ADDR, MODE_VAL)

    
    write_mem(RESTART_ADDR, RESTART_VAL)
    
    
    
if __name__ == "__main__":
    import sys
    timeout = int(sys.argv[1])
    clk_freq = int(sys.argv[2])
    config_watchdog(timeout, clk_freq)