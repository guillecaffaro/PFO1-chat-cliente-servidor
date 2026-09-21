import socket


HOST = "localhost"
PORT = 5000


def conectar_servidor():

    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        cliente.connect((HOST, PORT))

        print("Conectado al servidor.")

        return cliente

    except ConnectionRefusedError:
        print("No se pudo conectar.")
        print("Verificá que el servidor esté ejecutándose.")

        cliente.close()

        return None


def enviar_mensajes(cliente):

    print("\nEscribí tus mensajes.")
    print("Para finalizar escribí: éxito\n")

    while True:

        mensaje = input("Mensaje: ")

        # Se acepta la palabra de salida con o sin tilde.
        if mensaje.lower().strip() in ("éxito", "exito"):
            print("Finalizando cliente...")
            break

        if not mensaje.strip():
            print("El mensaje no puede estar vacío.")
            continue

        try:
            cliente.sendall(mensaje.encode("utf-8"))

            respuesta = cliente.recv(1024)

            # Si recv() devuelve vacío, el servidor cerró la conexión.
            if not respuesta:
                print("El servidor cerró la conexión.")
                break

            respuesta = respuesta.decode("utf-8")

            print("Servidor:", respuesta)

        except ConnectionError:
            print("Se perdió la conexión con el servidor.")
            break


def main():

    cliente = conectar_servidor()

    if cliente is None:
        return

    try:
        enviar_mensajes(cliente)

    finally:
        cliente.close()


if __name__ == "__main__":
    main()