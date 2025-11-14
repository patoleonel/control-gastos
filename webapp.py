# webapp.py
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
        return

    # Convertir a un DataFrame de Pandas para una mejor visualización
    df = pd.DataFrame(transacciones)
    df['monto'] = pd.to_numeric(df['monto']) # Asegurarse que el monto es numérico

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


# --- Barra Lateral para Ingresar Datos ---
st.sidebar.header("Nuevo Gasto")
categorias_dict = refrescar_categorias()

with st.sidebar.form("nuevo_gasto_form", clear_on_submit=True):
    monto = st.number_input("Monto:", min_value=0.0, format="%.2f")
    
    categoria_nombre = st.selectbox("Categoría:", options=list(categorias_dict.keys()))
    
    descripcion = st.text_input("Descripción (Opcional):")

    submitted = st.form_submit_button("Guardar Gasto")
    if submitted:
        id_categoria = categorias_dict[categoria_nombre]
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        if database.agregar_transaccion(fecha_actual, monto, id_categoria, descripcion):
            st.sidebar.success("¡Gasto guardado con éxito!")
        else:
            st.sidebar.error("Hubo un error al guardar.")

# --- Área Principal para el Reporte ---
mostrar_reporte()

# Botón para refrescar el reporte manualmente
if st.button('Refrescar Reporte'):

    st.experimental_rerun()