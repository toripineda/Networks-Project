import threading
import time
import random

class ChokeManager:
    def __init__(self, peer_process):
        self.peer_process = peer_process
        
        # Load intervals and limits from the config
        self.num_preferred = int(peer_process.config.get('NumberOfPreferredNeighbors', 2))
        self.unchoke_interval = int(peer_process.config.get('UnchokingInterval', 5))
        self.opt_unchoke_interval = int(peer_process.config.get('OptimisticUnchokingInterval', 15))
        
        self.running = False
        self.preferred_peers = []
        self.optimistic_peer = None

    # Starts the background timers
    def start_times(self):
        self.running = True
        threading.Thread(target=self.run_choking, daemon=True).start()
        threading.Thread(target=self.run_interested, daemon=True).start()

    # Stops the timers when the file is completely downloaded
    def stop_times(self):
        self.running = False

    # Timer loop for preferred neighbors
    def run_choking(self):
        while self.running:
            time.sleep(self.unchoke_interval)
            if self.running:
                self.preferred_neighbors()

    # Timer loop for optimistic unchoking
    def run_interested(self):
        while self.running:
            time.sleep(self.opt_unchoke_interval)
            if self.running:
                self.interested_neighbors()

    # Core Algorithm: Pick the best peers to share data with
    def preferred_neighbors(self):
        # 1. Get a list of all connections that are currently INTERESTED in our data
        interested_conns = [c for c in self.peer_process.connections.values() if c.peer_interested]

        # 2. Sort or Shuffle to find the best ones
        if self.peer_process.has_file:
            # If we have the full file, we don't care about download speed. Pick randomly.
            random.shuffle(interested_conns)
            best_conns = interested_conns[:self.num_preferred]
        else:
            # If we are downloading, sort by who is giving us data the fastest
            # Note: We assume connection.py has a 'download_rate' attribute. If not, it falls back to 0.
            interested_conns.sort(key=lambda c: getattr(c, 'download_rate', 0), reverse=True)
            best_conns = interested_conns[:self.num_preferred]

        new_preferred = [c.peer_id for c in best_conns]

        # 3. Send CHOKE to peers who used to be preferred but didn't make the cut this time
        for peer_id in self.preferred_peers:
            if peer_id not in new_preferred and peer_id != self.optimistic_peer:
                conn = self.peer_process.connections.get(peer_id)
                if conn and not conn.choked:
                    conn.send_choke()
                    conn.choked = True

        # 4. Send UNCHOKE to the new winners
        for conn in best_conns:
            if conn.choked:
                conn.send_unchoke()
                conn.choked = False
        
        self.preferred_peers = new_preferred

    # Optimistic Algorithm: Randomly unchoke one choked peer
    def interested_neighbors(self):
        # Find peers that are INTERESTED but currently CHOKED
        candidates = [c for c in self.peer_process.connections.values() 
                      if c.peer_interested and c.peer_id not in self.preferred_peers]

        if candidates:
            # Pick one randomly
            winner = random.choice(candidates)
            self.optimistic_peer = winner.peer_id
            
            if winner.choked:
                winner.send_unchoke()
                winner.choked = False