#!/usr/bin/env python3
import socket
import struct
import threading
import mmap
import os
import numpy as np
import subprocess


OP_WRITE = 1
OP_READ  = 2
OP_ADD_MMAP = 3
OP_LOAD_BIT = 4

STATUS_OK  = 0
STATUS_ERR = 1

REQ_HDR = struct.Struct("!BQI")   # opcode (1), address (8), size (4)
RESP_HDR = struct.Struct("!BI")   # status (1), size (4)

def execute_shell(cmd, raise_on_err=True):
    result = subprocess.run(cmd, capture_output=True,text=True, shell=True)
    if raise_on_err and result.returncode != 0:
        raise RuntimeError(f"command '{cmd}' failed with error: {result.stderr.strip()}")
    return result


def recv_exact(sock: socket.socket, n: int) -> bytes:
    """Receive exactly n bytes or raise ConnectionError."""
    chunks = []
    remaining = n
    while remaining:
        chunk = sock.recv(remaining)
        if not chunk:
            raise ConnectionError("peer closed")
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)

def send_response(sock: socket.socket, status: int, payload: bytes = b"") -> None:
    sock.sendall(RESP_HDR.pack(status, len(payload)) + payload)

class ZynqTcpCtrlServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.lock = threading.Lock()
        self.mmap_dict = {}  
        self._fp = "/sys/class/fpga_manager/fpga0"


    def add_mmap_region(self, address: int, size: int):
        size = max(size, 1)
        region_already_mapped = False
        for i in range(len(self.mmap_dict)):
            mmap_item = self.mmap_dict[i]
            if address >= mmap_item['address'] and address + size <= mmap_item["address"] + mmap_item["size"]:
                region_already_mapped = True
                break
        
        if not region_already_mapped:
            offset_page_aligned = address & ~(mmap.PAGESIZE - 1)
            size_page_aligned = size + (address - offset_page_aligned)
            f = os.open('/dev/mem', os.O_RDWR | os.O_SYNC)
            self.mmap_dict[len(self.mmap_dict)] = {
                "address": offset_page_aligned,
                "size": size_page_aligned,
                "mmap": memoryview(mmap.mmap(f, size_page_aligned, mmap.MAP_SHARED, mmap.PROT_READ | mmap.PROT_WRITE,offset=offset_page_aligned))
            }
        
      
    def _get_mmap_region(self, address: int, size: int):
        for i in range(len(self.mmap_dict)):
            mmap_item = self.mmap_dict[i]
            if (address >= mmap_item['address']) and ((address + size) <= mmap_item["address"] + mmap_item["size"]):
                mm =  mmap_item["mmap"]
                return mm[address - mmap_item['address'] : address - mmap_item['address'] + size]
        raise RuntimeError("no mmap region covers the requested address range")


    def read_mmap_region(self, address: int, size: int):
        mm = self._get_mmap_region(address, size)
        return mm
    
    def write_mmap_region(self, address: int, data: bytes):
        size = len(data)
        mm = self._get_mmap_region(address, size)
        mm[:] = data[:]

    def load_bitstream_fpgamanager(self, bin_data):
        execute_shell("echo 0 > /sys/class/fpga_manager/fpga0/flags")
        execute_shell("mkdir -p /lib/firmware")
        with open("/lib/firmware/bitstream.bin", "wb") as f:
            f.write(bin_data)
        execute_shell("echo bitstream.bin > /sys/class/fpga_manager/fpga0/firmware")

    def _handle_client(self, conn: socket.socket, addr):
        try:
            while True:
                hdr = recv_exact(conn, REQ_HDR.size)  # may raise ConnectionError
                opcode, address, size = REQ_HDR.unpack(hdr)
                
                if opcode == OP_ADD_MMAP:
                    with self.lock:
                        self.add_mmap_region(address, size)
                    send_response(conn, STATUS_OK)

                elif opcode == OP_WRITE:
                    data = recv_exact(conn, size)
                    with self.lock:
                        self.write_mmap_region(address, data)
                    send_response(conn, STATUS_OK)

                elif opcode == OP_READ:                    
                    with self.lock:
                        data = self.read_mmap_region(address, size)
                    send_response(conn, STATUS_OK, bytearray(data))

                elif opcode == OP_LOAD_BIT:
                    bin_data = recv_exact(conn, size)        
                    self.load_bitstream_fpgamanager(bin_data)
                    send_response(conn, STATUS_OK)

                else:
                    send_response(conn, STATUS_ERR, b"unknown opcode")

        except ConnectionError:
            pass  # client disconnected
        except Exception as e:
            try:
                send_response(conn, STATUS_ERR, f"server error: {e}".encode("utf-8"))
            except Exception:
                pass
        finally:
            conn.close()
      

    def serve_forever(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            s.listen()
            print(f"ZynqTcpCtrlServer listening on {self.host}:{self.port}")

            while True:
                conn, addr = s.accept()
                t = threading.Thread(target=self._handle_client, args=(conn, addr), daemon=True)
                t.start()

if __name__ == "__main__":
    ZynqTcpCtrlServer(host="0.0.0.0", port=9000).serve_forever()
