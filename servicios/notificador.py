class Notificador:
    def enviar(self, destinatario: str, mensaje: str) -> bool:
        print(f"\n[NOTIFICACIÓN -> {destinatario}]")
        print(mensaje)
        print("-" * 40)
        return True
