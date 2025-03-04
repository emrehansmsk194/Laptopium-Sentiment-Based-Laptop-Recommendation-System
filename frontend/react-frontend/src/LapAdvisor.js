import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import Chatbot from './Chatbot';

function LapAdvisor() {
  const [minPrice, setMinPrice] = useState('');
  const [maxPrice, setMaxPrice] = useState('');
  const [laptops, setLaptops] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const minVal = parseFloat(minPrice);
    const maxVal = parseFloat(maxPrice);

    if(minVal >= maxVal){
      setError('Min fiyat, max fiyattan büyük veya eşit olamaz!');
      setLoading(false);
      return;
    }

    fetch(`http://localhost:5000/top_laptops?minPrice=${minPrice}&maxPrice=${maxPrice}`)
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

  return (
    <div style={styles.container}>
       <img src="/images/1893363172985225217.jpg" alt="Laptop" width="300"/>
      <h1 style={styles.title}>LapAdvisor AI</h1>
     

      <p>
        LapAdvisor AI, E-Ticaret sitelerinde satılan bütün laptoplara gelen kullanıcı yorumlarını analiz eder
        ve size kullanıcılar tarafından en çok beğenilen laptopları önerir. 
      </p>
      <p>
        Aşağıdaki formu kullanarak fiyat aralığı belirleyerek size önerilen laptopları görebilirsiniz.
      </p>
      <h3>Fiyat aralığı dışında daha detaylı filtreleme yapmak isterseniz<Link to="/Chatbot" style={{
        textDecoration: 'none',
        color: 'red',
        marginLeft: '0.5rem',
        fontWeight: 'bold',
        fontSize: '1em'
      }}>Chatbot</Link> kullanabilirsiniz. </h3>

      <form onSubmit={handleSubmit} style={styles.form}>
        <label>
          Min Fiyat(TL):
          <input
            type="number"
            value={minPrice}
            onChange={(e) => setMinPrice(e.target.value)}
            style={styles.input}
          />
        </label>

        <label>
          Max Fiyat(TL):
          <input
            type="number"
            value={maxPrice}
            onChange={(e) => setMaxPrice(e.target.value)}
            style={styles.input}
          />
        </label>

        <button type="submit" style={styles.filterButton}>
          Laptop Öner
        </button>
      </form>

      {loading && <p>Yükleniyor...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}

      <div style={styles.results}>
        <h1 style = {styles.title}>Önerilen Laptoplar</h1>
        {laptops.map((item, index) => (
          <div key={index} style={styles.listItem}>
            <img
              src={item.image}
              alt={item.laptop_name}
              style={styles.image}
            />

            <div style={styles.textContainer}>
              <h3 style={styles.laptopName}>{item.laptop_name}</h3>
              <p style={styles.summary}>{item.summary}</p>
              <p style={styles.priceStyle}>Fiyat: {item.price} TL</p>
              <button style={styles.button2}>
                <a
                  href={item.link}
                  target="_blank"
                  rel="noreferrer"
                  style={styles.link}
                >
                  Satıcı Sayfasına Git
                </a>
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

const styles = {
  // 1) Dış alanları daraltıp ortaladık, yukarıdan da boşluk verdik
  container: {
    maxWidth: '1000px',     // 1000px genişlik
    margin: '2rem auto',    // ortalama + yukarıdan 2rem boşluk
    padding: '1rem'
  },
  title: {
    fontSize: '1.8rem',
    marginBottom: '1rem'
  },
  form: {
    display: 'flex',
    gap: '1rem',
    marginBottom: '1.5rem'
  },
  input: {
    marginLeft: '0.5rem',
    padding: '0.3rem'
  },
  filterButton: {
    padding: '0.5rem 1rem',
    cursor: 'pointer'
  },
  // Tüm listeyi dikeyde alt alta
  results: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem'
  },
  // 2) List item stilini daha estetik yapalım
  listItem: {
    display: 'flex',
    flexDirection: 'row',
    border: '1px solid #ccc',
    borderRadius: '8px',
    padding: '1.5rem',
    backgroundColor: '#fff',
    alignItems: 'center',
    gap: '1rem',
    boxShadow: '0 2px 5px rgba(0,0,0,0.1)' // hafif gölge
  },
  image: {
    width: '180px',
    height: 'auto',
    objectFit: 'cover'
  },
  textContainer: {
    display: 'flex',
    flexDirection: 'column',
    flex: 1 // geri kalan alanı kaplasın
  },
  laptopName: {
    margin: '0 0 0.5rem 0',
    fontSize: '1.2rem',
    fontWeight: 'bold'
  },
  summary: {
    marginBottom: '0.5rem'
  },
  priceStyle: {
    color: 'red',
    fontWeight: 'bold',
    fontSize: '1.1rem',
    marginBottom: '0.5rem'
  },
 
  button2: {
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
    fontWeight: 'bold',
    fontSize: '0.9rem' 
  },
  chatbotContainer: {
    display: 'flex',
    justifyContent: 'right',
    alignItems: 'right',
    marginBottom: '1rem',
    width: '50%',
    marginLeft: '2.5rem',
    padding: '1rem',
  }
};

export default LapAdvisor;
