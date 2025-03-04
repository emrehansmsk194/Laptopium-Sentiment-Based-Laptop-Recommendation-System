import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';


export default function HomePage() {
  const [query, setQuery] = useState('');
  const [laptops, setLaptops] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchData();
  }, []);
  // Öne çıkan laptoplar (örnek veriler)
  const fetchData = () => {
    setLoading(true);
    setError('');

    fetch('http://localhost:5000/most_reviewed_laptops')
      .then((res) => {
        if (!res.ok) {
          throw new Error('Sunucu hatası');
        }
        return res.json();
      })
      .then((data) => {
        setLaptops(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });

  };

  const handleSearch = (e) => {
    e.preventDefault();
    // Burada arama fonksiyonu (örn. setPage(1), fetch('laptops_by_name?query=...'))
    fetch(`http://localhost:5000/laptops_by_name?query=${query}`)
      .then((res) => {
        if (!res.ok) {
          throw new Error('Sunucu hatası');
        }
        return res.json();
      })
      .then((data) => {
        setSearchResults(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  };

  const handleBackToQuery = (e)  => {
    e.preventDefault();
    setQuery('');
    fetchData();

  }

  return (
    <div style={styles.container}>
      {/* Hero Section */}
      <div style={styles.hero}>
        <h1 style={styles.heroTitle}>Laptopium</h1>
        <p style={styles.heroSubtitle}>En iyi laptop önerileri için doğru adrestesiniz!
          <Link to="/LapAdvisor" style={styles.laptopLink}> LapAdvisor AI </Link>kullanarak bütçenize göre en iyi laptopları bulabilirsiniz.
        </p>
      </div>

      {/* Arama Kutusu */}
      <div style={styles.searchSection}>
        <form onSubmit={handleSearch} style={styles.searchForm}>
          <input
            type="text"
            placeholder="Laptop adı veya marka ara..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            style={styles.searchInput}
          />
          <button type="submit" style={styles.searchButton}>
            Ara
          </button>
        </form>
      </div>

     {/* Koşullu Render: Eğer query boşsa "featured", değilse arama sonuçları */}
     {!query.trim() ? (
        <>
          <h2 style={styles.featuredTitle}>Öne Çıkan Laptoplar</h2>
          <div style={styles.featuredContainer}>
            {laptops.map((lap, idx) => (
              <div key={idx} style={styles.laptopCard}>
                <img
                  src={lap.image}
                  alt={lap.laptop_name}
                  style={styles.laptopImage}
                />
                <h3 style={styles.laptopName}>
                  {lap.laptop_name.split(" ").slice(0, 6).join(" ")}
                </h3>
                <p style={styles.laptopPrice}>Fiyat: {lap.price} TL</p>
                <a
                  href={lap.link}
                  target="_blank"
                  rel="noreferrer"
                  style={styles.buyButton}
                >
                  Satıcıya Git
                </a>
              </div>
            ))}
          </div>
        </>
      ) : (
        <>
   
          <h2 style={styles.searchTitle}>Arama Sonuçları</h2>
          <button onClick={handleBackToQuery} style={styles.buyButton2} type='submit'>Öne Çıkan Laptoplara Geri Dön</button>
       
          <div style={styles.featuredContainer}>
            {searchResults.map((lap, idx) => (
              <div key={idx} style={styles.laptopCard}>
                <img
                  src={lap.image}
                  alt={lap.laptop_name}
                  style={styles.laptopImage}
                />
                <h3 style={styles.laptopName}>
                  {lap.laptop_name.split(" ").slice(0, 6).join(" ")}
                </h3>
                <p style={styles.laptopPrice}>Fiyat: {lap.price} TL</p>
                <p>{lap.summary}</p>
                <a
                  href={lap.link}
                  target="_blank"
                  rel="noreferrer"
                  style={styles.buyButton}
                >
                  Satıcıya Git
                </a>
              </div>
            ))}
          </div>
        </>
      )}

      {/* Footer */}
      <div style={styles.footer}>
        © 2025 LapAdvisor AI. Tüm hakları saklıdır.
      </div>
    </div>
  );
}

// Stil objesi (inline CSS)
const styles = {
  container: {
    fontFamily: 'sans-serif',
    margin: 0,
    padding: 0
  },
  hero: {
    background: 'linear-gradient(to right, #1e3c72, #2a5298)',
    color: '#fff',
    textAlign: 'center',
    padding: '3rem 1rem'
  },
  heroTitle: {
    fontSize: '3rem',
    marginBottom: '1rem'
  },
  heroSubtitle: {
    fontSize: '1.2rem'
  },
  searchSection: {
    textAlign: 'center',
    marginTop: '-1.5rem'
  },
  searchForm: {
    display: 'inline-block',
    background: '#fff',
    padding: '1rem',
    borderRadius: '8px',
    boxShadow: '0 2px 5px rgba(0,0,0,0.2)'
  },
  searchInput: {
    padding: '0.5rem',
    fontSize: '1rem',
    marginRight: '0.5rem'
  },
  searchButton: {
    padding: '0.6rem 1rem',
    backgroundColor: '#424141',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer'
  },
  featuredTitle: {
    textAlign: 'center',
    margin: '2rem 0 1rem',
    fontSize: '1.8rem'
  },
  searchTitle: {
    textAlign: 'center',
    fontSize: '1.8rem'
  },
  featuredContainer: {
    display: 'flex',
    justifyContent: 'center',
    gap: '1.5rem',
    flexWrap: 'wrap',
    padding: '0 1rem'
  },
  laptopCard: {
    display: 'flex',
    flexDirection: 'column',
    width: '220px',
    backgroundColor: '#fff',
    borderRadius: '8px',
    boxShadow: '0 2px 5px rgba(0,0,0,0.1)',
    padding: '1rem',
    textAlign: 'center'
  },
  laptopImage: {
    width: '100%',
    height: 'auto',
    margin: '0 auto',
    display: 'block',
    objectFit: 'cover'
  },
  laptopName: {
    fontSize: '1.1rem',
    margin: '0.5rem 0'
  },
  laptopPrice: {
    color: 'red',
    fontWeight: 'bold'
  },
  laptopSummary: {
    fontSize: '0.6rem',
    margin: '0.5rem 0'
  },
  buyButton: {
    display: 'inline-block',
    marginTop: 'auto',
    backgroundColor: '#424141',
    color: '#fff',
    padding: '0.5rem 1rem',
    textDecoration: 'none',
    borderRadius: '4px'
  },
  footer: {
    textAlign: 'center',
    marginTop: '2rem',
    padding: '1rem',
    backgroundColor: '#f2f2f2',
    fontSize: '0.9rem'
  },
  searchContainer: {
    display: 'flex',
    flexDirection: 'row',
    justifyContent: 'center',
    padding: '1rem 0'
  },
  buyButton2: {
    
    display: 'flex',
    justifyContent: 'center',
    margin:'1rem auto',
    textAlign: 'center',
    backgroundColor: '#424141',
    color: '#fff',
    padding: '0.5rem 1rem',
    textDecoration: 'none',
    borderRadius: '4px'
  },
  laptopLink: {
    color: 'gold',
    textDecoration: 'none',
    fontWeight: 'bold'
  }
};
