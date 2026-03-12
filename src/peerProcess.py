# main program
import socket
import threading
import sys
from config_loader import load_config, load_peer_info
from connectionPeer import ConnectionPeer
from choke_manager import ChokeManager
from piece_manager import PieceManager
from logger import Logger

class PeerProcess:
    def __init__(self, peer_id):
        self.peer_id = int(peer_id)
        self.config = load_config()
        self.peer_info = load_peer_info()
        self.logger = Logger(peer_id)
        self.piece_manager = PieceManager(self.peer_id, self.config)
        self.choke_manager = ChokeManager(self)
        self.connections = {}
        # self.host, self.port, self.has_file = self.get_peer_info()



def main():
    if len(sys.argv) != 2:
        print("Usage: python peerProcess.py <peer_id>")
        sys.exit(1)

    peer_id = int(sys.argv[1])
    config = load_config()
    peer_info = load_peer_info()

    # Initialize components
    logger = Logger(peer_id)
    piece_manager = PieceManager(config['file_name'], config['piece_size'])
    choke_manager = ChokeManager(config['num_preferred_neighbors'])
    
    # Start peer process
    connection_peer = ConnectionPeer(peer_id, peer_info, piece_manager, choke_manager, logger)
    connection_peer.start()