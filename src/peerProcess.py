# main program
import socket
import threading
import sys
from config_loader import load_common_config, load_peer_info
import choke_manager
import piece_manager
import message
import logger

class PeerProcess:
    def __init__(self, peer_id):
        self.peer_id = int(peer_id)

        # loading the configuration and peer information
        self.config = load_common_config()
        self.peer_info = load_peer_info()

        self.set_peer_info()
        # self.host, self.port, self.has_file = self.load_peer_info()

    # set info from config
    def set_peer_info(self):
        for peer in self.peer_info:
            if peer['peer_id'] == self.peer_id:
                self.host = peer['host']
                self.port = peer['port']
                self.has_file = peer['has_file']
                return
        raise ValueError(f"Peer ID {self.peer_id} not found in peer info")
    
    # starting the server socket to listen for incoming connections
    def start_socket_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen()

        print(f"Peer {self.peer_id} is listening on {self.host}:{self.port}")
        while True:
            connection, address = server.accept()
            print("\nConnection has been received")
            print("-" * 50)
            print(f"Peer {self.peer_id} accepted connection from {address}")

        # TODO: message handling goes here

    # musut connect peers to peers listed before it
    def previous_peer_connections(self):
        for peer in self.peer_info:
            if peer['peer_id'] < self.peer_id:
                try:
                    skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    skt.connect((peer['host'], peer['port']))
                    print(f"Peer {self.peer_id} connected to peer {peer['peer_id']} at {peer['host']}:{peer['port']}")
                except Exception as e:
                    print(f"Peer {self.peer_id} failed to connect to peer {peer['peer_id']} at {peer['host']}:{peer['port']}: {e}")

                    
    def start(self):
        thread = threading.Thread(target=self.start_socket_server, daemon=True)
        thread.start()

        self.previous_peer_connections()

    # TODO: finish implementing the connection peer class and the choke manager and piece manager classes later
    # self.logger = Logger(peer_id)
    # self.piece_manager = PieceManager(self.peer_id, self.config)
    # self.choke_manager = ChokeManager(self)
    # self.connections = {}
        

def main():
    print("Starting peer process...")
    if len(sys.argv) != 2:
        print("Usage: python peerProcess.py <peer_id>")
        sys.exit(1)

    peer_id = int(sys.argv[1])
    config = load_common_config()
    peer_info = load_peer_info()

    # Initialize components
    # logger = Logger(peer_id)
    # piece_manager = PieceManager(config['file_name'], config['piece_size'])
    # choke_manager = ChokeManager(config['num_preferred_neighbors'])
    
    # Start peer process
    connection_peer = PeerProcess(peer_id)
    connection_peer.start()
    print(f"Peer {peer_id} process started successfully.")
if __name__ == "__main__":
    main()
