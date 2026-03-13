# logging events
import logging
import os
from datetime import datetime

class Logger:
    def __init__(self, peer_id):
        self.peer_id = peer_id
        self.log_file = f"logs/peer_{peer_id}.log"
        
        self.logger = logging.getLogger(f"Peer{peer_id}")
        self.logger.setLevel(logging.INFO)

        file_manager = logging.FileHandler(self.log_file)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        file_manager.setFormatter(formatter)
        self.logger.addHandler(file_manager)

    def log_connection_to(self, target_peer_id): 
        self.logger.info(f"Peer {self.peer_id} makes a connection to Peer {target_peer_id}.")

    def log_connection_from(self, target_peer_id):
        self.logger.info(f"Peer {self.peer_id} is connected from Peer {target_peer_id}.")

    def log_downloading_piece(self, remote_peer_id, piece_index, total_pieces):
        self.logger.info(f"Peer {self.peer_id} has downloaded the piece {piece_index} from {remote_peer_id}. "
                         f"Now the number of pieces it has is {total_pieces}.")
    
    def log_complete_file(self):
        self.logger.info(f"Peer {self.peer_id} has downloaded the complete file.")