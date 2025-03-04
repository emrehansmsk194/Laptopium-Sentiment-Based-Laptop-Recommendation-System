import pandas as pd

def generate_detailed_summary(group):
    """
    Verilen laptop yorum grubundan, duygu dağılımı ve belirlenen anahtar kelimelerin sıklığına göre
    daha detaylı bir özet üretir.
    
    group: Her bir laptopa ait yorumları içeren DataFrame.
    """
    # Duygu dağılımını hesapla
    sentiments = group['label'].value_counts()
    total_reviews = len(group)
    positive_percentage = (sentiments.get('pozitif', 0) / total_reviews) * 100

    # Tüm yorumları birleştir ve küçük harfe çevir
    all_reviews = " ".join(group['Reviews'].astype(str).tolist()).lower()

    # Kullanılacak anahtar kelime listeleri
    positive_keywords = ['fiyat', 'performans', 'hız', 'tasarım', 'ekran', 'işlemci', 'ram', 'depolama']
    negative_keywords = ['pil', 'ısınma', 'gürültü', 'garanti', 'servis', 'sorun', 'hata']

    # Her anahtar kelimenin metindeki geçiş sayısını hesapla
    pos_counts = {kw: all_reviews.count(kw) for kw in positive_keywords}
    neg_counts = {kw: all_reviews.count(kw) for kw in negative_keywords}

    summary_parts = []

    # Detaylı özet oluşturma kuralları
    if positive_percentage >= 70:
        summary_parts.append("Kullanıcılar genel olarak üründen çok memnun.")
        # Belirli pozitif konular varsa, detay ekle
        pos_details = [kw for kw, count in pos_counts.items() if count > 3]
        if pos_details:
            summary_parts.append("Özellikle " + ", ".join(pos_details) + " konusunda övgüler mevcut.")
    elif positive_percentage >= 50:
        summary_parts.append("Kullanıcılar ürünü genel olarak olumlu değerlendiriyor, ancak bazı eksiklikler belirtilmiş.")
        # Negatif anahtar kelimeleri kontrol et
        neg_details = [kw for kw, count in neg_counts.items() if count > 2]
        if neg_details:
            summary_parts.append("Özellikle " + ", ".join(neg_details) + " konularında eleştiriler var.")
    else:
        summary_parts.append("Kullanıcı deneyimleri genel olarak olumsuz.")
        # Negatif konulara dair detay ekle
        neg_details = [kw for kw, count in neg_counts.items() if count > 2]
        if neg_details:
            summary_parts.append("Özellikle " + ", ".join(neg_details) + " konularında şikayetler öne çıkıyor.")

    return " ".join(summary_parts)


def analyze_laptop_reviews(csv_path):
    """
    CSV dosyasındaki laptop yorumlarını analiz eder:
      - Ürünlere göre gruplar,
      - Her grup için duygu dağılımı hesaplar,
      - Detaylı özet üretir.
    """
    df = pd.read_csv(csv_path)
    
    # "Product Name" sütununa göre gruplama
    grouped = df.groupby('Product Name')
    results = []

    for laptop_name, group in grouped:
        # Detaylı özet oluştur
        summary = generate_detailed_summary(group)
        
        sentiments = group['label'].value_counts()
        total_reviews = len(group)
        positive_percentage = (sentiments.get('pozitif', 0) / total_reviews) * 100
        neutral_percentage  = (sentiments.get('nötr', 0) / total_reviews) * 100
        negative_percentage = (sentiments.get('negatif', 0) / total_reviews) * 100
        
        # Fiyat bilgisini ilk kayıttan alalım (varsayım: tüm kayıtlar aynı fiyatı içeriyor)
        price = group.iloc[0]['Price']
        
        results.append({
            'laptop_name': laptop_name,
            'total_reviews': total_reviews,
            'positive_percentage': round(positive_percentage, 1),
            'neutral_percentage': round(neutral_percentage, 1),
            'negative_percentage': round(negative_percentage, 1),
            'price': price,
            'summary': summary
        })
        
    return results

if __name__ == "__main__":
    # CSV dosya yolunu belirtin
    csv_path = "C://Users/Emrehan/Desktop/Emrehan Simsek/veri çekme selenium/training/all_laptop_reviews.csv"
    results = analyze_laptop_reviews(csv_path)
    
    # Sonuçları yazdırma
    for res in results[:100]:
        print("="*50)
        print(f"Laptop: {res['laptop_name']}")
        print(f"Fiyat: {res['price']}")
        print(f"Toplam Yorum: {res['total_reviews']}")
        print(f"Pozitif: %{res['positive_percentage']}")
        print(f"Nötr: %{res['neutral_percentage']}")
        print(f"Negatif: %{res['negative_percentage']}")
        print("Özet:", res['summary'])
