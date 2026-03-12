# message encoding and decoding
#encode_message()
#decode_message()
#create_handshake()

import struct

#format as given by report
CHOKE = 0
UNCHOKE = 1
INTERESTED = 2
NOT_INTERESTED = 3
HAVE = 4
BITFIELD = 5 
REQUEST = 6
PIECE = 7

#the valid message types set (for validation)
VALID_MESSAGE_TYPES = {
    CHOKE,
    UNCHOKE,
    INTERESTED,
    NOT_INTERESTED,
    HAVE,
    BITFIELD,
    REQUEST,
    PIECE,
}

#The handshake constants
#every tcp starts with handshake
#FROM INSTRUCTIONS 
#format- 32 byte total : 18, 10, 4
HANDSHAKE_HEADER = b"P2PFILESHARINGPROJ"
ZERO_BITS = b"\x00" * 10
HANDSHAKE_LENGTH = 32

HANDSHAKE_HEADER_LENGTH = 18
ZERO_BITS_LENGTH = 10
PEER_ID_LENGTH = 4


#validation function helpers
#ensure messages are correct
def validate_peer_id(peer_id):
    if not isinstance(peer_id, int):
        raise TypeError("Peer ID must be an integer")

    if peer_id < 0:
        raise ValueError("Peer ID must be non-negative")

def validate_payload(payload):
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError("Payload must be bytes or bytearray")
    
def validate_message_type(message_type):
    if message_type not in VALID_MESSAGE_TYPES:
        raise ValueError(f"Invalid message type: {message_type}")

def pack_peer_id(peer_id):
    validate_peer_id(peer_id)
    peer_id_bytes = struct.pack(">I", peer_id)
    return peer_id_bytes

def unpack_peer_id(peer_id_bytes):

    if len(peer_id_bytes) != PEER_ID_LENGTH:
        raise ValueError("Peer ID must be exactly 4 bytes")

    peer_id = struct.unpack(">I", peer_id_bytes)[0]
    return peer_id

def encode_message(message_type, payload=b""):
    validate_message_type(message_type)
    validate_payload(payload)

    payload_length = len(payload)
    message_length = 1 + payload_length

    length_bytes = struct.pack(">I", message_length)
    type_bytes = struct.pack(">B", message_type)

    encoded_message = length_bytes + type_bytes + payload
    return encoded_message

def decode_message(data):
    if len(data) < 5:
        raise ValueError("Message too short")
    
    message_length = struct.unpack(">I", data[:4])[0]
    message_type = struct.unpack(">B", data[4:5])[0]
    payload = data[5:]


    if len(payload) !=message_length -1:
        raise ValueError("The payload doesn't match the message length")
    
    return message_length, message_type, payload

#this is the first message sent after the two peers connect
def create_handshake(peer_id):
    validate_peer_id(peer_id)

    header = HANDSHAKE_HEADER
    zero_bytes = ZERO_BITS
    peer_id_bytes = pack_peer_id(peer_id)

    handshake = header + zero_bytes + peer_id_bytes
    return handshake


#this function decodes a recieved message and works with helper
def decode_handshake(data):
    if len(data) != HANDSHAKE_LENGTH:
        raise ValueError("The handshake should be exactly 32 bytes")

    header_end = HANDSHAKE_HEADER_LENGTH
    zero_end = header_end + ZERO_BITS_LENGTH

    header = data[:header_end]
    zero_bytes =data[header_end:zero_end]
    peer_id_bytes = data[zero_end:]

    if header !=HANDSHAKE_HEADER:
        raise ValueError("handshake header is wrong")

    if zero_bytes != ZERO_BITS:
        raise ValueError("Invalid handshake zero bits")

    peer_id = unpack_peer_id(peer_id_bytes)
    return peer_id


def create_index_payload(piece_index):
    return struct.pack(">I", piece_index)

def parse_index_payload(payload):
    if len(payload) != 4:
        raise ValueError("The index payload has to be 4 bytes")
    return struct.unpack(">I", payload)[0]

def create_piece_payload(piece_index, piece_data):
    return struct.pack(">I", piece_index) + piece_data

def parse_piece_payload(payload):
    if len(payload) < 4:
        raise ValueError("Piece payload too short")

    piece_index = struct.unpack(">I", payload[:4])[0]
    piece_data = payload[4:]
    return piece_index, piece_data


        