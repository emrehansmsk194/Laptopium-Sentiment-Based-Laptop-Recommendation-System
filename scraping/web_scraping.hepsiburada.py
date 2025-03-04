import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Selenium start options
options = Options()
options.add_argument("--start-maximized")  # Open browser in full screen
options.add_argument("--disable-blink-features=AutomationControlled")  # Anti-bot detection

# Start ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 15)

# Standart yavaş scroll fonksiyonu (listeleme sayfaları için)
def slow_scroll():
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollBy(0, document.body.scrollHeight / 10);")
        time.sleep(1.5)  # Daha yavaş scroll için bekleme süresi
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

# Yorum sayfalarında, sayfanın en altına kadar 10 piksellik adımlarla ve 0.1 saniyelik beklemeyle scroll yapan fonksiyon
def very_slow_scroll_to_bottom():
    while True:
        driver.execute_script("window.scrollBy(0, 50);")
        time.sleep(0.1)
        scroll_position = driver.execute_script("return window.innerHeight + window.pageYOffset")
        total_height = driver.execute_script("return document.body.scrollHeight")
        if scroll_position >= total_height:
            break

# Ürün linklerini toplamak için 1-10 sayfaları dolaşma
base_url = "https://www.hepsiburada.com/laptop-notebook-dizustu-bilgisayarlar-c-98"
all_product_links = []

for page in range(1, 11):
    page_url = f"{base_url}?siralama=yorumsayisi&sayfa={page}"
    driver.get(page_url)
    time.sleep(3)  # Sayfanın yüklenmesi için bekle
    slow_scroll()
    
    # Ürün kartlarını içeren <a> etiketlerini, içinde <h3 data-test-id="product-card-name"> barındıranları çekiyoruz.
    product_elements = driver.find_elements(
        By.XPATH, 
        "//a[.//h3[@data-test-id='product-card-name']]"
    )
    print(f"Page {page}: Found {len(product_elements)} products")
    
    for elem in product_elements:
        href = elem.get_attribute("href")
        if href and href not in all_product_links:
            all_product_links.append(href)
    time.sleep(1)

print(f"Total product links collected: {len(all_product_links)}")

# CSV dosyası oluşturma (İngilizce sütun isimleri)
csv_file = "hepsiburada_laptops_reviews.csv"
with open(csv_file, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["Product Name", "Price", "Image URL", "Review Page URL", "Reviews"])
    
    # Ürün detay bilgilerini çekme (örneğin ürün adı, fiyat, görsel URL)
    # (Not: Bu örnekte tek bir ürün için çekim yapılıyor; eğer her ürün için isteniyorsa burayı döngü içine alabilirsiniz)
    try:
        product_name = driver.find_element(By.CSS_SELECTOR, '[data-test-id="product-card-name"]').text
    except Exception:
        product_name = "Unknown"
    try:
        product_price = driver.find_element(By.CSS_SELECTOR, '[data-test-id="price-current-price"]').text
    except Exception:
        product_price = "No Price"
    try:
        product_image = driver.find_element(By.CSS_SELECTOR, '[data-test-id="product-image-image"] img').get_attribute("src")
    except Exception:
        product_image = "No Image"

    # Her ürünün yorum sayfasını ziyaret etme
    for link in all_product_links:
        # Eğer linkin sonuna "-yorumlari" eklenmemişse ekleyelim
        if not link.endswith("-yorumlari"):
            review_link = link.rstrip("/") + "-yorumlari"
        else:
            review_link = link
        print(f"Processing review page: {review_link}")
        driver.get(review_link)
        time.sleep(3)
        slow_scroll()  # Yorum sayfasını en alta kadar çok yavaş kaydır

        # Yorumları çekme
        all_reviews = []
        try:
            # Yorum sayfasında pagination uygulanmış durumda.
            current_review_page = 1
            max_review_pages = 8

            while current_review_page <= max_review_pages:
                slow_scroll()  # Yorumların tamamen yüklenmesi için en alta kadar scroll
                review_elements = driver.find_elements(By.CSS_SELECTOR, '.hermes-src-universal-components-ReviewCard-ReviewCard-module__review')
                print(f"Review page {current_review_page}: Found {len(review_elements)} reviews")
                for review in review_elements:
                    try:
                        # Her yorum elementinin içindeki span etiketinin metnini çekiyoruz
                        span_elem = review.find_element(By.TAG_NAME, "span")
                        text = span_elem.text.strip()
                        if text:
                            all_reviews.append(text)
                    except Exception as e:
                        print("Error fetching span text from review:", e)
                next_page_number = current_review_page + 1
                if next_page_number > max_review_pages:
                    break
                try:
                    # Pagination bar içerisinden sayfa numarası içeren li elementini tespit edip tıklıyoruz.
                    next_page_li = wait.until(EC.element_to_be_clickable(
                        (By.XPATH, f"//ul[contains(@class,'PaginationBar-module__paginationBarPagesHolder')]//li[.//span[text()='{next_page_number}']]")
                    ))
                    driver.execute_script("arguments[0].scrollIntoView(true);", next_page_li)
                    time.sleep(1)
                    next_page_li.click()
                    time.sleep(3)
                    current_review_page += 1
                except Exception as e:
                    print(f"No more review pages for product: {review_link}. Error: {e}")
                    break
        except Exception as e:
            print(f"Error fetching reviews for product: {review_link}. Error: {e}")
            all_reviews = ["No Reviews"]

        writer.writerow([product_name, product_price, product_image, review_link, "; ".join(all_reviews)])

driver.quit()
print(f"Scraping completed, data saved to {csv_file}.")
