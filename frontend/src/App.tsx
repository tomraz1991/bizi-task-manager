import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Episodes from './pages/Episodes';
import Tasks from './pages/Tasks';
import Engineers from './pages/Engineers';
import Podcasts from './pages/Podcasts';
import Layout from './components/Layout';
import { NotificationProvider } from './contexts/NotificationContext';

function App() {
  return (
    <NotificationProvider>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/episodes" element={<Episodes />} />
            <Route path="/tasks" element={<Tasks />} />
            <Route path="/engineers" element={<Engineers />} />
            <Route path="/podcasts" element={<Podcasts />} />
          </Routes>
        </Layout>
      </Router>
    </NotificationProvider>
  );
}

export default App;
