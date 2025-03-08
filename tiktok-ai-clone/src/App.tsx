import { Routes, Route } from 'react-router-dom';
import { lazy, Suspense } from 'react';
import Layout from './components/Layout';

// Lazy load pages for better performance
const Home = lazy(() => import('./pages/Home'));
const Profile = lazy(() => import('./pages/Profile'));
const Discover = lazy(() => import('./pages/Discover'));
const Dashboard = lazy(() => import('./pages/Dashboard'));

const App = () => {
  return (
    <Suspense fallback={<div className="loading-spinner" />}>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="profile" element={<Profile />} />
          <Route path="discover" element={<Discover />} />
          <Route path="dashboard" element={<Dashboard />} />
        </Route>
      </Routes>
    </Suspense>
  );
};

export default App; 