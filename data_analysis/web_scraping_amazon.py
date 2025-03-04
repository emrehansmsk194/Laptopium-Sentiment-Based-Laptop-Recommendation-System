from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# Geckodriver yolunu tanımla
driver_path = "C:\\Users\\EMREHAN\\PycharmProjects\\geckodriver.exe"
service = Service(driver_path)

# Firefox WebDriver başlat
options = webdriver.FirefoxOptions()
# options.add_argument("--headless")  # Tarayıcıyı gizli modda çalıştırmak için (isteğe bağlı)
driver = webdriver.Firefox(service=service, options=options)

# İlk 15 sayfadaki ürünleri çekmek için liste
all_products = []

# Sayfa numarasını değiştirerek veri çekiyoruz
for page in range(1, 16):  # 1'den 15'e kadar
    url = f"https://www.amazon.com.tr/s?i=computers&rh=n%3A12601898031&s=popularity-rank&fs=true&page={page}"
    driver.get(url)
    time.sleep(3)  # Sayfanın tam yüklenmesi için bekleme süresi

    # Ürünleri bul
    products = driver.find_elements(By.XPATH, "//div[@data-component-type='s-search-result']")

    for product in products:
        try:
            name = product.find_element(By.TAG_NAME, "h2").text.strip()
            image = product.find_element(By.CLASS_NAME, "s-image").get_attribute("src")
            link = product.find_element(By.CLASS_NAME, "a-link-normal").get_attribute("href")

            # 🔍 **Fiyatı doğru yerden almak için bekleme ekliyoruz**
            try:
                price = WebDriverWait(product, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "a-offscreen"))
                ).text.strip()
            except:
                try:
                    whole = product.find_element(By.CLASS_NAME, "a-price-whole").text.strip()
                    fraction = product.find_element(By.CLASS_NAME, "a-price-fraction").text.strip()
                    price = f"{whole},{fraction} TL"
                except:
                    price = "N/A"  # Fiyat bulunamazsa "N/A" olarak ayarla

            all_products.append([name, price, image, link])

        except Exception as e:
            print(f"Hata oluştu, atlanıyor: {e}")
            continue

    print(f"{page}. sayfa tamamlandı...")

# Tarayıcıyı kapat
driver.quit()

# Veriyi CSV'ye kaydet
df = pd.DataFrame(all_products, columns=["Product Name", "Price", "Image URL", "Link"])
csv_file_path = "datasets/amazon_products.csv"
df.to_csv(csv_file_path, index=False, encoding="utf-8")

print(f"Tüm sayfalardan veriler çekildi ve CSV olarak kaydedildi: {csv_file_path}")
