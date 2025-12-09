import { useState, useEffect } from 'react';
import api from '../api/client';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const COLORS = ['#3b82f6', '#ef4444', '#f59e0b', '#10b981', '#8b5cf6', '#ec4899'];

function Dashboard() {
  const [stats, setStats] = useState({
    totalFlows: 0,
    totalAttacks: 0,
    attackRatio: 0,
    mostFrequentAttack: 'N/A',
  });
  const [attacksOverTime, setAttacksOverTime] = useState([]);
  const [attackTypeDistribution, setAttackTypeDistribution] = useState([]);
  const [recentFlows, setRecentFlows] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Fetch history
      const historyRes = await api.get('/predictions/history?limit=1000');
      const history = historyRes.data;

      // Calculate stats
      const totalFlows = history.length;
      const attacks = history.filter(h => h.is_attack);
      const totalAttacks = attacks.length;
      const attackRatio = totalFlows > 0 ? (totalAttacks / totalFlows) * 100 : 0;

      // Most frequent attack type
      const attackTypes = attacks.reduce((acc, a) => {
        acc[a.attack_type] = (acc[a.attack_type] || 0) + 1;
        return acc;
      }, {});
      const mostFrequent = Object.entries(attackTypes).sort((a, b) => b[1] - a[1])[0];
      const mostFrequentAttack = mostFrequent ? mostFrequent[0] : 'N/A';

      setStats({ totalFlows, totalAttacks, attackRatio, mostFrequentAttack });

      // Attacks over time (last 24 hours, grouped by hour)
      const now = new Date();
      const last24h = Array.from({ length: 24 }, (_, i) => {
        const hour = new Date(now.getTime() - (23 - i) * 60 * 60 * 1000);
        return {
          time: hour.getHours().toString().padStart(2, '0') + ':00',
          attacks: 0,
        };
      });

      history.forEach(h => {
        if (h.is_attack) {
          const date = new Date(h.created_at);
          const hoursAgo = Math.floor((now - date) / (60 * 60 * 1000));
          if (hoursAgo >= 0 && hoursAgo < 24) {
            last24h[23 - hoursAgo].attacks++;
          }
        }
      });

      setAttacksOverTime(last24h);

      // Attack type distribution
      const distribution = Object.entries(attackTypes).map(([type, count]) => ({
        name: type,
        value: count,
      }));
      setAttackTypeDistribution(distribution);

      // Recent flows (last 10)
      setRecentFlows(history.slice(0, 10));
      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
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

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-white text-xl">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-white mb-8">Dashboard</h1>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-gray-400 text-sm font-medium mb-2">Total Flows (Today)</h3>
          <p className="text-3xl font-bold text-white">{stats.totalFlows}</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-gray-400 text-sm font-medium mb-2">Total Attacks</h3>
          <p className="text-3xl font-bold text-red-400">{stats.totalAttacks}</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-gray-400 text-sm font-medium mb-2">Attack Ratio</h3>
          <p className="text-3xl font-bold text-yellow-400">{stats.attackRatio.toFixed(2)}%</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-gray-400 text-sm font-medium mb-2">Most Frequent Attack</h3>
          <p className="text-3xl font-bold text-orange-400">{stats.mostFrequentAttack}</p>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-white text-lg font-semibold mb-4">Attacks Over Time (24h)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={attacksOverTime}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="time" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }} />
              <Line type="monotone" dataKey="attacks" stroke="#ef4444" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-white text-lg font-semibold mb-4">Attack Type Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={attackTypeDistribution}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {attackTypeDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent Flows Table */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-white text-lg font-semibold mb-4">Recent Flows</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-700">
            <thead>
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Time</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Source</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Destination</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Severity</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              {recentFlows.map((flow) => (
                <tr key={flow.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                    {new Date(flow.created_at).toLocaleTimeString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                    {flow.src_ip}:{flow.src_port}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                    {flow.dst_ip}:{flow.dst_port}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span className={flow.is_attack ? 'text-red-400' : 'text-green-400'}>
                      {flow.attack_type}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getSeverityColor(flow.severity)}`}>
                      {flow.severity}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;

