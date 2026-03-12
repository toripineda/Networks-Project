# DOCUMENTATION for Group Structure & Getting Started

- Handshake Format:

- Message Structure:

- Peer States:

- Piece Selection:

# Order of Implementation, each part can be alternated between members
    Main Program (peerProcess) - Esther
1️⃣ Config file parsing - Esther
2️⃣ TCP connections - Annika & Esther
3️⃣ Handshake message - Anikka
4️⃣ Bitfield exchange - Tori
5️⃣ Interested / not interested
6️⃣ Request / piece transfer
7️⃣ Choking logic
8️⃣ Logging

# Runinng the three Peers
1. Open three terminals and run these commands in each:
    - python peerProcess.py 1001
    - python peerProcess.py 1002
    - python peerProcess.py 1003

Exected Output (which shows that the configs load, the socket work, and the peers connect)
Peer 1001 listening on 6001
Peer 1002 listening on 6002
Connected to peer 1001
Peer 1003 listening on 6003
Connected to peer 1001
Connected to peer 1002