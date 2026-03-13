# TCP connections

import socket
import threading 
import struct

from message import (
    create_handshake,
    decode_handshake,
    encode_message,
    decode_message, 
    BITFIELD, 
    INTERESTED,
    NOT_INTERESTED,
)


class ConnectionPeer:
    def __init__(self, peer_id, peer_info, piece_manager, choke_manager, logger):
        self.peer_id = peer_id
        self.peer_info = peer_info
        self.piece_manager = piece_manager
        self.choke_manager = choke_manager
        self.logger = logger

        self.server_socket = None

        #We need to map the neighor peerID to socket
        self.connections = {}

        #We need to also map the neighbor peer id to the last known bitfield
        self.neightbor_bitfields = {}

        self.host, self.port, self.has_file = self.get_my_info()
        #need to implement get info funct

    def get_my_info(self):
        #find peers info from config
        #expected format is peerid (host, port, has_file)
    
        for peer in self.peer_info:
            if int(peer["peer_id"]) ==self.peer_id:
                return peer["host"], int(peer["port"]), int(peer["has_file"])
            
        raise ValueError("This peer id {self.peer_id} cant be found in config")
    
    #this is how we start a peer
    #first wt listner thread thenw e want to conn to earlier peers
    def start(self):
        self.start_server()

        listener_thread = threading.Thread(target=self.accept_connections, daemon=True)
        listener_thread.start()

        self.connect_to_previous_peers()


