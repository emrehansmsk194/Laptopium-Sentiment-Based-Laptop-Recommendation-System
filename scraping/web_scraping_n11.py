import logging
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Loglama ayarları
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Tarayıcı ayarları
driver_path = "C:\\Users\\EMREHAN\\PycharmProjects\\geckodriver.exe"
service = Service(driver_path)
driver = webdriver.Firefox(service=service)
driver.set_page_load_timeout(30)

# Temel URL (n11 dizüstü bilgisayar ürünleri, yorumlara göre sıralanmış)
base_url = "https://www.n11.com/bilgisayar/dizustu-bilgisayar?srt=REVIEWS&pg="

def scrape_products(page_limit=25, products_per_page=20):
    """
    Belirtilen sayfa aralığında, her sayfadan 'products_per_page' kadar ürün bilgisini çekerek bir liste oluşturur.
    Her ürün için isim, fiyat ve detay sayfası linki alınır.
    """
    products = []
    for page_number in range(1, page_limit + 1):
        url = base_url + str(page_number)
        logging.info(f"{page_number}. sayfa işleniyor: {url}")
        try:
            driver.get(url)
            # Ürün elementlerinin yüklenmesini bekle
            WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "pro"))
            )
        except Exception as e:
            logging.error(f"{page_number}. sayfa yüklenirken hata: {e}")
            continue

        # Dinamik içerik yüklenebilmesi için sayfayı aşağı kaydır
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        try:
            product_elements = driver.find_elements(By.CLASS_NAME, "pro")
        except Exception as e:
            logging.error(f"{page_number}. sayfada ürün elementleri bulunamadı: {e}")
            continue

        # Sadece belirtilen ürün sayısını al
        for product in product_elements[:products_per_page]:
            try:
                product_name = product.find_element(By.CLASS_NAME, "productName").text.strip()
                product_price = product.find_element(By.CLASS_NAME, "newPrice").text.strip()
                product_link = product.find_element(By.CSS_SELECTOR, "a.plink").get_attribute("href")
                product_image = product.find_element(By.CSS_SELECTOR, "img.lazy.cardImage").get_attribute("data-original")
                products.append({
                    "Product Name": product_name,
                    "Price": product_price,
                    "Link": product_link,
                    "Image": product_image 
                })
            except Exception as e:
                logging.warning(f"Ürün bilgileri çekilirken hata: {e}")
                continue

    logging.info(f"Toplamda {len(products)} ürün çekildi.")
    return products

def scrape_reviews_for_product(product_link, max_reviews=100):
    """
    Belirtilen ürün detay sayfasında yorumları çekerek, maksimum 'max_reviews' kadar yorumu liste olarak döndürür.
    Her yorum için tarih, rating ve yorum metni alınır. 
    "a.next.navigation" butonuna tıklayarak sonraki sayfalardaki yorumlar da çekilir.
    """
    reviews = []
    try:
        driver.get(product_link)
        # İlk sayfadaki yorumların yüklenmesini bekle
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "comment"))
        )
        time.sleep(3)
    except Exception as e:
        logging.error(f"Ürün detay sayfası ({product_link}) yüklenirken hata: {e}")
        return reviews

    while True:
        try:
            # Mevcut sayfadaki tüm yorum elementlerini al
            comment_elements = driver.find_elements(By.CLASS_NAME, "comment")
            for comment in comment_elements:
                if len(reviews) >= max_reviews:
                    break
                try:
                    comment_date = comment.find_element(By.CLASS_NAME, "commentDate").text.strip()
                    rating_element = comment.find_element(By.CLASS_NAME, "ratingCont")
                    rating_class = rating_element.find_element(By.TAG_NAME, "span").get_attribute("class")
                    rating_parts = rating_class.split(' ')
                    rating = rating_parts[1].replace('r', '') if len(rating_parts) > 1 else rating_parts[0].replace('r', '')
                    comment_text = comment.find_element(By.TAG_NAME, "p").text.strip()
                    review_str = f"{comment_date} | Rating: {rating} | Comment: {comment_text}"
                    if review_str not in reviews:
                        reviews.append(review_str)
                except Exception as e:
                    logging.warning(f"Bir yorum çekilirken hata oluştu: {e}")
                    continue

            # Eğer maksimum yorum sayısına ulaştıysak döngüden çık
            if len(reviews) >= max_reviews:
                break

            # "Sonraki" butonunu bulmaya çalış (yorumlar için sayfalama)
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, "a.next.navigation")
                if next_button:
                    logging.info("Sonraki sayfa butonuna tıklanıyor...")
                    # Butonun görünür olmasını sağlamak için kaydırma yapabiliriz
                    driver.execute_script("arguments[0].scrollIntoView();", next_button)
                    next_button.click()
                    # Yeni sayfanın yüklenmesi için bekleme süresi (durumunuza göre ayarlanabilir)
                    time.sleep(3)
                else:
                    logging.info("Sonraki sayfa butonu bulunamadı, döngü sonlandırılıyor.")
                    break
            except Exception as e:
                logging.info("Sonraki sayfa butonu bulunamadı veya tıklanamadı, döngü sonlandırılıyor.")
                break

        except Exception as e:
            logging.error(f"Yorumlar çekilirken hata oluştu: {e}")
            break

    return reviews


def main():
    # Ürünleri çek
    products = scrape_products(page_limit=25, products_per_page=20)
    
    # Her ürün için detay sayfasından yorumları çek
    for product in products:
        logging.info(f"Ürün için yorumlar çekiliyor: {product['Product Name']}")
        product_reviews = scrape_reviews_for_product(product["Link"], max_reviews=100)
        product["Reviews"] = " || ".join(product_reviews)
    
    driver.quit()
    
    # Verileri CSV dosyasına aktar
    df = pd.DataFrame(products)
    df.to_csv("datasets/n11_products.csv", index=False)
    logging.info("Veri çekme işlemi tamamlandı ve CSV dosyasına kaydedildi.")

if __name__ == "__main__":
    main()

