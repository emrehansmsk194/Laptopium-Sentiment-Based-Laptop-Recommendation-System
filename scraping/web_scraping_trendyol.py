from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import logging

# Loglama ayarları
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Tarayıcı ayarları
driver_path = "C:\\Users\\EMREHAN\\PycharmProjects\\geckodriver.exe"
service = Service(driver_path)
options = Options()
options.headless = False  # Headless modda çalıştırmak istersen True yapabilirsin
driver = webdriver.Firefox(service=service, options=options)
driver.set_page_load_timeout(30)

# Başlangıç URL'si (laptop arama sonucu)
url = "https://www.trendyol.com/sr?q=Laptop&qt=Laptop&st=Laptop&os=1&sst=MOST_RATED"


def load_page_with_retry(driver, url, retries=3, wait_selector=None, wait_time=15):
    """
    Sayfanın yüklenmesini, belirli bir elementin (wait_selector) görünmesini bekleyerek yapar.
    Yeniden deneme mekanizması ile çalışır.
    """
    for attempt in range(1, retries + 1):
        try:
            logging.info(f"Sayfa yükleniyor: {url} (Deneme {attempt}/{retries})")
            driver.get(url)
            if wait_selector:
                WebDriverWait(driver, wait_time).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector))
                )
            return True
        except Exception as e:
            logging.warning(f"Sayfa yüklenirken hata oluştu (Deneme {attempt}): {e}")
            time.sleep(3)
    logging.error(f"{retries} denemede sayfa yüklenemedi: {url}")
    return False


def scroll_slowly(driver, pause_time=2, scroll_amount=400):
    """
    Sayfanın en altına kadar kademeli olarak scroll yapar.
    """
    try:
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            time.sleep(pause_time)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                logging.info("Sayfanın en altına ulaşıldı.")
                break
            last_height = new_height
        return True
    except Exception as e:
        logging.error(f"Scroll işlemi sırasında hata: {e}")
        return False


def scrape_products(driver, max_products=300):
    """
    Ürün listesini çekerek, ürün adı, fiyat, ürün sayfası URL'si ve resim URL'sini toplar.
    """
    products = []
    product_links_set = set()

    # İlk olarak ürünlerin yer aldığı elementlerin sayfada göründüğünü bekle
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "p-card-chldrn-cntnr"))
        )
    except Exception as e:
        logging.error(f"Ürün elemanları beklenirken hata: {e}")
        return products

    while len(products) < max_products:
        try:
            product_elements = driver.find_elements(By.CLASS_NAME, "p-card-chldrn-cntnr")
            logging.info(f"Mevcut görünümde {len(product_elements)} ürün bulundu.")
            for product in product_elements:
                if len(products) >= max_products:
                    break
                try:
                    # Ürün linkini al
                    link_element = product.find_element(By.TAG_NAME, "a")
                    product_link = link_element.get_attribute("href")
                    if product_link in product_links_set:
                        continue
                    product_links_set.add(product_link)

                    # Ürün adını oluştur (iki farklı elementten)
                    product_title_1 = product.find_element(By.CLASS_NAME, "prdct-desc-cntnr-ttl").text.strip()
                    product_title_2 = product.find_element(By.CLASS_NAME, "prdct-desc-cntnr-name").text.strip()
                    product_name = f"{product_title_1} {product_title_2}"

                    # Ürün fiyatını al
                    product_price = product.find_element(By.CLASS_NAME, "prc-box-dscntd").text.strip()

                    # Resim URL'sini al
                    product_image = product.find_element(By.CLASS_NAME, "p-card-img").get_attribute("src")

                    products.append({
                        "Product Name": product_name,
                        "Price": product_price,
                        "Link": product_link,
                        "Image": product_image
                    })
                except Exception as e:
                    logging.warning(f"Ürün bilgileri çekilirken hata: {e}")
                    continue
        except Exception as e:
            logging.error(f"Ürün listesini çekerken hata: {e}")

        # Yeni ürünler yükleniyorsa sayfayı aşağı kaydır
        if not scroll_slowly(driver, pause_time=2, scroll_amount=400):
            break

    logging.info(f"Toplamda {len(products)} ürün çekildi.")
    return products


def scrape_reviews_for_product(driver, product_url, max_reviews=100):
    """
    Ürün detay sayfasında yorumları çekerek, maksimum belirlenen sayıda (max_reviews) yorum toplar.
    """
    reviews = []
    # Ürün detay sayfasını yükle ve 'Tüm Yorumları Göster' butonunun görünmesini bekle
    if not load_page_with_retry(driver, product_url, retries=3, wait_selector=".navigate-all-reviews-btn"):
        return reviews
    try:
        show_all_reviews_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "navigate-all-reviews-btn"))
        )
        driver.execute_script("arguments[0].click();", show_all_reviews_button)
        # Yorumların yüklendiğine dair bekleme
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "comment-text"))
        )
        time.sleep(2)
    except Exception as e:
        logging.warning(f"'Tüm Yorumları Göster' butonuna tıklanırken hata: {e}")
        return reviews

    try:
        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        while scroll_attempts < 20 and len(reviews) < max_reviews:
            review_elements = driver.find_elements(By.CLASS_NAME, "comment-text")
            for review in review_elements:
                text = review.text.strip()
                if text and text not in reviews:  # Aynı yorumu tekrar çekmemek için
                    reviews.append(text)
                    if len(reviews) >= max_reviews:
                        break
            # Daha fazla yorum yüklenmesi için aşağı kaydır
            driver.execute_script("window.scrollBy(0, 900);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                logging.info("Yorumlar kısmında en alta ulaşıldı.")
                break
            last_height = new_height
            scroll_attempts += 1
    except Exception as e:
        logging.error(f"Yorumlar çekilirken hata oluştu: {e}")

    logging.info(f"Ürün {product_url} için {len(reviews)} yorum çekildi.")
    return reviews


# -------------------------
# Ana kod bloğu
# -------------------------
if __name__ == "__main__":
    # Ana ürün listesinin olduğu sayfayı explicit wait ile yükle
    if not load_page_with_retry(driver, url, retries=3, wait_selector=".p-card-chldrn-cntnr"):
        driver.quit()
        exit("Ürün listesinin olduğu sayfa yüklenemedi.")

    # Ürünleri çek
    products = scrape_products(driver, max_products=300)

    # Tüm ürünler için detay sayfasında yorumları çek
    for idx, product in enumerate(products, start=1):
        logging.info(f"{idx}. ürünün yorumları çekiliyor: {product['Product Name']}")
        reviews = scrape_reviews_for_product(driver, product["Link"], max_reviews=100)
        product["Reviews"] = " || ".join(reviews)

    driver.quit()

    # Verileri CSV olarak kaydet
    df = pd.DataFrame(products)
    df.to_csv("datasets/trendyol_products.csv", index=False)
    logging.info("Veri çekme işlemi tamamlandı. trendyol_products.csv dosyası oluşturuldu.")
