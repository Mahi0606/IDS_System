"""Flow manager for aggregating packets into flows."""
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import threading
import time


class Flow:
    """Represents a network flow (5-tuple)."""
    
    def __init__(self, src_ip: str, dst_ip: str, src_port: int, dst_port: int, protocol: str):
        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.src_port = src_port
        self.dst_port = dst_port
        self.protocol = protocol
        
        # Statistics
        self.total_fwd_packets = 0
        self.total_backward_packets = 0
        self.total_fwd_bytes = 0
        self.total_bwd_bytes = 0
        
        # Packet lengths
        self.fwd_packet_lengths = []
        self.bwd_packet_lengths = []
        
        # Timestamps
        self.first_seen = datetime.utcnow()
        self.last_seen = datetime.utcnow()
        self.fwd_timestamps = []
        self.bwd_timestamps = []
        
        # Flags
        self.fwd_psh_flags = 0
        self.fwd_urg_flags = 0
        self.fin_flags = 0
        self.syn_flags = 0
        self.rst_flags = 0
        self.psh_flags = 0
        self.ack_flags = 0
        self.urg_flags = 0
        self.cwe_flags = 0
        self.ece_flags = 0
        
        # Header lengths
        self.fwd_header_length = 0
        self.bwd_header_length = 0
        
        # Window sizes
        self.init_win_bytes_forward = 0
        self.init_win_bytes_backward = 0
        
        # Additional stats
        self.act_data_pkt_fwd = 0
        self.min_seg_size_forward = 0
        
        # Subflow stats
        self.subflow_fwd_packets = 0
        self.subflow_fwd_bytes = 0
        self.subflow_bwd_packets = 0
        self.subflow_bwd_bytes = 0
        
        # Active/Idle times (simplified - would need more complex tracking)
        self.active_times = []
        self.idle_times = []
    
    def add_packet(self, packet_info: Dict):
        """Add a packet to this flow."""
        direction = packet_info.get('direction', 'forward')  # 'forward' or 'backward'
        packet_size = packet_info.get('size', 0)
        header_size = packet_info.get('header_size', 0)
        flags = packet_info.get('flags', {})
        timestamp = packet_info.get('timestamp', datetime.utcnow())
        window_size = packet_info.get('window_size', 0)
        
        if direction == 'forward':
            self.total_fwd_packets += 1
            self.total_fwd_bytes += packet_size
            self.fwd_packet_lengths.append(packet_size)
            self.fwd_timestamps.append(timestamp)
            self.fwd_header_length += header_size
            if self.init_win_bytes_forward == 0:
                self.init_win_bytes_forward = window_size
        else:
            self.total_backward_packets += 1
            self.total_bwd_bytes += packet_size
            self.bwd_packet_lengths.append(packet_size)
            self.bwd_timestamps.append(timestamp)
            self.bwd_header_length += header_size
            if self.init_win_bytes_backward == 0:
                self.init_win_bytes_backward = window_size
        
        # Update flags
        if flags.get('PSH'):
            self.psh_flags += 1
            if direction == 'forward':
                self.fwd_psh_flags += 1
        if flags.get('URG'):
            self.urg_flags += 1
            if direction == 'forward':
                self.fwd_urg_flags += 1
        if flags.get('FIN'):
            self.fin_flags += 1
        if flags.get('SYN'):
            self.syn_flags += 1
        if flags.get('RST'):
            self.rst_flags += 1
        if flags.get('ACK'):
            self.ack_flags += 1
        if flags.get('CWE'):
            self.cwe_flags += 1
        if flags.get('ECE'):
            self.ece_flags += 1
        
        self.last_seen = timestamp
    
    def to_feature_dict(self) -> Dict:
        """Convert flow to feature dictionary matching FEATURE_COLUMNS."""
        import numpy as np
        
        flow_duration = (self.last_seen - self.first_seen).total_seconds() * 1000000  # microseconds
        
        # Calculate statistics
        fwd_packet_lengths = np.array(self.fwd_packet_lengths) if self.fwd_packet_lengths else np.array([0])
        bwd_packet_lengths = np.array(self.bwd_packet_lengths) if self.bwd_packet_lengths else np.array([0])
        all_packet_lengths = np.concatenate([fwd_packet_lengths, bwd_packet_lengths]) if len(fwd_packet_lengths) > 0 or len(bwd_packet_lengths) > 0 else np.array([0])
        
        # IAT (Inter-Arrival Time) calculations
        fwd_iat = np.diff([ts.timestamp() for ts in self.fwd_timestamps]) * 1000000 if len(self.fwd_timestamps) > 1 else np.array([0])
        bwd_iat = np.diff([ts.timestamp() for ts in self.bwd_timestamps]) * 1000000 if len(self.bwd_timestamps) > 1 else np.array([0])
        all_iat = np.concatenate([fwd_iat, bwd_iat]) if len(fwd_iat) > 0 or len(bwd_iat) > 0 else np.array([0])
        
        # Flow rates
        flow_bytes_per_s = (self.total_fwd_bytes + self.total_bwd_bytes) / flow_duration * 1000000 if flow_duration > 0 else 0
        flow_packets_per_s = (self.total_fwd_packets + self.total_backward_packets) / flow_duration * 1000000 if flow_duration > 0 else 0
        
        # Build feature dictionary
        features = {
            'Destination Port': self.dst_port,
            'Flow Duration': int(flow_duration),
            'Total Fwd Packets': self.total_fwd_packets,
            'Total Backward Packets': self.total_backward_packets,
            'Total Length of Fwd Packets': self.total_fwd_bytes,
            'Total Length of Bwd Packets': self.total_bwd_bytes,
            'Fwd Packet Length Max': int(fwd_packet_lengths.max()) if len(fwd_packet_lengths) > 0 else 0,
            'Fwd Packet Length Min': int(fwd_packet_lengths.min()) if len(fwd_packet_lengths) > 0 else 0,
            'Fwd Packet Length Mean': float(fwd_packet_lengths.mean()) if len(fwd_packet_lengths) > 0 else 0.0,
            'Fwd Packet Length Std': float(fwd_packet_lengths.std()) if len(fwd_packet_lengths) > 0 else 0.0,
            'Bwd Packet Length Max': int(bwd_packet_lengths.max()) if len(bwd_packet_lengths) > 0 else 0,
            'Bwd Packet Length Min': int(bwd_packet_lengths.min()) if len(bwd_packet_lengths) > 0 else 0,
            'Bwd Packet Length Mean': float(bwd_packet_lengths.mean()) if len(bwd_packet_lengths) > 0 else 0.0,
            'Bwd Packet Length Std': float(bwd_packet_lengths.std()) if len(bwd_packet_lengths) > 0 else 0.0,
            'Flow Bytes/s': flow_bytes_per_s if not np.isinf(flow_bytes_per_s) and not np.isnan(flow_bytes_per_s) else 0.0,
            'Flow Packets/s': flow_packets_per_s if not np.isinf(flow_packets_per_s) and not np.isnan(flow_packets_per_s) else 0.0,
            'Flow IAT Mean': float(all_iat.mean()) if len(all_iat) > 0 else 0.0,
            'Flow IAT Std': float(all_iat.std()) if len(all_iat) > 0 else 0.0,
            'Flow IAT Max': int(all_iat.max()) if len(all_iat) > 0 else 0,
            'Flow IAT Min': int(all_iat.min()) if len(all_iat) > 0 else 0,
            'Fwd IAT Total': int(fwd_iat.sum()) if len(fwd_iat) > 0 else 0,
            'Fwd IAT Mean': float(fwd_iat.mean()) if len(fwd_iat) > 0 else 0.0,
            'Fwd IAT Std': float(fwd_iat.std()) if len(fwd_iat) > 0 else 0.0,
            'Fwd IAT Max': int(fwd_iat.max()) if len(fwd_iat) > 0 else 0,
            'Fwd IAT Min': int(fwd_iat.min()) if len(fwd_iat) > 0 else 0,
            'Bwd IAT Total': int(bwd_iat.sum()) if len(bwd_iat) > 0 else 0,
            'Bwd IAT Mean': float(bwd_iat.mean()) if len(bwd_iat) > 0 else 0.0,
            'Bwd IAT Std': float(bwd_iat.std()) if len(bwd_iat) > 0 else 0.0,
            'Bwd IAT Max': int(bwd_iat.max()) if len(bwd_iat) > 0 else 0,
            'Bwd IAT Min': int(bwd_iat.min()) if len(bwd_iat) > 0 else 0,
            'Fwd PSH Flags': self.fwd_psh_flags,
            'Fwd URG Flags': self.fwd_urg_flags,
            'Fwd Header Length': self.fwd_header_length,
            'Bwd Header Length': self.bwd_header_length,
            'Fwd Packets/s': self.total_fwd_packets / flow_duration * 1000000 if flow_duration > 0 else 0.0,
            'Bwd Packets/s': self.total_backward_packets / flow_duration * 1000000 if flow_duration > 0 else 0.0,
            'Min Packet Length': int(all_packet_lengths.min()) if len(all_packet_lengths) > 0 else 0,
            'Max Packet Length': int(all_packet_lengths.max()) if len(all_packet_lengths) > 0 else 0,
            'Packet Length Mean': float(all_packet_lengths.mean()) if len(all_packet_lengths) > 0 else 0.0,
            'Packet Length Std': float(all_packet_lengths.std()) if len(all_packet_lengths) > 0 else 0.0,
            'Packet Length Variance': float(all_packet_lengths.var()) if len(all_packet_lengths) > 0 else 0.0,
            'FIN Flag Count': self.fin_flags,
            'SYN Flag Count': self.syn_flags,
            'RST Flag Count': self.rst_flags,
            'PSH Flag Count': self.psh_flags,
            'ACK Flag Count': self.ack_flags,
            'URG Flag Count': self.urg_flags,
            'CWE Flag Count': self.cwe_flags,
            'ECE Flag Count': self.ece_flags,
            'Down/Up Ratio': self.total_fwd_packets / self.total_backward_packets if self.total_backward_packets > 0 else 0,
            'Average Packet Size': float(all_packet_lengths.mean()) if len(all_packet_lengths) > 0 else 0.0,
            'Avg Fwd Segment Size': float(fwd_packet_lengths.mean()) if len(fwd_packet_lengths) > 0 else 0.0,
            'Avg Bwd Segment Size': float(bwd_packet_lengths.mean()) if len(bwd_packet_lengths) > 0 else 0.0,
            'Fwd Header Length.1': self.fwd_header_length,  # Duplicate in original dataset
            'Subflow Fwd Packets': self.subflow_fwd_packets,
            'Subflow Fwd Bytes': self.subflow_fwd_bytes,
            'Subflow Bwd Packets': self.subflow_bwd_packets,
            'Subflow Bwd Bytes': self.subflow_bwd_bytes,
            'Init_Win_bytes_forward': self.init_win_bytes_forward,
            'Init_Win_bytes_backward': self.init_win_bytes_backward,
            'act_data_pkt_fwd': self.act_data_pkt_fwd,
            'min_seg_size_forward': self.min_seg_size_forward,
            'Active Mean': float(np.mean(self.active_times)) if self.active_times else 0.0,
            'Active Std': float(np.std(self.active_times)) if self.active_times else 0.0,
            'Active Max': int(np.max(self.active_times)) if self.active_times else 0,
            'Active Min': int(np.min(self.active_times)) if self.active_times else 0,
            'Idle Mean': float(np.mean(self.idle_times)) if self.idle_times else 0.0,
            'Idle Std': float(np.std(self.idle_times)) if self.idle_times else 0.0,
            'Idle Max': int(np.max(self.idle_times)) if self.idle_times else 0,
            'Idle Min': int(np.min(self.idle_times)) if self.idle_times else 0,
        }
        
        return features


class FlowManager:
    """Manages network flows and expires idle flows."""
    
    def __init__(self, idle_timeout: int = 60):
        self.flows: Dict[Tuple[str, str, int, int, str], Flow] = {}
        self.idle_timeout = idle_timeout
        self.lock = threading.Lock()
        self._running = False
        self._cleanup_thread = None
    
    def start(self):
        """Start the cleanup thread."""
        if self._running:
            return
        self._running = True
        self._cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self._cleanup_thread.start()
    
    def stop(self):
        """Stop the cleanup thread."""
        self._running = False
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=2)
    
    def _cleanup_loop(self):
        """Periodically clean up expired flows."""
        while self._running:
            time.sleep(5)  # Check every 5 seconds
            self.expire_flows()
    
    def get_flow_key(self, src_ip: str, dst_ip: str, src_port: int, dst_port: int, protocol: str) -> Tuple[str, str, int, int, str]:
        """Get flow key (normalized 5-tuple)."""
        # Normalize: always use smaller IP/port as source
        if src_ip > dst_ip or (src_ip == dst_ip and src_port > dst_port):
            return (dst_ip, src_ip, dst_port, src_port, protocol)
        return (src_ip, dst_ip, src_port, dst_port, protocol)
    
    def add_packet(self, src_ip: str, dst_ip: str, src_port: int, dst_port: int, protocol: str, packet_info: Dict) -> Optional[Flow]:
        """Add a packet to a flow. Returns the flow if it was just expired."""
        key = self.get_flow_key(src_ip, dst_ip, src_port, dst_port, protocol)
        
        with self.lock:
            if key not in self.flows:
                self.flows[key] = Flow(src_ip, dst_ip, src_port, dst_port, protocol)
            
            flow = self.flows[key]
            flow.add_packet(packet_info)
            
            return None
    
    def expire_flows(self) -> list[Flow]:
        """Expire flows that have been idle too long. Returns expired flows."""
        now = datetime.utcnow()
        expired = []
        
        with self.lock:
            keys_to_remove = []
            for key, flow in self.flows.items():
                idle_time = (now - flow.last_seen).total_seconds()
                if idle_time > self.idle_timeout:
                    expired.append(flow)
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self.flows[key]
        
        return expired
    
    def flush_active_flows(self, min_packets: int = 5, max_age_seconds: int = 10) -> list[Flow]:
        """Flush active flows that have enough packets or are old enough. Returns flushed flows."""
        now = datetime.utcnow()
        flushed = []
        
        with self.lock:
            keys_to_remove = []
            for key, flow in self.flows.items():
                age = (now - flow.first_seen).total_seconds()
                # Calculate total packet count from forward and backward packets
                packet_count = flow.total_fwd_packets + flow.total_backward_packets
                
                # Flush if flow has enough packets OR is old enough
                if packet_count >= min_packets or age >= max_age_seconds:
                    flushed.append(flow)
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self.flows[key]
        
        return flushed
    
    def get_expired_flows(self) -> list[Flow]:
        """Get expired flows without removing them (for inspection)."""
        now = datetime.utcnow()
        expired = []
        
        with self.lock:
            for flow in self.flows.values():
                idle_time = (now - flow.last_seen).total_seconds()
                if idle_time > self.idle_timeout:
                    expired.append(flow)
        
        return expired
    
    def get_active_flow_count(self) -> int:
        """Get number of active flows."""
        with self.lock:
            return len(self.flows)

