from scraper.rextie_scraper import RextieScraper
from scraper.utils import setup_logger
import csv
from datetime import datetime
import os
import pandas as pd

def init_csv(filename="data/rextie_dolar.csv"):
    if not os.path.exists("data"):
        os.makedirs("data")

    if not os.path.exists(filename):
        with open(filename, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["fecha", "hora", "compra", "venta", "fuente"])
        print("✅ Archivo CSV inicializado correctamente.")
    else:
        print("⚠️ El archivo ya existe. No se modificó.")



def save_to_csv(data, filename="data/rextie_dolar.csv"):
    """Convierte datos a DataFrame y los guarda en CSV, agregando nuevas filas sin borrar anteriores."""
    if not os.path.exists("data"):
        os.makedirs("data")

    now = datetime.now()

    if not data or "compra" not in data or "venta" not in data:
        return False

    # Crear nuevo DataFrame con la fila actual
    new_row = {
        "fecha": now.strftime("%Y-%m-%d"),
        "hora": now.strftime("%H:%M:%S"),
        "compra": data["compra"],
        "venta": data["venta"],
        "fuente": data.get("fuente", "desconocido")
    }

    new_df = pd.DataFrame([new_row])

    try:
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            existing_df = pd.read_csv(filename)
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        else:
            combined_df = new_df

        # Guardar todo nuevamente con encabezado
        combined_df.to_csv(filename, index=False)
        return True

    except Exception as e:
        print(f"❌ Error guardando en CSV: {e}")
        return False

if __name__ == "__main__":
    init_csv()
    logger = setup_logger()
    logger.info("🚀 Iniciando scraping de tasas de cambio...")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    urls = {
        "Kambista": "https://kambista.com/",
        "Tkambio": "https://tkambio.com/",
        'CambioSeguro': "https://cambioseguro.com/",
        "TuCambista": "https://tucambista.pe/"
    }

    for nombre, url in urls.items():
        try:
            scraper = RextieScraper(url, headers, logger)
            html = scraper.fetch_page()

            if not html:
                logger.warning(f"⚠️ No se pudo obtener HTML de {nombre}")
                continue

            if "kambista" in url:
                data = scraper.parse_data_kambista(html)
            elif "cambioseguro" in url:
                data = scraper.parse_data_cambioseguro(html)
            elif "tkambio" in url:
                data = scraper.parse_data_tkambio(html)

            if data:
                data["fuente"] = nombre
                logger.info(f"✅ {nombre} -> Compra: {data['compra']}, Venta: {data['venta']}")
                save_to_csv(data)
            else:
                logger.warning(f"⚠️ No se pudo extraer datos de {nombre}")
        except Exception as e:
            logger.error(f"❌ Error procesando {nombre}: {e}")