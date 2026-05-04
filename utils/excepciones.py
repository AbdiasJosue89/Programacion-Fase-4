"""
Módulo de excepciones personalizadas para Software FJ.
Define toda la jerarquía de errores del sistema.
"""


class SoftwareFJError(Exception):
    """Excepción base del sistema Software FJ."""
    def __init__(self, mensaje: str, codigo: str = "ERR_GENERAL"):
        self.mensaje = mensaje
        self.codigo = codigo
        super().__init__(f"[{codigo}] {mensaje}")


# ── Excepciones de Cliente ────────────────────────────────────────────────────

class ClienteError(SoftwareFJError):
    """Errores relacionados con la entidad Cliente."""
    pass


class ClienteNombreInvalidoError(ClienteError):
    def __init__(self, valor):
        super().__init__(
            f"Nombre de cliente inválido: '{valor}'. Debe tener al menos 2 caracteres y solo letras/espacios.",
            "ERR_CLIENTE_NOMBRE"
        )


class ClienteEmailInvalidoError(ClienteError):
    def __init__(self, valor):
        super().__init__(
            f"Email inválido: '{valor}'. Formato esperado: usuario@dominio.ext",
            "ERR_CLIENTE_EMAIL"
        )


class ClienteTelefonoInvalidoError(ClienteError):
    def __init__(self, valor):
        super().__init__(
            f"Teléfono inválido: '{valor}'. Solo se admiten dígitos, entre 7 y 15 caracteres.",
            "ERR_CLIENTE_TELEFONO"
        )


class ClienteYaExisteError(ClienteError):
    def __init__(self, email):
        super().__init__(
            f"Ya existe un cliente registrado con el email: '{email}'.",
            "ERR_CLIENTE_DUPLICADO"
        )


class ClienteNoEncontradoError(ClienteError):
    def __init__(self, identificador):
        super().__init__(
            f"No se encontró ningún cliente con el identificador: '{identificador}'.",
            "ERR_CLIENTE_NO_ENCONTRADO"
        )


# ── Excepciones de Servicio ───────────────────────────────────────────────────

class ServicioError(SoftwareFJError):
    """Errores relacionados con la entidad Servicio."""
    pass


class ServicioNoDisponibleError(ServicioError):
    def __init__(self, nombre):
        super().__init__(
            f"El servicio '{nombre}' no está disponible actualmente.",
            "ERR_SERVICIO_NO_DISPONIBLE"
        )


class ServicioCapacidadExcedidaError(ServicioError):
    def __init__(self, nombre, capacidad):
        super().__init__(
            f"El servicio '{nombre}' ha alcanzado su capacidad máxima de {capacidad} reservas.",
            "ERR_SERVICIO_CAPACIDAD"
        )


class ServicioParametroInvalidoError(ServicioError):
    def __init__(self, parametro, valor, detalle=""):
        msg = f"Parámetro '{parametro}' con valor '{valor}' no es válido."
        if detalle:
            msg += f" {detalle}"
        super().__init__(msg, "ERR_SERVICIO_PARAMETRO")


class ServicioCostoInvalidoError(ServicioError):
    def __init__(self, detalle):
        super().__init__(
            f"Error al calcular el costo del servicio: {detalle}",
            "ERR_SERVICIO_COSTO"
        )


# ── Excepciones de Reserva ────────────────────────────────────────────────────

class ReservaError(SoftwareFJError):
    """Errores relacionados con la entidad Reserva."""
    pass


class ReservaNoEncontradaError(ReservaError):
    def __init__(self, id_reserva):
        super().__init__(
            f"No se encontró la reserva con ID: '{id_reserva}'.",
            "ERR_RESERVA_NO_ENCONTRADA"
        )


class ReservaEstadoInvalidoError(ReservaError):
    def __init__(self, estado_actual, accion):
        super().__init__(
            f"No se puede ejecutar '{accion}' sobre una reserva en estado '{estado_actual}'.",
            "ERR_RESERVA_ESTADO"
        )


class ReservaDuracionInvalidaError(ReservaError):
    def __init__(self, duracion, minimo, maximo):
        super().__init__(
            f"Duración de reserva inválida: {duracion}h. Debe estar entre {minimo}h y {maximo}h.",
            "ERR_RESERVA_DURACION"
        )


class ReservaFechaInvalidaError(ReservaError):
    def __init__(self, detalle):
        super().__init__(
            f"Fecha de reserva inválida: {detalle}",
            "ERR_RESERVA_FECHA"
        )