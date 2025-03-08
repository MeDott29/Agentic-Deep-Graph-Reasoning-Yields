import { Link, useLocation } from 'react-router-dom';
import styled from '@emotion/styled';
import React from 'react';

const BottomNavContainer = styled.nav`
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 60px;
  background-color: var(--bg-primary);
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: space-around;
  align-items: center;
  z-index: 100;
`;

// Base styled components without isActive prop
const StyledNavItem = styled(Link)`
  display: flex;
  flex-direction: column;
  align-items: center;
  font-size: 10px;
`;

const ActiveNavItem = styled(StyledNavItem)`
  color: var(--primary);
  font-weight: 600;
`;

const InactiveNavItem = styled(StyledNavItem)`
  color: var(--text-secondary);
  font-weight: 400;
`;

// Base icon component
const BaseIcon = styled.div`
  width: 24px;
  height: 24px;
  margin-bottom: 4px;
  mask-size: contain;
  mask-repeat: no-repeat;
  mask-position: center;
`;

const ActiveIcon = styled(BaseIcon)`
  background-color: var(--primary);
`;

const InactiveIcon = styled(BaseIcon)`
  background-color: var(--text-secondary);
`;

// Home icon variants
const ActiveHomeIcon = styled(ActiveIcon)`
  mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z'/%3E%3C/svg%3E");
`;

const InactiveHomeIcon = styled(InactiveIcon)`
  mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z'/%3E%3C/svg%3E");
`;

// Discover icon variants
const ActiveDiscoverIcon = styled(ActiveIcon)`
  mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z'/%3E%3C/svg%3E");
`;

const InactiveDiscoverIcon = styled(InactiveIcon)`
  mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z'/%3E%3C/svg%3E");
`;

// Profile icon variants
const ActiveProfileIcon = styled(ActiveIcon)`
  mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z'/%3E%3C/svg%3E");
`;

const InactiveProfileIcon = styled(InactiveIcon)`
  mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z'/%3E%3C/svg%3E");
`;

// Dashboard icon variants
const ActiveDashboardIcon = styled(ActiveIcon)`
  mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z'/%3E%3C/svg%3E");
`;

const InactiveDashboardIcon = styled(InactiveIcon)`
  mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z'/%3E%3C/svg%3E");
`;

// Custom NavItem component that doesn't pass isActive to DOM
const NavItem = ({ to, isActive, children }) => {
  if (isActive) {
    return <ActiveNavItem to={to}>{children}</ActiveNavItem>;
  }
  return <InactiveNavItem to={to}>{children}</InactiveNavItem>;
};

// Custom Icon component that doesn't pass isActive to DOM
const HomeIcon = ({ isActive }) => {
  return isActive ? <ActiveHomeIcon /> : <InactiveHomeIcon />;
};

const DiscoverIcon = ({ isActive }) => {
  return isActive ? <ActiveDiscoverIcon /> : <InactiveDiscoverIcon />;
};

const ProfileIcon = ({ isActive }) => {
  return isActive ? <ActiveProfileIcon /> : <InactiveProfileIcon />;
};

const DashboardIcon = ({ isActive }) => {
  return isActive ? <ActiveDashboardIcon /> : <InactiveDashboardIcon />;
};

const BottomNav = () => {
  const location = useLocation();
  const isHome = location.pathname === '/';
  const isDiscover = location.pathname === '/discover';
  const isProfile = location.pathname === '/profile';
  const isDashboard = location.pathname === '/dashboard';
  
  return (
    <BottomNavContainer>
      <NavItem to="/" isActive={isHome}>
        <HomeIcon isActive={isHome} />
        <span>Home</span>
      </NavItem>
      
      <NavItem to="/discover" isActive={isDiscover}>
        <DiscoverIcon isActive={isDiscover} />
        <span>Discover</span>
      </NavItem>
      
      <NavItem to="/profile" isActive={isProfile}>
        <ProfileIcon isActive={isProfile} />
        <span>Profile</span>
      </NavItem>
      
      <NavItem to="/dashboard" isActive={isDashboard}>
        <DashboardIcon isActive={isDashboard} />
        <span>Dashboard</span>
      </NavItem>
    </BottomNavContainer>
  );
};

export default BottomNav; 