import { useState } from 'react';
import api from '../api/client';

function FlowAnalyzer() {
  const [formData, setFormData] = useState({
    src_ip: '',
    dst_ip: '',
    src_port: '',
    dst_port: '',
    protocol: 'TCP',
    // Initialize all feature fields (simplified - in production you'd want all 70 features)
    destination_port: '',
    flow_duration: '',
    total_fwd_packets: '',
    total_backward_packets: '',
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      // Convert form data to API format
      const payload = {
        ...formData,
        src_port: parseInt(formData.src_port) || 0,
        dst_port: parseInt(formData.dst_port) || 0,
        destination_port: parseInt(formData.destination_port) || 0,
        flow_duration: parseInt(formData.flow_duration) || 0,
        total_fwd_packets: parseInt(formData.total_fwd_packets) || 0,
        total_backward_packets: parseInt(formData.total_backward_packets) || 0,
        // Set defaults for missing features (0 or null)
        // In a real implementation, you'd have all 70 features in the form
      };

      const response = await api.post('/predictions/predict-flow', payload);
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high': return 'bg-red-500';
      case 'medium': return 'bg-yellow-500';
      case 'low': return 'bg-orange-500';
      default: return 'bg-green-500';
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-white mb-8">Single Flow Analyzer</h1>

      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 mb-6">
        <p className="text-gray-400 text-sm mb-4">
          Enter flow information to analyze. The system will predict whether the flow is benign or an attack,
          and if it's an attack, classify the attack type.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="bg-gray-800 rounded-lg p-6 border border-gray-700 mb-6">
        <h2 className="text-xl font-semibold text-white mb-4">Flow Information</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Source IP</label>
            <input
              type="text"
              name="src_ip"
              value={formData.src_ip}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="192.168.1.100"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Destination IP</label>
            <input
              type="text"
              name="dst_ip"
              value={formData.dst_ip}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="192.168.1.1"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Source Port</label>
            <input
              type="number"
              name="src_port"
              value={formData.src_port}
              onChange={handleChange}
              required
              min="0"
              max="65535"
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="12345"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Destination Port</label>
            <input
              type="number"
              name="dst_port"
              value={formData.dst_port}
              onChange={handleChange}
              required
              min="0"
              max="65535"
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="80"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Protocol</label>
            <select
              name="protocol"
              value={formData.protocol}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="TCP">TCP</option>
              <option value="UDP">UDP</option>
              <option value="ICMP">ICMP</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Flow Duration (microseconds)</label>
            <input
              type="number"
              name="flow_duration"
              value={formData.flow_duration}
              onChange={handleChange}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="1000000"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Total Forward Packets</label>
            <input
              type="number"
              name="total_fwd_packets"
              value={formData.total_fwd_packets}
              onChange={handleChange}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="10"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Total Backward Packets</label>
            <input
              type="number"
              name="total_backward_packets"
              value={formData.total_backward_packets}
              onChange={handleChange}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="10"
            />
          </div>
        </div>

        <div className="bg-gray-700/50 rounded p-4 mb-4">
          <p className="text-gray-400 text-sm">
            <strong>Note:</strong> This is a simplified form. In production, all 70 features from the training dataset
            would be included. Missing features will default to 0.
          </p>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Analyzing...' : 'Analyze Flow'}
        </button>
      </form>

      {error && (
        <div className="bg-red-900/50 border border-red-500 rounded-lg p-4 mb-6">
          <p className="text-red-300">{error}</p>
        </div>
      )}

      {result && (
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h2 className="text-xl font-semibold text-white mb-4">Analysis Result</h2>
          <div className="space-y-4">
            <div className="flex items-center space-x-4">
              <span className="text-gray-400">Classification:</span>
              <span className={`text-2xl font-bold ${result.is_attack ? 'text-red-400' : 'text-green-400'}`}>
                {result.attack_type}
              </span>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-gray-400">Confidence:</span>
              <span className="text-xl font-semibold text-white">{(result.binary_confidence * 100).toFixed(2)}%</span>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-gray-400">Severity:</span>
              <span className={`inline-flex px-3 py-1 text-sm font-semibold rounded-full ${getSeverityColor(result.severity)}`}>
                {result.severity}
              </span>
            </div>
            {Object.keys(result.class_probabilities).length > 0 && (
              <div>
                <h3 className="text-gray-300 font-semibold mb-2">
                  Class Probabilities{result.is_attack ? ' (attack classes only)' : ''}
                </h3>

                {(() => {
                  // If this is an attack, hide the BENIGN row
                  const entries = Object.entries(result.class_probabilities).filter(
                    ([cls]) => !(result.is_attack && cls === 'BENIGN')
                  );

                  return (
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                      {entries.map(([cls, prob]) => (
                        <div key={cls} className="bg-gray-700/50 rounded p-2">
                          <div className="text-gray-400 text-xs">{cls}</div>
                          <div className="text-white font-semibold">
                            {(prob * 100).toFixed(1)}%
                          </div>
                        </div>
                      ))}
                    </div>
                  );
                })()}
              </div>
            )}

            {result.is_attack && (
              <div className="bg-yellow-900/30 border border-yellow-500 rounded p-4 mt-4">
                <p className="text-yellow-300 text-sm">
                  <strong>Recommendation:</strong> This flow has been classified as an attack.
                  Consider blocking the source IP and investigating further.
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default FlowAnalyzer;

