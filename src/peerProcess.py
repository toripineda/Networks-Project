import socket
import threading
import sys
import time
from config_loader import load_common_config, load_peer_info
import choke_manager
import piece_manager
from logger import Logger
from connection import Connection

class PeerProcess:
    def __init__(self, peer_id):
        self.peer_id = int(peer_id)

        self.config = load_common_config()
        self.peer_info = load_peer_info()

        self.set_peer_info()
        piece_manager.init(self.peer_id, self.has_file, self.config)
        
        # Initialize the Logger
        self.logger = Logger(self.peer_id)
        
        self.connections = {}
        self.choke_manager = choke_manager.ChokeManager(self)
        self.choke_manager.start_times()

    def set_peer_info(self):
        for peer in self.peer_info:
            if peer['peer_id'] == self.peer_id:
                self.host = peer['host']
                self.port = peer['port']
                self.has_file = peer['has_file']
                return
        raise ValueError(f"Peer ID {self.peer_id} not found in peer info")
    
    def start_socket_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen()

        print(f"Peer {self.peer_id} is listening on {self.host}:{self.port}")
        while True:
            sock, address = server.accept()
            # Wrap the socket in our new Connection engine
            conn = Connection(sock, self)
            conn.start()

    def previous_peer_connections(self):
        for peer in self.peer_info:
            if peer['peer_id'] < self.peer_id:
                try:
                    skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    skt.connect((peer['host'], peer['port']))
                    self.logger.log_connection_to(peer['peer_id'])
                    
                    # Wrap the outgoing connection in our engine
                    conn = Connection(skt, self, peer['peer_id'])
                    conn.start()
                except Exception as e:
                    print(f"Peer {self.peer_id} failed to connect to peer {peer['peer_id']}: {e}")
                    
    def start(self):
        thread = threading.Thread(target=self.start_socket_server, daemon=True)
        thread.start()
        self.previous_peer_connections()
        
    def check_if_everyone_done(self):
        # 1. Do we have the complete file?
        if not piece_manager.is_complete(): return False
        
        # 2. Are we connected to everyone?
        if len(self.connections) != (len(self.peer_info) - 1): return False
        
        # 3. Do all our neighbors have the complete file?
        for conn in self.connections.values():
            if not all(conn.peer_bitfield): return False
            
        return True

def main():
    print("Starting peer process...")
    if len(sys.argv) != 2:
        print("Usage: python peerProcess.py <peer_id>")
        sys.exit(1)

    peer_id = int(sys.argv[1])
    peer = PeerProcess(peer_id)
    peer.start()
    print(f"Peer {peer_id} process started successfully.")
    
    # Termination Loop
    try:
        while True:
            time.sleep(2)
            if peer.check_if_everyone_done():
                print(f"SUCCESS: Peer {peer_id} and all neighbors have the complete file. Shutting down!")
                peer.choke_manager.stop_times()
                sys.exit(0)
    except KeyboardInterrupt:
        print(f"\nShutting down Peer {peer_id}...")
        sys.exit(0)

if __name__ == "__main__":
    main()