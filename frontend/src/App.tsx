import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import VisitorDashboardLayout from './pages/visitor/VisitorDashboardLayout';
import VisitorHome from './pages/visitor/VisitorHome';
import SubmitVerification from './pages/visitor/SubmitVerification';
import CompleteProfile from './pages/visitor/CompleteProfile';
import VisitorProfile from './pages/visitor/VisitorProfile';
import VisitorHistory from './pages/visitor/VisitorHistory';
import ForceDashboardLayout from './pages/force/ForceDashboardLayout';
import ForceOverview from './pages/force/ForceOverview';
import VerificationWorkspace from './pages/force/VerificationWorkspace';
import ForceHistory from './pages/force/ForceHistory';
import PlaceholderPage from './pages/PlaceholderPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        
        {/* Visitor Routes */}
        <Route path="/complete-profile" element={<CompleteProfile />} />
        <Route path="/visitor-dashboard" element={<VisitorDashboardLayout />}>
          <Route index element={<VisitorHome />} />
          <Route path="submit" element={<SubmitVerification />} />
          <Route path="profile" element={<VisitorProfile />} />
          
          {/* Missing sidebar routes to prevent redirect to login */}
          <Route path="history" element={<VisitorHistory />} />
          <Route path="notifications" element={<PlaceholderPage />} />
          <Route path="help" element={<PlaceholderPage />} />
        </Route>

        {/* Force Routes */}
        <Route path="/force-dashboard" element={<ForceDashboardLayout />}>
          <Route index element={<ForceOverview />} />
          <Route path="verify/:id" element={<VerificationWorkspace />} />
          
          {/* Missing sidebar routes to prevent redirect to login */}
          <Route path="queue" element={<ForceOverview />} /> {/* Queue is part of overview */}
          <Route path="alerts" element={<PlaceholderPage />} />
          <Route path="notifications" element={<PlaceholderPage />} />
          <Route path="history" element={<ForceHistory />} />
          <Route path="reports" element={<PlaceholderPage />} />
          <Route path="profile" element={<PlaceholderPage />} />
          <Route path="settings" element={<PlaceholderPage />} />
        </Route>

        {/* Catch-all redirect to login for entirely unknown paths */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
