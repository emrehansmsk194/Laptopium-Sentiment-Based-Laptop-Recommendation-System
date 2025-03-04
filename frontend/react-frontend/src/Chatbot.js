import React, { useState } from 'react';

function Chatbot() {
  const [message, setMessage] = useState('');
  const [conversation, setConversation] = useState([]);

  // Tek parça handleSend fonksiyonu:
  const handleSend = async () => {
    if (!message.trim()) return; // Boş mesaj yollamayalım

    // 1) Kullanıcı mesajını ekrana ekle
    setConversation((prev) => [
      ...prev,
      { sender: 'user', text: message }
    ]);

    try {
      // 2) Flask'taki /chat endpoint'ine POST isteği at
      const response = await fetch('http://localhost:5000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
      });

      if (!response.ok) {
        // istersen burada bir hata mesajı yazma, sessiz geçebilirsin
        return;
      }

      // 3) Yanıtı JSON olarak parse et
      const data = await response.json();
      // data örneği: { "message": "Önerilen ürünler", "data": [ { "laptop_name": "...", "price": "...", "link": "..." }, ... ] }

      // 4) Sohbete bot mesajı ekle
      //    "message" normal metin, "data" da varsa laptop listesi
      setConversation((prev) => [
        ...prev,
        {
          sender: 'bot',
          // text: data.message, // eğer sadece text göstereceksen
          // Yukarıdaki "text" alanını iptal edip, hem "message" hem "data" tutabiliriz
          // Aşağıda "recommendations" diye kaydediyoruz
          text: data.message || data.response,            // "Önerilen ürünler" vb.
          recommendations: data.data || []     // Laptop listesi
        }
      ]);
    } catch (err) {
      console.error(err);
    }

    // 5) Metin kutusunu temizle
    setMessage('');
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Chatbot</h2>
      <p style={styles.hero}>Chatbot ile gelişmiş öneri sistemini kullanabilirsiniz.</p>

      <div style={styles.chatWindow}>
        {conversation.map((msg, index) => (
          <div key={index} style={styles.messageBlock}>
           
            <p style={{
                backgroundColor: msg.sender === 'user' ? '#f0f0f0' : '#e1f7d5',
                textAlign: msg.sender === 'user' ? 'right' : 'left',
                border: '1px solid #ccc',
                borderRadius: '8px',
                padding: '0.5rem'
            }}><strong>{msg.sender === 'user' ? 'Sen' : 'Bot'}:</strong> {msg.text}</p>

            {/* Eğer msg.recommendations varsa, HTML formatıyla göster */}
            {msg.recommendations && msg.recommendations.length > 0 && (
              <div style={styles.recommendationContainer}>
                {msg.recommendations.map((item, idx) => (
                  <div key={idx} style={styles.recommendationCard}>
                    <img src={item.image} width={'200px'}></img>
                    <p style={{ fontWeight: 'bold' }}>{item.laptop_name}</p>
                    <p>Fiyat: {item.price}</p>
                    <p>
                        <button style={styles.button}>
                      <a href={item.link} target="_blank" rel="noreferrer" style={styles.link}>
                        Satıcıya Git
                      </a>
                      </button>
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      <div style={styles.inputArea}>
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Mesaj yaz..."
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              handleSend();
            }
          }}
          style={styles.input}
        />
        <button onClick={handleSend} style={styles.sendButton}>
          Gönder
        </button>
      </div>
    </div>
  );
}

// Stil nesneleri
const styles = {
  container: {
    maxWidth: '600px',
    margin: '2rem auto',
    fontFamily: 'sans-serif',
    border: '1px solid #ccc',
    borderRadius: '8px',
    padding: '1rem',
    backgroundImage: 'url("/images/tipos-de-chatbots.webp")',
    backgroundSize: 'cover',
    backgroundPosition: 'center'
  },
  title: {
    textAlign: 'center',
    color: 'white'
  },
  chatWindow: {
    border: 'none',
    borderRadius: '4px',
    minHeight: '100px',
    padding: '1rem',
    marginBottom: '1rem',
    overflowY: 'auto'
  },
  messageBlock: {
    marginBottom: '1rem'
  },
  recommendationContainer: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '1rem',
    marginTop: '0.5rem',
    textAlign: 'center'
  },
  recommendationCard: {
    border: '1px solid #ddd',
    borderRadius: '4px',
    padding: '0.5rem',
    minWidth: '566px',
    backgroundColor: '#f9f9f9'
  },
  inputArea: {
    display: 'flex',
    gap: '0.5rem'
  },
  input: {
    flex: 1,
    padding: '0.5rem'
  },
  sendButton: {
    padding: '0.5rem 1rem',
    backgroundColor: '#ff3e3e',
    border: 'none',
    borderRadius: '4px',
    color: '#fff',
    cursor: 'pointer'
  },
  button: {
    padding: '0.5rem 1rem',
    backgroundColor: '#424141',
  },
  link: {
    textDecoration: 'none',
    color: '#fff'
  },
  hero: {
    fontFamily: 'sans-serif',
    fontWeight: 'bold',
    textAlign: 'center',
    fontSize: '1.1em',
    color: 'white'
  }
};

export default Chatbot;
