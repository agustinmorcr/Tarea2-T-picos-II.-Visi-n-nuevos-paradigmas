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
    img = cv2.imread(ruta, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("No se pudo cargar la imagen")
    _, binaria = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    return binaria

# ======================================================
# 2. Código de Cadena 
# ======================================================
def ordenar_contorno(contorno):
    if contorno is None or contorno.size == 0:
        return None
    puntos = contorno.reshape(-1, 2)
    p0 = min(range(len(puntos)), key=lambda i: (puntos[i][1], puntos[i][0]))
    puntos = np.concatenate((puntos[p0:], puntos[:p0]), axis=0)
    puntos = puntos[::-1]
    return puntos.reshape((-1, 1, 2))

def detectar_contorno(img):
    contornos, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not contornos:
        raise ValueError("No se detectaron contornos")
    contorno = max(contornos, key=cv2.contourArea)
    return ordenar_contorno(contorno)

def encontrar_inicio(img):
    padded = np.pad(img, 1, 'constant', constant_values=0)
    for y in range(1, padded.shape[0] - 1):
        for x in range(1, padded.shape[1] - 1):
            if padded[y, x] == 255:
                if padded[y - 1, x] == 0 or padded[y, x - 1] == 0:
                    return x, y
    return None

def cad_F4(img_binaria):
    dirs = {
        0: (1, 0), 1: (0, 1),
        2: (-1, 0), 3: (0, -1)
    }
    padded = np.pad(img_binaria, 1, 'constant', constant_values=0)

    inicio = encontrar_inicio(img_binaria)
    if inicio is None:
        return []

    x0, y0 = inicio
    x, y = x0, y0
    dir = 0
    cadena = []

    for _ in range(10000):
        dx, dy = dirs[dir]
        x += dx
        y += dy
        cadena.append(dir)

        if (x, y) == (x0, y0):
            break

        dir = (dir + 3) % 4

        for _ in range(4):
            dx, dy = dirs[dir]

            if dir == 0:
                px, py = x, y
            elif dir == 1:
                px, py = x - 1, y
            elif dir == 2:
                px, py = x - 1, y - 1
            else:
                px, py = x, y - 1

            if padded[py, px] == 255:
                break

            dir = (dir + 1) % 4

    return cadena

def cad_F8(img_binaria):
    contorno = detectar_contorno(img_binaria)
    if contorno is None:
        return []
    dirs = {
        (0, 1): 0, (1, 1): 1, (1, 0): 2, (1, -1): 3,
        (0, -1): 4, (-1, -1): 5, (-1, 0): 6, (-1, 1): 7
    }

    cadena = []

    for i in range(len(contorno)):
        p = contorno[i][0]
        q = contorno[(i + 1) % len(contorno)][0]

        dy = q[1] - p[1]
        dx = q[0] - p[0]

        if (dy, dx) in dirs:
            cadena.append(dirs[(dy, dx)])

    if cadena:
        cadena = cadena[-1:] + cadena[:-1]

    return cadena

def cad_AF8(f8):
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
    return [F8_AF8[(f8[i - 1], f8[i])] for i in range(len(f8))]

def cad_VCC(f4):
    F4_VCC = {
        (0, 0): 0, (0, 1): 1, (0, 3): 2,
        (1, 0): 2, (1, 1): 0, (1, 2): 1,
        (2, 1): 2, (2, 2): 0, (2, 3): 1,
        (3, 0): 1, (3, 2): 2, (3, 3): 0
    }
    return [F4_VCC.get((f4[i - 1], f4[i]), 0) for i in range(len(f4))]

def cad_3OT(f4):
    if len(f4) < 2:
        return []

    cadena = []
    ref = f4[0]
    sup = f4[0]
    cambio = False

    for i in range(1, len(f4)):
        x = f4[i]

        if x == sup:
            cadena.append(0)
        else:
            if not cambio:
                cadena.append(2)
                cambio = True
            elif x == ref:
                cadena.append(1)
                ref = sup
            elif (x - ref) % 4 == 2:
                cadena.append(2)
                ref = sup
            else:
                cadena.append(1)
                ref = sup

        sup = x

    # cierre circular
    x = f4[0]

    if x == sup:
        cadena.append(0)
    elif not cambio:
        cadena.append(2)
    elif x == ref:
        cadena.append(1)
    elif (x - ref) % 4 == 2:
        cadena.append(2)
    else:
        cadena.append(1)

    return cadena

# ======================================================
# 3. Decodificación
# ======================================================
def decodificar_cadena(cadena, tipo):
    if tipo == "F4":
        return decodificar_f4_a_img(cadena)
    elif tipo == "F8":
        return decodificar_f8_a_img(cadena)
    elif tipo == "AF8":
        img = decodificar_f8_a_img(af8_a_f8(cadena))
        return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    elif tipo == "VCC":
        img = decodificar_f4_a_img(vcc_a_f4(cadena))
        return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    elif tipo == "3OT":
        return decodificar_f4_a_img(c3ot_a_f4(cadena))
       
    return np.zeros((100,100), dtype=np.uint8)

def expancion_imagen(img, x, y):
    h, w = img.shape
    new_h, new_w = h, w
    offset_x, offset_y = 0, 0

    if x < 0:
        offset_x = 20
        new_h += 20
    elif x >= h:
        new_h += 20

    if y < 0:
        offset_y = 20
        new_w += 20
    elif y >= w:
        new_w += 20

    new_img = np.zeros((new_h, new_w), dtype=np.uint8)
    new_img[offset_x:offset_x+h, offset_y:offset_y+w] = img

    return new_img, x + offset_x, y + offset_y

def relleno_imagen(img_binaria):
    contours, _ = cv2.findContours(img_binaria, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cnt = max(contours, key=cv2.contourArea)
    img_rellena = np.zeros_like(img_binaria)
    cv2.drawContours(img_rellena, [cnt], -1, 255, thickness=-1)
    return img_rellena

def decodificar_f4_a_img(cadena, size=(200, 200)):
    img = np.zeros(size, dtype=np.uint8)
    x, y = size[0]//2, size[1]//2
    moves = {0:(0,1), 1:(1,0), 2:(0,-1), 3:(-1,0)}
    for d in cadena:
        dx, dy = moves[int(d)]
        x, y = x + dx, y + dy
        if not (0 <= x < img.shape[0] and 0 <= y < img.shape[1]):
            img, x, y = expancion_imagen(img, x, y)
        img[x, y] = 255
    if cadena:
        return relleno_imagen(img)
    else:
        return img

def decodificar_f8_a_img(cadena, size=(200, 200)):
    img = np.zeros(size, dtype=np.uint8)
    x, y = size[0]//2, size[1]//2
    moves = {0:(0,1), 1:(1,1), 2:(1,0), 3:(1,-1), 
             4:(0,-1), 5:(-1,-1), 6:(-1,0), 7:(-1,1)}
    for d in cadena:
        dx, dy = moves[int(d)]
        x, y = x + dx, y + dy
        if not (0 <= x < img.shape[0] and 0 <= y < img.shape[1]):
            img, x, y = expancion_imagen(img, x, y)
        img[x, y] = 255
    return relleno_imagen(img)

def af8_a_f8(af8):        
    moves = {0:(0,1), 1:(1,1), 2:(1,0), 3:(1,-1), 
             4:(0,-1), 5:(-1,-1), 6:(-1,0), 7:(-1,1)}
    for inicial in range(8):
        f8, estado = [], inicial
        x, y = 0, 0
        for simbolo in af8:
            estado = (estado + int(simbolo)) % 8
            f8.append(estado)
        for dir in f8:
            dx, dy = moves[dir]
            x, y = x + dx, y + dy
        if x == 0 and y == 0: return f8
    return f8

def vcc_a_f4(vcc, inicial=0):
    tabla_vcc = {(0,1):1, (0,2):3, (0,3):0, 
                 (1,1):2, (1,2):0, (1,3):1, 
                 (2,1):3, (2,2):1, (2,3):2, 
                 (3,1):0, (3,2):2, (3,3):3}
    f4, prev = [], inicial
    for simbolo in vcc:
        nuevo = tabla_vcc.get((prev, int(simbolo)), prev)
        f4.append(nuevo)
        prev = nuevo
    return f4

def c3ot_a_f4(c3ot):
    mejor_f4 = None
    mejor_distancia = float('inf')
    # Ajuste de movimientos para que coincidan con tu decodificar_f4_a_img (0: Derecha/Y+, 1: Abajo/X+, etc)
    moves = {0: (0, 1), 1: (1, 0), 2: (0, -1), 3: (-1, 0)}

    for inicial in range(4):
        for sentido_primer_giro in [1, -1]:
            f4 = []
            ref = inicial
            support = inicial
            primer_cambio_visto = False
            x, y = 0, 0
            posible = True

            for simbolo in c3ot:
                simbolo = int(simbolo)
                if simbolo == 0:
                    nueva_dir = support
                else:
                    if not primer_cambio_visto:
                        nueva_dir = (support + sentido_primer_giro) % 4
                        primer_cambio_visto = True
                    else:
                        encontrada = False
                        for giro in [1, -1]:
                            prueba_dir = (support + giro) % 4
                            # Lógica de generación de símbolo para validar
                            if prueba_dir == ref:
                                s_gen = 1
                            elif (prueba_dir - ref) % 4 == 2:
                                s_gen = 2
                            else:
                                s_gen = 1
                            
                            if s_gen == simbolo:
                                nueva_dir = prueba_dir
                                encontrada = True
                                break
                        if not encontrada:
                            posible = False
                            break
                    ref = support
                
                support = nueva_dir
                f4.append(nueva_dir)
                dx, dy = moves[nueva_dir]
                x += dx
                y += dy

            if posible:
                distancia = abs(x) + abs(y)
                if distancia < mejor_distancia:
                    mejor_distancia = distancia
                    mejor_f4 = f4
                    if distancia == 0: break 

    return mejor_f4 if mejor_f4 else []

# ======================================================
# 4. Histograma 
# ======================================================
def tabla(cadena):
    frecuencia = Counter(cadena)
    N = len(cadena)
    datos = pd.DataFrame({
        'Simbolo': list(frecuencia.keys()),
        'Frecuencia': list(frecuencia.values())
    })
    datos['Probabilidad'] = datos['Frecuencia'] / N
    datos = datos.sort_values(by='Simbolo')

    return datos

def histograma(tabla, codigo):
    """Crear histograma"""
    
    # Gráfica de barras (Frecuencia)
    fig, axf = plt.subplots()
    axf.bar(tabla['Simbolo'], tabla['Frecuencia'], width=0.9, facecolor="#3f6deb", linewidth=0.1)
    axf.set(xlim=(-0.5, np.max(codigo)+0.5), xticks=(np.arange(0, np.max(codigo)+1)), 
           ylim=(0, np.max(tabla['Frecuencia'])+max(0.5,np.max(tabla['Frecuencia']//10))), yticks=np.arange(0, np.max(tabla['Frecuencia'])+1, max(1,np.max(tabla['Frecuencia']//10))))
    axf.set_xlabel("Elemento del código")
    axf.set_ylabel("Frecuencia", color="#3f6deb")
    
    # Gráfica de líneas (Probabilidad)
    axp = axf.twinx()
    axp.plot(tabla['Simbolo'], tabla['Probabilidad'], color='#eb3f3f', marker='.', markersize=10, linewidth=2)
    axp.set_ylabel("Probabilidad", color='#eb3f3f', fontsize=12)
    axp.tick_params(axis='y', labelcolor='#eb3f3f')
    axp.set_ylim(0, max(tabla['Probabilidad']) * 1.2)
    axp.set_yticks(np.arange(0, 1.1, 0.1))
    
    axf.set_title("Distribución de frecuencias y probabilidad del código")
    
    # Mostrar histograma
    return fig

# ======================================================
# 5. Entropía de Shannon 
# ======================================================
def entropia(tabla):
    """Generar entropía de Shannon"""
    hx = -1*(sum((tabla['Probabilidad'])*np.log2((tabla['Probabilidad']))))
    return hx

# ======================================================
# 6. Compresión Huffman
# ======================================================
def huffman(cadena):
    N = len(cadena) 
    conteo = Counter(cadena)
    heap = [[freq, [sim, ""]] for sim, freq in conteo.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        lo = heapq.heappop(heap)
        hi = heapq.heappop(heap)

        for pair in lo[1:]:
            pair[1] = '0' + pair[1]
        for pair in hi[1:]:
            pair[1] = '1' + pair[1]

        heapq.heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])

    resultado_huffman = heapq.heappop(heap)[1:]
    longitud_promedio = 0
    bits_totales = 0
    
    for simbolo, bits in resultado_huffman:
        frecuencia = conteo[simbolo]
        bits_simbolo = frecuencia * len(bits)
        bits_totales += bits_simbolo
    longitud_promedio = bits_totales / N
    return longitud_promedio

# ======================================================
# 7. Compresión Aritmética 
# ======================================================
def comprension_aritmetica(tabla):
    diccionario_probabilidades = tabla.set_index('Simbolo')['Probabilidad'].to_dict()

    longitud_promedio = 0.0

    for simbolo in diccionario_probabilidades:
                
        prob = diccionario_probabilidades[simbolo]
        
        if prob > 0:
            # log2(P) = ln(P) / ln(2)
            log2_prob = math.log(prob) / math.log(2)
            
            calculo_simbolo = prob * (-log2_prob)
            
            longitud_promedio = longitud_promedio + calculo_simbolo

    return longitud_promedio

# ======================================================
# 8. Propiedades Geométricas
# ======================================================
def propiedades(img_binaria, cadena_f4):
    area = 0
    perimetro_contacto = 0
    
    # 1. Perímetro basado en F4 (Longitud de la cadena)
    perimetro = len(cadena_f4)
    
    # 2. Área basada en objeto binario (conteo de pixeles blancos)
    area = np.sum(img_binaria == 255)

    # 3. Perímetro de Contacto (Pc) usando tu fórmula: Pc = (4n - P) / 2
    # Nota: Usamos // para obtener un resultado entero
    perimetro_contacto = (4 * area - perimetro) // 2

    # 4. Característica de Euler (E = Objetos - Agujeros)
    contours, hierarchy = cv2.findContours(img_binaria, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    num_objetos = 0
    num_agujeros = 0
    if hierarchy is not None:
        for i in range(len(contours)):
            if hierarchy[0][i][3] == -1: # No tiene padre, es objeto
                num_objetos += 1
            else: # Tiene padre, es agujero
                num_agujeros += 1
    euler = num_objetos - num_agujeros
    
    # 5. Compacidad Discreta
    if area > 1: # Evitar división por cero o raíz de 1
        numerador = area - (perimetro / 4)
        denominador = area - np.sqrt(area)
        compacidad = numerador / denominador
    else:
        compacidad = 0

    return perimetro, area, perimetro_contacto, euler, compacidad
