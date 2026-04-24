# file pieces + bitfield
#has_pieces()
#store_pieces()
#get_piece()
#needed_pieces()
import threading
import os
import math

#variables used for all functions in module
_peer_id = None
_file_name = None
_file_size = None
_piece_size = None
_num_pieces = None
_file_path = None
_bitfield = []
#lock prevents race conditions because of simultaneous threads
_lock = threading.Lock()

def init(peer_id, has_file, config):
    global _peer_id, _file_name, _file_size, _piece_size, _num_pieces, _file_path, _bitfield
    
    _peer_id = peer_id
    
    # Clean up the dictionary keys to prevent KeyErrors
    clean_config = {}
    for key, value in config.items():
        clean_key = str(key).strip().lower()
        clean_config[clean_key] = value

    _file_name = clean_config.get('filename')
    _file_size = int(clean_config.get('filesize', 0))
    _piece_size = int(clean_config.get('piecesize', 1))

    if _file_name is None:
        print("\nERROR: Could not find 'FileName' in your Common.cfg.")
        raise ValueError("Missing file name in configuration.")

    # --- THE PATH FIX ---
    # 1. Get the folder this script is in (src/)
    # --- THE PATH FIX ---
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Automatically create the peer_100X folder if it doesn't exist!
    peer_dir = os.path.abspath(os.path.join(base_dir, '..', 'peers', f"peer_{_peer_id}"))
    if not os.path.exists(peer_dir):
        os.makedirs(peer_dir)
        
    _file_path = os.path.join(peer_dir, str(_file_name))
    
    # Auto-generate a dummy file for the seed if it is missing!
    if has_file and not os.path.exists(_file_path):
        print(f"\n[!] WARNING: Seed file missing. Auto-generating a {_file_size} byte dummy file for testing...")
        with open(_file_path, 'wb') as f:
            f.write(b'0' * _file_size)
    # --------------------
    
    # calculating how many pieces fit in the file
    _num_pieces = math.ceil(_file_size / _piece_size)
    # bits are true if the peer has the file, otherwise false
    global _bitfield
    _bitfield = [has_file] * _num_pieces


#function to check if we have a piece and return if true
def has_pieces(index):
    if index < 0 or index >= _num_pieces:
        raise IndexError("Piece index out of range")
    
    _lock.acquire()

    try:
        return _bitfield[index]
    finally:
        _lock.release()

#function to store a file in the correct spot
def store_pieces(index, data):
    if index < 0 or index >= _num_pieces:
        raise IndexError("Piece index out of range")
    if data is None or len(data) == 0:
        raise ValueError("Data is empty")

    #calculating where the piece should go
    offset = index * _piece_size

    _lock.acquire()

    #write the piece to the correct file
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

#function to obtain a file piece
def get_piece(index):
    if index < 0 or index >= _num_pieces:
        raise IndexError("Piece index out of range")
    
    #calculate where the piece will start in the file
    offset = index * _piece_size

    _lock.acquire()

    #read the correct piece
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

#function to determine what pieces are needed
def needed_pieces(neighbor_bitfield):
    if neighbor_bitfield is None:
        raise ValueError("neighbor_bitfield cannot be None")
    if len(neighbor_bitfield) != _num_pieces:
        raise ValueError(f"neighbor_bitfield length {len(neighbor_bitfield)} does not match expected {_num_pieces}")
    
    _lock.acquire()

    #check if a neighbor has a missing piece
    try:
        missing = []
        for i in range(_num_pieces):
            if neighbor_bitfield[i] and _bitfield[i] == False:
                missing.append(i)
        return missing
    finally:
        _lock.release()

#turn bitfield into bytes
def get_bitfield():
    num_bytes = math.ceil(_num_pieces / 8)
    result = bytearray(num_bytes)

    _lock.acquire()

    try:
        for i, has in enumerate(_bitfield):
            if has:
                byte_index = i // 8
                bit_pos = 7 - (i % 8)
                result[byte_index] |= (1 << bit_pos)
        return bytes(result)
    finally:
        _lock.release()

def parse_bitfield(data):
    if data is None or len(data) == 0:
        raise ValueError("Bitfield is empty")
    
    bits = []
    for byte in data:
        for bit_pos in range(7,-1,-1):
            bit_value = (byte >> bit_pos) & 1
            bits.append(bool(bit_value))

    return bits[:_num_pieces]

# check if the peer has downloaded the entire file
def is_complete():
    _lock.acquire()
    try:
        # If the bitfield hasn't been created yet, return False
        if not _bitfield: 
            return False
        # returns True if every piece in the bitfield is True
        return all(_bitfield)
    finally:
        _lock.release()
