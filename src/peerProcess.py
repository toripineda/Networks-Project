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
        piece_manager.init(self.peer_id, self.has_file, self.config)

        # Initialize connections dictionary and choke manager
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
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind((self.host, self.port))
            server.listen()

            print(f"Peer {self.peer_id} is listening on {self.host}:{self.port}")
            while True:
                connection, address = server.accept()
                print("\nConnection has been received")
                print("-" * 50)
                print(f"Peer {self.peer_id} accepted connection from {address}")
        except Exception as e:
            print(f"Peer {self.peer_id} server error: {e}")

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
        self.server_thread = threading.Thread(target=self.start_socket_server)
        self.server_thread.start()

        self.previous_peer_connections()


def main():
    print("Starting peer process...")
    if len(sys.argv) != 2:
        print("Usage: python peerProcess.py <peer_id>")
        sys.exit(1)

    peer_id = int(sys.argv[1])

    connection_peer = PeerProcess(peer_id)
    connection_peer.start()
    print(f"Peer {peer_id} process started successfully.")

    connection_peer.server_thread.join()


if __name__ == "__main__":
    main()