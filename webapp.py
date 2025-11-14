# webapp.py (VERSIÓN ACTUALIZADA)
import streamlit as st
from datetime import datetime
import database  # ¡Reutilizamos nuestra lógica!
import pandas as pd

# --- Configuración de la Página ---
st.set_page_config(page_title="Control de Gastos", layout="wide")
st.title("📊 Mi Panel de Control de Gastos")

# --- Funciones de la App ---
def refrescar_categorias():
    """Obtiene las categorías de la BD para usarlas en los selectbox."""
    categorias_data = database.obtener_categorias()
    # Creamos un diccionario que mapea el nombre de la categoría a su ID
    if categorias_data:
        return {cat['nombre']: cat['id'] for cat in categorias_data}
    return {}

def mostrar_reporte():
    """Obtiene y muestra el reporte de transacciones del mes."""
    st.header(f"Reporte de {datetime.now().strftime('%B %Y')}")
    
    # Obtener transacciones del mes actual
    transacciones = database.obtener_transacciones_mes(mes=datetime.now().month, anio=datetime.now().year)

    if not transacciones:
        st.warning("Aún no hay transacciones para mostrar este mes.")
        return transacciones # Devolvemos una lista vacía

    # Convertir a un DataFrame de Pandas para una mejor visualización
    df = pd.DataFrame(transacciones)
    df['monto'] = pd.to_numeric(df['monto'])

    # --- Métricas Principales ---
    total_mes = df['monto'].sum()
    total_fijos = df[df['tipo_gasto'] == 'Fijo']['monto'].sum()
    total_variables = df[df['tipo_gasto'] == 'Variable']['monto'].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Gasto Total del Mes", f"${total_mes:,.2f}")
    col2.metric("Total Fijos", f"${total_fijos:,.2f}")
    col3.metric("Total Variables", f"${total_variables:,.2f}")

    # --- Tabla de Transacciones ---
    st.dataframe(df[['fecha', 'categoria_nombre', 'tipo_gasto', 'monto']], use_container_width=True)
    
    return transacciones # Devolvemos los datos para usarlos en la sección de eliminar

# --- Barra Lateral (Sidebar) ---
st.sidebar.header("Acciones")

# Diccionario de categorías para usar en los menús
categorias_dict = refrescar_categorias()

# --- NUEVO: Expansor para crear nuevas categorías ---
with st.sidebar.expander("➕ Crear Nueva Categoría"):
    with st.form("nueva_categoria_form", clear_on_submit=True):
        nuevo_nombre = st.text_input("Nombre de la nueva categoría:")
        nuevo_tipo = st.selectbox("Tipo de Gasto:", ["Variable", "Fijo"])
        submitted_cat = st.form_submit_button("Guardar Categoría")
        
        if submitted_cat:
            if nuevo_nombre:
                nueva_cat, error = database.agregar_categoria(nuevo_nombre, nuevo_tipo)
                if error:
                    st.error(f"Error: {error}")
                else:
                    st.success(f"¡Categoría '{nueva_cat['nombre']}' creada!")
                    # Forzamos un rerun para que el menú de categorías se actualice
                    st.experimental_rerun()
            else:
                st.warning("El nombre no puede estar vacío.")

# Formulario para agregar un nuevo gasto
st.sidebar.header("Nuevo Gasto")
with st.sidebar.form("nuevo_gasto_form", clear_on_submit=True):
    monto = st.number_input("Monto:", min_value=0.0, format="%.2f")
    
    # Usamos el diccionario de categorías para el menú
    categoria_nombre = st.selectbox("Categoría:", options=list(categorias_dict.keys()))
    
    descripcion = st.text_input("Descripción (Opcional):")

    submitted_gasto = st.form_submit_button("Guardar Gasto")
    if submitted_gasto:
        id_categoria = categorias_dict[categoria_nombre]
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        if database.agregar_transaccion(fecha_actual, monto, id_categoria, descripcion):
            st.sidebar.success("¡Gasto guardado con éxito!")
            # Forzamos un rerun para que el reporte principal se actualice
            st.experimental_rerun()
        else:
            st.sidebar.error("Hubo un error al guardar.")

# --- Área Principal ---
transacciones_actuales = mostrar_reporte()

st.markdown("---") # Separador visual

# --- NUEVO: Sección para eliminar un gasto ---
st.header("❌ Eliminar un Gasto")

if transacciones_actuales:
    # Creamos una lista de strings descriptivos para el menú de selección
    opciones_eliminar = {f"{t['fecha']} - {t['categoria_nombre']} - ${t['monto']:.2f} (ID: {t['id']})": t['id'] for t in transacciones_actuales}
    
    gasto_a_eliminar_str = st.selectbox("Selecciona el gasto a eliminar:", options=opciones_eliminar.keys())
    
    if st.button("Eliminar Gasto Seleccionado"):
        id_a_eliminar = opciones_eliminar[gasto_a_eliminar_str]
        if database.eliminar_transaccion(id_a_eliminar):
            st.success("Gasto eliminado correctamente.")
            st.experimental_rerun()
        else:
            st.error("No se pudo eliminar el gasto.")
else:
    st.info("No hay gastos para eliminar este mes.")