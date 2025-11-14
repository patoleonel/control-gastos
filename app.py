# app.py (MODIFICADO)
import customtkinter as ctk
from datetime import datetime
import database # Importamos nuestro módulo de base de datos

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Control de Gastos")
        self.geometry("800x600")
        ctk.set_appearance_mode("dark")

        # --- Frame de Entrada de Datos ---
        self.entry_frame = ctk.CTkFrame(self)
        self.entry_frame.pack(pady=20, padx=20, fill="x")

        ctk.CTkLabel(self.entry_frame, text="Monto:").grid(row=0, column=0, padx=(10,5), pady=10)
        self.monto_entry = ctk.CTkEntry(self.entry_frame, placeholder_text="$0.00")
        self.monto_entry.grid(row=0, column=1, padx=5, pady=10)

        ctk.CTkLabel(self.entry_frame, text="Categoría:").grid(row=0, column=2, padx=(20,5), pady=10)
        
        self.categoria_menu = ctk.CTkOptionMenu(self.entry_frame, values=["Cargando..."])
        self.categoria_menu.grid(row=0, column=3, padx=5, pady=10)
        
        # --- NUEVO: Botón para añadir categoría ---
        self.add_cat_button = ctk.CTkButton(self.entry_frame, text="+", width=30, command=self.abrir_ventana_nueva_categoria)
        self.add_cat_button.grid(row=0, column=4, padx=(0,10), pady=10)

        self.guardar_button = ctk.CTkButton(self.entry_frame, text="Guardar Gasto", command=self.guardar_gasto)
        self.guardar_button.grid(row=0, column=5, padx=10, pady=10, sticky="e")
        
        self.entry_frame.grid_columnconfigure(5, weight=1) # Para que el botón se alinee a la derecha

        # --- Frame de Reporte ---
        self.report_frame = ctk.CTkFrame(self)
        self.report_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        ctk.CTkLabel(self.report_frame, text="Transacciones de Noviembre 2025", font=("Arial", 16)).pack(pady=10)
        
        self.report_text = ctk.CTkTextbox(self.report_frame, width=700, height=400)
        self.report_text.pack(padx=10, pady=10, fill="both", expand=True)

        # Cargar los datos iniciales
        self.refrescar_categorias()
        self.actualizar_reporte()

    def refrescar_categorias(self):
        """Obtiene las categorías de la BD y actualiza el menú desplegable."""
        self.categorias = database.obtener_categorias()
        if self.categorias:
            self.categorias_nombres = [cat['nombre'] for cat in self.categorias]
            self.categoria_menu.configure(values=self.categorias_nombres)
            self.categoria_menu.set(self.categorias_nombres[0]) # Seleccionar la primera
        else:
            self.categoria_menu.configure(values=["Sin categorías"])
            self.categoria_menu.set("Sin categorías")

    def abrir_ventana_nueva_categoria(self):
        """Crea una ventana emergente para añadir una nueva categoría."""
        self.new_cat_window = ctk.CTkToplevel(self)
        self.new_cat_window.title("Nueva Categoría")
        self.new_cat_window.geometry("350x200")
        self.new_cat_window.transient(self) # Mantenerla encima de la ventana principal
        
        ctk.CTkLabel(self.new_cat_window, text="Nombre de la Categoría:").pack(pady=(20,5))
        self.new_cat_name_entry = ctk.CTkEntry(self.new_cat_window, placeholder_text="Ej: Supermercado")
        self.new_cat_name_entry.pack(pady=5, padx=20, fill="x")

        ctk.CTkLabel(self.new_cat_window, text="Tipo de Gasto:").pack(pady=(10,5))
        self.new_cat_type_menu = ctk.CTkOptionMenu(self.new_cat_window, values=["Variable", "Fijo"])
        self.new_cat_type_menu.pack(pady=5)

        save_button = ctk.CTkButton(self.new_cat_window, text="Guardar", command=self.guardar_nueva_categoria)
        save_button.pack(pady=20)
    
    def guardar_nueva_categoria(self):
        """Llama a la función de la base de datos y actualiza la UI."""
        nombre = self.new_cat_name_entry.get()
        tipo = self.new_cat_type_menu.get()

        nueva_cat, error = database.agregar_categoria(nombre, tipo)

        if error:
            print(f"Error al crear categoría: {error}")
            # Aquí podrías mostrar un mensaje de error en la ventana emergente
            return

        print(f"Categoría '{nueva_cat['nombre']}' creada con éxito.")
        self.new_cat_window.destroy() # Cerrar la ventana emergente
        self.refrescar_categorias() # Actualizar el menú desplegable en la ventana principal
        self.categoria_menu.set(nueva_cat['nombre']) # Seleccionar la categoría recién creada

    def guardar_gasto(self):
        # ... (esta función se mantiene exactamente igual que antes) ...
        monto_str = self.monto_entry.get()
        categoria_nombre = self.categoria_menu.get()

        if not monto_str or categoria_nombre == "Sin categorías":
            print("Monto y categoría son requeridos.")
            return

        try:
            monto = float(monto_str.replace('$', '').replace(',', '.'))
        except ValueError:
            print("El monto debe ser un número.")
            return

        id_cat_seleccionada = next((cat['id'] for cat in self.categorias if cat['nombre'] == categoria_nombre), None)
        
        if id_cat_seleccionada is not None:
            fecha_actual = datetime.now().strftime("%Y-%m-%d")
            if database.agregar_transaccion(fecha_actual, monto, id_cat_seleccionada):
                print("Gasto guardado con éxito.")
                self.monto_entry.delete(0, 'end')
                self.actualizar_reporte()
            else:
                print("Error al guardar el gasto.")

    def actualizar_reporte(self):
        # ... (esta función se mantiene exactamente igual que antes) ...
        self.report_text.delete("1.0", "end")
        transacciones = database.obtener_transacciones_mes(mes=11, anio=2025)
        total_mes = 0
        total_fijos = 0
        total_variables = 0
        
        self.report_text.insert("end", f"{'Fecha':<12} {'Categoría':<20} {'Tipo':<10} {'Monto':>12}\n")
        self.report_text.insert("end", "="*56 + "\n")

        if transacciones:
            for t in transacciones:
                monto = float(t['monto'])
                self.report_text.insert("end", f"{t['fecha']:<12} {t['categoria_nombre']:<20} {t['tipo_gasto']:<10} ${monto:>10.2f}\n")
                total_mes += monto
                if t['tipo_gasto'] == 'Fijo':
                    total_fijos += monto
                else:
                    total_variables += monto
        
        self.report_text.insert("end", "\n" + "="*56 + "\n")
        self.report_text.insert("end", f"TOTAL GASTOS FIJOS:   ${total_fijos:,.2f}\n")
        self.report_text.insert("end", f"TOTAL GASTOS VARIABLES: ${total_variables:,.2f}\n")
        self.report_text.insert("end", f"TOTAL DEL MES:          ${total_mes:,.2f}\n")

if __name__ == "__main__":
    app = App()
    app.mainloop()