from datetime import datetime, date
from typing import Type, TypeVar

E = TypeVar("E")


def pedir_texto(prompt: str, obligatorio: bool = True) -> str:
    while True:
        valor = input(prompt).strip()
        if valor or not obligatorio:
            return valor
        print("  Este dato es obligatorio, intenta de nuevo.")

def pedir_float_rango(prompt: str, minimo: float, maximo: float) -> float:
    while True:
        crudo = input(prompt).strip()
        try:
            valor = float(crudo)
        except ValueError:
            print(f"  '{crudo}' no es un número válido.")
            continue
        if minimo <= valor <= maximo:
            return valor
        print(f"  Debe estar entre {minimo} y {maximo}.")

def pedir_fecha(prompt: str) -> date:
    formatos_aceptados = ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%Y/%m/%d"]
    while True:
        crudo = input(prompt + " (DD/MM/AAAA): ").strip()
        for formato in formatos_aceptados:
            try:
                return datetime.strptime(crudo, formato).date()
            except ValueError:
                continue
        print(f"  '{crudo}' no es una fecha válida. Usa el formato DD/MM/AAAA (ej. 27/09/2026).")

def pedir_si_no(prompt: str) -> bool:
    while True:
        crudo = input(prompt + " (s/n): ").strip().lower()
        if crudo in ("s", "si", "sí"):
            return True
        if crudo in ("n", "no"):
            return False
        print("  Responde 's' o 'n'.")

def pedir_opcion_enum(prompt: str, enum_cls: Type[E]) -> E:
    opciones = list(enum_cls)
    print(prompt)
    for i, op in enumerate(opciones, start=1):
        print(f"  {i}. {op.value}")
    while True:
        crudo = input("Elige una opción: ").strip()
        if crudo.isdigit() and 1 <= int(crudo) <= len(opciones):
            return opciones[int(crudo) - 1]
        print("  Opción inválida, intenta de nuevo.")