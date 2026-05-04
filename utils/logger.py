"""
Módulo de logging para Software FJ.
Registra todos los eventos y errores en archivo de log con timestamp.
"""

import logging
import os
from datetime import datetime

# Ruta del archivo de log (dentro de la carpeta logs/)
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "software_fj.log")


def _configurar_logger() -> logging.Logger:
    logger = logging.getLogger("SoftwareFJ")
    logger.setLevel(logging.DEBUG)

    # Evitar duplicar handlers si se importa varias veces
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Handler → archivo
    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)

    # Handler → consola (solo WARNING en adelante para no saturar la salida)
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


logger = _configurar_logger()


# ── Funciones públicas de conveniencia ────────────────────────────────────────

def log_info(mensaje: str) -> None:
    """Registra un evento informativo."""
    logger.info(mensaje)


def log_advertencia(mensaje: str) -> None:
    """Registra una advertencia."""
    logger.warning(mensaje)


def log_error(mensaje: str, exc: Exception = None) -> None:
    """Registra un error. Si se pasa la excepción, incluye el traceback."""
    if exc:
        logger.error(f"{mensaje} | Excepción: {type(exc).__name__}: {exc}")
    else:
        logger.error(mensaje)


def log_critico(mensaje: str, exc: Exception = None) -> None:
    """Registra un error crítico."""
    if exc:
        logger.critical(f"{mensaje} | Excepción: {type(exc).__name__}: {exc}")
    else:
        logger.critical(mensaje)


def log_evento(entidad: str, accion: str, detalle: str) -> None:
    """Registra un evento de negocio estructurado."""
    logger.info(f"[{entidad.upper()}] {accion} | {detalle}")