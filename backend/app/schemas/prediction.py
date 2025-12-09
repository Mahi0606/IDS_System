"""Pydantic schemas for API requests and responses."""
from pydantic import BaseModel, Field
from typing import Dict, Optional
from datetime import datetime


class FlowInput(BaseModel):
    """Input schema for flow prediction."""
    # Basic flow identifiers
    src_ip: str = Field(..., description="Source IP address")
    dst_ip: str = Field(..., description="Destination IP address")
    src_port: int = Field(..., ge=0, le=65535, description="Source port")
    dst_port: int = Field(..., ge=0, le=65535, description="Destination port")
    protocol: str = Field(..., description="Protocol (TCP, UDP, etc.)")
    
    # Flow statistics - all features from FEATURE_COLUMNS
    destination_port: Optional[int] = None
    flow_duration: Optional[int] = None
    total_fwd_packets: Optional[int] = None
    total_backward_packets: Optional[int] = None
    total_length_of_fwd_packets: Optional[int] = None
    total_length_of_bwd_packets: Optional[int] = None
    fwd_packet_length_max: Optional[int] = None
    fwd_packet_length_min: Optional[int] = None
    fwd_packet_length_mean: Optional[float] = None
    fwd_packet_length_std: Optional[float] = None
    bwd_packet_length_max: Optional[int] = None
    bwd_packet_length_min: Optional[int] = None
    bwd_packet_length_mean: Optional[float] = None
    bwd_packet_length_std: Optional[float] = None
    flow_bytes_s: Optional[float] = None
    flow_packets_s: Optional[float] = None
    flow_iat_mean: Optional[float] = None
    flow_iat_std: Optional[float] = None
    flow_iat_max: Optional[int] = None
    flow_iat_min: Optional[int] = None
    fwd_iat_total: Optional[int] = None
    fwd_iat_mean: Optional[float] = None
    fwd_iat_std: Optional[float] = None
    fwd_iat_max: Optional[int] = None
    fwd_iat_min: Optional[int] = None
    bwd_iat_total: Optional[int] = None
    bwd_iat_mean: Optional[float] = None
    bwd_iat_std: Optional[float] = None
    bwd_iat_max: Optional[int] = None
    bwd_iat_min: Optional[int] = None
    fwd_psh_flags: Optional[int] = None
    fwd_urg_flags: Optional[int] = None
    fwd_header_length: Optional[int] = None
    bwd_header_length: Optional[int] = None
    fwd_packets_s: Optional[float] = None
    bwd_packets_s: Optional[float] = None
    min_packet_length: Optional[int] = None
    max_packet_length: Optional[int] = None
    packet_length_mean: Optional[float] = None
    packet_length_std: Optional[float] = None
    packet_length_variance: Optional[float] = None
    fin_flag_count: Optional[int] = None
    syn_flag_count: Optional[int] = None
    rst_flag_count: Optional[int] = None
    psh_flag_count: Optional[int] = None
    ack_flag_count: Optional[int] = None
    urg_flag_count: Optional[int] = None
    cwe_flag_count: Optional[int] = None
    ece_flag_count: Optional[int] = None
    down_up_ratio: Optional[int] = None
    average_packet_size: Optional[float] = None
    avg_fwd_segment_size: Optional[float] = None
    avg_bwd_segment_size: Optional[float] = None
    fwd_header_length_1: Optional[int] = None
    subflow_fwd_packets: Optional[int] = None
    subflow_fwd_bytes: Optional[int] = None
    subflow_bwd_packets: Optional[int] = None
    subflow_bwd_bytes: Optional[int] = None
    init_win_bytes_forward: Optional[int] = None
    init_win_bytes_backward: Optional[int] = None
    act_data_pkt_fwd: Optional[int] = None
    min_seg_size_forward: Optional[int] = None
    active_mean: Optional[float] = None
    active_std: Optional[float] = None
    active_max: Optional[int] = None
    active_min: Optional[int] = None
    idle_mean: Optional[float] = None
    idle_std: Optional[float] = None
    idle_max: Optional[int] = None
    idle_min: Optional[int] = None
    
    def to_flow_dict(self) -> Dict:
        """Convert to dictionary with proper column names matching FEATURE_COLUMNS."""
        # Map schema field names to feature column names
        # Note: destination_port in features should use dst_port if destination_port not provided
        mapping = {
            'destination_port': 'Destination Port',
            'flow_duration': 'Flow Duration',
            'total_fwd_packets': 'Total Fwd Packets',
            'total_backward_packets': 'Total Backward Packets',
            'total_length_of_fwd_packets': 'Total Length of Fwd Packets',
            'total_length_of_bwd_packets': 'Total Length of Bwd Packets',
            'fwd_packet_length_max': 'Fwd Packet Length Max',
            'fwd_packet_length_min': 'Fwd Packet Length Min',
            'fwd_packet_length_mean': 'Fwd Packet Length Mean',
            'fwd_packet_length_std': 'Fwd Packet Length Std',
            'bwd_packet_length_max': 'Bwd Packet Length Max',
            'bwd_packet_length_min': 'Bwd Packet Length Min',
            'bwd_packet_length_mean': 'Bwd Packet Length Mean',
            'bwd_packet_length_std': 'Bwd Packet Length Std',
            'flow_bytes_s': 'Flow Bytes/s',
            'flow_packets_s': 'Flow Packets/s',
            'flow_iat_mean': 'Flow IAT Mean',
            'flow_iat_std': 'Flow IAT Std',
            'flow_iat_max': 'Flow IAT Max',
            'flow_iat_min': 'Flow IAT Min',
            'fwd_iat_total': 'Fwd IAT Total',
            'fwd_iat_mean': 'Fwd IAT Mean',
            'fwd_iat_std': 'Fwd IAT Std',
            'fwd_iat_max': 'Fwd IAT Max',
            'fwd_iat_min': 'Fwd IAT Min',
            'bwd_iat_total': 'Bwd IAT Total',
            'bwd_iat_mean': 'Bwd IAT Mean',
            'bwd_iat_std': 'Bwd IAT Std',
            'bwd_iat_max': 'Bwd IAT Max',
            'bwd_iat_min': 'Bwd IAT Min',
            'fwd_psh_flags': 'Fwd PSH Flags',
            'fwd_urg_flags': 'Fwd URG Flags',
            'fwd_header_length': 'Fwd Header Length',
            'bwd_header_length': 'Bwd Header Length',
            'fwd_packets_s': 'Fwd Packets/s',
            'bwd_packets_s': 'Bwd Packets/s',
            'min_packet_length': 'Min Packet Length',
            'max_packet_length': 'Max Packet Length',
            'packet_length_mean': 'Packet Length Mean',
            'packet_length_std': 'Packet Length Std',
            'packet_length_variance': 'Packet Length Variance',
            'fin_flag_count': 'FIN Flag Count',
            'syn_flag_count': 'SYN Flag Count',
            'rst_flag_count': 'RST Flag Count',
            'psh_flag_count': 'PSH Flag Count',
            'ack_flag_count': 'ACK Flag Count',
            'urg_flag_count': 'URG Flag Count',
            'cwe_flag_count': 'CWE Flag Count',
            'ece_flag_count': 'ECE Flag Count',
            'down_up_ratio': 'Down/Up Ratio',
            'average_packet_size': 'Average Packet Size',
            'avg_fwd_segment_size': 'Avg Fwd Segment Size',
            'avg_bwd_segment_size': 'Avg Bwd Segment Size',
            'fwd_header_length_1': 'Fwd Header Length.1',
            'subflow_fwd_packets': 'Subflow Fwd Packets',
            'subflow_fwd_bytes': 'Subflow Fwd Bytes',
            'subflow_bwd_packets': 'Subflow Bwd Packets',
            'subflow_bwd_bytes': 'Subflow Bwd Bytes',
            'init_win_bytes_forward': 'Init_Win_bytes_forward',
            'init_win_bytes_backward': 'Init_Win_bytes_backward',
            'act_data_pkt_fwd': 'act_data_pkt_fwd',
            'min_seg_size_forward': 'min_seg_size_forward',
            'active_mean': 'Active Mean',
            'active_std': 'Active Std',
            'active_max': 'Active Max',
            'active_min': 'Active Min',
            'idle_mean': 'Idle Mean',
            'idle_std': 'Idle Std',
            'idle_max': 'Idle Max',
            'idle_min': 'Idle Min',
        }
        
        flow_dict = {}
        for schema_key, feature_name in mapping.items():
            value = getattr(self, schema_key, None)
            if value is not None:
                flow_dict[feature_name] = value
        
        # Handle destination_port special case (use dst_port if destination_port not set)
        if 'Destination Port' not in flow_dict and self.dst_port is not None:
            flow_dict['Destination Port'] = self.dst_port
        
        return flow_dict


class PredictionResponse(BaseModel):
    """Response schema for flow prediction."""
    is_attack: bool
    attack_type: str
    binary_confidence: float
    class_probabilities: Dict[str, float]
    severity: str


class PredictionHistoryItem(BaseModel):
    """Schema for prediction history item."""
    id: int
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: str
    is_attack: bool
    attack_type: str
    binary_confidence: float
    severity: str
    created_at: str

