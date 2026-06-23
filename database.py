import sqlite3
import pandas as pd

DB_NAME = "usuarios_api.db"

def conectar():
    return sqlite3.connect(DB_NAME)

def crear_tabla():
    """Crea la tabla usuarios si no existe."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY,
            nombre TEXT,
            usuario TEXT,
            email TEXT,
            ciudad TEXT,
            telefono TEXT,
            sitio_web TEXT
        )
    """)
    conn.commit()
    conn.close()

def guardar_usuarios(usuarios):
    """Inserta los usuarios de la API en SQLite, evitando duplicados por id."""
    conn = conectar()
    cursor = conn.cursor()
    insertados = 0
    for u in usuarios:
        direccion = u.get("address", {})
        cursor.execute("""
            INSERT OR IGNORE INTO usuarios (id, nombre, usuario, email, ciudad, telefono, sitio_web)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            u.get("id"),
            u.get("name"),
            u.get("username"),
            u.get("email"),
            direccion.get("city"),
            u.get("phone"),
            u.get("website"),
        ))
        if cursor.rowcount > 0:
            insertados += 1
    conn.commit()
    conn.close()
    return insertados

def consultar_usuarios():
    """Retorna todos los registros como DataFrame de pandas."""
    conn = conectar()
    df = pd.read_sql_query("SELECT * FROM usuarios", conn)
    conn.close()
    return df

def buscar_usuario(termino):
    """Busca usuarios por nombre, usuario o email."""
    conn = conectar()
    df = pd.read_sql_query(
        "SELECT * FROM usuarios WHERE nombre LIKE ? OR usuario LIKE ? OR email LIKE ?",
        conn,
        params=(f"%{termino}%", f"%{termino}%", f"%{termino}%"),
    )
    conn.close()
    return df

def eliminar_datos():
    """Elimina todos los registros de la tabla."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios")
    conn.commit()
    conn.close()

def contar_registros():
    """Retorna el número total de registros."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    total = cursor.fetchone()[0]
    conn.close()
    return total
