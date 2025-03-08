import { Routes, Route } from 'react-router-dom';
import { lazy, Suspense } from 'react';
import Layout from './components/Layout';

// Lazy load pages for better performance
const Home = lazy(() => import('./pages/Home'));
const Profile = lazy(() => import('./pages/Profile'));
const Discover = lazy(() => import('./pages/Discover'));

const App = () => {
  return (
    <Suspense fallback={<div className="loading-spinner" />}>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="profile" element={<Profile />} />
          <Route path="discover" element={<Discover />} />
        </Route>
      </Routes>
    </Suspense>
  );
};

export default App; 