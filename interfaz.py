# ======================================================
# LIBRERIAS
# ======================================================
import os, sys
import cv2
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import logica

def ruta_recurso(relative_path):
    """ Obtiene la ruta absoluta para recursos (imágenes, iconos, etc) """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

# ======================================================
# Interfaz
# ======================================================
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Análisis")
        self.root.geometry("900x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.iconbitmap(ruta_recurso("icono.ico")) 
        self.root.configure(bg="#1e1e1e")

        self.nombre_base = None
        self.img = None
        self.contorno = None
        self.cadena = None
        self.tipo = None

        # Frames
        left = tk.Frame(root, bg="#2c2c2c", width=300)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        right = tk.Frame(root, bg="#1e1e1e")
        right.pack(side="right", expand=True, fill="both")

        # FRAME SUPERIOR (TABS)
        top_frame = tk.Frame(right, bg="#1e1e1e")
        top_frame.pack(side="top", expand=True, fill="both")

        # FRAME INFERIOR (CONSOLA)
        bottom_frame = tk.Frame(right, bg="#2c2c2c", height=150)
        bottom_frame.pack(side="bottom", fill="x")
        bottom_frame.pack_propagate(False) 
        
        # Consola de datos
        tk.Label(left, text="Datos", bg="#2c2c2c", fg="white", font=("Arial", 12, "bold")).pack(anchor="center", padx=10, pady=(10,0))
        self.text = tk.Text(left, bg="#000000", fg="white", relief="flat")
        self.text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Estilo de las ventanas
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

        # Ventanas
        self.tabs = ttk.Notebook(top_frame)
        self.tabs.pack(expand=True, fill="both")

        # Tabs
        self.tab1 = tk.Frame(self.tabs, bg="#1e1e1e")
        self.tabs.add(self.tab1, text="Imagen Original")
        
        self.tab2 = tk.Frame(self.tabs, bg="#1e1e1e")
        self.tabs.add(self.tab2, text="Imagen Decodificada")

        self.tab3 = tk.Frame(self.tabs, bg="#1e1e1e")
        self.tabs.add(self.tab3, text="Imagen Contorno")

        self.tab4 = tk.Frame(self.tabs, bg="#1e1e1e")
        self.tabs.add(self.tab4, text="Histograma")
        self.tab4.pack_propagate(False)

        # Área de imagen original
        self.original = tk.Label(self.tab1, bg="#1e1e1e")
        self.original.pack(expand=True)

        self.decodificar =  tk.Label(self.tab2, bg="#1e1e1e")
        self.decodificar.pack(expand=True)

        self.borde = tk.Label(self.tab3, bg="#1e1e1e")
        self.borde.pack(expand=True)

        # Consola de cadena
        tk.Label(bottom_frame, text="Cadena Generada", bg="#2c2c2c", fg="white", font=("Arial", 12, "bold")).pack(anchor="center", padx=10, pady=(10,0))
        self.text_cadena = tk.Text(bottom_frame, height=100, bg="#000000", fg="white")
        self.text_cadena.pack(fill="both", expand=True, padx=10, pady=10, )

        # Menú superior
        menubar = tk.Menu(root)

        archivo_menu = tk.Menu(menubar, tearoff=0)
        archivo_menu.add_command(label="Cargar Imagen", command=self.cargar)
        archivo_menu.add_separator()
        archivo_menu.add_command(label="Salir", command=root.quit)
        menubar.add_cascade(label="Archivo", menu=archivo_menu)

        proceso_menu = tk.Menu(menubar, tearoff=0)
        proceso_menu.add_command(label="Detectar Contorno", command=self.contornos)
        proceso_menu.add_separator()
        sub = tk.Menu(proceso_menu, tearoff=0)
        sub.add_command(label="F4", command=lambda: self.generar_cadena("F4"))
        sub.add_command(label="F8", command=lambda: self.generar_cadena("F8"))
        sub.add_command(label="AF8", command=lambda: self.generar_cadena("AF8"))
        sub.add_command(label="VCC", command=lambda: self.generar_cadena("VCC"))
        sub.add_command(label="3OT", command=lambda: self.generar_cadena("3OT"))
        proceso_menu.add_cascade(label="Generar Cadena", menu=sub)
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
    
    def limpiar(self):
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
        self.text.insert("end", "——————————————————————————————————\n")
        self.text.insert("end", msg+"\n")
        self.text.see("end")

    # ======================================================
    # 1. Visualización de la Imagen
    # ======================================================
    def cargar(self):
        ruta = filedialog.askopenfilename()
        if not ruta: return
        self.limpiar()
        self.nombre_base = os.path.splitext(os.path.basename(ruta))[0]
        self.img = logica.cargar_imagen(ruta)
        self.mostrar_img(self.img, 1)
        self.tabs.select(self.tab1)
        self.log("Imagen cargada")

    def mostrar_img(self, img, band):
        img = cv2.resize(img, (400,400))
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
        if self.img is None:
            messagebox.showerror("Error", "Carga una imagen primero")
            return
        
        self.contorno = logica.detectar_contorno(self.img)
        img_c = cv2.cvtColor(self.img, cv2.COLOR_GRAY2BGR)
        cv2.drawContours(img_c, [self.contorno], -1, (255,0,0), 2)
        self.mostrar_img(img_c, 3)
        self.tabs.select(self.tab3)
        self.log("Contorno detectado")

    def generar_cadena(self, tipo):
        if self.img is None:
            messagebox.showerror("Error", "Carga una imagen primero")
            return
        
        self.tipo = tipo

        funciones = {
            "F4": lambda: logica.cad_F4(self.img),
            "F8": lambda: logica.cad_F8(self.img),
            "AF8": lambda: logica.cad_AF8(logica.cad_F8(self.img)),
            "VCC": lambda: logica.cad_VCC(logica.cad_F4(self.img)),
            "3OT": lambda: logica.cad_3OT(logica.cad_F4(self.img))
        }

        self.cadena = funciones[tipo]()
        self.mostrar_cadena(f"{tipo}: {self.cadena}")
        self.log(f"Longitud de cadena {tipo} \n ► {len(self.cadena)}")

    def mostrar_cadena(self, cadena):
        self.text.delete("1.0", "end")
        self.text_cadena.delete("1.0", "end")
        self.text_cadena.insert("end", str(cadena))

    def decodificar_cadena(self, tipo):
        if self.img is None:
            messagebox.showerror("Error", "Carga una imagen primero")
            return
        elif self.cadena is None:
            messagebox.showerror("Error", "Genera la cadena primero")
            return
        elif self.tipo != tipo:
            messagebox.showerror("Error", "Seleccione el mismo tipo de la cadena generada")
            return

        img_dec = logica.decodificar_cadena(self.cadena, tipo)
        self.mostrar_img(img_dec, 2) # Mostrar en Tab 2
        self.tabs.select(self.tab2)
        self.log(f"Decodificación {tipo} completada")
        
    def guardar_cadenas(self):
        if self.img is None:
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

    def ver_histograma(self):
        if self.img is None:
            messagebox.showerror("Error", "Carga una imagen primero")
            return
        elif self.cadena is None:
            messagebox.showerror("Error", "Genera la cadena primero")
            return
        
        self.log(f"{logica.tabla(self.cadena).to_string(index=False)}")
        fig = logica.histograma(logica.tabla(self.cadena), self.cadena)

        for widget in self.tab4.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(fig, master=self.tab4)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill="both")

        self.tabs.select(self.tab4)

    def ver_entropia(self):
        if self.img is None:
            messagebox.showerror("Error", "Carga una imagen primero")
            return
        elif self.cadena is None:
            messagebox.showerror("Error", "Genera la cadena primero")
            return
        
        E = logica.entropia(logica.tabla(self.cadena))
        self.log(f"Entropía de Shannon \n ► {E}")

    def ver_huffman(self):
        if self.img is None:
            messagebox.showerror("Error", "Carga una imagen primero")
            return
        elif self.cadena is None:
            messagebox.showerror("Error", "Genera la cadena primero")
            return
        
        H = logica.huffman(self.cadena)
        self.log(f"Compresión Huffman \nLongitud Promedio \n ► {H}")

    def ver_aritmetica(self):
        if self.img is None:
            messagebox.showerror("Error", "Carga una imagen primero")
            return
        elif self.cadena is None:
            messagebox.showerror("Error", "Genera la cadena primero")
            return
        
        A = logica.comprension_aritmetica(logica.tabla(self.cadena))
        self.log(f"Compresión Aritmética \nLongitud Promedio \n ► {A}")

    def ver_propiedades(self):
        if self.img is None:
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
# Main
# ======================================================

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()

