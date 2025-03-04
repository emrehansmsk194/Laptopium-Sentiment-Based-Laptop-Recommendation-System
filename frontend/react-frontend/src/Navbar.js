import React from 'react';
import { Link } from 'react-router-dom';

function Navbar(){
    return(
        <nav style={styles.navbar}>
        
        <ul style={styles.menu}>
          <h1 style={styles.logo}>Laptopium</h1>
          <li style={styles.menuItem}><Link to="/" style={styles.link}>Anasayfa</Link></li>
          <li style={styles.menuItem}><Link to="/LaptopList" style={styles.link}>Tüm Laptoplar</Link></li>
          <li style={styles.menuItem}><Link to="/LapAdvisor" style={styles.link}>LapAdvisor AI</Link></li>
          <li style={styles.menuItem}><Link to="/Chatbot" style={styles.link}>Chatbot</Link></li>
        </ul>
      </nav>
    );
}

const styles = {
    navbar: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      backgroundColor: '#424141',
      padding: '1rem',
      position: 'top'
    },
    logo: {
      color: '#fff',
      margin: 0
    },
    menu: {
      listStyle: 'none',
      display: 'flex',
      gap: '3rem',
      margin: 0,
      padding:0
    },
    menuItem: {
        fontSize: '1.2rem'
    },
    link: {
      color: '#fff',
      textDecoration: 'none'
    }
  };
  
  export default Navbar;