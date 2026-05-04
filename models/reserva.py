"""
Módulo de la clase Reserva para Software FJ.
Integra cliente, servicio, duración y estado.
Implementa confirmación, cancelación y procesamiento con manejo robusto de excepciones.
"""

from datetime import datetime
from enum import Enum, auto

from models.entidades import Cliente
from models.servicios import Servicio
from utils.excepciones import (
    ReservaEstadoInvalidoError,
    ReservaDuracionInvalidaError,
    ReservaNoEncontradaError,
    ServicioNoDisponibleError,
    ServicioParametroInvalidoError,
    SoftwareFJError,
)
from utils.logger import log_evento, log_error, log_info, log_advertencia


# ── Estado de la Reserva ──────────────────────────────────────────────────────

class EstadoReserva(Enum):
    PENDIENTE   = auto()
    CONFIRMADA  = auto()
    CANCELADA   = auto()
    COMPLETADA  = auto()


# ── Clase Reserva ─────────────────────────────────────────────────────────────

class Reserva:
    """
    Representa una reserva de un cliente para un servicio específico.
    Gestiona el ciclo de vida: PENDIENTE → CONFIRMADA → COMPLETADA / CANCELADA.
    """

    DURACION_MIN = 0.5     # horas
    DURACION_MAX = 240.0   # horas

    _contador: int = 0

    def __init__(self, cliente: Cliente, servicio: Servicio,
                 duracion_horas: float, notas: str = ""):
        Reserva._contador += 1
        self.__id = Reserva._contador
        self.__cliente = cliente
        self.__servicio = servicio
        self.__duracion_horas = 0.0
        self.__estado = EstadoReserva.PENDIENTE
        self.__fecha_creacion = datetime.now()
        self.__fecha_confirmacion = None
        self.__fecha_cancelacion = None
        self.__notas = notas
        self.__costo_calculado: float = 0.0

        # Valida duración antes de asignar
        self._validar_duracion(duracion_horas)
        self.__duracion_horas = duracion_horas

        log_evento("RESERVA", "CREADA",
                   f"id={self.__id} | cliente='{cliente.nombre}' | "
                   f"servicio='{servicio.nombre}' | duración={duracion_horas}h")

    # ── Propiedades de solo lectura ───────────────────────────────────────────

    @property
    def id(self) -> int:
        return self.__id

    @property
    def cliente(self) -> Cliente:
        return self.__cliente

    @property
    def servicio(self) -> Servicio:
        return self.__servicio

    @property
    def duracion_horas(self) -> float:
        return self.__duracion_horas

    @property
    def estado(self) -> EstadoReserva:
        return self.__estado

    @property
    def costo_calculado(self) -> float:
        return self.__costo_calculado

    @property
    def fecha_creacion(self) -> datetime:
        return self.__fecha_creacion

    # ── Ciclo de vida de la reserva ───────────────────────────────────────────

    def confirmar(self, con_iva: bool = False, descuento: float = 0.0) -> float:
        """
        Confirma la reserva, calcula el costo y registra en servicio y cliente.
        Retorna el costo total calculado.
        Usa try/except/else/finally.
        """
        try:
            if self.__estado != EstadoReserva.PENDIENTE:
                raise ReservaEstadoInvalidoError(self.__estado.name, "confirmar")

            self.__servicio.verificar_disponibilidad()
            self.__servicio.validar_parametros(duracion_horas=self.__duracion_horas)

            costo = self.__servicio.calcular_costo(
                self.__duracion_horas,
                con_iva=con_iva,
                descuento=descuento
            )

        except (ReservaEstadoInvalidoError, ServicioNoDisponibleError,
                ServicioParametroInvalidoError, SoftwareFJError) as e:
            log_error(f"Error al confirmar reserva #{self.__id}", e)
            raise

        except Exception as e:
            log_error(f"Error inesperado al confirmar reserva #{self.__id}", e)
            raise SoftwareFJError(f"Error inesperado: {e}") from e

        else:
            # Solo si NO hubo excepción
            self.__servicio.registrar_reserva()
            self.__cliente.agregar_reserva(self)
            self.__estado = EstadoReserva.CONFIRMADA
            self.__fecha_confirmacion = datetime.now()
            self.__costo_calculado = costo
            log_evento("RESERVA", "CONFIRMADA",
                       f"id={self.__id} | costo=${costo:,.2f} COP | "
                       f"iva={'sí' if con_iva else 'no'} | descuento={descuento*100:.1f}%")
            return costo

        finally:
            # Siempre se ejecuta
            log_info(f"Proceso de confirmación de reserva #{self.__id} finalizado. "
                     f"Estado actual: {self.__estado.name}")

    def cancelar(self, motivo: str = "Sin motivo especificado") -> None:
        """
        Cancela la reserva. Solo posible en estado PENDIENTE o CONFIRMADA.
        Usa try/except/finally.
        """
        try:
            if self.__estado not in (EstadoReserva.PENDIENTE, EstadoReserva.CONFIRMADA):
                raise ReservaEstadoInvalidoError(self.__estado.name, "cancelar")

            self.__estado = EstadoReserva.CANCELADA
            self.__fecha_cancelacion = datetime.now()
            self.__servicio.liberar_reserva()

        except ReservaEstadoInvalidoError as e:
            log_error(f"No se puede cancelar reserva #{self.__id}", e)
            raise

        except Exception as e:
            log_error(f"Error inesperado al cancelar reserva #{self.__id}", e)
            raise SoftwareFJError(f"Error inesperado al cancelar: {e}") from e

        finally:
            log_evento("RESERVA", "CANCELACION_INTENTADA",
                       f"id={self.__id} | motivo='{motivo}' | estado_final={self.__estado.name}")

    def completar(self) -> None:
        """
        Marca la reserva como completada. Solo desde estado CONFIRMADA.
        """
        try:
            if self.__estado != EstadoReserva.CONFIRMADA:
                raise ReservaEstadoInvalidoError(self.__estado.name, "completar")
            self.__estado = EstadoReserva.COMPLETADA
            log_evento("RESERVA", "COMPLETADA", f"id={self.__id} | cliente='{self.__cliente.nombre}'")

        except ReservaEstadoInvalidoError:
            log_advertencia(f"Intento de completar reserva #{self.__id} en estado inválido.")
            raise

    # ── Validación interna ────────────────────────────────────────────────────

    def _validar_duracion(self, horas: float) -> None:
        if not isinstance(horas, (int, float)) or not (self.DURACION_MIN <= horas <= self.DURACION_MAX):
            raise ReservaDuracionInvalidaError(horas, self.DURACION_MIN, self.DURACION_MAX)

    # ── Representación ────────────────────────────────────────────────────────

    def describir(self) -> str:
        return (
            f"Reserva #{self.__id} | "
            f"Cliente: {self.__cliente.nombre} | "
            f"Servicio: {self.__servicio.nombre} | "
            f"Duración: {self.__duracion_horas}h | "
            f"Estado: {self.__estado.name} | "
            f"Costo: ${self.__costo_calculado:,.2f} COP"
        )

    def __str__(self) -> str:
        return self.describir()

    def __repr__(self) -> str:
        return f"Reserva(id={self.__id}, estado={self.__estado.name})"