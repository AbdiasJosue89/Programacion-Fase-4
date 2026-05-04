"""
Módulo de modelos de entidades principales: EntidadBase y Cliente.
Implementa abstracción, encapsulación y validaciones robustas.
"""

import re
from abc import ABC, abstractmethod
from datetime import datetime

from utils.excepciones import (
    ClienteNombreInvalidoError,
    ClienteEmailInvalidoError,
    ClienteTelefonoInvalidoError,
)
from utils.logger import log_evento


# ── Clase Abstracta Base ──────────────────────────────────────────────────────

class EntidadBase(ABC):
    """
    Clase abstracta que representa cualquier entidad del sistema Software FJ.
    Obliga a todas las subclases a implementar una descripción y validación.
    """

    _contador_ids: int = 0

    def __init__(self, nombre: str):
        EntidadBase._contador_ids += 1
        self.__id = EntidadBase._contador_ids
        self.__nombre = nombre
        self.__fecha_creacion = datetime.now()

    # ── Propiedades ───────────────────────────────────────────────────────────

    @property
    def id(self) -> int:
        return self.__id

    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str):
        self._validar_nombre(valor)
        self.__nombre = valor

    @property
    def fecha_creacion(self) -> datetime:
        return self.__fecha_creacion

    # ── Métodos abstractos ────────────────────────────────────────────────────

    @abstractmethod
    def describir(self) -> str:
        """Retorna una descripción legible de la entidad."""
        pass

    @abstractmethod
    def validar(self) -> bool:
        """Valida la integridad de los datos de la entidad."""
        pass

    # ── Métodos concretos ─────────────────────────────────────────────────────

    def _validar_nombre(self, valor: str) -> None:
        """Validación base de nombre: mínimo 2 chars, solo letras/espacios."""
        if not valor or not isinstance(valor, str):
            raise ClienteNombreInvalidoError(valor)
        limpio = valor.strip()
        if len(limpio) < 2 or not re.match(r"^[A-Za-záéíóúÁÉÍÓÚñÑüÜ\s]+$", limpio):
            raise ClienteNombreInvalidoError(valor)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.__id}, nombre='{self.__nombre}')"


# ── Clase Cliente ─────────────────────────────────────────────────────────────

class Cliente(EntidadBase):
    """
    Representa un cliente de Software FJ.
    Encapsula datos personales con validaciones estrictas.
    """

    def __init__(self, nombre: str, email: str, telefono: str):
        self._validar_nombre(nombre)          # valida antes de llamar super
        super().__init__(nombre)
        self.__email = ""
        self.__telefono = ""
        self.email = email                    # usa los setters validadores
        self.telefono = telefono
        self.__reservas: list = []            # lista interna de reservas del cliente
        log_evento("CLIENTE", "REGISTRO", f"id={self.id} | nombre='{nombre}' | email='{email}'")

    # ── Propiedades encapsuladas ──────────────────────────────────────────────

    @property
    def email(self) -> str:
        return self.__email

    @email.setter
    def email(self, valor: str):
        if not valor or not isinstance(valor, str):
            raise ClienteEmailInvalidoError(valor)
        patron = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(patron, valor.strip()):
            raise ClienteEmailInvalidoError(valor)
        self.__email = valor.strip().lower()

    @property
    def telefono(self) -> str:
        return self.__telefono

    @telefono.setter
    def telefono(self, valor: str):
        if not valor or not isinstance(valor, str):
            raise ClienteTelefonoInvalidoError(valor)
        limpio = re.sub(r"[\s\-\+\(\)]", "", valor)
        if not limpio.isdigit() or not (7 <= len(limpio) <= 15):
            raise ClienteTelefonoInvalidoError(valor)
        self.__telefono = limpio

    @property
    def reservas(self) -> list:
        """Copia defensiva de la lista de reservas."""
        return list(self.__reservas)

    # ── Métodos internos ──────────────────────────────────────────────────────

    def agregar_reserva(self, reserva) -> None:
        """Asocia una reserva al cliente (llamado internamente por Reserva)."""
        self.__reservas.append(reserva)

    def total_reservas(self) -> int:
        return len(self.__reservas)

    # ── Implementación de métodos abstractos ─────────────────────────────────

    def describir(self) -> str:
        return (
            f"Cliente #{self.id} | Nombre: {self.nombre} | "
            f"Email: {self.__email} | Teléfono: {self.__telefono} | "
            f"Reservas: {len(self.__reservas)}"
        )

    def validar(self) -> bool:
        return bool(self.nombre and self.__email and self.__telefono)

    def __str__(self) -> str:
        return self.describir()