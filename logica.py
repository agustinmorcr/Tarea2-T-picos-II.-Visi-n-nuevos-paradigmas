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
import cv2
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt
import pandas as pd
import heapq
import math

# ======================================================
# 1. Visualización de la Imagen 
# ======================================================
def cargar_imagen(ruta):
    """
    Carga una imagen en escala de grises y la convierte a binaria (blanco y negro).
    Usa un umbral de 127 para separar el objeto del fondo.
    """
    img = cv2.imread(ruta, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("No se pudo cargar la imagen")
    # Umbralizado: Pixeles > 127 pasan a 255 (blanco), los demás a 0 (negro)
    _, binaria = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    return binaria

# ======================================================
# 2. Código de Cadena 
# ======================================================
def ordenar_contorno(contorno):
    """
    Ordena los puntos de un contorno para asegurar que el recorrido comience desde el punto más superior-izquierdo y siga un orden lógico.
    """
    if contorno is None or contorno.size == 0:
        return None
    puntos = contorno.reshape(-1, 2)
    # Busca el punto inicial (mínimo en Y, luego mínimo en X)
    p0 = min(range(len(puntos)), key=lambda i: (puntos[i][1], puntos[i][0]))
    # Rota lista para iniciar en ese punto
    puntos = np.concatenate((puntos[p0:], puntos[:p0]), axis=0)
    puntos = puntos[::-1] # Inverte el sentido
    return puntos.reshape((-1, 1, 2))

def detectar_contorno(img):
    """
    Detecta el contorno externo más grande de la imagen binaria.
    """
    # Busca todos los contornos en la imagen binaria
    contornos, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not contornos:
        raise ValueError("No se detectaron contornos")
    # Selecciona el contorno con mayor área
    contorno = max(contornos, key=cv2.contourArea)
    return ordenar_contorno(contorno)

def encontrar_inicio(img):
    """
    Busca el primer pixel blanco (255) que toque el fondo para iniciar el seguimiento.
    """
    padded = np.pad(img, 1, 'constant', constant_values=0)
    for y in range(1, padded.shape[0] - 1):
        for x in range(1, padded.shape[1] - 1):
            if padded[y, x] == 255:
                # Verifica si es un borde (tiene un vecino negro)
                if padded[y - 1, x] == 0 or padded[y, x - 1] == 0:
                    return x, y
    return None

def cad_F4(img):
    """
    Genera el Código de Cadena de Freeman de 4 direcciones (N, S, E, O).
    Implementa un algoritmo de seguimiento de bordes.
    """
    # Direcciones de vecindad 4
    dirs = {
        0: (1, 0), 1: (0, 1),
        2: (-1, 0), 3: (0, -1)
    }
    padded = np.pad(img, 1, 'constant', constant_values=0)

    inicio = encontrar_inicio(img)
    if inicio is None:
        return []

    x0, y0 = inicio
    x, y = x0, y0
    dir = 0
    cadena = []

    for _ in range(10000): # Límite de seguridad para recorrido del contorno
        dx, dy = dirs[dir]
        x += dx
        y += dy
        cadena.append(dir)

        if (x, y) == (x0, y0): break # Se cerró la forma cuando regresa al punto inicial

        dir = (dir + 3) % 4  # Cambia dirección de búsqueda a la izquierda

        for _ in range(4): #Busca la siguiente direccion validada
            dx, dy = dirs[dir]
            # Determina pixel de prueba según la dirección actual
            if dir == 0: px, py = x, y
            elif dir == 1: px, py = x - 1, y
            elif dir == 2: px, py = x - 1, y - 1
            else: px, py = x, y - 1

            # Se termina antes el ciclo si el pixel no es parte del objeto binario
            if padded[py, px] == 255: break

            dir = (dir + 1) % 4 # Cambia dirección de búsqueda a la derecha

    return cadena

def cad_F8(img):
    """
    Genera el Código de Cadena de Freeman de 8 direcciones (incluye diagonales).
    Se basa en la diferencia de coordenadas entre puntos adyacentes del contorno.
    """
    contorno = detectar_contorno(img)
    if contorno is None: return []
    
    # Direcciones de vecindad 8
    dirs = {
        (0, 1): 0, (1, 1): 1, (1, 0): 2, (1, -1): 3,
        (0, -1): 4, (-1, -1): 5, (-1, 0): 6, (-1, 1): 7
    }

    cadena = []

    # Hace una comparacion del pixel actual con el siguiente
    for i in range(len(contorno)):
        p = contorno[i][0]
        q = contorno[(i + 1) % len(contorno)][0]

        dy = q[1] - p[1]
        dx = q[0] - p[0]

        if (dy, dx) in dirs:
            cadena.append(dirs[(dy, dx)])

    if cadena: # Ajuste de alineacion con el inicio
        cadena = cadena[-1:] + cadena[:-1]

    return cadena

def cad_AF8(F8):
    """
    Calcula el Código de Cadena Diferencial (AF8) a partir de un F8.
    Representa el cambio de dirección relativo.
    """
    # Tabla de transiciones
    F8_AF8 = {
        (0, 0): 0, (0, 1): 1, (0, 2): 2, (0, 3): 3, (0, 4): 4, (0, 5): 5, (0, 6): 6, (0, 7): 7,
        (1, 0): 7, (1, 1): 0, (1, 2): 1, (1, 3): 2, (1, 4): 3, (1, 5): 4, (1, 6): 5, (1, 7): 6,
        (2, 0): 6, (2, 1): 7, (2, 2): 0, (2, 3): 1, (2, 4): 2, (2, 5): 3, (2, 6): 4, (2, 7): 5,
        (3, 0): 5, (3, 1): 6, (3, 2): 7, (3, 3): 0, (3, 4): 1, (3, 5): 2, (3, 6): 3, (3, 7): 4,
        (4, 0): 4, (4, 1): 5, (4, 2): 6, (4, 3): 7, (4, 4): 0, (4, 5): 1, (4, 6): 2, (4, 7): 3,
        (5, 0): 3, (5, 1): 4, (5, 2): 5, (5, 3): 6, (5, 4): 7, (5, 5): 0, (5, 6): 1, (5, 7): 2,
        (6, 0): 2, (6, 1): 3, (6, 2): 4, (6, 3): 5, (6, 4): 6, (6, 5): 7, (6, 6): 0, (6, 7): 1,
        (7, 0): 1, (7, 1): 2, (7, 2): 3, (7, 3): 4, (7, 4): 5, (7, 5): 6, (7, 6): 7, (7, 7): 0
    }
    return [F8_AF8[(F8[i - 1], F8[i])] for i in range(len(F8))]

def cad_VCC(F4):
    """
    Vertex Chain Code (VCC). Basado en los cambios de dirección en una cadena F4.
    """
    # Tabla de transiciones
    F4_VCC = {
        (0, 0): 0, (0, 1): 1, (0, 3): 2,
        (1, 0): 2, (1, 1): 0, (1, 2): 1,
        (2, 1): 2, (2, 2): 0, (2, 3): 1,
        (3, 0): 1, (3, 2): 2, (3, 3): 0
    }
    return [F4_VCC.get((F4[i - 1], F4[i]), 0) for i in range(len(F4))]

def cad_3OT(F4):
    """
    Three Orthogonal (3OT). 
    Genera un código de cadena de solo 3 símbolos (0, 1, 2) basado en movimientos ortogonales.
    Invariante a la rotación mediante el uso de una dirección de referencia dinámica.
    """
    if len(F4) < 2: return []

    cadena = []
    dir_ref = F4[0]     # Dirección de referencia inicial para determinar el tipo de giro
    aux = F4[0]         # Almacena el movimiento anterior (soporte) para detectar cambios
    giro = False        # Flag que identifica si ya ocurrió la primera desviación del camino recto

    # Iteración sobre la cadena Freeman de 4 direcciones (F4)
    for i in range(1, len(F4)):
        x = F4[i]       # Movimiento actual en la secuencia F4

        if x == aux:
            # Si la dirección no cambia respecto al paso anterior, se codifica como '0'
            cadena.append(0) 
        else:
            # Si hay un cambio de dirección, evaluamos el tipo de quiebre
            if not giro:
                # El primer giro de la cadena siempre se marca con el símbolo '2'
                cadena.append(2)
                giro = True
            elif x == dir_ref:
                # Si el nuevo movimiento coincide con la referencia, es un giro de tipo '1'
                cadena.append(1)
                dir_ref = aux   # La referencia se actualiza al último soporte
            elif (x - dir_ref) % 4 == 2:
                # Si el movimiento es opuesto a la referencia (giro de 180° relativo), es tipo '2'
                cadena.append(2)
                dir_ref = aux
            else:
                # Cualquier otra transición ortogonal se codifica como tipo '1'
                cadena.append(1)
                dir_ref = aux

        aux = x         # Actualiza el soporte para la siguiente iteración

    # --- Lógica de Cierre Circular ---
    # Se compara el último movimiento con el primero para cerrar la forma del objeto
    x = F4[0]

    if x == aux:
        cadena.append(0)
    elif not giro:
        cadena.append(2)
    elif x == dir_ref:
        cadena.append(1)
    elif (x - dir_ref) % 4 == 2:
        cadena.append(2)
    else:
        cadena.append(1)

    return cadena

# ======================================================
# 3. Decodificación (Reconstrucción de Imagen)
# ======================================================
def decodificar_cadena(cadena, tipo):
    """ Función maestra para elegir el decodificador según el tipo de código """
    if tipo == "F4":
        return decodificar_F4_a_img(cadena)
    elif tipo == "F8":
        return decodificar_F8_a_img(cadena)
    elif tipo == "AF8":
        img = decodificar_F8_a_img(AF8_a_F8(cadena))
        return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE) # Se rota la imagen ya que por la convercion F8 a AF8 roto la imagen original
    elif tipo == "VCC":
        img = decodificar_F4_a_img(VCC_a_F4(cadena))
        return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE) # Se rota la imagen ya que por la convercion F4 a VCC roto la imagen original
    elif tipo == "3OT":
        return decodificar_F4_a_img(c3OT_a_F4(cadena))

def expancion_imagen(img, x, y):
    """ 
    Expande el lienzo dinámicamente si el dibujo del contorno se sale de los bordes actuales.
    """
    h, w = img.shape                     # Extrae la resolución espacial (alto y ancho) de la matriz original
    nueva_h, nueva_w = h, w              # Define las dimensiones del nuevo contenedor basadas en la imagen base
    offset_x, offset_y = 0, 0            # Inicialización de los factores de traslación

    if x < 0:                            # Si el punto excede el límite superior del lienzo
        offset_x = 10                    # Aplica margen de seguridad en el eje X
        nueva_h += 10                    # Incrementa resolución vertical
    elif x >= h:                         # Si el punto excede el límite inferior
        nueva_h += 10                    # Expandi altura del contenedor

    if y < 0:                            # Si el punto excede el límite lateral izquierdo
        offset_y = 10                    # Aplica margen de seguridad en el eje Y
        nueva_w += 10                    # Incrementa resolución horizontal
    elif y >= w:                         # Si el punto excede el límite lateral derecho
        nueva_w += 10                    # Expande ancho del contenedor

    nueva_img = np.zeros((nueva_h, nueva_w), dtype=np.uint8)   # Instanciar nueva matriz de ceros (lienzo)
    nueva_img[offset_x:offset_x+h, offset_y:offset_y+w] = img  # Mapear imagen original en la nueva superficie

    x += offset_x                        # Traslada coordenada X al nuevo sistema de referencia
    y += offset_y                        # Traslada coordenada Y al nuevo sistema de referencia

    return nueva_img, x, y               # Retorna estado actualizado del lienzo y puntero

def rellenar_contorno(img):
    """ Rellena el interior de un contorno cerrado usando drawContours con espesor -1 """
    # Busca todos los contornos en la imagen binaria
    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE) 
    # Seleccionar el contorno con mayor área
    cnt = max(contours, key=cv2.contourArea) 
    img_solida = np.zeros_like(img) # Se crea una lienzo negro del mismo tamaño que la imagen original
    cv2.drawContours(img_solida, [cnt], -1, 255, thickness=-1) # Rellena contorno
    return img_solida # Retorna imagen con relleno

def decodificar_F4_a_img(cadena, size=(200, 200)):
    """ Reconstruye la imagen binaria a partir de la cadena F4 """
    img = np.zeros(size, dtype=np.uint8)         # Crea un lienzo negro para empezar a dibujar
    x, y = size[0]//2, size[1]//2                # Define el punto inicial en la mitad de la imagen
    mov = {0:(0,1), 1:(1,0), 2:(0,-1), 3:(-1,0)} # Reglas de movimiento
    for d in cadena:                             # Lee cada direccion de la cadena
        dx, dy = mov[int(d)]                     # Extrae los movimientos segun la direccion
        x, y = x + dx, y + dy                    # Actualiza las coordenadas de movimiento
        if not (0 <= x < img.shape[0] and 0 <= y < img.shape[1]):   # Control de desbordamiento de límites
            img, x, y = expancion_imagen(img, x, y)                 # Redimensionar el lienzo dinámicamente
        img[x, y] = 255               # Dibuja el píxel como parte del contorno activo
    if cadena:
        return rellenar_contorno(img) # Retorna imagen reconstruida
    else:
        return img

def decodificar_F8_a_img(cadena, size=(200, 200)):
    """ Reconstruye la imagen binaria a partir de la cadena F8 """
    img = np.zeros(size, dtype=np.uint8)         # Crea un lienzo negro para empezar a dibujar
    x, y = size[0]//2, size[1]//2                # Define el punto inicial en la mitad de la imagen
    mov = {0:(0,1), 1:(1,1), 2:(1,0), 3:(1,-1), 
           4:(0,-1), 5:(-1,-1), 6:(-1,0), 7:(-1,1)} # Reglas de movimiento
    for d in cadena:                             # Lee cada direccion de la cadena
        dx, dy = mov[int(d)]                     # Extrae los movimientos segun la direccion
        x, y = x + dx, y + dy                    # Actualiza las coordenadas de movimiento
        if not (0 <= x < img.shape[0] and 0 <= y < img.shape[1]):   # Control de desbordamiento de límites
            img, x, y = expancion_imagen(img, x, y)                 # Redimensionar el lienzo dinámicamente
        img[x, y] = 255           # Dibuja el píxel como parte del contorno activo
    return rellenar_contorno(img) # Retorna imagen reconstruida

def AF8_a_F8(AF8):
    """
    Convercion de una cadena AF8 a F8.
    """
    # Ajuste de movimientos para que coincidan con tu decodificar_F8_a_img   
    mov = {0:(0,1), 1:(1,1), 2:(1,0), 3:(1,-1), 
           4:(0,-1), 5:(-1,-1), 6:(-1,0), 7:(-1,1)}
    for inicial in range(8):        # Probar las 8 orientaciones posibles de inicio
        F8, estado = [], inicial    # Crea lista F8 y se establece el estado inicial
        x, y = 0, 0                 # Inicializamos posiciones
        for simbolo in AF8:         # Recorremos la cadena AF8
            estado = (estado + int(simbolo)) % 8 # Convertir giros relativos en direcciones reales
            F8.append(estado)       # Guardamos direcciones reales en F8
        for dir in F8:              # Lee cada direccion de la cadena F8
            dx, dy = mov[dir]       # Extrae los movimientos segun la direccion
            x, y = x + dx, y + dy   # Actualiza las coordenadas de movimiento
        if x == 0 and y == 0: return F8 # Si la figura se cierra correctamente, la orientación es válida
    return F8   # Retorna el último intento si no hay cierre perfecto

def VCC_a_F4(VCC):
    """
    Convercion de una cadena VCC a F4.
    """
    # Tabla de transiciones
    tabla_VCC = {(0,1):1, (0,2):3, (0,3):0, 
                 (1,1):2, (1,2):0, (1,3):1, 
                 (2,1):3, (2,2):1, (2,3):2, 
                 (3,1):0, (3,2):2, (3,3):3}
    F4, dir = [], 0      # Crea lista F4 y se establece la direccion inicial
    for simbolo in VCC:  # Lee los símbolos del código de vértices (0, 1, 2)
        nuevo = tabla_VCC.get((dir, int(simbolo)), dir) # Recibe una nueva direccion o se mentiene en la direccion actual (sigue recto)
        F4.append(nuevo) # Guarda la direccion en la lista F4
        dir = nuevo      # Actualiza direccion
    return F4 # Retorna cadena F4

def c3OT_a_F4(c3OT):
    """
    Convercion de una cadena 3OT a F4.
    """
    mejor_F4 = None
    mejor_dist = float('inf')
    # Ajuste de movimientos para que coincidan con tu decodificar_F4_a_img
    mov = {0: (0, 1), 1: (1, 0), 2: (0, -1), 3: (-1, 0)}

    # Se evalúan las 4 orientaciones cardinales iniciales (Norte, Sur, Este, Oeste)
    for inicial in range(4):
        # El código 3OT es ambivalente (2) respecto al primer giro.
        # Se prueban ambos sentidos: horario (1) y antihorario (-1).
        for giro_inicial_detectado in [1, -1]:
            F4 = []                 # Crear lista F4
            dir_ref = inicial       # Dirección de referencia para el cálculo de giros
            aux = inicial           # Dirección auxiliar (último movimiento realizado)
            giro_inicial = False    # Flag para identificar el quiebre inicial del contorno
            x, y = 0, 0             # Coordenadas para verificar el cierre de la trayectoria
            viable = True           # Estado de validez de la combinación actual

            for simbolo in c3OT:
                simbolo = int(simbolo)
                if simbolo == 0: # El símbolo '0' indica que se mantiene la dirección previa (movimiento recto)
                    nueva_dir = aux
                else:
                    # Los símbolos '1' o '2' indican un cambio de dirección (giro ortogonal)
                    if not giro_inicial:
                        # Se aplica el sentido de giro (horario/antihorario) de la iteración actual
                        nueva_dir = (aux + giro_inicial_detectado) % 4
                        giro_inicial = True
                    else:
                        # Se busca cuál de los dos giros posibles genera el símbolo actual
                        detectada = False
                        for giro in [1, -1]:
                            prueba_dir = (aux + giro) % 4
                            # Lógica de generación de símbolo para validar
                            if prueba_dir == dir_ref:
                                s_gen = 1
                            elif (prueba_dir - dir_ref) % 4 == 2:
                                s_gen = 2
                            else:
                                s_gen = 1
                            # Si el giro probado coincide con el código, se valida la dirección
                            if s_gen == simbolo:
                                nueva_dir = prueba_dir
                                detectada = True
                                break
                        if not detectada:
                            viable = False  # Combinación inválida para esta secuencia
                            break
                    dir_ref = aux   # Al existir un giro, la dirección de referencia se actualiza al auxiliar anterior
                
                # Actualización de estado: nueva dirección, trayectoria y posición espacial
                aux = nueva_dir
                F4.append(nueva_dir)    # Guarda la direccion en la lista F4
                dx, dy = mov[nueva_dir] # Extrae los movimientos segun la direccion
                x, y = x + dx, y + dy   # Actualiza las coordenadas de movimiento

            # Evaluación de la solución encontrada
            if viable:
                # Se calcula la distancia Manhattan al origen para verificar el cierre
                dist = abs(x) + abs(y)
                if dist < mejor_dist:
                    mejor_dist = dist
                    mejor_F4 = F4
                    if dist == 0: break # Cierre perfecto encontrado

    return mejor_F4 if mejor_F4 else [] # Retorna la cadena reconstruida o vacia si no tiene cierre

# ======================================================
# 4. Histograma 
# ======================================================
def tabla(cadena):
    """
    Genera un análisis estadístico de la cadena de entrada.
    Calcula la frecuencia absoluta y la probabilidad de aparición de cada símbolo.
    """
    frecuencia = Counter(cadena)    # Contabiliza ocurrencias de cada símbolo del código
    N = len(cadena)                 # Longitud total de la secuencia para normalizar
    # Estructuración de datos en un DataFrame para facilitar su manipulación
    datos = pd.DataFrame({
        'Simbolo': list(frecuencia.keys()),
        'Frecuencia': list(frecuencia.values())
    })
    # Cálculo de la probabilidad (frecuencia relativa): P(s) = count(s) / N
    datos['Probabilidad'] = datos['Frecuencia'] / N
    # Ordena por símbolo para una visualización lógica en el histograma
    datos = datos.sort_values(by='Simbolo')
    return datos

def histograma(tabla, cadena):
    """
    Crea una representación visual de la distribución del código.
    Utiliza un gráfico de doble eje: barras para frecuencia y líneas para probabilidad.
    """
    # Gráfica de barras (Frecuencia)
    fig, axf = plt.subplots() # Configuración del lienzo y del eje principal (Frecuencia)
    # Representación de Frecuencia mediante barras azules
    axf.bar(tabla['Simbolo'], tabla['Frecuencia'], width=0.9, facecolor="#3f6deb", linewidth=0.1)
    # Ajuste dinámico de los límites y etiquetas del eje X e Y según los datos
    axf.set(xlim=(-0.5, np.max(cadena)+0.5), xticks=(np.arange(0, np.max(cadena)+1)), 
           ylim=(0, np.max(tabla['Frecuencia'])+max(0.5,np.max(tabla['Frecuencia']//10))), yticks=np.arange(0, np.max(tabla['Frecuencia'])+1, max(1,np.max(tabla['Frecuencia']//10))))
    axf.set_xlabel("Elemento del código")
    axf.set_ylabel("Frecuencia", color="#3f6deb")
    
    # Gráfica de líneas (Probabilidad)
    axp = axf.twinx() # Creación de un segundo eje Y (derecho) para la Probabilidad
    # Representación de Probabilidad mediante una línea roja con marcadores
    axp.plot(tabla['Simbolo'], tabla['Probabilidad'], color='#eb3f3f', marker='.', markersize=10, linewidth=2)
    # Configuración estética del eje de probabilidad
    axp.set_ylabel("Probabilidad", color='#eb3f3f', fontsize=12)
    axp.tick_params(axis='y', labelcolor='#eb3f3f')
    axp.set_ylim(0, max(tabla['Probabilidad']) * 1.2)
    axp.set_yticks(np.arange(0, 1.1, 0.1))
    
    axf.set_title("Distribución de frecuencias y probabilidad del código")
    
    # Retorna el objeto figura para ser embebido en la interfaz Tkinter
    return fig

# ======================================================
# 5. Entropía de Shannon 
# ======================================================
def entropia(tabla):
    """
    Calcula la Entropía de Shannon (H) del código de cadena.
    Representa el límite teórico de compresión sin pérdida.
    
    Fórmula: H(X) = -Σ P(xi) * log2(P(xi))
    """
    # Se multiplica la probabilidad de cada símbolo por su logaritmo en base 2.
    # El signo negativo al inicio es para que el resultado sea positivo (ya que log2 de una probabilidad < 1 es negativo).
    hx = -1 * (sum((tabla['Probabilidad']) * np.log2((tabla['Probabilidad']))))
    
    return hx  # Retorna el valor en bits/símbolo

# ======================================================
# 6. Compresión Huffman
# ======================================================
def huffman(cadena):
    """
    Calcula la longitud promedio de bits tras aplicar la codificación de Huffman.
    Determina qué tan eficiente es la compresión basada en la frecuencia de los símbolos.
    """
    N = len(cadena) 
    conteo = Counter(cadena)
    
    # Crea un "heap" (montículo) de prioridad con las frecuencias y símbolos.
    # Cada elemento es [frecuencia, [símbolo, código_binario]]
    heap = [[freq, [sim, ""]] for sim, freq in conteo.items()]
    heapq.heapify(heap)

    # Construcción del árbol de Huffman de abajo hacia arriba
    while len(heap) > 1:
        # Extraer los dos nodos con las frecuencias más bajas
        lo = heapq.heappop(heap)
        hi = heapq.heappop(heap)

        # Asigna '0' a la rama de menor frecuencia y '1' a la de mayor
        for pair in lo[1:]:
            pair[1] = '0' + pair[1]
        for pair in hi[1:]:
            pair[1] = '1' + pair[1]

        # Fusiona ambos nodos y reinsertarlos en el heap con la suma de sus frecuencias
        heapq.heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])

    # Extrae la estructura final del árbol con los códigos asignados
    resultado_huffman = heapq.heappop(heap)[1:]
    longitud_promedio = 0
    bits_totales = 0
    
    # Calcula el costo total en bits de la cadena comprimida
    for simbolo, bits in resultado_huffman:
        frecuencia = conteo[simbolo]
        bits_simbolo = frecuencia * len(bits) # Cantidad de veces que aparece * longitud de su código
        bits_totales += bits_simbolo
    
    # Longitud promedio: total de bits divididos entre el número de símbolos originales
    longitud_promedio = bits_totales / N
    
    return longitud_promedio

# ======================================================
# 7. Compresión Aritmética 
# ======================================================
def comprension_aritmetica(tabla):
    """
    Estima la longitud promedio de bits por símbolo usando codificación aritmética.
    Este método es más eficiente que Huffman al no estar limitado por bits enteros.
    """
    # Convertir el DataFrame de frecuencias en un diccionario para acceso rápido
    diccionario_probabilidades = tabla.set_index('Simbolo')['Probabilidad'].to_dict()

    longitud_promedio = 0.0

    for simbolo in diccionario_probabilidades:
        prob = diccionario_probabilidades[simbolo]
        
        # Solo se calculan símbolos con probabilidad mayor a cero para evitar errores logarítmicos
        if prob > 0:
            # Cambio de base para obtener el logaritmo en base 2: log2(P) = ln(P) / ln(2)
            log2_prob = math.log(prob) / math.log(2)
            
            # El aporte de cada símbolo a la longitud total es: P * -log2(P)
            # Esto es equivalente al cálculo de la Entropía de Shannon.
            calculo_simbolo = prob * (-log2_prob)
            
            # Acumulación de la longitud promedio bit a bit
            longitud_promedio = longitud_promedio + calculo_simbolo

    return longitud_promedio

# ======================================================
# 8. Propiedades Geométricas
# ======================================================
def propiedades(img, cadena_F4):
    """
    Calcula los descriptores geométricos del objeto detectado.
    Extrae medidas de tamaño, forma y topología (Euler).
    """    
    # 1. Perímetro: Basado en la conectividad-4 de Freeman.
    # En F4, cada símbolo representa un salto de 1 unidad de distancia.
    perimetro = len(cadena_F4)
    
    # 2. Área: Cálculo basado en el conteo de píxeles activos (blancos) en la máscara binaria.
    area = np.sum(img == 255)

    # 3. Perímetro de Contacto (Pc): Representa las fronteras internas de los píxeles.
    # Se calcula con la relación entre el área total y el perímetro externo.
    perimetro_contacto = (4 * area - perimetro) // 2

    # 4. Característica de Euler (E): Descriptor topológico (E = Cuerpos - Agujeros).
    # Se analiza la jerarquía de los contornos para identificar huecos internos.
    contours, hierarchy = cv2.findContours(img, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    num_objetos = 0
    num_agujeros = 0
    
    if hierarchy is not None:
        for i in range(len(contours)):
            # Un valor de -1 en el cuarto elemento indica que el contorno no tiene 'padre'.
            if hierarchy[0][i][3] == -1: 
                num_objetos += 1
            else: 
                num_agujeros += 1
    
    euler = num_objetos - num_agujeros
    
    # 5. Compacidad Discreta: Mide qué tan cercana es la forma a un cuadrado/círculo digital.
    # Es un valor normalizado que ayuda a identificar la "redondez" del objeto.
    if area > 1: 
        numerador = area - (perimetro / 4)
        denominador = area - np.sqrt(area)
        compacidad = numerador / denominador
    else:
        compacidad = 0

    return perimetro, area, perimetro_contacto, euler, compacidad