import logging
import os


def setup_logger(name=__name__, log_file="scraper.log"):
    """Configura un logger con salida a consola y archivo"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Crear directorio de logs si no existe
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Formato del log
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Handler para consola
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)

    # Handler para archivo
    fh = logging.FileHandler(os.path.join(log_dir, log_file))
    fh.setFormatter(formatter)

    # Agregar handlers
    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger