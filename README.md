# Programacion-Fase-4
Sistema Integral de Gestión de Clientes, Servicios y Reservas


---

## Descripción

Sistema orientado a objetos que gestiona **clientes**, **servicios** y **reservas** para la empresa Software FJ, sin uso de bases de datos. Todo el estado se mantiene en memoria mediante objetos y listas; los errores se registran en un archivo de log.

---

## Estructura del Proyecto

```
software_fj/
├── main.py                  ← Punto de entrada (≥10 operaciones simuladas)
├── README.md
├── models/
│   ├── __init__.py
│   ├── entidades.py         ← EntidadBase (abstracta), Cliente
│   ├── servicios.py         ← Servicio (abstracta), ReservaSala,
│   │                          AlquilerEquipo, AsesoriaEspecializada
│   └── reserva.py           ← Reserva, EstadoReserva
├── services/
│   ├── __init__.py
│   └── gestores.py          ← GestorClientes, GestorServicios, GestorReservas
├── utils/
│   ├── __init__.py
│   ├── excepciones.py       ← Jerarquía de excepciones personalizadas
│   └── logger.py            ← Sistema de logging (archivo + consola)
└── logs/
    └── software_fj.log      ← Generado automáticamente al ejecutar
```

---

## Principios OOP Implementados

| Principio | Dónde |
|-----------|-------|
| **Abstracción** | `EntidadBase`, `Servicio` (clases abstractas con `@abstractmethod`) |
| **Herencia** | `Cliente → EntidadBase`; `ReservaSala`, `AlquilerEquipo`, `AsesoriaEspecializada → Servicio` |
| **Polimorfismo** | `calcular_costo()` sobrescrito en cada servicio; llamado de forma uniforme |
| **Encapsulación** | Atributos privados (`__email`, `__precio_base`, …) con propiedades y setters validadores |
| **Sobrecarga lógica** | `calcular_costo_evento()`, `calcular_costo_lote()`, `calcular_costo_paquete()` como variantes de cálculo |

---

## Manejo de Excepciones

- **Excepciones personalizadas** con jerarquía propia (`SoftwareFJError → ClienteError → ...`)
- **`try/except`** en todos los bloques de negocio
- **`try/except/else`** en `Reserva.confirmar()` (el bloque `else` solo ejecuta si no hubo error)
- **`try/except/finally`** en `Reserva.confirmar()` y `Reserva.cancelar()` (log siempre registrado)
- **Encadenamiento** con `raise ... from e` en errores inesperados
- **Registro en archivo** de cada error y evento mediante `utils/logger.py`

---

## Cómo Ejecutar

```bash
# Desde la carpeta raíz del proyecto:
python main.py
```

No requiere dependencias externas.

---

## Operaciones Simuladas (≥10)

| # | Operación | Resultado esperado |
|---|-----------|-------------------|
| 1 | Registrar cliente válido (Ana Torres) | ✔ Éxito |
| 2 | Registrar cliente válido (Luis Pérez) | ✔ Éxito |
| 3 | Registrar cliente con email duplicado | ✘ `ClienteYaExisteError` |
| 4 | Registrar cliente con email inválido | ✘ `ClienteEmailInvalidoError` |
| 5 | Registrar cliente con nombre inválido | ✘ `ClienteNombreInvalidoError` |
| 6 | Registrar cliente con teléfono inválido | ✘ `ClienteTelefonoInvalidoError` |
| 7 | Registrar tercer cliente válido | ✔ Éxito |
| 8 | Crear servicios válidos (sala, alquiler, asesoría) | ✔ Éxito |
| 9 | Crear servicio con precio negativo | ✘ `ServicioParametroInvalidoError` |
| 10 | Reserva válida → confirmar | ✔ Éxito con costo calculado |
| 11 | Reserva válida → confirmar → completar | ✔ Éxito |
| 12 | Reserva → cancelar | ✔ Éxito |
| 13 | Duración inválida en reserva | ✘ `ReservaDuracionInvalidaError` |
| 14 | Re-confirmar reserva ya confirmada | ✘ `ReservaEstadoInvalidoError` |
| 15 | Descuento > 30 % | ✘ `ServicioCostoInvalidoError` |
