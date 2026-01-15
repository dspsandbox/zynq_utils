#!/usr/bin/env python3
import socket
import struct
import numpy as np
import math

OP_WRITE = 1
OP_READ  = 2
OP_ADD_MMAP = 3

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
    def __init__(self, host="127.0.0.1", port=9000, timeout=5.0):
        self.sock = socket.create_connection((host, port), timeout=timeout)

    def close(self):
        try:
            self.sock.close()
        except Exception:
            pass

    def _recv_response(self) -> bytes:
        hdr = recv_exact(self.sock, RESP_HDR.size)
        status, size = RESP_HDR.unpack(hdr)
        payload = recv_exact(self.sock, size) if size else b""
        if status == STATUS_OK:
            return payload
        # error
        msg = payload.decode("utf-8", errors="replace")
        raise RuntimeError(msg)

    def write(self, address, val):
        if not isinstance(val, (int, bytes, np.ndarray)):
            raise TypeError("content must be of type bytes, int (mapped to uint32) or numpy.ndarray")
        if isinstance(val, int):
            content = np.array([val], dtype=np.uint32).tobytes()
        elif isinstance(val, np.ndarray):
            content = val.tobytes()
        else:  # bytes
            content = val
        self.sock.sendall(REQ_HDR.pack(OP_WRITE, address, len(content)) + content)
        _ = self._recv_response()  # should be empty on OK

    def read(self, address, dtype=np.uint32, size=1):
        if dtype == bytes:
            if isinstance(size, int):
                size_bytes = size
            else:
                raise TypeError("for dtype=bytes, size must be an integer")
        else:
            if isinstance(size, int):
                size_bytes = size * np.dtype(dtype).itemsize 
            size_bytes = math.prod(size) * np.dtype(dtype).itemsize 
        
        self.sock.sendall(REQ_HDR.pack(OP_READ, address, size_bytes))
        
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
        self.sock.sendall(REQ_HDR.pack(OP_ADD_MMAP, address, size))
        _ = self._recv_response()  # should be empty on OK  
        
