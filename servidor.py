import socket
import sqlite3
from datetime import datetime


HOST = "localhost"
PORT = 5000
DB_NAME = "mensajes.db"


def inicializar_db():
    try:
        conexion = sqlite3.connect(DB_NAME)
        cursor = conexion.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mensajes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contenido TEXT NOT NULL,
                fecha_envio TEXT NOT NULL,
                ip_cliente TEXT NOT NULL
            )
        """)

        conexion.commit()
        conexion.close()

        print("Base de datos inicializada correctamente.")

    except sqlite3.Error as error:
        print("Error al acceder a la base de datos:", error)
        raise


def guardar_mensaje(contenido, ip_cliente):

    fecha_envio = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conexion = None

    try:
        conexion = sqlite3.connect(DB_NAME)
        cursor = conexion.cursor()

        # Los signos ? funcionan como parámetros y evitan
        # concatenar directamente los datos dentro de la consulta SQL.
        cursor.execute("""
            INSERT INTO mensajes (contenido, fecha_envio, ip_cliente)
            VALUES (?, ?, ?)
        """, (contenido, fecha_envio, ip_cliente))

        conexion.commit()

        return fecha_envio

    except sqlite3.Error as error:
        print("Error al guardar el mensaje:", error)
        return None

    finally:
        if conexion is not None:
            conexion.close()


def inicializar_socket():

    # Configuración del socket TCP/IP:
    # AF_INET utiliza direcciones IPv4 y SOCK_STREAM establece una conexión TCP.
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # bind() asocia el servidor con localhost y el puerto 5000.
        # Si el puerto ya está ocupado, se produce un OSError.
        servidor.bind((HOST, PORT))

        # listen() deja el servidor esperando conexiones de clientes.
        servidor.listen()

        print(f"Servidor escuchando en {HOST}:{PORT}")

        return servidor

    except OSError as error:
        print(f"Error al iniciar el servidor: {error}")
        print("El puerto 5000 podría estar ocupado.")

        servidor.close()

        return None


def manejar_cliente(conexion, direccion):

    # direccion contiene la IP y el puerto del cliente.
    # direccion[0] permite obtener solamente la IP.
    ip_cliente = direccion[0]

    print(f"Cliente conectado desde: {ip_cliente}")

    try:
        while True:

            # recv(1024) permite recibir hasta 1024 bytes por vez.
            datos = conexion.recv(1024)

            if not datos:
                break

            mensaje = datos.decode("utf-8")

            print(f"Mensaje recibido: {mensaje}")

            fecha = guardar_mensaje(mensaje, ip_cliente)

            if fecha:
                respuesta = f"Mensaje recibido: {fecha}"
            else:
                respuesta = "Error al guardar el mensaje."

            conexion.sendall(respuesta.encode("utf-8"))

    except ConnectionError:
        print("El cliente perdió la conexión.")

    finally:
        conexion.close()
        print("Cliente desconectado.")


def aceptar_conexiones(servidor):

    while True:
        try:
            conexion, direccion = servidor.accept()

            manejar_cliente(conexion, direccion)

        except KeyboardInterrupt:
            print("\nServidor detenido.")
            break

        except OSError as error:
            print("Error en la conexión:", error)


def main():

    try:
        inicializar_db()

    except sqlite3.Error:
        print("No se pudo iniciar la base de datos.")
        return

    servidor = inicializar_socket()

    if servidor is None:
        return

    try:
        aceptar_conexiones(servidor)

    finally:
        servidor.close()


if __name__ == "__main__":
    main()