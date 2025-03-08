import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';
import BottomNav from './BottomNav';
import { useState, useEffect } from 'react';

const Layout = () => {
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth <= 768);
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <div className="app-container">
      {!isMobile && <Navbar />}
      <main className="main-content">
        <Outlet />
      </main>
      {isMobile && <BottomNav />}
    </div>
  );
};

export default Layout; 