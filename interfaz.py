# ========================================================================= #
# VISION Y NUEVOS PARADIGMAS TECNOLOGICOS - 2do Semestre                    #
# Universidad Autonoma de Aguascalientes                                    #
# Maestría en Ciencias con opciones a la Computación, Matemáticas Aplicadas #
# Profesor: Dr. Hermilo Sánchez Cruz                                        #
# Integrantes:                                                              #
# 207614 ~ Agustin Moreno Cruz                                              #
# 269606 ~ Angela María Gallegos Martínez                                   #
# Fecha: 01/04/2026                                                         #
# ========================================================================= #

# ======================================================
# LIBRERIAS
# ======================================================
import os, sys
import cv2
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import logica  # Archivo externo donde reside la lógica de procesamiento

def ruta_recurso(relative_path):
    """ 
    Obtiene la ruta absoluta para recursos (imágenes, iconos, etc.).
    Es vital para que el programa encuentre el icono si se convierte en un .exe 
    """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

# ======================================================
# CLASE PRINCIPAL DE LA INTERFAZ
# ======================================================
class App:
    def __init__(self, root):
        # Configuración inicial de la ventana principal
        self.root = root
        self.root.title("Sistema de Análisis")
        self.root.geometry("900x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing) # Manejo de cierre limpio
        self.root.iconbitmap(ruta_recurso("icono.ico")) 
        self.root.configure(bg="#1e1e1e") # Color de fondo oscuro (Dark Mode)

        # Variables de control de datos
        self.nombre_base = None # Nombre del archivo cargado
        self.img = None         # Imagen en memoria (OpenCV)
        self.contorno = None    # Datos de contornos detectados
        self.cadena = None      # Cadena de Freeman (u otros códigos) generada
        self.tipo = None        # Tipo de codificación actual (F4, F8, etc.)

        # --- ESTRUCTURA DE DISEÑO (LAYOUT) ---
        # Panel Izquierdo: Consola lateral para mostrar logs y datos
        left = tk.Frame(root, bg="#2c2c2c", width=300)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)
        # Panel Derecho: Contenedor principal para visualización
        right = tk.Frame(root, bg="#1e1e1e")
        right.pack(side="right", expand=True, fill="both")

        # Frame superior dentro del panel derecho para las pestañas (Tabs)
        top_frame = tk.Frame(right, bg="#1e1e1e")
        top_frame.pack(side="top", expand=True, fill="both")

        # Frame inferior dentro del panel derecho para mostrar la cadena generada
        bottom_frame = tk.Frame(right, bg="#2c2c2c", height=150)
        bottom_frame.pack(side="bottom", fill="x")
        bottom_frame.pack_propagate(False) 
        
        # Elementos de la consola lateral (Datos)
        tk.Label(left, text="Datos", bg="#2c2c2c", fg="white", font=("Arial", 12, "bold")).pack(anchor="center", padx=10, pady=(10,0))
        self.text = tk.Text(left, bg="#000000", fg="white", relief="flat")
        self.text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # --- ESTILOS DE COMPONENTES TTK ---
        style = ttk.Style()
        style.theme_use("clam")  # importante para permitir cambios
        # Fondo general del Notebook
        style.configure("TNotebook", background="#1e1e1e", borderwidth=0)
        # Pestañas normales
        style.configure("TNotebook.Tab",
                        background="#2c2c2c",
                        foreground="white",
                        padding=[10, 5],
                        font=("Arial", 10, "bold"))
        # Pestaña seleccionada
        style.map("TNotebook.Tab",
                background=[("selected", "#618BC2"), ("active", "#505050")],  
                foreground=[("selected", "white")])

        # --- CONFIGURACIÓN DE PESTAÑAS (NOTEBOOK) ---
        self.tabs = ttk.Notebook(top_frame)
        self.tabs.pack(expand=True, fill="both")

        # Definición de cada Tab
        self.tab1 = tk.Frame(self.tabs, bg="#1e1e1e")
        self.tabs.add(self.tab1, text="Imagen Original")
        
        self.tab2 = tk.Frame(self.tabs, bg="#1e1e1e")
        self.tabs.add(self.tab2, text="Imagen Decodificada")

        self.tab3 = tk.Frame(self.tabs, bg="#1e1e1e")
        self.tabs.add(self.tab3, text="Imagen Contorno")

        self.tab4 = tk.Frame(self.tabs, bg="#1e1e1e")
        self.tabs.add(self.tab4, text="Histograma")
        self.tab4.pack_propagate(False)

        # Etiquetas (Labels) donde se renderizarán las imágenes procesadas
        self.original = tk.Label(self.tab1, bg="#1e1e1e")
        self.original.pack(expand=True)

        self.decodificar =  tk.Label(self.tab2, bg="#1e1e1e")
        self.decodificar.pack(expand=True)

        self.borde = tk.Label(self.tab3, bg="#1e1e1e")
        self.borde.pack(expand=True)

        # Consola inferior para mostrar la cadena de texto masiva
        tk.Label(bottom_frame, text="Cadena Generada", bg="#2c2c2c", fg="white", font=("Arial", 12, "bold")).pack(anchor="center", padx=10, pady=(10,0))
        self.text_cadena = tk.Text(bottom_frame, height=100, bg="#000000", fg="white")
        self.text_cadena.pack(fill="both", expand=True, padx=10, pady=10, )

        # --- MENÚ SUPERIOR ---
        menubar = tk.Menu(root)
        
        # Menú Archivo
        archivo_menu = tk.Menu(menubar, tearoff=0)
        archivo_menu.add_command(label="Cargar Imagen", command=self.cargar)
        archivo_menu.add_separator()
        archivo_menu.add_command(label="Salir", command=root.quit)
        menubar.add_cascade(label="Archivo", menu=archivo_menu)

        # Menú Procesos (Contornos y Cadenas)
        proceso_menu = tk.Menu(menubar, tearoff=0)
        proceso_menu.add_command(label="Detectar Contorno", command=self.contornos)
        proceso_menu.add_separator()
        # Submenú para generar diferentes tipos de cadenas
        sub = tk.Menu(proceso_menu, tearoff=0)
        sub.add_command(label="F4", command=lambda: self.generar_cadena("F4"))
        sub.add_command(label="F8", command=lambda: self.generar_cadena("F8"))
        sub.add_command(label="AF8", command=lambda: self.generar_cadena("AF8"))
        sub.add_command(label="VCC", command=lambda: self.generar_cadena("VCC"))
        sub.add_command(label="3OT", command=lambda: self.generar_cadena("3OT"))
        proceso_menu.add_cascade(label="Generar Cadena", menu=sub)
        # Submenú para decodificar cadenas existentes
        sub2 = tk.Menu(proceso_menu, tearoff=0)
        sub2.add_command(label="F4", command=lambda: self.decodificar_cadena("F4"))
        sub2.add_command(label="F8", command=lambda: self.decodificar_cadena("F8"))
        sub2.add_command(label="AF8", command=lambda: self.decodificar_cadena("AF8"))
        sub2.add_command(label="VCC", command=lambda: self.decodificar_cadena("VCC"))
        sub2.add_command(label="3OT", command=lambda: self.decodificar_cadena("3OT"))
        proceso_menu.add_cascade(label="Decodificar Cadena", menu=sub2)
        proceso_menu.add_separator()
        proceso_menu.add_command(label="Guardar Cadenas", command=self.guardar_cadenas)
        menubar.add_cascade(label="Procesos", menu=proceso_menu)
        
        # Menú Análisis (Matemáticas y Propiedades)
        analisis_menu = tk.Menu(menubar, tearoff=0)
        analisis_menu.add_command(label="Histograma", command=self.ver_histograma)
        analisis_menu.add_separator()
        analisis_menu.add_command(label="Entropía de Shannon", command=self.ver_entropia)
        analisis_menu.add_command(label="Compresión Huffman", command=self.ver_huffman)
        analisis_menu.add_command(label="Compresión Aritmética", command=self.ver_aritmetica)
        analisis_menu.add_separator()
        analisis_menu.add_command(label="Propiedades", command=self.ver_propiedades)
        menubar.add_cascade(label="Análisis", menu=analisis_menu)

        root.config(menu=menubar)

    # --- MÉTODOS DE SOPORTE ---    
    def limpiar(self):
        """ Reinicia la interfaz y las variables para procesar una nueva imagen """
        self.original.config(image="")
        self.decodificar.config(image="")
        self.borde.config(image="")
        self.original.config(image="")
        for widget in self.tab4.winfo_children():
            widget.destroy()
        self.text.delete("1.0", "end")
        self.text_cadena.delete("1.0", "end")
        self.nombre_base = None
        self.img = None
        self.contorno = None
        self.cadena = None
        self.tipo = None

    def log(self, msg):
        """ Escribe mensajes en la consola lateral izquierda """
        self.text.insert("end", "——————————————————————————————————\n")
        self.text.insert("end", msg+"\n")
        self.text.see("end")

    # ======================================================
    # MÉTODOS DE CARGA Y VISUALIZACIÓN
    # ======================================================
    def cargar(self):
        """ Abre el explorador de archivos para cargar una imagen """
        ruta = filedialog.askopenfilename()
        if not ruta: return
        self.limpiar()
        self.nombre_base = os.path.splitext(os.path.basename(ruta))[0]
        self.img = logica.cargar_imagen(ruta) # Llama a la lógica para leer la imagen
        self.mostrar_img(self.img, 1) # Muestra en el tab de original
        self.tabs.select(self.tab1)
        self.log("Imagen cargada")

    def mostrar_img(self, img, band):
        """ Convierte imágenes de OpenCV (Array) a formato compatible con Tkinter """
        img = cv2.resize(img, (400,400))    # Redimensionar para que quepa en la interfaz
        img = Image.fromarray(img)
        img = ImageTk.PhotoImage(img)
        if(band == 1):
            self.original.configure(image=img)
            self.original.image = img
        elif(band == 2):
            self.decodificar.configure(image=img)
            self.decodificar.image = img    
        else:
            self.borde.configure(image=img)
            self.borde.image = img

    def contornos(self):
        """ Detecta y dibuja los contornos de la imagen cargada """
        if self.img is None:    # Validaciones
            messagebox.showerror("Error", "Carga una imagen primero")
            return
        
        self.contorno = logica.detectar_contorno(self.img)
        img_c = cv2.cvtColor(self.img, cv2.COLOR_GRAY2BGR) # Convertir a color para dibujar contorno
        cv2.drawContours(img_c, [self.contorno], -1, (255,0,0), 2)
        self.mostrar_img(img_c, 3)  # Mostrar en tab 3 de contorno
        self.tabs.select(self.tab3)
        self.log("Contorno detectado")

    def generar_cadena(self, tipo):
        """ Ejecuta los algoritmos de codificación basados en el tipo seleccionado """
        if self.img is None:
            messagebox.showerror("Error", "Carga una imagen primero")
            return
        
        self.tipo = tipo

        # Diccionario de funciones para evitar múltiples If/Else
        funciones = {
            "F4": lambda: logica.cad_F4(self.img),
            "F8": lambda: logica.cad_F8(self.img),
            "AF8": lambda: logica.cad_AF8(logica.cad_F8(self.img)),
            "VCC": lambda: logica.cad_VCC(logica.cad_F4(self.img)),
            "3OT": lambda: logica.cad_3OT(logica.cad_F4(self.img))
        }

        self.cadena = funciones[tipo]() # Ejecuta la función correspondiente
        self.mostrar_cadena(f"{tipo}: {self.cadena}")
        self.log(f"Longitud de cadena {tipo} \n ► {len(self.cadena)}")

    def mostrar_cadena(self, cadena):
        """ Limpia e inserta la cadena de texto en la consola inferior """
        self.text.delete("1.0", "end")
        self.text_cadena.delete("1.0", "end")
        self.text_cadena.insert("end", str(cadena))

    def decodificar_cadena(self, tipo):
        """ Reconstruye la imagen a partir de la cadena generada """
        if self.img is None:    # Validaciones
            messagebox.showerror("Error", "Carga una imagen primero")
            return
        elif self.cadena is None:
            messagebox.showerror("Error", "Genera la cadena primero")
            return
        elif self.tipo != tipo:
            messagebox.showerror("Error", "Seleccione el mismo tipo de la cadena generada")
            return

        img_dec = logica.decodificar_cadena(self.cadena, tipo)
        self.mostrar_img(img_dec, 2) # Mostrar en Tab 2 de Imagen Decodificada
        self.tabs.select(self.tab2)
        self.log(f"Decodificación {tipo} completada")
        
    def guardar_cadenas(self):
        """ Exporta todas las codificaciones posibles a un archivo .txt """
        if self.img is None:    # Validaciones
            messagebox.showerror("Error", "Carga una imagen primero")
            return
        
        directorio = filedialog.askdirectory(title="Selecciona la carpeta para guardar tus archivos")
        
        if directorio:
            nombre_archivo = f"Cadenas_{self.nombre_base}.txt"
            ruta_completa = f"{directorio}/{nombre_archivo}"
            try:
                with open(ruta_completa, "w", encoding="utf-8") as f:
                    f.write(f"REPORTE DE CADENAS - IMAGEN: {self.nombre_base}\n")
                    f.write("="*50 + "\n\n")
                    # Escribe cada tipo de código llamando a la lógica
                    f.write(f"------ CODIGO F4 ------\n")
                    f.write(f"{logica.cad_F4(self.img)}\n\n")
                    f.write(f"------ CODIGO F8 ------\n")
                    f.write(f"{logica.cad_F8(self.img)}\n\n")
                    f.write(f"------ CODIGO AF8 ------\n")
                    f.write(f"{logica.cad_AF8(logica.cad_F8(self.img))}\n\n")
                    f.write(f"------ CODIGO VCC ------\n")
                    f.write(f"{logica.cad_VCC(logica.cad_F4(self.img))}\n\n")
                    f.write(f"------ CODIGO 3OT ------\n")
                    f.write(f"{logica.cad_3OT(logica.cad_F4(self.img))}\n\n")
            
                self.log(f"Archivos guardados en:\n ► {directorio}")
                messagebox.showinfo("Éxito", f"Se creó el archivo {nombre_archivo}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo escribir el archivo: {e}")
        else:
            self.log(f"Operación cancelada por el usuario")

    # ======================================================
    # MÉTODOS DE ANÁLISIS
    # ======================================================
    def ver_histograma(self):
        """ Genera y embebe un gráfico de Matplotlib en el Tab 4 """
        if self.img is None:    # Validaciones
            messagebox.showerror("Error", "Carga una imagen primero")
            return
        elif self.cadena is None:
            messagebox.showerror("Error", "Genera la cadena primero")
            return

        # Obtiene datos de la tabla de frecuencias
        self.log(f"{logica.tabla(self.cadena).to_string(index=False)}")
        fig = logica.histograma(logica.tabla(self.cadena), self.cadena)

        # Limpiar el Tab antes de dibujar
        for widget in self.tab4.winfo_children():
            widget.destroy()

        # Conectar Matplotlib con Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.tab4)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill="both")

        self.tabs.select(self.tab4)

    def ver_entropia(self):
        """ Calcula y muestra la entropía de Shannon de la cadena """
        if self.img is None:    # Validaciones
            messagebox.showerror("Error", "Carga una imagen primero")
            return
        elif self.cadena is None:
            messagebox.showerror("Error", "Genera la cadena primero")
            return
        
        E = logica.entropia(logica.tabla(self.cadena))
        self.log(f"Entropía de Shannon \n ► {E}")

    def ver_huffman(self):
        """ Calcula la longitud promedio tras compresión Huffman """
        if self.img is None:    # Validaciones
            messagebox.showerror("Error", "Carga una imagen primero")
            return
        elif self.cadena is None:
            messagebox.showerror("Error", "Genera la cadena primero")
            return
        
        H = logica.huffman(self.cadena)
        self.log(f"Compresión Huffman \nLongitud Promedio \n ► {H}")

    def ver_aritmetica(self):
        """ Calcula la longitud promedio tras compresión aritmética """
        if self.img is None:    # Validaciones
            messagebox.showerror("Error", "Carga una imagen primero")
            return
        elif self.cadena is None:
            messagebox.showerror("Error", "Genera la cadena primero")
            return
        
        A = logica.comprension_aritmetica(logica.tabla(self.cadena))
        self.log(f"Compresión Aritmética \nLongitud Promedio \n ► {A}")

    def ver_propiedades(self):
        """ Muestra propiedades geométricas de la forma detectada """
        if self.img is None:    # Validaciones
            messagebox.showerror("Error", "Carga una imagen primero")
            return
        elif self.cadena is None:
            messagebox.showerror("Error", "Genera la cadena primero")
            return
        
        self.tabs.select(self.tab1)
        p,a,pc,e,c = logica.propiedades(self.img, logica.cad_F4(self.img))
        self.log(f"Perímetro: \n ► {p} \nÁrea: \n ► {a} \nPerímetro de contacto: \n ► {pc} \nEuler: \n ► {e}\nCompacidad discreta: \n ► {c}")

    def on_closing(self):
        """Cierra el programa de forma limpia para evitar bloqueos de archivos."""
        import matplotlib.pyplot as plt
        plt.close('all') # Cierra gráficas de fondo
        self.root.quit() # Detiene el mainloop
        self.root.destroy() # Destruye la ventana
        os._exit(0) # Fuerza la salida del proceso de Python

# ======================================================
# EJECUCIÓN DEL PROGRAMA
# ======================================================

if __name__ == "__main__":
    root = tk.Tk()      # Crear la ventana base
    App(root)           # Iniciar la clase App
    root.mainloop()     # Mantener la ventana abierta