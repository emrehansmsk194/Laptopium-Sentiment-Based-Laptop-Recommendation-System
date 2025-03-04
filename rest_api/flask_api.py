from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import math
import numpy as np
import nltk
import warnings
import re 

nltk.download('punkt_tab')
app = Flask(__name__)
CORS(app)

df = pd.read_csv("C://Users/Emrehan/Desktop/Emrehan Simsek/veri çekme selenium/training/all_laptop_reviews.csv")
df_unique = df.drop_duplicates(subset=['Product Name']).reset_index(drop=True)
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    tokens = nltk.word_tokenize(text, language='turkish')
    return tokens

def extract_brand(query):
    brands = ["asus", "lenovo", "dell", "hp", "acer", "msi", "apple", "razer", "monster", "casper", "huawei", "samsung"]
    query_lower = query.lower()
    for brand in brands:
        if brand in query_lower:
            return brand
    return None

def extract_ram(query):
    match = re.search(r'(\d+)\s*gb', query, re.IGNORECASE)
    if match:
        return match.group(1)  # Örneğin "16"
    return None


def convert_price(price_str):
    cleaned = price_str.replace("TL", "").strip()
    if ',' in cleaned:
        cleaned = cleaned.replace('.', '').replace(',', '.')
    else:
        cleaned = cleaned.replace('.', '')
    return float(cleaned)

def greet(text):
    cleaned_text = re.sub(r'[^\w\s]', '', text.lower())
    greetings = ['merhaba', 'selam', 'iyi günler']
    for word in greetings:
        if word in cleaned_text.split():
            return "Merhaba, nasıl yardımcı olabilirim?"
    return None

def get_top_laptops_by_keywords(query, df, top_n=5):
    # Sorgudan marka ve RAM bilgilerini ayıklıyoruz.
    brand = extract_brand(query)
    ram = extract_ram(query)
    
    # Sorguyu ön işleme tabi tutarak anahtar kelimeleri elde ediyoruz.
    keywords = preprocess_text(query)
    if not keywords:
        return "Üzgünüm, arama kriterlerini belirleyemedim."
    
    # Ürün başlıklarının ön işlenmiş hali yoksa oluşturuyoruz.
    if 'preprocessed_str' not in df.columns:
        df['preprocessed_title'] = df['Product Name'].apply(preprocess_text)
        df['preprocessed_str'] = df['preprocessed_title'].apply(lambda tokens: ' '.join(tokens))
    
    # Eğer marka varsa, sadece o markalı ürünleri filtreleyelim.
    if brand:
        df = df[df['preprocessed_str'].str.contains(brand, flags=re.IGNORECASE, na=False)]
    
    # Eğer sorguda RAM bilgisi varsa, ürün başlığında bu değerin geçmesini bekleyelim.
    if ram:
        ram_pattern = rf'\b{ram}\s*gb\b'
        df = df[df['preprocessed_str'].str.contains(ram_pattern, flags=re.IGNORECASE, na=False)]
    
    # Esnek eşleşme: Sorgudaki diğer kelimelerin eşleşme skorunu hesaplıyoruz.
    def keyword_match_score(text):
        tokens = text.split()
        matches = sum(1 for keyword in keywords if keyword in tokens)
        return matches
    
    df['match_score'] = df['preprocessed_str'].apply(keyword_match_score)
    filtered_df = df[df['match_score'] > 0]
    
    if filtered_df.empty:
        return "Belirttiğiniz kriterlere uygun ürün bulunamadı."
    
    # Yorumlardan skor hesaplaması (ürün bazında)
    scores = filtered_df.groupby('Product Name').apply(compute_laptop_score).reset_index(name='score')
    merged_df = filtered_df.merge(scores, on='Product Name')
    
    # Aynı üründen tekrar edenleri temizleyip skor üzerinden sıralıyoruz.
    sorted_df = merged_df.sort_values(by='score', ascending=False).drop_duplicates(subset=['Product Name']).head(top_n)
    
    # Sonuçları oluşturuyoruz.
    recommendations = []
    for _, row in sorted_df.iterrows():
        recommendations.append({
            "laptop_name": row["Product Name"],
            "image": row["Image"],
            "price": row["Price"],
            "link": row["Link"]
        })

    return {
        "message": "Önerilen ürünler (Kullanıcılar tarafından en fazla olumlu yorum alanlar):",
        "data": recommendations
    }

df['Price'] = df['Price'].apply(convert_price)

def generate_detailed_summary(group):
    sentiments = group["label"].value_counts() 
    total_reviews = len(group) 
    positive_percentage = (sentiments.get("pozitif", 0) / total_reviews) * 100 if total_reviews > 0 else 0
    all_reviews = " ".join(group['Reviews'].astype(str).tolist()).lower()

    positive_keywords = ['fiyat','performans','hız','tasarım','ekran','işlemci','ram','depolama']
    negative_keywords = ['pil', 'ısınma', 'gürültü', 'garanti', 'servis', 'sorun', 'hata']

    pos_counts = {kw: all_reviews.count(kw) for kw in positive_keywords}
    neg_counts = {kw: all_reviews.count(kw) for kw in negative_keywords}
    summary_parts = []

    if positive_percentage >= 70:
        summary_parts.append(f"%{positive_percentage:.2f} oranında olumlu yorum var.")
        summary_parts.append("Kullanıcılar genel olarak üründen çok memnun.")
        pos_details = [kw for kw, count in pos_counts.items() if count > 3]
        if pos_details:
            summary_parts.append("Özellikle " + ", ".join(pos_details) + " konusunda övgüler mevcut.")
    elif positive_percentage >= 50:
        summary_parts.append("Kullanıcılar ürünü genel olarak olumlu değerlendiriyor, ancak bazı eksiklikler belirtilmiş.")
        neg_details = [kw for kw, count in neg_counts.items() if count > 2]
        if neg_details:
            summary_parts.append("Özellikle " + ", ".join(neg_details) + " konularında eleştiriler var.")   
    else:
        summary_parts.append("Kullanıcı deneyimleri genel olarak olumsuz.")
        neg_details = [kw for kw, count in neg_counts.items() if count > 2]
        if neg_details:
            summary_parts.append("Özellikle " + ", ".join(neg_details) + " konularında şikayetler öne çıkıyor.")
    return " ".join(summary_parts)

def compute_laptop_score(group):
    sentiments = group["label"].value_counts()
    total_reviews = len(group)
    if total_reviews == 0:
        return 0
    positive_percentage = (sentiments.get("pozitif", 0) / total_reviews) * 100
    score = positive_percentage * math.log(total_reviews + 1)
    return score





@app.route('/top_laptops', methods=['GET'])
def get_top_laptops():
    try:
        min_price = float(request.args.get('minPrice', 0))
        max_price = float(request.args.get('maxPrice', 1e9))
    except ValueError:
        return jsonify({"error": "Geçersiz fiyat parametreleri!"}), 400
    
    filtered_df = df[(df['Price'] >= min_price) & (df['Price'] <= max_price)]
    grouped = filtered_df.groupby('Product Name')
    laptops = []
    for laptop_name, group in grouped:
        score = compute_laptop_score(group)
        summary = generate_detailed_summary(group)
        price = group.iloc[0]['Price']
        image = group.iloc[0]['Image'] if 'Image' in group.columns else ""
        link = group.iloc[0]['Link'] if 'Link' in group.columns else ""
        
        laptops.append({
            "laptop_name": laptop_name,
            "image": image,
            "link": link,
            "price": price,
            "summary": summary,
            "score": score
            
        })
    laptops = sorted(laptops, key=lambda x: x['score'], reverse=True)[:10]
    
    
    
    return jsonify(laptops)

@app.route('/get_all_laptops', methods=['GET'])
def get_all_laptops():
    page_param = request.args.get('page', None)
    limit_param = request.args.get('limit', None)

    grouped = df.groupby('Product Name')
    laptops = []
    for laptop_name, group in grouped:
        summary = generate_detailed_summary(group)
        price = group.iloc[0]['Price']
        image = group.iloc[0]['Image'] if 'Image' in group.columns else ""
        link = group.iloc[0]['Link'] if 'Link' in group.columns else ""

        laptops.append({
            "laptop_name": laptop_name,
            "image": image,
            "link": link,
            "price": price,
            "summary": summary
        })

    total_laptops = len(laptops)

    # Eğer page veya limit parametresi gelmezse (None veya boş),
    # tüm laptopları döndürüyoruz.
    if not page_param and not limit_param:
        return jsonify({
            "page": None,
            "limit": None,
            "total": total_laptops,
            "data": laptops
        })

    # Aksi halde sayfalama yapalım
    try:
        page = int(page_param or 1)
        limit = int(limit_param or 20)
    except ValueError:
        return jsonify({"error": "Geçersiz sayfa parametreleri!"}), 400

    start_index = (page - 1) * limit
    end_index = start_index + limit

    laptops_page = laptops[start_index:end_index]

    return jsonify({
        "page": page,
        "limit": limit,
        "total": total_laptops,
        "data": laptops_page
    })

@app.route('/laptops_by_name', methods=['GET'])
def get_laptops_byName():
    try:
        query = request.args.get('query', None)
    except ValueError:
        return jsonify({"error": "Geçersiz arama parametresi!"}), 400
    filtered_df = df[df['Product Name'].astype(str).str.contains(query, case=False, na=False)]
    grouped = filtered_df.groupby('Product Name')
    laptops = []
    for laptop_name, group in grouped:
        summary = generate_detailed_summary(group)
        price = group.iloc[0]['Price']
        image = group.iloc[0]['Image'] if 'Image' in group.columns else ""
        link = group.iloc[0]['Link'] if 'Link' in group.columns else ""

        laptops.append({
            "laptop_name": laptop_name,
            "image": image,
            "link": link,
            "price": price,
            "summary": summary
        })
    return jsonify(laptops)

@app.route('/most_reviewed_laptops', methods=['GET'])
def most_reviewed_laptops():
    grouped = df.groupby('Product Name')
    laptops = []
    for laptop_name, group in grouped:
        total_reviews = len(group)
        summary = generate_detailed_summary(group)
        price = group.iloc[0]['Price']
        image = group.iloc[0]['Image'] if 'Image' in group.columns else ""
        link = group.iloc[0]['Link'] if 'Link' in group.columns else ""

        laptops.append({
            "laptop_name": laptop_name,
            "total_reviews": total_reviews,
            "image": image,
            "link": link,
            "price": price,
            "summary": summary
        })
    laptops = sorted(laptops, key=lambda x: x['total_reviews'], reverse=True)[:5] # Bunların arasından rastgele 5 tane seçmeye çalış.
    return jsonify(laptops)


@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "Mesaj alanı boş olamaz!"}), 400
    user_message = data['message']

    greeting_response = greet(user_message)
    if greeting_response:
        return jsonify({"response": greeting_response})
    response_json = get_top_laptops_by_keywords(user_message, df_unique, top_n=5)
    return jsonify(response_json)
    
if __name__ == '__main__':
    app.run(port=5000,debug=True)