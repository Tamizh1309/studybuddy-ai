# Computer Networks: Architecture, Protocols & The Transport Layer

## 1. Network Layered Architecture
Computer networks are organized into modular hierarchical layers:
- **OSI 7-Layer Model**: Physical, Data Link, Network, Transport, Session, Presentation, Application.
- **TCP/IP 4-Layer Model**: Network Access, Internet (IP, ICMP, ARP), Transport (TCP, UDP), Application (HTTP, DNS, SSH, SMTP).

## 2. The Transport Layer: TCP vs UDP
- **Transmission Control Protocol (TCP)**:
  - Connection-oriented protocol providing reliable, ordered, and error-checked delivery of octets.
  - Three-Way Handshake: SYN -> SYN-ACK -> ACK.
  - Flow Control: Uses Sliding Window protocol to prevent receiver buffer overflow.
  - Congestion Control: Algorithms include Slow Start, Congestion Avoidance (AIMD - Additive Increase Multiplicative Decrease), Fast Retransmit, and Fast Recovery.
- **User Datagram Protocol (UDP)**:
  - Connectionless, lightweight, and fast protocol with no delivery guarantees or ordering.
  - Used for real-time applications: DNS queries, VoIP, video streaming, and online gaming.

## 3. The Internet Protocol (IPv4 & IPv6)
- **IPv4**: 32-bit addresses written in dotted-decimal format (e.g., 192.168.1.1). Subnetting uses CIDR notation.
- **IPv6**: 128-bit addresses written in hexadecimal colon format, resolving IPv4 address exhaustion and providing native IPsec support.
- **Routing Algorithms**:
  - Distance Vector Routing (Bellman-Ford Algorithm, RIP).
  - Link State Routing (Dijkstra's Shortest Path First, OSPF).
  - Border Gateway Protocol (BGP) for Inter-Autonomous System path vector routing.
