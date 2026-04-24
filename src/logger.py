# logging events
import logging
import os
from datetime import datetime

class Logger:
    def __init__(self, peer_id):
        self.peer_id = peer_id
        
        # 1. Get the directory where logger.py lives (src/)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 2. Step UP one level, then into the 'logs' folder
        log_dir = os.path.abspath(os.path.join(base_dir, '..', 'logs'))
        
        # 3. CRITICAL FIX: Automatically create the 'logs' folder if it is missing!
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        # 4. Define the exact file path (matches the project description format)
        self.log_file = os.path.join(log_dir, f"log_peer_{peer_id}.log")
        
        self.logger = logging.getLogger(f"Peer{peer_id}")
        self.logger.setLevel(logging.INFO)

        # Prevent duplicate logs from printing multiple times
        if not self.logger.handlers:
            # Writes to the .log file
            file_manager = logging.FileHandler(self.log_file)
            formatter = logging.Formatter('%(asctime)s - %(message)s')
            file_manager.setFormatter(formatter)
            self.logger.addHandler(file_manager)

            # --- ADD THIS: Prints to the Console! ---
            import sys
            console_manager = logging.StreamHandler(sys.stdout)
            console_manager.setFormatter(formatter)
            self.logger.addHandler(console_manager)
            # ----------------------------------------

    def log_connection_to(self, target_peer_id): 
        self.logger.info(f"Peer {self.peer_id} makes a connection to Peer {target_peer_id}.")

    def log_connection_from(self, target_peer_id):
        self.logger.info(f"Peer {self.peer_id} is connected from Peer {target_peer_id}.")

    def log_downloading_piece(self, remote_peer_id, piece_index, total_pieces):
        self.logger.info(f"Peer {self.peer_id} has downloaded the piece {piece_index} from {remote_peer_id}. "
                         f"Now the number of pieces it has is {total_pieces}.")
    
    def log_complete_file(self):
        self.logger.info(f"Peer {self.peer_id} has downloaded the complete file.")