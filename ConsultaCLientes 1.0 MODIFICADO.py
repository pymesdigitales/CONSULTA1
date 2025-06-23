import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sqlite3
import logging
from datetime import datetime
import os

class EnergyConsultaApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Energy - Consulta clientes")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Configurar logging
        self.setup_logging()
        
        # Variables
        self.usuario_var = tk.StringVar()
        self.cliente_id_var = tk.StringVar()
        
        # Crear interfaz
        self.create_widgets()
        
        # Configurar la ventana para que se cierre correctamente
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Log de inicio de sesión
        self.log_event("Aplicación iniciada")
    
    def setup_logging(self):
        """Configurar el sistema de logging"""
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        log_filename = f"logs/energy_consulta_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def log_event(self, mensaje):
        """Registrar evento en el log"""
        self.logger.info(mensaje)
    
    def log_error(self, mensaje, error=None):
        """Registrar error en el log"""
        if error:
            self.logger.error(f"{mensaje}: {str(error)}")
        else:
            self.logger.error(mensaje)
    
    def create_widgets(self):
        """Crear todos los widgets de la interfaz"""
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar el grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="Energy - Consulta Clientes", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Fecha y hora actual
        self.datetime_label = ttk.Label(main_frame, text="", font=('Arial', 10))
        self.datetime_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        self.update_datetime()
        
        # Campo Usuario
        ttk.Label(main_frame, text="Nombre de usuario:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.usuario_entry = ttk.Entry(main_frame, textvariable=self.usuario_var, width=30)
        self.usuario_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Campo ID Cliente  
        ttk.Label(main_frame, text="Cédula de cliente:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.cliente_entry = ttk.Entry(main_frame, textvariable=self.cliente_id_var, width=30)
        self.cliente_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Botón Buscar
        self.buscar_btn = ttk.Button(main_frame, text="Buscar", command=self.buscar_cliente)
        self.buscar_btn.grid(row=4, column=0, columnspan=2, pady=20)
        
        # Área de resultados
        ttk.Label(main_frame, text="Resultados:").grid(row=5, column=0, sticky=tk.W, pady=(10, 5))
        
        # Text widget con scrollbar para mostrar resultados
        self.resultados_text = scrolledtext.ScrolledText(main_frame, height=10, width=70)
        self.resultados_text.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Frame para botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=20)
        
        # Botones Nueva Búsqueda y Salir
        self.nueva_busqueda_btn = ttk.Button(button_frame, text="Nueva Búsqueda", 
                                           command=self.nueva_busqueda)
        self.nueva_busqueda_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.salir_btn = ttk.Button(button_frame, text="Salir", command=self.on_closing)
        self.salir_btn.pack(side=tk.LEFT)
        
        # Configurar el grid para que se expanda
        main_frame.rowconfigure(6, weight=1)
        
        # Bind Enter key para buscar
        self.root.bind('<Return>', lambda event: self.buscar_cliente())
    
    def update_datetime(self):
        """Actualizar la fecha y hora mostrada"""
        now = datetime.now()
        fecha_hora = now.strftime("%d/%m/%Y - %H:%M:%S")
        self.datetime_label.config(text=f"Fecha y Hora: {fecha_hora}")
        # Programar próxima actualización en 1 segundo
        self.root.after(1000, self.update_datetime)
    
    def conectar_bd(self):
        """Conectar a la base de datos SQLite"""
        try:
            conn = sqlite3.connect('BD_CONTROL_CARTERA.db')
            return conn
        except sqlite3.Error as e:
            self.log_error("Error al conectar con la base de datos", e)
            return None
    
    def buscar_cliente(self):
        """Buscar cliente en la base de datos"""
        usuario = self.usuario_var.get().strip()
        cliente_id = self.cliente_id_var.get().strip()
        
        # Validar campos
        if not usuario:
            messagebox.showwarning("Advertencia", "Por favor ingrese el nombre de usuario")
            self.usuario_entry.focus()
            return
        
        if not cliente_id:
            messagebox.showwarning("Advertencia", "Por favor ingrese Cédula del cliente")
            self.cliente_entry.focus()
            return
        
        # Log de búsqueda
        self.log_event(f"Búsqueda iniciada - Usuario: {usuario}, Cédula Cliente: {cliente_id}")
        
        # Limpiar resultados anteriores
        self.resultados_text.delete(1.0, tk.END)
        
        # Conectar a la base de datos
        conn = self.conectar_bd()
        if not conn:
            messagebox.showerror("Error", "No se pudo conectar a la base de datos")
            return
        
        try:
            cursor = conn.cursor()
            
            # Buscar el cliente en la tabla X_SUBIR_DATA por campo Nro
            query = "SELECT * FROM X_SUBIR_DATA MAESTRO_CARTERA WHERE Campo2= ?"
            cursor.execute(query, (cliente_id,))
            resultados = cursor.fetchall()
            
            if resultados:
                self.resultados_text.insert(tk.END, f"    No hacer Visita.   Operaciones encontrados para id: {cliente_id}\n")
                self.resultados_text.insert(tk.END, "=" * 50 + "\n\n")
                
                # Obtener nombres de columnas
                column_names = [description[0] for description in cursor.description]
                
                # Encontrar el índice del campo Estado
                estado_index = None
                for i, col_name in enumerate(column_names):
                    if col_name.lower() == 'Campo3':
                        estado_index = i
                        break
                
                if estado_index is not None:
                    for i, row in enumerate(resultados, 1):
                        estado_value = row[estado_index]
                        self.resultados_text.insert(tk.END, f"Registro {i}: {estado_value}\n")
                else:
                    #self.resultados_text.insert(tk.END, "No se encontró el campo 'Estado' en la tabla.\n")
                    self.log_error("Campo 'Estado' no encontrado en la tabla X_SUBIR_DATA")
                
                self.log_event(f"Búsqueda exitosa - {len(resultados)} estado(s) encontrado(s)")
                
            else:
                self.resultados_text.insert(tk.END, f"Hacer Visita. No se encontraron resultados para ID : {cliente_id}")
                self.log_event(f"Búsqueda sin resultados - Cédula Cliente: {cliente_id}")
                
        except sqlite3.Error as e:
            error_msg = f"Error al consultar la base de datos: {str(e)}"
            self.resultados_text.insert(tk.END, error_msg)
            self.log_error("Error en consulta de base de datos", e)
            messagebox.showerror("Error de Base de Datos", error_msg)
            
        except Exception as e:
            error_msg = f"Error inesperado: {str(e)}"
            self.resultados_text.insert(tk.END, error_msg)
            self.log_error("Error inesperado durante la búsqueda", e)
            messagebox.showerror("Error", error_msg)
            
        finally:
            if conn:
                conn.close()
    
    def nueva_busqueda(self):
        """Limpiar campos para nueva búsqueda"""
        self.usuario_var.set("")
        self.cliente_id_var.set("")
        self.resultados_text.delete(1.0, tk.END)
        self.usuario_entry.focus()
        self.log_event("Nueva búsqueda iniciada - Campos limpiados")
    
    def on_closing(self):
        """Manejar el cierre de la aplicación"""
        self.log_event("Aplicación cerrada por el usuario")
        self.root.destroy()
    
    def run(self):
        """Ejecutar la aplicación"""
        self.root.mainloop()

# Función para crear la base de datos de ejemplo (opcional)
def crear_bd_ejemplo():
    """Crear base de datos de ejemplo si no existe"""
    try:
        conn = sqlite3.connect('BD_CONTROL_CARTERA.db')
        cursor = conn.cursor()
        
        # Crear tabla si no existe
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS X_SUBIR_DATA (
                Cedula TEXT,
                nombre TEXT,
                Estado TEXT,
                fecha_registro DATE,
                monto REAL
            )
        ''')
        
        # Insertar datos de ejemplo si la tabla está vacía
        cursor.execute("SELECT COUNT(*) FROM X_SUBIR_DATA")
        if cursor.fetchone()[0] == 0:
            datos_ejemplo = [
                ('12345', 'Juan Pérez', 'ACTIVO', '2024-01-15', 1500.00),
                ('67890', 'María García', 'INACTIVO', '2024-02-20', 2300.50),
                ('11111', 'Carlos López', 'ACTIVO', '2024-03-10', 800.75),
                ('12345', 'Juan Pérez', 'MOROSO', '2024-04-05', 500.00),  # Mismo Nro, diferente estado
            ]
            
            cursor.executemany(
                "INSERT INTO X_SUBIR_DATA (Cedula, nombre, Estado, fecha_registro, monto) VALUES (?, ?, ?, ?, ?)",
                datos_ejemplo
            )
        
        conn.commit()
        conn.close()
        print("Base de datos creada/verificada exitosamente")
        
    except sqlite3.Error as e:
        print(f"Error al crear la base de datos: {e}")

if __name__ == "__main__":
    # Crear base de datos de ejemplo (comentar si ya existe)
    crear_bd_ejemplo()
    
    # Ejecutar la aplicación
    app = EnergyConsultaApp()
    app.run()