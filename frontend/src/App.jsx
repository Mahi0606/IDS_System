import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import LiveMonitoring from './pages/LiveMonitoring';
import ModelInsights from './pages/ModelInsights';
import FlowAnalyzer from './pages/FlowAnalyzer';

function NavLink({ to, children }) {
  const location = useLocation();
  const isActive = location.pathname === to;
  
  return (
    <Link
      to={to}
      className={`${
        isActive
          ? 'border-blue-500 text-white'
          : 'border-transparent text-gray-300 hover:border-gray-300 hover:text-white'
      } inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium`}
    >
      {children}
    </Link>
  );
}

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-ids-dark">
        <nav className="bg-ids-darker border-b border-gray-800">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex">
                <div className="flex-shrink-0 flex items-center">
                  <h1 className="text-xl font-bold text-white">IDS System</h1>
                </div>
                <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                  <NavLink to="/">Dashboard</NavLink>
                  <NavLink to="/live">Live Monitoring</NavLink>
                  <NavLink to="/insights">Model Insights</NavLink>
                  <NavLink to="/analyzer">Flow Analyzer</NavLink>
                </div>
              </div>
            </div>
          </div>
        </nav>

        <main>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/live" element={<LiveMonitoring />} />
            <Route path="/insights" element={<ModelInsights />} />
            <Route path="/analyzer" element={<FlowAnalyzer />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
