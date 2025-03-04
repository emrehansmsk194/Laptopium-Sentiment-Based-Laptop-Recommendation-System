import React, { useState } from 'react';

export default function FilterLaptops() {
  const [query, setQuery] = useState('');
  const [laptops, setLaptops] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    fetch(`http://localhost:5000/laptops_by_name?query=${query}`)
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
    <div>
      <form onSubmit={handleSubmit}>
        <input
          type='text'
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder='Marka veya model ara...'
        />
        <button type='submit'>Filtrele</button>
      </form>

      {loading && <p>Yükleniyor...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}

      {laptops.length === 0 && !loading && !error && (
        <p>Hiç sonuç bulunamadı.</p>
      )}

      {laptops.map((lap, idx) => (
        <div key={idx} style={{ border: '1px solid #ccc', margin: '1rem 0', padding: '1rem' }}>
          <h3>{lap.laptop_name}</h3>
          <p>Fiyat: {lap.price} TL</p>
          <p>{lap.summary}</p>
          <img src={lap.image} alt={lap.laptop_name} width={200} />
          <br />
          <a href={lap.link} target='_blank' rel='noreferrer'>
            Satıcıya Git
          </a>
        </div>
      ))}
    </div>
  );
}
