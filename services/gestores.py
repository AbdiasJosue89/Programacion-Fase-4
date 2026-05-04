"""
Módulo de servicios de gestión (capa de negocio) para Software FJ.
Contiene los gestores: GestorClientes, GestorServicios, GestorReservas.
"""

from models.entidades import Cliente
from models.servicios import Servicio
from models.reserva import Reserva, EstadoReserva
from utils.excepciones import (
    ClienteYaExisteError,
    ClienteNoEncontradoError,
    ReservaNoEncontradaError,
    SoftwareFJError,
)
from utils.logger import log_evento, log_error, log_info


# ── Gestor de Clientes ────────────────────────────────────────────────────────

class GestorClientes:
    """Administra el registro y consulta de clientes en memoria."""

    def __init__(self):
        self.__clientes: list[Cliente] = []

    def registrar(self, nombre: str, email: str, telefono: str) -> Cliente:
        """Crea y registra un cliente. Lanza excepción si el email ya existe."""
        try:
            if self.buscar_por_email(email, silencioso=True):
                raise ClienteYaExisteError(email)
            cliente = Cliente(nombre, email, telefono)
            self.__clientes.append(cliente)
            return cliente

        except ClienteYaExisteError:
            log_error(f"Intento de registro duplicado: email='{email}'")
            raise

        except Exception as e:
            log_error(f"Error al registrar cliente '{nombre}'", e)
            raise

    def buscar_por_email(self, email: str, silencioso: bool = False) -> Cliente | None:
        """Busca cliente por email. Lanza excepción si no existe (a menos que silencioso=True)."""
        email_lower = email.strip().lower()
        for c in self.__clientes:
            if c.email == email_lower:
                return c
        if not silencioso:
            raise ClienteNoEncontradoError(email)
        return None

    def buscar_por_id(self, id_cliente: int) -> Cliente:
        for c in self.__clientes:
            if c.id == id_cliente:
                return c
        raise ClienteNoEncontradoError(id_cliente)

    def listar(self) -> list[Cliente]:
        return list(self.__clientes)

    def total(self) -> int:
        return len(self.__clientes)


# ── Gestor de Servicios ───────────────────────────────────────────────────────

class GestorServicios:
    """Administra los servicios disponibles en el sistema."""

    def __init__(self):
        self.__servicios: list[Servicio] = []

    def agregar(self, servicio: Servicio) -> None:
        self.__servicios.append(servicio)
        log_evento("GESTOR_SERVICIOS", "AGREGADO", servicio.describir())

    def buscar_por_id(self, id_servicio: int) -> Servicio:
        for s in self.__servicios:
            if s.id == id_servicio:
                return s
        raise SoftwareFJError(f"Servicio con id={id_servicio} no encontrado.", "ERR_SERVICIO_NO_ENCONTRADO")

    def buscar_por_nombre(self, nombre: str) -> Servicio | None:
        nombre_lower = nombre.strip().lower()
        for s in self.__servicios:
            if s.nombre.lower() == nombre_lower:
                return s
        return None

    def listar(self) -> list[Servicio]:
        return list(self.__servicios)

    def listar_disponibles(self) -> list[Servicio]:
        return [s for s in self.__servicios if s.disponible]


# ── Gestor de Reservas ────────────────────────────────────────────────────────

class GestorReservas:
    """Administra el ciclo de vida completo de las reservas."""

    def __init__(self):
        self.__reservas: list[Reserva] = []

    def crear(self, cliente: Cliente, servicio: Servicio,
              duracion_horas: float, notas: str = "") -> Reserva:
        """Crea una reserva en estado PENDIENTE."""
        try:
            reserva = Reserva(cliente, servicio, duracion_horas, notas)
            self.__reservas.append(reserva)
            return reserva
        except Exception as e:
            log_error("Error al crear reserva", e)
            raise

    def confirmar(self, id_reserva: int, con_iva: bool = False,
                  descuento: float = 0.0) -> float:
        """Confirma la reserva indicada y retorna el costo total."""
        reserva = self._obtener_reserva(id_reserva)
        return reserva.confirmar(con_iva=con_iva, descuento=descuento)

    def cancelar(self, id_reserva: int, motivo: str = "") -> None:
        reserva = self._obtener_reserva(id_reserva)
        reserva.cancelar(motivo)

    def completar(self, id_reserva: int) -> None:
        reserva = self._obtener_reserva(id_reserva)
        reserva.completar()

    def buscar_por_id(self, id_reserva: int) -> Reserva:
        return self._obtener_reserva(id_reserva)

    def listar(self) -> list[Reserva]:
        return list(self.__reservas)

    def listar_por_estado(self, estado: EstadoReserva) -> list[Reserva]:
        return [r for r in self.__reservas if r.estado == estado]

    def _obtener_reserva(self, id_reserva: int) -> Reserva:
        for r in self.__reservas:
            if r.id == id_reserva:
                return r
        raise ReservaNoEncontradaError(id_reserva)