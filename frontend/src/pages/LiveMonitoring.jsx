import { useState, useEffect, useRef, useCallback } from 'react';
import api from '../api/client';
import { useWebSocket } from '../contexts/WebSocketContext';

function LiveMonitoring() {
  const [flows, setFlows] = useState([]);
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [filter, setFilter] = useState('all'); // 'all', 'attacks', or specific attack type
  const [stats, setStats] = useState({ total: 0, attacks: 0 });
  const [interfaceInfo, setInterfaceInfo] = useState(null);
  const [snifferStats, setSnifferStats] = useState(null);
  const [selectedInterface, setSelectedInterface] = useState('');
  const { isConnected, subscribe, connect, disconnect } = useWebSocket();

  // Subscribe to WebSocket messages
  useEffect(() => {
    const unsubscribe = subscribe((data) => {
      console.log('WebSocket message received in LiveMonitoring:', data);
      
      // Ensure confidence field exists
      const flowData = {
        ...data,
        confidence: data.confidence || data.binary_confidence || 0,
      };
      
      setFlows(prev => {
        const newFlows = [flowData, ...prev].slice(0, 200); // Keep last 200
        return newFlows;
      });
      
      // Update stats
      setStats(prev => ({
        total: prev.total + 1,
        attacks: prev.attacks + (data.is_attack ? 1 : 0),
      }));
    });

    return unsubscribe;
  }, [subscribe]);

  useEffect(() => {
    // Check sniffer status on mount
    checkSnifferStatus();
    // Also refresh stats on mount to show existing data
    refreshStats();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const checkSnifferStatus = useCallback(async () => {
    try {
      const response = await api.get('/health');
      const running = response.data.sniffer_running || false;
      setIsMonitoring(running);
      setInterfaceInfo({
        interface: response.data.interface,
        available: response.data.available_interfaces || [],
        exists: response.data.interface_exists,
        active_flows: response.data.active_flows || 0,
      });
      setSnifferStats(response.data.sniffer_stats || {});
      if (!selectedInterface && response.data.interface) {
        setSelectedInterface(response.data.interface);
      }
      return running;
    } catch (error) {
      console.error('Error checking sniffer status:', error);
      return false;
    }
  }, []);

  // Periodically check sniffer status (only when monitoring should be active)
  useEffect(() => {
    if (isMonitoring) {
      const interval = setInterval(() => {
        checkSnifferStatus().then(status => {
          // If monitoring was supposed to be on but sniffer stopped, update state
          if (isMonitoring && !status) {
            setIsMonitoring(false);
          }
        });
      }, 3000);
      return () => clearInterval(interval);
    }
  }, [isMonitoring, checkSnifferStatus]);

  // WebSocket is managed globally, no need for local connect/disconnect

  const startMonitoring = async () => {
    try {
      // Refresh stats before starting
      await refreshStats();
      // Start the sniffer
      const response = await api.post('/health/sniffer/start');
      
      // Wait a moment and check actual status
      await new Promise(resolve => setTimeout(resolve, 1000));
      const actualStatus = await checkSnifferStatus();
      
      // Check the response status
      if (response.data.status === 'started' && actualStatus) {
        setIsMonitoring(true);
        // Ensure WebSocket is connected (it's managed globally)
        if (!isConnected) {
          connect();
        }
        // Refresh stats after starting to load existing history
        await refreshStats();
      } else if (response.data.status === 'warning' || response.data.status === 'failed' || !actualStatus) {
        // Sniffer didn't actually start
        setIsMonitoring(false);
        const message = response.data.message || 'Sniffer failed to start. This may be due to:\n- Interface not found\n- Permission issues (need root/admin)\n- Interface not accessible';
        alert(`Warning: ${message}\n\nYou can still use manual flow analysis, but live monitoring may not work.`);
      } else {
        // Already running or started
        setIsMonitoring(actualStatus);
        if (actualStatus && !isConnected) {
          connect();
        }
      }
    } catch (error) {
      console.error('Error starting monitoring:', error);
      setIsMonitoring(false);
      alert(`Failed to start monitoring: ${error.response?.data?.detail || error.message}`);
    }
  };

  const stopMonitoring = async () => {
    try {
      // Stop the sniffer
      await api.post('/health/sniffer/stop');
      setIsMonitoring(false);
      // Don't disconnect WebSocket - keep it connected for other tabs
      // Don't clear flows and stats - keep them visible
    } catch (error) {
      console.error('Error stopping monitoring:', error);
      alert(`Failed to stop monitoring: ${error.response?.data?.detail || error.message}`);
    }
  };

  const changeInterface = async (newInterface) => {
    if (!newInterface || newInterface === selectedInterface) {
      return;
    }

    const wasMonitoring = isMonitoring;
    
    try {
      // Stop monitoring if running
      if (wasMonitoring) {
        await stopMonitoring();
        await new Promise(resolve => setTimeout(resolve, 500)); // Wait a bit
      }

      // Change interface
      const response = await api.post(`/health/sniffer/interface?interface=${encodeURIComponent(newInterface)}`);

      setSelectedInterface(newInterface);
      
      // Restart monitoring if it was running
      if (wasMonitoring) {
        await new Promise(resolve => setTimeout(resolve, 500));
        await startMonitoring();
      }

      alert(`Interface changed to ${newInterface}`);
    } catch (error) {
      console.error('Error changing interface:', error);
      alert(`Failed to change interface: ${error.response?.data?.detail || error.message}`);
    }
  };

  const refreshStats = useCallback(async () => {
    try {
      // Fetch recent history to update stats
      const historyRes = await api.get('/predictions/history?limit=1000');
      const history = historyRes.data;
      
      const totalFlows = history.length;
      const attacks = history.filter(h => h.is_attack);
      const totalAttacks = attacks.length;
      
      setStats({
        total: totalFlows,
        attacks: totalAttacks,
      });
      
      // Also update flows from history - convert history format to flow format
      const flowsFromHistory = history.map(h => ({
        timestamp: h.created_at || h.timestamp,
        src_ip: h.src_ip,
        dst_ip: h.dst_ip,
        src_port: h.src_port,
        dst_port: h.dst_port,
        protocol: h.protocol,
        is_attack: h.is_attack,
        attack_type: h.attack_type,
        severity: h.severity,
        confidence: h.binary_confidence || h.confidence || 0,
      }));
      
      setFlows(flowsFromHistory.sort((a, b) => new Date(b.timestamp || b.created_at) - new Date(a.timestamp || a.created_at)).slice(0, 200));
    } catch (error) {
      console.error('Error refreshing stats:', error);
    }
  }, []);

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high': return 'bg-red-500';
      case 'medium': return 'bg-yellow-500';
      case 'low': return 'bg-orange-500';
      default: return 'bg-green-500';
    }
  };

  const filteredFlows = flows.filter(flow => {
    if (filter === 'all') return true;
    if (filter === 'attacks') return flow.is_attack;
    return flow.attack_type === filter;
  });

  const uniqueAttackTypes = [...new Set(flows.filter(f => f.is_attack).map(f => f.attack_type))];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-white">Live Monitoring</h1>
        <div className="flex items-center space-x-4">
          <div className={`px-4 py-2 rounded-lg ${isMonitoring ? 'bg-green-500' : 'bg-red-500'}`}>
            <span className="text-white font-semibold">
              {isMonitoring ? 'Sniffer: ON' : 'Sniffer: OFF'}
            </span>
          </div>
          <div className={`px-4 py-2 rounded-lg ${isConnected ? 'bg-blue-500' : 'bg-gray-500'}`}>
            <span className="text-white font-semibold">
              {isConnected ? 'WebSocket: Connected' : 'WebSocket: Disconnected'}
            </span>
          </div>
          {!isMonitoring ? (
            <button
              onClick={startMonitoring}
              className="px-6 py-2 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition-colors"
            >
              Start Monitoring
            </button>
          ) : (
            <button
              onClick={stopMonitoring}
              className="px-6 py-2 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg transition-colors"
            >
              Stop Monitoring
            </button>
          )}
        </div>
      </div>

      {/* Interface Info & Sniffer Stats */}
      {interfaceInfo && (
        <div className={`mb-6 p-4 rounded-lg border ${
          interfaceInfo.exists === false 
            ? 'bg-yellow-900/30 border-yellow-500' 
            : 'bg-gray-800 border-gray-700'
        }`}>
          <div className="text-sm space-y-2">
            <div className="flex items-center gap-4">
              <div>
                <span className="text-gray-400">Interface: </span>
                <span className="text-white font-semibold">{interfaceInfo.interface}</span>
                {interfaceInfo.exists === false && (
                  <span className="ml-2 text-yellow-400">⚠ Not found</span>
                )}
              </div>
              {interfaceInfo.available.length > 0 && (
                <div className="flex items-center gap-2">
                  <label className="text-gray-400">Change Interface:</label>
                  <select
                    value={selectedInterface || interfaceInfo.interface}
                    onChange={(e) => changeInterface(e.target.value)}
                    disabled={isMonitoring}
                    className="bg-gray-700 text-white px-3 py-1 rounded border border-gray-600 focus:outline-none focus:border-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {interfaceInfo.available.map(iface => (
                      <option key={iface} value={iface}>
                        {iface} {iface === interfaceInfo.interface ? '(current)' : ''}
                      </option>
                    ))}
                  </select>
                  {isMonitoring && (
                    <span className="text-yellow-400 text-xs">(Stop monitoring to change)</span>
                  )}
                </div>
              )}
            </div>
            {snifferStats && isMonitoring && (
              <div className="mt-3 pt-3 border-t border-gray-700">
                <div className="text-gray-400 text-xs mb-1">Sniffer Statistics:</div>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-gray-400">Packets Captured: </span>
                    <span className="text-white font-semibold">{snifferStats.packet_count || 0}</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Packets Processed: </span>
                    <span className="text-white font-semibold">{snifferStats.processed_count || 0}</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Active Flows: </span>
                    <span className="text-white font-semibold">{interfaceInfo.active_flows || 0}</span>
                  </div>
                </div>
                {snifferStats.last_error && (
                  <div className="mt-2 text-red-400 text-xs">
                    ⚠ Error: {snifferStats.last_error}
                  </div>
                )}
                {snifferStats.packet_count === 0 && isMonitoring && (
                  <div className="mt-2 text-yellow-400 text-xs">
                    ⚠ No packets captured yet. Check:
                    <ul className="list-disc list-inside ml-2 mt-1">
                      <li>Interface exists and is accessible</li>
                      <li>Backend has network permissions (may need sudo)</li>
                      <li>VM traffic is visible on this interface</li>
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-gray-400 text-sm font-medium mb-2">Total Flows</h3>
          <p className="text-3xl font-bold text-white">{stats.total}</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-gray-400 text-sm font-medium mb-2">Attacks Detected</h3>
          <p className="text-3xl font-bold text-red-400">{stats.attacks}</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-gray-400 text-sm font-medium mb-2">Active Flows</h3>
          <p className="text-3xl font-bold text-blue-400">{flows.length}</p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 mb-6">
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded ${filter === 'all' ? 'bg-blue-500 text-white' : 'bg-gray-700 text-gray-300'}`}
          >
            All
          </button>
          <button
            onClick={() => setFilter('attacks')}
            className={`px-4 py-2 rounded ${filter === 'attacks' ? 'bg-blue-500 text-white' : 'bg-gray-700 text-gray-300'}`}
          >
            Attacks Only
          </button>
          {uniqueAttackTypes.map(type => (
            <button
              key={type}
              onClick={() => setFilter(type)}
              className={`px-4 py-2 rounded ${filter === type ? 'bg-blue-500 text-white' : 'bg-gray-700 text-gray-300'}`}
            >
              {type}
            </button>
          ))}
        </div>
      </div>

      {/* Flows Table */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-white text-lg font-semibold mb-4">Live Flows</h3>
        <div className="overflow-x-auto max-h-96 overflow-y-auto">
          <table className="min-w-full divide-y divide-gray-700">
            <thead className="sticky top-0 bg-gray-800">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Time</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Source</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Destination</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Protocol</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Severity</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Confidence</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              {filteredFlows.length === 0 ? (
                <tr>
                  <td colSpan="7" className="px-6 py-4 text-center text-gray-400">
                    {!isMonitoring 
                      ? 'Monitoring is stopped. Click "Start Monitoring" to begin.' 
                      : isConnected 
                        ? 'No flows yet. Waiting for network traffic...' 
                        : 'WebSocket disconnected. Reconnecting...'}
                  </td>
                </tr>
              ) : (
                filteredFlows.map((flow, index) => (
                  <tr key={index} className={flow.is_attack ? 'bg-red-900/20' : ''}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                      {new Date(flow.timestamp).toLocaleTimeString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                      {flow.src_ip}:{flow.src_port}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                      {flow.dst_ip}:{flow.dst_port}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                      {flow.protocol}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={flow.is_attack ? 'text-red-400 font-semibold' : 'text-green-400'}>
                        {flow.attack_type}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getSeverityColor(flow.severity)}`}>
                        {flow.severity}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                      {((flow.confidence || flow.binary_confidence || 0) * 100).toFixed(1)}%
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default LiveMonitoring;

