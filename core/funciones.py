import os
from datetime import datetime
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

# --- Configuración de la base de datos ---
db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)

cursor = db.cursor()

# --- Obtener ruta absoluta de la carpeta donde está el script ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) 

def ruta_imagen(nombre_archivo):
    return os.path.join(BASE_DIR, "img", nombre_archivo)

def cargar_menu():
    cursor.execute("SELECT id, nombre, descripcion, imagen FROM menu")
    resultados = cursor.fetchall()
    menu_db = {}
    for id_, nombre, descripcion, imagen in resultados:
        menu_db[str(id_)] = {
            "nombre": nombre,
            "descripcion": descripcion,
            "imagen": ruta_imagen(imagen)
        }
    return menu_db

def guardar_pedido(usuario, pedido, fecha):
    sql = "INSERT INTO pedidos (usuario, pedido, fecha) VALUES (%s, %s, %s)"
    cursor.execute(sql, (usuario, pedido, fecha))
    db.commit()
    return cursor.lastrowid
