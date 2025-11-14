import os
import streamlit as st # Importar streamlit
from supabase import create_client, Client

# Usar los secrets de Streamlit cuando esté desplegado, sino usar variables locales
try:
    # Esto funcionará en Streamlit Cloud
    url: str = "https://pwxcmeennjksbtheekez.supabase.co"
    key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB3eGNtZWVubmprc2J0aGVla2V6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMwNjA3OTQsImV4cCI6MjA3ODYzNjc5NH0.Pdr78VTSsf9reyIs-rR2GzoJk1_driv7OspzGwgJVug"

except:
    # Esto funcionará para pruebas locales (reemplaza con tus claves)
    url: str = "https://pwxcmeennjksbtheekez.supabase.co"
    key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB3eGNtZWVubmprc2J0aGVla2V6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMwNjA3OTQsImV4cCI6MjA3ODYzNjc5NH0.Pdr78VTSsf9reyIs-rR2GzoJk1_driv7OspzGwgJVug"

    
supabase: Client = create_client(url, key)



def agregar_transaccion(fecha, monto, id_categoria, descripcion=""):
    """Inserta una nueva transacción en la base de datos."""
    try:
        # CAMBIO: 'Transacciones' -> 'transacciones'
        response = supabase.table('transacciones').insert({
            "fecha": fecha,
            "monto": monto,
            "id_categoria": id_categoria,
            "descripcion": descripcion
        }).execute()
        print("Transacción agregada:", response)
        return True
    except Exception as e:
        print(f"Error al agregar transacción: {e}")
        return False

def obtener_transacciones_mes(mes, anio):
    """Obtiene todas las transacciones de un mes y año específicos."""
    try:
        primer_dia = f"{anio}-{mes:02d}-01"
        proximo_mes = mes + 1 if mes < 12 else 1
        proximo_anio = anio if mes < 12 else anio + 1
        primer_dia_proximo_mes = f"{proximo_anio}-{proximo_mes:02d}-01"

        response = supabase.rpc('get_transactions_details', {
            'start_date': primer_dia,
            'end_date': primer_dia_proximo_mes
        }).execute()
        
        # Si la llamada a la función falla por el mismo error de mayúsculas,
        # asegúrate de que el SQL que ejecutaste en Supabase también usa minúsculas.
        if response.data is None:
             print("Error en la respuesta de la función RPC:", response.error)

        return response.data
    except Exception as e:
        print(f"Error al obtener transacciones: {e}")
        return []
            
def obtener_categorias():
    """Obtiene todas las categorías de la base de datos."""
    try:
        # CAMBIO: 'Categorias' -> 'categorias'
        response = supabase.table('categorias').select('*').order('nombre').execute()
        return response.data
    except Exception as e:
        print(f"Error al obtener categorías: {e}")
        return []
    
def agregar_categoria(nombre, tipo_gasto):

    if not nombre or not tipo_gasto:
        print("El nombre y el tipo de gasto son requeridos.")
        return None, "Datos incompletos"
    try:
        # La opción 'returning="representation"' hace que Supabase nos devuelva el registro creado
        response = supabase.table('categorias').insert({
            'nombre': nombre,
            'tipo_gasto': tipo_gasto
        }).execute()
        
        # Comprobar si hubo un error (ej: categoría duplicada)
        if hasattr(response, 'error') and response.error:
            return None, response.error.message

        return response.data[0], None # Devuelve la categoría creada y ningún error

    except Exception as e:
        print(f"Error al agregar categoría: {e}")
        return None, str(e)