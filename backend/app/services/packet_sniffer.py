"""Packet sniffer for live network monitoring."""
import threading
from typing import Callable, Optional
from datetime import datetime

try:
    from scapy.all import sniff, IP, TCP, UDP, ICMP
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    print("Warning: scapy not available. Install with: pip install scapy")


class PacketSniffer:
    """Packet sniffer that captures packets and feeds them to a flow manager."""
    
    def __init__(self, interface: str, flow_manager, on_flow_complete: Callable):
        self.interface = interface
        self.flow_manager = flow_manager
        self.on_flow_complete = on_flow_complete
        self._running = False
        self._sniff_thread: Optional[threading.Thread] = None
        self._packet_count = 0
        self._processed_count = 0
        self._last_error: Optional[str] = None
    
    def start(self):
        """Start packet sniffing."""
        if not SCAPY_AVAILABLE:
            raise RuntimeError("scapy is not installed. Install with: pip install scapy")
        
        if self._running:
            return
        
        self._running = True
        self._sniff_thread = threading.Thread(target=self._sniff_loop, daemon=True)
        self._sniff_thread.start()
        print(f"✓ Started packet sniffer on interface: {self.interface}")
    
    def stop(self):
        """Stop packet sniffing."""
        self._running = False
        if self._sniff_thread:
            self._sniff_thread.join(timeout=2)
    
    def _sniff_loop(self):
        """Main sniffing loop."""
        try:
            # Check if interface exists before starting
            from scapy.all import get_if_list
            available_interfaces = get_if_list()
            if self.interface not in available_interfaces:
                print(f"⚠ Warning: Interface '{self.interface}' not found. Available interfaces: {available_interfaces}")
                print(f"   Sniffer will continue but may fail. Consider setting INTERFACE_NAME to a valid interface.")
            
            sniff(
                iface=self.interface,
                prn=self._process_packet,
                store=False,
                stop_filter=lambda x: not self._running,
            )
        except OSError as e:
            # Handle permission/interface errors gracefully
            error_msg = str(e)
            self._last_error = error_msg
            if "BIOCSETIF" in error_msg or "Operation not permitted" in error_msg:
                print(f"⚠ Permission error: Cannot access interface '{self.interface}'")
                print(f"   Run with sudo or grant network permissions to your terminal/IDE.")
                print(f"   Example: sudo uvicorn app.main:app --reload")
            else:
                print(f"⚠ Interface error: {error_msg}")
            self._running = False
        except Exception as e:
            error_msg = str(e)
            self._last_error = error_msg
            print(f"⚠ Error in packet sniffer: {error_msg}")
            import traceback
            traceback.print_exc()
            self._running = False
    
    def _process_packet(self, packet):
        """Process a single packet."""
        if not self._running:
            return
        
        self._packet_count += 1
        
        try:
            # Extract IP layer
            if IP not in packet:
                return
            
            ip_layer = packet[IP]
            src_ip = ip_layer.src
            dst_ip = ip_layer.dst
            protocol = "Unknown"
            src_port = 0
            dst_port = 0
            
            # Extract protocol and ports
            if TCP in packet:
                protocol = "TCP"
                tcp_layer = packet[TCP]
                src_port = tcp_layer.sport
                dst_port = tcp_layer.dport
                flags = {
                    'FIN': bool(tcp_layer.flags & 0x01),
                    'SYN': bool(tcp_layer.flags & 0x02),
                    'RST': bool(tcp_layer.flags & 0x04),
                    'PSH': bool(tcp_layer.flags & 0x08),
                    'ACK': bool(tcp_layer.flags & 0x10),
                    'URG': bool(tcp_layer.flags & 0x20),
                    'ECE': bool(tcp_layer.flags & 0x40),
                    'CWE': bool(tcp_layer.flags & 0x80),
                }
                window_size = tcp_layer.window
            elif UDP in packet:
                protocol = "UDP"
                udp_layer = packet[UDP]
                src_port = udp_layer.sport
                dst_port = udp_layer.dport
                flags = {}
                window_size = 0
            elif ICMP in packet:
                protocol = "ICMP"
                flags = {}
                window_size = 0
            else:
                return  # Skip non-TCP/UDP/ICMP
            
            # Determine direction (simplified: assume first packet is forward)
            # In a real system, you'd track connection state
            direction = "forward" if src_port < dst_port or src_ip < dst_ip else "backward"
            
            # Calculate packet size
            packet_size = len(packet)
            header_size = len(ip_layer) - (len(ip_layer.payload) if hasattr(ip_layer, 'payload') else 0)
            
            # Build packet info
            packet_info = {
                'direction': direction,
                'size': packet_size,
                'header_size': header_size,
                'flags': flags,
                'timestamp': datetime.utcnow(),
                'window_size': window_size,
            }
            
            # Add to flow manager
            self.flow_manager.add_packet(
                src_ip, dst_ip, src_port, dst_port, protocol, packet_info
            )
            self._processed_count += 1
            
            # Log first few packets for debugging
            if self._processed_count <= 5:
                print(f"  [Sniffer] Processed packet #{self._processed_count}: {src_ip}:{src_port} -> {dst_ip}:{dst_port} ({protocol})")
        
        except Exception as e:
            # Log errors for debugging
            if self._packet_count <= 10:
                print(f"  [Sniffer] Error processing packet: {e}")
            self._last_error = str(e)
    
    def get_stats(self):
        """Get sniffer statistics."""
        return {
            "packet_count": self._packet_count,
            "processed_count": self._processed_count,
            "last_error": self._last_error,
        }

