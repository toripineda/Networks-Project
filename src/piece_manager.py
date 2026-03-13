# file pieces + bitfield
#has_pieces()
#store_pieces()
#get_piece()
#needed_pieces()
import threading
import os
import math

_peer_id = None
_file_name = None
_file_size = None
_piece_size = None
_num_pieces = None
_file_path = None
_bitfield = []
_lock = threading.Lock()

def init(peer_id, config):
    global _peer_id, _file_name, _file_size, _piece_size, _num_pieces, _file_path, _bitfield
    
    _peer_id = peer_id
    _file_name = config['file_name']
    _file_size = config['file_size']
    _piece_size = config['piece_size']
    _num_pieces = math.ceil(_file_size / _piece_size)

    peers = config.get('peers', {})
    peer_data = peers.get(peer_id, {})
    has_file = config.get('peers', {}).get(peer_id, {}).get('has file', False)
    _bitfield = [has_file] * _num_pieces



def has_pieces(index):
    if index < 0 or index >= _num_pieces:
        raise IndexError("Piece index out of range")
    
    _lock.acquire()

    try:
        return _bitfield[index]
    finally:
        _lock.release()

def store_pieces(index, data):
    if index < 0 or index >= _num_pieces:
        raise IndexError("Piece index out of range")
    if data is None or len(data) == 0:
        raise ValueError("Data is empty")

    offset = index * _piece_size

    _lock.acquire()

    try:
        mode = 'r+b' if os.path.exists(_file_path) else 'wb'
        f = open(_file_path, mode)
        try:
            f.seek(offset)
            f.write(data)
        finally:
            f.close()

        _bitfield[index] = True
    finally:
        _lock.release()

def get_piece(index):
    if index < 0 or index >= _num_pieces:
        raise IndexError("Piece index out of range")
    
    offset = index * _piece_size

    _lock.acquire()

    try:
        f = open(_file_path, 'rb')
        try:
            f.seek(offset)
            size = _piece_size
            data = f.read(size)
        finally:
            f.close()

        if len(data) != size:
            raise IOError(f"Expected {size} bytes for piece {index} but read {len(data)}")
        
        return data
    finally:
        _lock.release()

def needed_pieces(neighbor_bitfield):
    if neighbor_bitfield is None:
        raise ValueError("neighbor_bitfield cannot be None")
    if len(neighbor_bitfield) != _num_pieces:
        raise ValueError(f"neighbor_bitfield length {len(neighbor_bitfield)} does not match expected {_num_pieces}")
    
    _lock.acquire()

