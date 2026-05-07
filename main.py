"""
╔══════════════════════════════════════════════════════════════════╗
║          Software FJ – Sistema de Gestión de Servicios           ║
║          Programación Orientada a Objetos                        ║
╚══════════════════════════════════════════════════════════════════╝

Punto de entrada del sistema.
Simula más de 10 operaciones completas (válidas e inválidas)
demostrando:
  • Clases abstractas y herencia
  • Polimorfismo y métodos sobrescritos/sobrecargados
  • Encapsulación y validaciones
  • Manejo avanzado de excepciones (try/except/else/finally,
    encadenamiento, excepciones personalizadas)
  • Registro en archivo de logs
"""

import sys
import os

# Permite importar los paquetes cuando se ejecuta desde la raíz del proyecto
sys.path.insert(0, os.path.dirname(__file__))

from models import Cliente, ReservaSala, AlquilerEquipo, AsesoriaEspecializada
from services import GestorClientes, GestorServicios, GestorReservas
from models.reserva import EstadoReserva
from utils.excepciones import (
    ClienteYaExisteError,
    ClienteEmailInvalidoError,
    ClienteNombreInvalidoError,
    ClienteTelefonoInvalidoError,
    ServicioNoDisponibleError,
    ServicioParametroInvalidoError,
    ReservaEstadoInvalidoError,
    ReservaDuracionInvalidaError,
    SoftwareFJError,
)
from utils.logger import log_info, log_error, log_evento


# ── Utilidades de presentación ────────────────────────────────────────────────

def separador(titulo: str = "") -> None:
    linea = "─" * 65
    if titulo:
        print(f"\n{linea}")
        print(f"  {titulo}")
        print(linea)
    else:
        print(linea)


def ok(msg: str) -> None:
    print(f"  ✔  {msg}")


def err(msg: str) -> None:
    print(f"  ✘  {msg}")


def info(msg: str) -> None:
    print(f"     {msg}")


# ── Instancias globales de gestores ──────────────────────────────────────────

gestor_clientes  = GestorClientes()
gestor_servicios = GestorServicios()
gestor_reservas  = GestorReservas()


# ══════════════════════════════════════════════════════════════════════════════
#  BLOQUE 1 – Registro de clientes (válidos e inválidos)
# ══════════════════════════════════════════════════════════════════════════════

def bloque_clientes():
    separador("BLOQUE 1 · Registro de Clientes")

    # Op 1 – Cliente válido
    try:
        c1 = gestor_clientes.registrar("Ana Torres", "ana.torres@email.com", "3001234567")
        ok(f"Cliente registrado → {c1.describir()}")
    except SoftwareFJError as e:
        err(f"Error inesperado: {e}")

    # Op 2 – Cliente válido
    try:
        c2 = gestor_clientes.registrar("Luis Pérez", "luis.perez@correo.co", "3157654321")
        ok(f"Cliente registrado → {c2.describir()}")
    except SoftwareFJError as e:
        err(f"Error inesperado: {e}")

    # Op 3 – Email duplicado (debe fallar)
    try:
        gestor_clientes.registrar("Ana Duplicada", "ana.torres@email.com", "3009999999")
        err("No debería llegar aquí.")
    except ClienteYaExisteError as e:
        ok(f"[Esperado] Email duplicado detectado → {e}")

    # Op 4 – Email inválido (debe fallar)
    try:
        gestor_clientes.registrar("Carlos Gómez", "correo_invalido", "3001111111")
    except ClienteEmailInvalidoError as e:
        ok(f"[Esperado] Email inválido → {e}")

    # Op 5 – Nombre inválido con números (debe fallar)
    try:
        gestor_clientes.registrar("123abc", "valido@test.com", "3002222222")
    except ClienteNombreInvalidoError as e:
        ok(f"[Esperado] Nombre inválido → {e}")

    # Op 6 – Teléfono inválido (debe fallar)
    try:
        gestor_clientes.registrar("María López", "maria@test.com", "abc-xyz")
    except ClienteTelefonoInvalidoError as e:
        ok(f"[Esperado] Teléfono inválido → {e}")

    # Op 7 – Tercer cliente válido
    try:
        c3 = gestor_clientes.registrar("Jorge Ramírez", "jorge.r@empresa.org", "3201112233")
        ok(f"Cliente registrado → {c3.describir()}")
    except SoftwareFJError as e:
        err(f"Error: {e}")

    info(f"Total clientes registrados: {gestor_clientes.total()}")


# ══════════════════════════════════════════════════════════════════════════════
#  BLOQUE 2 – Creación de servicios (válidos e inválidos)
# ══════════════════════════════════════════════════════════════════════════════

def bloque_servicios():
    separador("BLOQUE 2 · Creación de Servicios")

    # Op 8 – Sala estándar válida
    try:
        sala_std = ReservaSala("Sala Innovación", precio_hora=80_000, es_premium=False)
        gestor_servicios.agregar(sala_std)
        ok(f"Servicio creado → {sala_std.describir()}")
    except SoftwareFJError as e:
        err(f"Error: {e}")

    # Op 9 – Sala premium válida
    try:
        sala_prm = ReservaSala("Sala Ejecutiva", precio_hora=150_000, es_premium=True, capacidad_maxima=4)
        gestor_servicios.agregar(sala_prm)
        ok(f"Servicio creado → {sala_prm.describir()}")
    except SoftwareFJError as e:
        err(f"Error: {e}")

    # Op 10 – Alquiler de equipo válido
    try:
        alquiler = AlquilerEquipo("Portátil Dell XPS", precio_dia=50_000, tipo_equipo="Portátil")
        gestor_servicios.agregar(alquiler)
        ok(f"Servicio creado → {alquiler.describir()}")
    except SoftwareFJError as e:
        err(f"Error: {e}")

    # Op 11 – Asesoría válida
    try:
        asesoria = AsesoriaEspecializada("Asesoría Cloud AWS", tarifa_hora=200_000, area="Infraestructura Cloud")
        gestor_servicios.agregar(asesoria)
        ok(f"Servicio creado → {asesoria.describir()}")
    except SoftwareFJError as e:
        err(f"Error: {e}")

    # Op 12 – Servicio con precio inválido (debe fallar)
    try:
        ReservaSala("Sala Gratis", precio_hora=-1000)
    except ServicioParametroInvalidoError as e:
        ok(f"[Esperado] Precio inválido → {e}")

    # Op 13 – AlquilerEquipo sin tipo (debe fallar)
    try:
        AlquilerEquipo("Sin tipo", precio_dia=30_000, tipo_equipo="")
    except ServicioParametroInvalidoError as e:
        ok(f"[Esperado] Tipo de equipo vacío → {e}")

    info(f"Servicios disponibles: {len(gestor_servicios.listar_disponibles())}")


# ══════════════════════════════════════════════════════════════════════════════
#  BLOQUE 3 – Cálculo de costos (polimorfismo + métodos sobrecargados)
# ══════════════════════════════════════════════════════════════════════════════

def bloque_costos():
    separador("BLOQUE 3 · Cálculo Polimórfico de Costos")

    servicios = gestor_servicios.listar()

    # Polimorfismo: llamar calcular_costo sobre tipos distintos
    for srv in servicios:
        try:
            costo = srv.calcular_costo(2.0)
            ok(f"{srv.__class__.__name__} '{srv.nombre}' · 2h → ${costo:,.2f} COP")
        except ServicioParametroInvalidoError as e:
            err(f"Parámetro inválido en '{srv.nombre}': {e}")

    separador("Métodos sobrecargados")

    sala_std = servicios[0]   # ReservaSala estándar
    alquiler  = servicios[2]  # AlquilerEquipo
    asesoria  = servicios[3]  # AsesoriaEspecializada

    # ReservaSala.calcular_costo_evento
    try:
        costo_evento = sala_std.calcular_costo_evento(3.0, num_asistentes=10, descuento=0.10)
        ok(f"Sala evento (3h, 10 asistentes, 10% desc) → ${costo_evento:,.2f} COP")
    except SoftwareFJError as e:
        err(f"{e}")

    # AlquilerEquipo.calcular_costo_lote
    try:
        costo_lote = alquiler.calcular_costo_lote(8.0, cantidad=6)
        ok(f"Alquiler lote (1 día, 6 equipos, desc volumen) → ${costo_lote:,.2f} COP")
    except SoftwareFJError as e:
        err(f"{e}")

    # AsesoriaEspecializada.calcular_costo_paquete
    try:
        costo_paquete = asesoria.calcular_costo_paquete(sesiones=3, horas_por_sesion=2.0)
        ok(f"Asesoría paquete (3 sesiones x 2h, desc automático 15%) → ${costo_paquete:,.2f} COP")
    except SoftwareFJError as e:
        err(f"{e}")

    # Asesoría urgente con IVA
    try:
        costo_urgente = asesoria.calcular_costo(1.0, urgente=True, con_iva=True)
        ok(f"Asesoría urgente (1h, IVA incluido) → ${costo_urgente:,.2f} COP")
    except SoftwareFJError as e:
        err(f"{e}")

    # Duración inválida en asesoría (debe fallar)
    try:
        asesoria.calcular_costo(10.0)   # máximo es 8h
    except ServicioParametroInvalidoError as e:
        ok(f"[Esperado] Duración fuera de rango → {e}")


# ══════════════════════════════════════════════════════════════════════════════
#  BLOQUE 4 – Reservas (válidas, fallidas, canceladas, completadas)
# ══════════════════════════════════════════════════════════════════════════════

def bloque_reservas():
    separador("BLOQUE 4 · Gestión de Reservas")

    clientes  = gestor_clientes.listar()
    servicios = gestor_servicios.listar()

    c1, c2, c3 = clientes[0], clientes[1], clientes[2]
    sala_std, sala_prm, alquiler, asesoria = servicios

    # Op R1 – Reserva válida → confirmar
    try:
        r1 = gestor_reservas.crear(c1, sala_std, duracion_horas=3.0)
        costo = gestor_reservas.confirmar(r1.id, con_iva=True, descuento=0.05)
        ok(f"Reserva #{r1.id} confirmada → Costo: ${costo:,.2f} COP")
    except SoftwareFJError as e:
        err(f"Error R1: {e}")

    # Op R2 – Reserva válida → confirmar → completar
    try:
        r2 = gestor_reservas.crear(c2, asesoria, duracion_horas=2.0)
        costo = gestor_reservas.confirmar(r2.id)
        gestor_reservas.completar(r2.id)
        ok(f"Reserva #{r2.id} completada → Costo: ${costo:,.2f} COP")
    except SoftwareFJError as e:
        err(f"Error R2: {e}")

    # Op R3 – Reserva válida → cancelar
    try:
        r3 = gestor_reservas.crear(c3, alquiler, duracion_horas=8.0)
        gestor_reservas.confirmar(r3.id)
        gestor_reservas.cancelar(r3.id, motivo="Cliente cambió de planes")
        ok(f"Reserva #{r3.id} cancelada correctamente.")
    except SoftwareFJError as e:
        err(f"Error R3: {e}")

    # Op R4 – Duración inválida (debe fallar)
    try:
        gestor_reservas.crear(c1, sala_std, duracion_horas=300.0)
    except ReservaDuracionInvalidaError as e:
        ok(f"[Esperado] Duración inválida → {e}")

    # Op R5 – Confirmar reserva ya confirmada (encadenamiento de excepciones)
    try:
        r1_ref = gestor_reservas.buscar_por_id(r1.id)
        r1_ref.confirmar()   # ya está CONFIRMADA → debe lanzar error
    except ReservaEstadoInvalidoError as e:
        ok(f"[Esperado] Estado inválido al re-confirmar → {e}")

    # Op R6 – Cancelar reserva ya completada (debe fallar)
    try:
        gestor_reservas.cancelar(r2.id, motivo="Intento erróneo")
    except ReservaEstadoInvalidoError as e:
        ok(f"[Esperado] No se puede cancelar reserva COMPLETADA → {e}")

    # Op R7 – Servicio no disponible
    try:
        sala_prm.disponible = False
        gestor_reservas.crear(c1, sala_prm, duracion_horas=1.0).confirmar()
    except ServicioNoDisponibleError as e:
        ok(f"[Esperado] Servicio no disponible → {e}")
    finally:
        sala_prm.disponible = True   # restaurar

    # Op R8 – Reserva sala premium con descuento y IVA (variante sobrecargada)
    try:
        r8 = gestor_reservas.crear(c1, sala_prm, duracion_horas=2.0)
        costo = gestor_reservas.confirmar(r8.id, con_iva=True, descuento=0.10)
        ok(f"Reserva #{r8.id} sala premium (2h, 10% desc, IVA) → ${costo:,.2f} COP")
    except SoftwareFJError as e:
        err(f"Error R8: {e}")

    # Op R9 – Descuento excesivo > 30 % (debe fallar con encadenamiento)
    try:
        r9 = gestor_reservas.crear(c2, sala_std, duracion_horas=1.0)
        gestor_reservas.confirmar(r9.id, descuento=0.50)
    except SoftwareFJError as e:
        ok(f"[Esperado] Descuento excesivo detectado → {e}")


# ══════════════════════════════════════════════════════════════════════════════
#  BLOQUE 5 – Resumen del sistema
# ══════════════════════════════════════════════════════════════════════════════

def bloque_resumen():
    separador("BLOQUE 5 · Resumen del Sistema")

    print("\n  CLIENTES:")
    for c in gestor_clientes.listar():
        info(c.describir())

    print("\n  SERVICIOS:")
    for s in gestor_servicios.listar():
        info(s.describir())

    print("\n  RESERVAS:")
    for r in gestor_reservas.listar():
        info(r.describir())

    estados = {e: len(gestor_reservas.listar_por_estado(e)) for e in EstadoReserva}
    print()
    for estado, cantidad in estados.items():
        info(f"  {estado.name:<12} : {cantidad} reserva(s)")

    separador()
    info(f"Archivo de log generado en: logs/software_fj.log")
    separador()


# ── Punto de entrada ──────────────────────────────────────────────────────────

def main():
    print("\n" + "═" * 65)
    print("   SOFTWARE FJ · Sistema Integral de Gestión de Servicios")
    print("   Universidad Nacional Abierta y a Distancia · UNAD")
    print("═" * 65)

    log_info("═══ Inicio de sesión del sistema Software FJ ═══")

    bloque_clientes()
    bloque_servicios()
    bloque_costos()
    bloque_reservas()
    bloque_resumen()

    log_info("═══ Sesión finalizada correctamente ═══")
    print("\n  Sistema finalizado sin interrupciones. ✔\n")


if __name__ == "__main__":
    main()