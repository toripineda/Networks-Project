import socket
import threading
import struct
import random
import message
import piece_manager

# Helper function to ensure we read EXACTLY the right amount of bytes over TCP
def recvall(sock, n):
    data = bytearray()
    while len(data) < n:
        try:
            packet = sock.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        except:
            return None
    return bytes(data)

class Connection:
    def __init__(self, sock, peer_process, remote_peer_id=None):
        self.sock = sock
        self.peer_process = peer_process
        self.remote_peer_id = remote_peer_id
        
        self.choked = True
        self.peer_interested = False
        self.peer_bitfield = [False] * piece_manager._num_pieces
        self.running = True

    def start(self):
        threading.Thread(target=self.run, daemon=True).start()

    def send_message(self, msg_type, payload=b""):
        # 4-byte length + 1-byte type + payload
        length = 1 + len(payload)
        msg = struct.pack(">I", length) + struct.pack(">B", msg_type) + payload
        self.sock.sendall(msg)

    def run(self):
        try:
            # 1. Exchange Handshakes
            hs_out = message.create_handshake(self.peer_process.peer_id)
            self.sock.sendall(hs_out)
            
            hs_in = recvall(self.sock, 32)
            if not hs_in: return
            
            self.remote_peer_id = message.decode_handshake(hs_in)
            self.peer_process.connections[self.remote_peer_id] = self
            
            # Log connection from (if we accepted it)
            if self.remote_peer_id > self.peer_process.peer_id:
                self.peer_process.logger.logger.info(f"Peer {self.peer_process.peer_id} is connected from Peer {self.remote_peer_id}.")

            # 2. Send our bitfield (if we have pieces)
            bf = piece_manager.get_bitfield()
            if any(piece_manager._bitfield):
                self.send_message(message.BITFIELD, bf)

            # 3. Main Message Loop
            while self.running:
                length_data = recvall(self.sock, 4)
                if not length_data: break
                msg_length = struct.unpack(">I", length_data)[0]

                if msg_length == 0: continue # Keep-alive message

                type_data = recvall(self.sock, 1)
                msg_type = struct.unpack(">B", type_data)[0]

                payload_length = msg_length - 1
                payload = recvall(self.sock, payload_length) if payload_length > 0 else b""

                self.handle_message(msg_type, payload)

        except Exception as e:
            print(f"\n[!] Connection Error with Peer {self.remote_peer_id}: {repr(e)}")
        finally:
            self.running = False
            if self.remote_peer_id in self.peer_process.connections:
                del self.peer_process.connections[self.remote_peer_id]

    def handle_message(self, msg_type, payload):
        log = self.peer_process.logger.logger
        my_id = self.peer_process.peer_id
        
        if msg_type == message.CHOKE:
            log.info(f"Peer {my_id} is choked by {self.remote_peer_id}.")
            self.choked = True
            
        elif msg_type == message.UNCHOKE:
            log.info(f"Peer {my_id} is unchoked by {self.remote_peer_id}.")
            self.choked = False
            self.request_random_piece()
            
        elif msg_type == message.INTERESTED:
            log.info(f"Peer {my_id} received the 'interested' message from {self.remote_peer_id}.")
            self.peer_interested = True
            
        elif msg_type == message.NOT_INTERESTED:
            log.info(f"Peer {my_id} received the 'not interested' message from {self.remote_peer_id}.")
            self.peer_interested = False
            
        elif msg_type == message.HAVE:
            index = message.parse_index_payload(payload)
            log.info(f"Peer {my_id} received the 'have' message from {self.remote_peer_id} for the piece {index}.")
            self.peer_bitfield[index] = True
            self.check_if_interested()
            
        elif msg_type == message.BITFIELD:
            self.peer_bitfield = piece_manager.parse_bitfield(payload)
            self.check_if_interested()
            
        elif msg_type == message.REQUEST:
            index = message.parse_index_payload(payload)
            if not self.choked:
                data = piece_manager.get_piece(index)
                piece_payload = message.create_index_payload(index) + data
                self.send_message(message.PIECE, piece_payload)
                
        elif msg_type == message.PIECE:
            index = struct.unpack(">I", payload[:4])[0]
            data = payload[4:]
            
            # Save data and check completion
            was_complete = piece_manager.is_complete()
            piece_manager.store_pieces(index, data)
            
            total_pieces = sum(1 for x in piece_manager._bitfield if x)
            log.info(f"Peer {my_id} has downloaded the piece {index} from {self.remote_peer_id}. Now the number of pieces it has is {total_pieces}.")

            # Broadcast to everyone else that we now have this piece
            for conn in self.peer_process.connections.values():
                conn.send_message(message.HAVE, message.create_index_payload(index))
                conn.check_if_interested()

            if piece_manager.is_complete() and not was_complete:
                log.info(f"Peer {my_id} has downloaded the complete file.")

            if not self.choked:
                self.request_random_piece()

    def check_if_interested(self):
        needed = piece_manager.needed_pieces(self.peer_bitfield)
        if needed:
            self.send_message(message.INTERESTED)
        else:
            self.send_message(message.NOT_INTERESTED)

    def request_random_piece(self):
        needed = piece_manager.needed_pieces(self.peer_bitfield)
        if needed:
            index = random.choice(needed)
            self.send_message(message.REQUEST, message.create_index_payload(index))
            
    def send_choke(self):
        self.send_message(message.CHOKE)
        
    def send_unchoke(self):
        self.send_message(message.UNCHOKE)