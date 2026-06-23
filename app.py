import streamlit as st
import pandas as pd
from api_client import obtener_usuarios_api
from database import (
    crear_tabla,
    guardar_usuarios,
    consultar_usuarios,
    buscar_usuario,
    eliminar_datos,
    contar_registros,
)

# ── Configuración de la página ──────────────────────────────────────────────
st.set_page_config(
    page_title="Cloud Project · API + SQLite",
    page_icon="☁️",
    layout="wide",
)

# Asegurar que la tabla exista al iniciar
crear_tabla()

# ── Menú lateral ────────────────────────────────────────────────────────────
st.sidebar.title("☁️ Proyecto Cloud")
st.sidebar.caption("API + SQLite + Streamlit")

menu = st.sidebar.selectbox(
    "Seleccione una opción",
    ["Inicio", "Consumir API", "Ver base de datos", "Buscar usuario", "Eliminar datos"],
)

# ── Página: Inicio ───────────────────────────────────────────────────────────
if menu == "Inicio":
    st.title("☁️ Proyecto Cloud: API + SQLite + Streamlit")
    st.markdown(
        """
        Esta aplicación simula una arquitectura cloud sencilla:

        | Componente | Función |
        |---|---|
        | **API pública** (`jsonplaceholder`) | Fuente de datos externos vía GET |
        | **SQLite** (`usuarios_api.db`) | Persistencia local de los datos |
        | **Streamlit** | Interfaz web interactiva |
        | **GitHub + Streamlit Cloud** | Despliegue público |

        ### ¿Cómo usar la app?
        1. Ve a **Consumir API** para obtener y guardar usuarios.
        2. Ve a **Ver base de datos** para revisar los registros guardados.
        3. Usa **Buscar usuario** para filtrar por nombre, usuario o email.
        4. Usa **Eliminar datos** para limpiar la tabla si necesitas empezar de nuevo.
        """
    )
    st.info(f"📦 Registros actuales en SQLite: **{contar_registros()}**")

# ── Página: Consumir API ─────────────────────────────────────────────────────
elif menu == "Consumir API":
    st.title("🌐 Consumir API")
    st.markdown("Fuente: `https://jsonplaceholder.typicode.com/users`")

    if st.button("📥 Obtener y guardar usuarios desde la API"):
        with st.spinner("Consultando API..."):
            usuarios = obtener_usuarios_api()

        if not usuarios:
            st.error("❌ No se pudo conectar a la API. Verifica tu conexión a internet.")
        else:
            st.success(f"✅ {len(usuarios)} usuarios obtenidos desde la API.")

            # Mostrar datos crudos de la API
            df_api = pd.DataFrame([
                {
                    "id": u["id"],
                    "nombre": u["name"],
                    "usuario": u["username"],
                    "email": u["email"],
                    "ciudad": u["address"]["city"],
                    "telefono": u["phone"],
                    "sitio_web": u["website"],
                }
                for u in usuarios
            ])
            st.subheader("Datos recibidos de la API")
            st.dataframe(df_api, use_container_width=True)

            # Guardar en SQLite
            insertados = guardar_usuarios(usuarios)
            if insertados > 0:
                st.success(f"💾 {insertados} registro(s) nuevo(s) guardado(s) en SQLite.")
            else:
                st.warning("⚠️ Los datos ya existían en la base de datos (no se insertaron duplicados).")

# ── Página: Ver base de datos ────────────────────────────────────────────────
elif menu == "Ver base de datos":
    st.title("🗄️ Ver base de datos SQLite")

    df = consultar_usuarios()

    if df.empty:
        st.warning("La base de datos está vacía. Ve a **Consumir API** primero.")
    else:
        st.success(f"✅ {len(df)} registro(s) encontrado(s) en `usuarios_api.db`.")
        st.dataframe(df, use_container_width=True)

        # Estadística extra: usuarios por ciudad
        st.subheader("📊 Usuarios por ciudad")
        ciudades = df.groupby("ciudad").size().reset_index(name="cantidad")
        st.bar_chart(ciudades.set_index("ciudad"))

# ── Página: Buscar usuario ───────────────────────────────────────────────────
elif menu == "Buscar usuario":
    st.title("🔍 Buscar usuario")

    termino = st.text_input("Ingresa nombre, usuario o email a buscar:")

    if termino:
        resultado = buscar_usuario(termino)
        if resultado.empty:
            st.warning(f"No se encontraron resultados para: **{termino}**")
        else:
            st.success(f"✅ {len(resultado)} resultado(s) encontrado(s).")
            st.dataframe(resultado, use_container_width=True)
    else:
        st.info("Escribe algo en el campo de búsqueda para filtrar.")

# ── Página: Eliminar datos ───────────────────────────────────────────────────
elif menu == "Eliminar datos":
    st.title("🗑️ Eliminar datos")
    st.warning("⚠️ Esta acción eliminará **todos** los registros de la tabla `usuarios`.")

    total = contar_registros()
    st.info(f"Registros actuales: **{total}**")

    if total == 0:
        st.success("La tabla ya está vacía.")
    else:
        if st.button("🗑️ Eliminar todos los registros"):
            eliminar_datos()
            st.success("✅ Todos los registros han sido eliminados.")
            st.rerun()
