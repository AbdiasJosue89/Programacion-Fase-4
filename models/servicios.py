"""
Módulo de servicios de Software FJ.
Define la clase abstracta Servicio y sus tres especializaciones:
  - ReservaSala
  - AlquilerEquipo
  - AsesoriaEspecializada
Implementa polimorfismo, métodos sobrescritos y sobrecargados.
"""

from abc import abstractmethod
from datetime import datetime

from models.entidades import EntidadBase
from utils.excepciones import (
    ServicioNoDisponibleError,
    ServicioCapacidadExcedidaError,
    ServicioParametroInvalidoError,
    ServicioCostoInvalidoError,
)
from utils.logger import log_evento, log_advertencia


# ── Clase Abstracta Servicio ──────────────────────────────────────────────────

class Servicio(EntidadBase):
    """
    Clase abstracta que representa cualquier servicio ofrecido por Software FJ.
    Define el contrato que todas las especializaciones deben cumplir.
    """

    TARIFA_IVA = 0.19          # 19 % IVA Colombia
    MAX_DESCUENTO = 0.30       # descuento máximo permitido 30 %

    def __init__(self, nombre: str, precio_base: float, capacidad_maxima: int = 10):
        self._validar_nombre(nombre)
        self._validar_precio(precio_base)
        super().__init__(nombre)
        self.__precio_base = precio_base
        self.__capacidad_maxima = capacidad_maxima
        self.__reservas_activas = 0
        self.__disponible = True

    # ── Propiedades ───────────────────────────────────────────────────────────

    @property
    def precio_base(self) -> float:
        return self.__precio_base

    @property
    def capacidad_maxima(self) -> int:
        return self.__capacidad_maxima

    @property
    def reservas_activas(self) -> int:
        return self.__reservas_activas

    @property
    def disponible(self) -> bool:
        return self.__disponible

    @disponible.setter
    def disponible(self, valor: bool):
        self.__disponible = bool(valor)

    # ── Métodos abstractos (polimorfismo) ─────────────────────────────────────

    @abstractmethod
    def calcular_costo(self, duracion_horas: float, **kwargs) -> float:
        """Calcula el costo total según la duración y parámetros adicionales."""
        pass

    @abstractmethod
    def validar_parametros(self, **kwargs) -> bool:
        """Valida que los parámetros de reserva sean correctos para este servicio."""
        pass

    # ── Métodos concretos compartidos ─────────────────────────────────────────

    def _validar_precio(self, precio: float) -> None:
        if not isinstance(precio, (int, float)) or precio <= 0:
            raise ServicioParametroInvalidoError("precio_base", precio, "Debe ser un número positivo.")

    def verificar_disponibilidad(self) -> None:
        """Lanza excepción si el servicio no está disponible o está lleno."""
        if not self.__disponible:
            raise ServicioNoDisponibleError(self.nombre)
        if self.__reservas_activas >= self.__capacidad_maxima:
            raise ServicioCapacidadExcedidaError(self.nombre, self.__capacidad_maxima)

    def registrar_reserva(self) -> None:
        self.verificar_disponibilidad()
        self.__reservas_activas += 1
        log_evento("SERVICIO", "RESERVA_REGISTRADA",
                   f"'{self.nombre}' | activas={self.__reservas_activas}/{self.__capacidad_maxima}")

    def liberar_reserva(self) -> None:
        if self.__reservas_activas > 0:
            self.__reservas_activas -= 1

    def _aplicar_descuento(self, costo: float, descuento: float) -> float:
        """Aplica descuento validado al costo."""
        if not (0 <= descuento <= self.MAX_DESCUENTO):
            raise ServicioCostoInvalidoError(
                f"Descuento {descuento*100:.1f}% fuera del rango permitido (0–{self.MAX_DESCUENTO*100:.0f}%)."
            )
        return round(costo * (1 - descuento), 2)

    def _aplicar_iva(self, costo: float) -> float:
        return round(costo * (1 + self.TARIFA_IVA), 2)

    def describir(self) -> str:
        estado = "Disponible" if self.__disponible else "No disponible"
        return (
            f"{self.__class__.__name__} #{self.id} | '{self.nombre}' | "
            f"Base: ${self.__precio_base:,.0f} COP | Estado: {estado} | "
            f"Reservas: {self.__reservas_activas}/{self.__capacidad_maxima}"
        )

    def validar(self) -> bool:
        return self.nombre is not None and self.__precio_base > 0


# ══════════════════════════════════════════════════════════════════════════════
# Servicio 1 – Reserva de Sala
# ══════════════════════════════════════════════════════════════════════════════

class ReservaSala(Servicio):
    """
    Servicio de reserva de salas de reunión/conferencias.
    Precio: precio_base * horas. Aplica recargo por sala premium.
    """

    RECARGO_PREMIUM = 0.25      # 25 % adicional para salas premium

    def __init__(self, nombre: str, precio_hora: float, es_premium: bool = False, capacidad_maxima: int = 8):
        super().__init__(nombre, precio_hora, capacidad_maxima)
        self.__es_premium = bool(es_premium)
        log_evento("SERVICIO", "CREADO", f"ReservaSala '{nombre}' | premium={es_premium}")

    @property
    def es_premium(self) -> bool:
        return self.__es_premium

    # ── calcular_costo sobrecargado ───────────────────────────────────────────

    def calcular_costo(self, duracion_horas: float, descuento: float = 0.0,
                       con_iva: bool = False, **kwargs) -> float:
        """
        Variante 1: costo = precio_hora * horas [+ recargo premium] [- descuento] [+ IVA]
        Parámetros opcionales: descuento (0–0.30), con_iva (bool)
        """
        self._validar_duracion(duracion_horas)
        costo = self.precio_base * duracion_horas
        if self.__es_premium:
            costo *= (1 + self.RECARGO_PREMIUM)
        if descuento > 0:
            costo = self._aplicar_descuento(costo, descuento)
        if con_iva:
            costo = self._aplicar_iva(costo)
        return round(costo, 2)

    def calcular_costo_evento(self, duracion_horas: float, num_asistentes: int,
                               descuento: float = 0.0) -> float:
        """
        Variante 2 (sobrecarga lógica): agrega costo por asistente adicional.
        Cada asistente suma el 2 % del precio_base.
        """
        self._validar_duracion(duracion_horas)
        if num_asistentes < 1:
            raise ServicioParametroInvalidoError("num_asistentes", num_asistentes, "Mínimo 1 asistente.")
        costo_base = self.calcular_costo(duracion_horas, descuento=descuento)
        recargo_asistentes = self.precio_base * 0.02 * num_asistentes
        return round(costo_base + recargo_asistentes, 2)

    def validar_parametros(self, duracion_horas: float = None, **kwargs) -> bool:
        if duracion_horas is None:
            raise ServicioParametroInvalidoError("duracion_horas", None, "Parámetro requerido.")
        self._validar_duracion(duracion_horas)
        return True

    def _validar_duracion(self, horas: float) -> None:
        if not isinstance(horas, (int, float)) or not (0.5 <= horas <= 12):
            raise ServicioParametroInvalidoError(
                "duracion_horas", horas, "Debe ser entre 0.5 y 12 horas."
            )

    def describir(self) -> str:
        tipo = "Premium" if self.__es_premium else "Estándar"
        return super().describir() + f" | Tipo: {tipo}"


# ══════════════════════════════════════════════════════════════════════════════
# Servicio 2 – Alquiler de Equipos
# ══════════════════════════════════════════════════════════════════════════════

class AlquilerEquipo(Servicio):
    """
    Servicio de alquiler de equipos tecnológicos (portátiles, proyectores, etc.).
    Precio: precio_base * días. Aplica seguro opcional.
    """

    COSTO_SEGURO_DIARIO = 15_000   # COP por día de seguro

    def __init__(self, nombre: str, precio_dia: float, tipo_equipo: str,
                 capacidad_maxima: int = 15):
        super().__init__(nombre, precio_dia, capacidad_maxima)
        if not tipo_equipo or not isinstance(tipo_equipo, str):
            raise ServicioParametroInvalidoError("tipo_equipo", tipo_equipo, "No puede estar vacío.")
        self.__tipo_equipo = tipo_equipo.strip()
        log_evento("SERVICIO", "CREADO", f"AlquilerEquipo '{nombre}' | tipo='{tipo_equipo}'")

    @property
    def tipo_equipo(self) -> str:
        return self.__tipo_equipo

    # ── calcular_costo sobrecargado ───────────────────────────────────────────

    def calcular_costo(self, duracion_horas: float, con_seguro: bool = False,
                       descuento: float = 0.0, con_iva: bool = False, **kwargs) -> float:
        """
        Variante 1: días = ceil(horas/8). Aplica seguro y/o descuento opcionales.
        """
        self._validar_duracion(duracion_horas)
        import math
        dias = math.ceil(duracion_horas / 8)
        costo = self.precio_base * dias
        if con_seguro:
            costo += self.COSTO_SEGURO_DIARIO * dias
        if descuento > 0:
            costo = self._aplicar_descuento(costo, descuento)
        if con_iva:
            costo = self._aplicar_iva(costo)
        return round(costo, 2)

    def calcular_costo_lote(self, duracion_horas: float, cantidad: int,
                             descuento: float = 0.0) -> float:
        """
        Variante 2 (sobrecarga lógica): alquiler de varios equipos del mismo tipo.
        """
        self._validar_duracion(duracion_horas)
        if not isinstance(cantidad, int) or cantidad < 1:
            raise ServicioParametroInvalidoError("cantidad", cantidad, "Debe ser un entero >= 1.")
        costo_unitario = self.calcular_costo(duracion_horas, descuento=descuento)
        # Descuento por volumen: >5 unidades → 10 % adicional
        if cantidad > 5:
            costo_unitario = self._aplicar_descuento(costo_unitario, 0.10)
        return round(costo_unitario * cantidad, 2)

    def validar_parametros(self, duracion_horas: float = None, **kwargs) -> bool:
        if duracion_horas is None:
            raise ServicioParametroInvalidoError("duracion_horas", None, "Parámetro requerido.")
        self._validar_duracion(duracion_horas)
        return True

    def _validar_duracion(self, horas: float) -> None:
        if not isinstance(horas, (int, float)) or not (1 <= horas <= 240):
            raise ServicioParametroInvalidoError(
                "duracion_horas", horas, "Debe ser entre 1 y 240 horas (30 días máx)."
            )

    def describir(self) -> str:
        return super().describir() + f" | Tipo equipo: {self.__tipo_equipo}"


# ══════════════════════════════════════════════════════════════════════════════
# Servicio 3 – Asesoría Especializada
# ══════════════════════════════════════════════════════════════════════════════

class AsesoriaEspecializada(Servicio):
    """
    Servicio de asesorías técnicas o profesionales.
    Precio: tarifa_hora * horas. Se puede cobrar con tarifa urgente.
    """

    RECARGO_URGENTE = 0.50      # 50 % adicional si es urgente

    def __init__(self, nombre: str, tarifa_hora: float, area: str,
                 capacidad_maxima: int = 5):
        super().__init__(nombre, tarifa_hora, capacidad_maxima)
        if not area or not isinstance(area, str):
            raise ServicioParametroInvalidoError("area", area, "El área de asesoría no puede estar vacía.")
        self.__area = area.strip()
        log_evento("SERVICIO", "CREADO", f"AsesoriaEspecializada '{nombre}' | área='{area}'")

    @property
    def area(self) -> str:
        return self.__area

    # ── calcular_costo sobrecargado ───────────────────────────────────────────

    def calcular_costo(self, duracion_horas: float, urgente: bool = False,
                       descuento: float = 0.0, con_iva: bool = False, **kwargs) -> float:
        """
        Variante 1: tarifa * horas [+ recargo urgente] [- descuento] [+ IVA]
        """
        self._validar_duracion(duracion_horas)
        costo = self.precio_base * duracion_horas
        if urgente:
            costo *= (1 + self.RECARGO_URGENTE)
            log_advertencia(f"Asesoría '{self.nombre}' solicitada como urgente. Recargo aplicado.")
        if descuento > 0:
            costo = self._aplicar_descuento(costo, descuento)
        if con_iva:
            costo = self._aplicar_iva(costo)
        return round(costo, 2)

    def calcular_costo_paquete(self, sesiones: int, horas_por_sesion: float,
                                descuento: float = 0.0) -> float:
        """
        Variante 2 (sobrecarga lógica): paquete de varias sesiones con descuento por paquete.
        """
        if not isinstance(sesiones, int) or sesiones < 1:
            raise ServicioParametroInvalidoError("sesiones", sesiones, "Debe ser un entero >= 1.")
        self._validar_duracion(horas_por_sesion)
        # Descuento automático por paquete >=3 sesiones
        descuento_paquete = 0.15 if sesiones >= 3 else 0.0
        descuento_total = min(descuento + descuento_paquete, self.MAX_DESCUENTO)
        costo_sesion = self.calcular_costo(horas_por_sesion, descuento=descuento_total)
        return round(costo_sesion * sesiones, 2)

    def validar_parametros(self, duracion_horas: float = None, **kwargs) -> bool:
        if duracion_horas is None:
            raise ServicioParametroInvalidoError("duracion_horas", None, "Parámetro requerido.")
        self._validar_duracion(duracion_horas)
        return True

    def _validar_duracion(self, horas: float) -> None:
        if not isinstance(horas, (int, float)) or not (0.5 <= horas <= 8):
            raise ServicioParametroInvalidoError(
                "duracion_horas", horas, "Las asesorías deben durar entre 0.5 y 8 horas."
            )

    def describir(self) -> str:
        return super().describir() + f" | Área: {self.__area}"