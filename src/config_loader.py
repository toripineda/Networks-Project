# This file reads Common.cg and PeerInfo.cfg, starts the peer process

"""

PeerInfo Structure: peerID hostName portNumber hasFile
1001 loclhost 6008 1

Common Structure: 
NumberOfPreferredNeighbors 2

"""
import os
import sys

def load_common_config():
    config = {}
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_dir = os.path.abspath(os.path.join(base_dir, '..', 'configs', 'small'))
    
    # Bypass Windows extensions: Find ANY file that starts with 'common'
    actual_filename = None
    if os.path.exists(config_dir):
        for f in os.listdir(config_dir):
            if f.lower().startswith('common'):
                actual_filename = f
                break

    if not actual_filename:
        print(f"\nCRITICAL ERROR: I looked in {config_dir} but couldn't find any file starting with 'Common'")
        sys.exit(1)

    config_path = os.path.join(config_dir, actual_filename)

    with open(config_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'): continue
            parts = line.split()
            if len(parts) >= 2:
                config[parts[0]] = " ".join(parts[1:])
    return config

def load_peer_info():
    peer_info = []
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_dir = os.path.abspath(os.path.join(base_dir, '..', 'configs', 'small'))
    
    # Bypass Windows extensions: Find ANY file that starts with 'peerinfo'
    actual_filename = None
    if os.path.exists(config_dir):
        for f in os.listdir(config_dir):
            if f.lower().startswith('peerinfo'):
                actual_filename = f
                break

    if not actual_filename:
        print(f"\nCRITICAL ERROR: I looked in {config_dir} but couldn't find any file starting with 'PeerInfo'")
        sys.exit(1)

    config_path = os.path.join(config_dir, actual_filename)

    with open(config_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'): continue
            parts = line.split()
            if len(parts) >= 4:
                peer_info.append({
                    'peer_id': int(parts[0]),
                    'host': parts[1],
                    'port': int(parts[2]),
                    'has_file': parts[3] == '1'
                })
    return peer_info