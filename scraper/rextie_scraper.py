import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import time
import re

class RextieScraper:
    def __init__(self, url, headers, logger):
        self.url = url
        self.headers = headers
        self.logger = logger
        self.driver = None

    def __del__(self):
        if self.driver:
            self.driver.quit()

    def fetch_page(self):
        try:
            if "tkambio" in self.url:
                return self.fetch_page_selenium()
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            self.logger.error(f"Error al obtener la página {self.url}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error inesperado al obtener la página: {e}")
            return None

    def fetch_page_selenium(self):
        try:
            options = Options()
            options.add_argument("--headless=new")  # Usar el nuevo modo headless
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--remote-debugging-port=9222')  # Puerto fijo para debugging
            options.add_argument('--window-size=1920,1080')

            # Configuración adicional importante
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)

            # Especificar la ubicación exacta del binario
            options.binary_location = "/usr/bin/chromium-browser"  # Asegurar que esta ruta es correcta

            service = Service(ChromeDriverManager().install())

            self.driver = webdriver.Chrome(
                service=service,
                options=options
            )

            self.driver.get(self.url)

            time.sleep(5)

            return self.driver.page_source

        except Exception as e:
            self.logger.error(f"Error Selenium en {self.url}: {str(e)[:200]}")  # Limitar longitud del error
            return None

    def parse_data_kambista(self, html):
        try:
            soup = BeautifulSoup(html, 'html.parser')
            compra = soup.find("strong", id="valcompra").get_text(strip=True)
            venta = soup.find("strong", id="valventa").get_text(strip=True)
            return {"compra": compra, "venta": venta}
        except AttributeError as e:
            self.logger.error(f"Elemento no encontrado en Kambista: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error al parsear HTML de Kambista: {e}")
            return None

    def parse_data_tkambio(self, html):
        try:
            soup = BeautifulSoup(html, 'html.parser')
            prices = soup.find_all("span", class_="price")
            self.logger.debug(f"Precios encontrados en Tkambio: {len(prices)}")

            if len(prices) >= 2:
                compra = prices[0].get_text(strip=True)
                venta = prices[1].get_text(strip=True)
                return {"compra": compra, "venta": venta}
            return None
        except Exception as e:
            self.logger.error(f"Error al parsear HTML de Tkambio: {e}")
            return None

    def parse_data_rextie(self, html):
        try:
            soup = BeautifulSoup(html, "html.parser")
            result = {}

            # Extracción más robusta que maneja diferentes estructuras HTML
            def extract_price(container_class):
                container = soup.find('a', class_=lambda x: x and container_class.lower() in x.lower())

                if container:
                    price_div = container.find('div', class_=lambda x: 'text-xs' in x if x else False)
                    if price_div:
                        # Limpieza avanzada del texto para obtener solo el valor numérico
                        price_text = price_div.get_text(" ", strip=True)
                        # Busca el último número con decimales en el texto
                        matches = re.findall(r"(\d+\.\d{2,})", price_text)
                        if matches:
                            return matches[-1]  # Devuelve el último match (por si hay múltiples)
                return None

            # Obtener ambos precios
            result["compra"] = extract_price("buy")
            result["venta"] = extract_price("sell")

            # Validar que ambos precios existen
            if None in result.values():
                missing = [k for k, v in result.items() if v is None]
                self.logger.warning(f"Valores faltantes: {missing}")
                return None

            result["fuente"] = "Rextie"
            self.logger.debug(f"Datos extraídos de Rextie: {result}")
            return result

        except Exception as e:
            self.logger.error(f"Error crítico al parsear Rextie: {str(e)}", exc_info=True)
            return None