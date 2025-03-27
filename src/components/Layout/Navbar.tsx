import React from 'react';
import { Link } from 'react-router-dom';
import { styled } from '@mui/material';

const Nav = styled('nav')({
  margin: '20px 0',
  '& a': {
    margin: '0 15px',
    textDecoration: 'none',
    color: '#007BFF',
  }
});

const Navbar: React.FC = () => {
  return (
    <Nav>
      <Link to="/">Dashboard</Link>
      <Link to="/data-ingestion">Data Ingestion</Link>
      <Link to="/market-analysis">Market Analysis</Link>
      <Link to="/reports">Reports</Link>
    </Nav>
  );
};

export default Navbar; 