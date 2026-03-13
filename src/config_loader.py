# This file reads Common.cg and PeerInfo.cfg, starts the peer process

"""

PeerInfo Structure: peerID hostName portNumber hasFile
1001 loclhost 6008 1

Common Structure: 
NumberOfPreferredNeighbors 2

"""

# load configuration from Common.cfg into dictionary
def load_common_config(filename="../configs/small/Common.cfg"):
    common = {}

    with open(filename, 'r') as file:
        for line in file:

            cfg = line.strip().split()
            if len(common) != 2:
                continue
            key = cfg[0]
            value = cfg[1]

            if value.isdigit():
                value = int(value)
            common[key] = value
    
    return common
            
# load peer information from PeerInfo.cfg into list of dictionaries
def load_peer_info(filename="../configs/small/PeerInfo_test.cfg"):
    peer_info = []

    with open(filename, 'r') as file:
        for line in file:
            peer = line.strip().split()

            if len(peer) != 4:
                continue

            peer_id = int(peer[0])
            host_name = peer[1]
            port_number = int(peer[2])
            has_file = bool(int(peer[3]))

            peer_info.append({
                "peer_id": peer_id,
                "host": host_name,
                "port": port_number,
                "has_file": has_file
            })

    return peer_info