#!/usr/bin/env python3
import socket
import struct
import numpy as np
import math
from pathlib import Path


OP_WRITE = 1
OP_READ  = 2
OP_ADD_MMAP = 3
OP_LOAD_BIT = 4

STATUS_OK  = 0
STATUS_ERR = 1

REQ_HDR = struct.Struct("!BQI")  # opcode, address, size
RESP_HDR = struct.Struct("!BI")  # status, size

def recv_exact(sock: socket.socket, n: int) -> bytes:
    chunks = []
    remaining = n
    while remaining:
        chunk = sock.recv(remaining)
        if not chunk:
            raise ConnectionError("server closed")
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


class ZynqTcpCtrlClient:
    def __init__(self, host, port=9000, timeout=5.0):
        """
        Initialize the TCP client and connect to the server.
        :param host: IP address or hostname of the server.
        :param port: TCP port of the server (default: 9000).
        :param timeout: Connection timeout in seconds (default: 5.0).
        """
        self.sock = socket.create_connection((host, port), timeout=timeout)


    def close(self):
        """
        Close the TCP connection to the server.
        """
        try:
            self.sock.close()
        except Exception:
            pass


    def write(self, addr, val):
        """
        Write a value to a given memory address.

        :param addr: Address to write to (needs to be within a mapped region, see *add_mmap_region*).
        :param val: Value to write. Can be an int (mapped to uint32), bytes, or numpy.ndarray.
        """
        if not isinstance(val, (int, bytes, np.ndarray)):
            raise TypeError("content must be of type bytes, int (mapped to uint32) or numpy.ndarray")
        if isinstance(val, int):
            content = np.array([val], dtype=np.uint32).tobytes()
        elif isinstance(val, np.ndarray):
            content = val.tobytes()
        else:  # bytes
            content = val
        self.sock.sendall(REQ_HDR.pack(OP_WRITE, addr, len(content)) + content)
        _ = self._recv_response()  # should be empty on OK

    def read(self, addr, dtype=np.uint32, size=1):
        """
        Read a value from a given memory address.
        
        :param addr: Address to read from (needs to be within a mapped region, see *add_mmap_region*).
        :param dtype: Data type of the returned value. Can be bytes or any numpy dtype.
        :param size: Number of elements to read. For dtype=bytes, size must be an integer (number of bytes).
                     For other dtypes, size can be an integer (1D array) or a tuple (multi-D array).
        :return: The read value, either as bytes or a numpy array.
        """
        if dtype == bytes:
            if isinstance(size, int):
                size_bytes = size
            else:
                raise TypeError("for dtype=bytes, size must be an integer")
        else:
            if isinstance(size, int):
                size_bytes = size * np.dtype(dtype).itemsize 
            else:
                size_bytes = math.prod(size) * np.dtype(dtype).itemsize 
        
        self.sock.sendall(REQ_HDR.pack(OP_READ, addr, size_bytes))
        
        data_bytes = self._recv_response()
        if dtype == bytes:
            return data_bytes
        else:
            data_array = np.frombuffer(data_bytes, dtype=dtype)
            if size == 1:
                return data_array[0]
            else:
                return np.reshape(data_array, size)

    def add_mmap_region(self, address: int, size: int):
        """
        Create a memory-mapped region for remote read/write operations. In case of more than one region, 
        call this method multiple times with the corresponding address and size parameters. If the new region
        is equal to or a subset of an already mapped region, the call will be ignored. Created memory-mapped
        regions will stay mapped for the lifetime of the remote service (until FPGA is restarted). 

        :param address: Base address of the memory-mapped region.
        :param size: Size (in bytes) of the memory-mapped region.
        """
        self.sock.sendall(REQ_HDR.pack(OP_ADD_MMAP, address, size))
        _ = self._recv_response()  # should be empty on OK  

    
    def load_bitstream(self, path):
        """
        Load a bitstream into the FPGA using the Linux FPGA Manager interface. 
        The bitstream file can be either in .bit or .bin format.
        :param path: Path to the bitstream file (.bit or .bin).
        """ 
        if path.endswith('.bin'):
            with open(path, "rb") as f:
                bin_data = f.read()
        elif path.endswith('.bit'):
            bit_data = self._get_bitstream_dict(path)["data"]
            bin_data = self._bit2bin(bit_data)
        else:
            raise ValueError("File must be .bin or .bit format")
        
        self.sock.sendall(REQ_HDR.pack(OP_LOAD_BIT, 0, len(bin_data)) + bin_data)
        _ = self._recv_response()  # should be empty on OK

    

    def _recv_response(self) -> bytes:
        hdr = recv_exact(self.sock, RESP_HDR.size)
        status, size = RESP_HDR.unpack(hdr)
        payload = recv_exact(self.sock, size) if size else b""
        if status == STATUS_OK:
            return payload
        # error
        msg = payload.decode("utf-8", errors="replace")
        raise RuntimeError(msg)
    

    def _get_bitstream_dict(self, data_bin):
        with Path(data_bin) as p:
            contents = p.read_bytes()
        
        finished = False
        offset = 0
        
        bit_dict = {}

        # Strip the (2+n)-byte first field (2-bit length, n-bit data)
        length = struct.unpack(">h", contents[offset : offset + 2])[0]
        offset += 2 + length

        # Strip a two-byte unknown field (usually 1)
        offset += 2

        # Strip the remaining headers. 0x65 signals the bit data field
        while not finished:
            desc = contents[offset]
            offset += 1

            if desc != 0x65:
                length = struct.unpack(">h", contents[offset : offset + 2])[0]
                offset += 2
                fmt = ">{}s".format(length)
                data = struct.unpack(fmt, contents[offset : offset + length])[0]
                data = data.decode("ascii")[:-1]
                offset += length

            if desc == 0x61:
                s = data.split(";")
                bit_dict["design"] = s[0]
                bit_dict["version"] = s[-1]
            elif desc == 0x62:
                bit_dict["part"] = data
            elif desc == 0x63:
                bit_dict["date"] = data
            elif desc == 0x64:
                bit_dict["time"] = data
            elif desc == 0x65:
                finished = True
                length = struct.unpack(">i", contents[offset : offset + 4])[0]
                offset += 4
                # Expected length values can be verified in the chip TRM
                bit_dict["length"] = str(length)
                if length + offset != len(contents):
                    raise RuntimeError("Invalid length found")
                bit_dict["data"] = contents[offset : offset + length]
            else:
                raise RuntimeError("Unknown field: {}".format(hex(desc)))
        return bit_dict


    def _bit2bin(self, bit_data):
        bin_data = bytes(np.frombuffer(bit_data, "i4").byteswap())
        return bin_data

    
