import { Link, useLocation } from 'react-router-dom';
import { css } from '@emotion/react';
import styled from '@emotion/styled';

const NavbarContainer = styled.nav`
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 60px;
  background-color: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  z-index: 100;
`;

const Logo = styled.div`
  font-size: 24px;
  font-weight: 700;
  color: var(--primary);
  display: flex;
  align-items: center;
`;

const NavLinks = styled.div`
  display: flex;
  gap: 32px;
`;

// Create a base styled component without the isActive prop
const StyledLink = styled(Link)`
  font-size: 16px;
  font-weight: 600;
  padding: 8px 0;
  position: relative;
`;

// Create an active styled component that extends the base
const ActiveLink = styled(StyledLink)`
  color: var(--primary);
  
  &::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 2px;
    background-color: var(--primary);
  }
`;

// Create a custom NavLink component that doesn't pass isActive to the DOM
const NavLink = ({ to, isActive, children }) => {
  if (isActive) {
    return <ActiveLink to={to}>{children}</ActiveLink>;
  }
  return <StyledLink to={to}>{children}</StyledLink>;
};

const Navbar = () => {
  const location = useLocation();
  
  return (
    <NavbarContainer>
      <Logo>
        <span>AI TikTok</span>
      </Logo>
      
      <NavLinks>
        <NavLink to="/" isActive={location.pathname === '/'}>
          For You
        </NavLink>
        <NavLink to="/discover" isActive={location.pathname === '/discover'}>
          Discover
        </NavLink>
        <NavLink to="/profile" isActive={location.pathname === '/profile'}>
          Profile
        </NavLink>
      </NavLinks>
      
      <div>
        {/* Placeholder for search and user actions */}
      </div>
    </NavbarContainer>
  );
};

export default Navbar; 