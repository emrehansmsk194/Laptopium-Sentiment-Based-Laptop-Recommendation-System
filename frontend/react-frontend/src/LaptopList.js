import React, { useState, useEffect } from 'react';

function LaptopList() {
  const [laptops, setLaptops] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [query, setQuery] = useState('');
  const [page, setPage] = useState(1);
  const limit = 20;         // Sayfa başına 20 kayıt
  const [total, setTotal] = useState(0);


  useEffect(() => {
    fetchData();
  }, [page]);


  const fetchData = () => {
    setLoading(true);
    setError('');

   
    let url = '';
    if (!query.trim()) {
      url = `http://localhost:5000/get_all_laptops?page=${page}&limit=${limit}`;
    } else {
      url = `http://localhost:5000/laptops_by_name?query=${query}`;
    }

    fetch(url)
      .then((res) => {
        if (!res.ok) {
          throw new Error('Sunucu hatası');
        }
        return res.json();
      })
      .then((data) => {
        if (!query.trim()) {
          setLaptops(data.data || []);
          setTotal(data.total || 0);
        } else {
          setLaptops(data);
          setTotal(data.length); 
        }
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  };


  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1);
    fetchData();
  };

 
  const handlePrevPage = () => {
    if (page > 1) {
      setPage(page - 1);
    }
  };
  const handleNextPage = () => {
    const maxPage = Math.ceil(total / limit);
    if (page < maxPage) {
      setPage(page + 1);
    }
  };

  if (loading) {
    return <p>Yükleniyor...</p>;
  }

  return (
    <div>
      {/* Üst kısım */}
      <div style={styles.content}>
        <h1 style={styles.title}>Hoş Geldiniz</h1>
        <p style={styles.paragraph}>
          Burada en popüler laptopları bulabilir ve inceleyebilirsiniz.
        </p>
      </div>

      {/* Arama Formu */}
      <div style={{ textAlign: 'center', marginBottom: '1rem' }}>
        {error && <p style={{ color: 'red' }}>{error}</p>}
        <form onSubmit={handleSearch}>
          <input
            type="text"
            placeholder="Laptop adı veya marka ara..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            style={{ padding: '0.5rem' }}
          />
          <button type="submit" style={{ marginLeft: '0.5rem', padding: '0.5rem 1rem' }}>
            Ara
          </button>
        </form>
      </div>

      <h2 style={{ textAlign: 'center' }}>Tüm Laptoplar</h2>
      <ul style={styles.gridContainer}>
        {laptops.map((item, index) => (
          <li key={index} style={styles.gridItem}>
            <h3>{item.laptop_name}</h3>
            <img src={item.image} alt={item.laptop_name} width="250" />
            <p style={styles.priceStyle}>Fiyat: {item.price} TL</p>
            <div style={styles.reviewContainer}>
              <h4 style={styles.reviewTitle}>Kullanıcı Değerlendirmeleri</h4>
              <p style={styles.reviewText}>{item.summary}</p>
            </div>
            <button style={styles.button}>
              <a
                href={item.link}
                target="_blank"
                rel="noreferrer"
                style={styles.link}
              >
                Satıcı Sayfasına Git
              </a>
            </button>
          </li>
        ))}
      </ul>

      {/* Eğer query boşsa sayfalama göster */}
      {!query.trim() && (
        <div style={{ textAlign: 'center', margin: '1rem' }}>
          <button onClick={handlePrevPage} disabled={page <= 1}>
            Önceki
          </button>
          <span style={{ margin: '0 1rem' }}>
            Sayfa {page} / {Math.ceil(total / limit)}
          </span>
          <button
            onClick={handleNextPage}
            disabled={page >= Math.ceil(total / limit)}
          >
            Sonraki
          </button>
        </div>
      )}
    </div>
  );
}

const styles = {
  gridContainer: {
    display: 'grid',
    gridTemplateColumns: 'repeat(4, 1fr)',
    gap: '16px',
    listStyleType: 'none',
    padding: 0,
    margin: 0
  },
  gridItem: {
    border: '1px solid #ccc',
    padding: '16px',
    backgroundColor: '#fff',
    textAlign: 'center'
  },
  priceStyle: {
    color: 'red',
    fontWeight: 'bold',
    fontSize: '1.2em'
  },
  reviewContainer: {
    margin: '1.5 rem 0',
    padding: '1rem',
    backgroundColor: '#f8f8f8',
    borderRadius: '5px',
    height: '194px'
  },
  reviewTitle: {
    fontSize: '1.1rem',
    fontWeight: 'bold',
    marginBottom: '0.5rem'
  },
  reviewText: {
    fontSize: '0.95rem',
    lineHeight: '1.4',
    color: '#333'
  },
  button: {
    backgroundColor: '#424141',
    border: 'none',
    borderRadius: '4px',
    padding: '0.6rem 1rem',
    margin: 'auto', 
    cursor: 'pointer',
    width: '50%'
  },
  link: {
    color: '#fff',
    textDecoration: 'none',
    fontWeight: 'bold'
  },
  content: {
    padding: '1rem 2rem'
  },
  title: {
    fontSize: '2rem',
    marginBottom: '1rem'
  },
  paragraph: {
    fontSize: '1.1rem',
    marginBottom: '2rem'
  }
};

export default LaptopList;
