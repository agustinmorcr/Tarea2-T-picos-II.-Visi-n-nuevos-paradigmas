# Interfaz de Sistema de Análisis para imágenes 2D

## Descripción
La aplicación de análisis de imágenes 2D contiene un conjnto de herramientas útiles para detectar contornos en imágenes 2D y obtener distintos tipos de códigos de cadenas del contorno, entre los cuales están los códigos de Freeman *F8, F4,* además de los códigos *VCC, 3OT y AF8*. 

La aplicación además genera un histograma con las frecuencias y probabilidades obtenidas por cada elemento del código seleccionado con la finalidad de identificar los principales elementos que conforman la imágen.

A partir del código de cadena, la aplicación también tiene la capacidad de decodificar dicho código para regresar a la imagen original, existen varias ventanas de visualización, en dos de ellas podrás ver la imagen original y en la otra la imagen generada a partir de decodificar el código de cadena para poder comparar visualmente las dos imágenes.

Otras de las funcionalidades de la aplicación es que podemos obtener información variada de la imágen, como lo es la entropía de Shannon, compresión de Huffman, compresión Aritmética y algunas propiedades, dentro de las cuales se encuentra el perímetro de la figura, el área, perímetro de contacto, característica de Euler y compacidad discreta.

A continuación, se muestra una guía de uso para el correcto funcionamiento de la aplicación.

## Manual de Usuario
Al ingresar por primera vez a la aplicación, se podrá observar la interfaz inicial con todos los menús pero sin información alguna.

***INTERFAZ_INICIAL***

#### Menú Archivo
En el primer menú le aparecerán dos opciones, al seleccionar la primera opción, le desplegará un explorador de archivos en donde usted podrá seleccionar la imagen que desea analizar. Para fines ilustrativos de este manual, utilizaremos las imágenes .gif pertenecientes al MPEG7dataset. 

***ARCHIVO***

***CARGAR_IMAGEN***

Una vez seleccionada la imagen que desea analizar, en el panel izquierdo de la aplicación podrá observar la leyenda "*Imagen cargada*" y podrá ver también la imagen en la pestaña "*Imagen Original*". Para el ejemplo de esta guía utilizaremos la imagen butterfly-14.gif del dataset MPEG7 mencionado anteriormente.

***IMAGEN_CARGADA***

La segunda opción del menú archivo se llama salir. Su función es únicamente la de cerrar la aplicación, el mismo resultado se puede conseguir al presionar el botón de cerrar ventana que viene por defecto en la parte superior derecha o izquierda (dependiendo de su sistema operativo).

#### Menú Procesos

El segundo menú de la aplicación lleva por nombre procesos, en el que le permite seleccionar distintas opciones.

***PROCESOS***

La primera opción detecta el contorno de la imagen y lo muestra en color rojo en la pestaña "*Imagen contorno*". De igual manera, en el panel izquierdo podrá observar una leyenda confirmando que la operación se realizó con éxito.

***CONTORNO***

La segunda opción del menú procesos es la que genera la cadena, al poner el cursor encima de la opción "*Generar cadena*", se desplegará un menú secundario mostrando los cinco tipos de cadenas de texto que la aplicación puede generar. Al seleccionar uno de ellos, en el panel inferior de la interfaz se mostrará el tipo de cadena seleccionado (para el ejemplo de esta guía se seleccionó el código de Freeman *F8*), seguido de la cadena completa generada. En el panel izquierdo se muestra además la longitud total de la cadena.

***SUBMENU_CADENAS***

***CADENA_GENERADA***

La tercera opción del menú procesos muestra de igual manera un submenú con las cinco cadenas disponibles, para hacer uso de esta opción se debe seleccionar el mismo tipo de código de cadena generado anteriormente, ya que esta opción toma este mismo código y, a partir de ahí, realiza una codificación para volver a la imagen original. Esta nueva imagen generada la puede observar en la pestaña "*Imagen decodificada*" con la posibilidad de compararla visualmente con la imagen original que se encuentra en la pestaña "*Imagen original*".

***SUBMENU_DECODIFICAR***

***IMAGEN_DECODIFICADA***

La cuarta y última opción del menú procesos muestra de nueva cuenta el explorador de archivos, al seleccionar una carpeta de destino, le guardará un archivo de texto en esa ubicación seleccionada. El archivo contiene los códigos de cadena de los 5 tipos posibles.

***ARCHIVO_TEXTO_CADENAS***

#### Menú Análisis

En el tercer menú es aparecen todas las opciones de análisis posibles que usted puede realizar. En este apartado se detalla cómo acceder a cada una y qué es lo que muestra.

***ANALISIS***

La primera opción es la que genera el histograma, que usted podrá observar en la pestaña "*Histograma*". En el eje de las *x* del histograma usted puede observar los elementos correspondientes al código seleccioando. En el caso del ejemplo aparecen los elementos del 0 al 7 ya que estamos trabajando con el códio de Freeman *F8*, pero esto puede variar dependiendo del tipo de código que usted haya seleccionado. En el eje izquierdo de las *y* aparecen las frecuencias que se encontraron en los elementos del código y están representadas por medio de un gráfico de barras. El rango de frecuencias que aparecen varían dependiendo al tipo de código y a la imagen que se seleccione, ya que pueden contener diferentes frecuencias. En el eje derecho de las *y* se muestra la probabilidad en escala de 0.0 a 1.0. Esta escala se mantiene constante y es representada mediante una gráfica de puntos y líneas que indican la probabilidad que tiene cada elemnto en aparecer en la cadena. 

En el panel derecho de la interfaz se muestra una tabla que contiene los simbolos, la frecuencia y su probabilidad exacta que tuvieron cada uno de ellos en la cadena. Esto con la finalidad de ver la información real y precisa de estos datos. 

***HISTOGRAMA***

Las siguientes opciones del menú análisis hace uso únicamente del panel izquierdo de datos, donde muestra el valor de la operación solicitada.

***DATOS***

#### Cargar nueva imagen

Al finalizar de realizar las operaciones que usted desee, puede cargar otra imagen sin necesidad de cerrar y volver a abrir la aplicación. La información generada para la imagen anterior se borra para dar paso a información nueva de la siguiente imagen que desee analizar. Esto evita que se mezcle información de diferentes imágenes, lo que podría causar sesgos en los resultados. La nueva imagen cargada para este ejemplo fué bell-1.gif del mismo dataset MPEG7.

***NUEVA_IMAGEN***

Al finalizar su sesión, puede salir de la aplicación al seleccionar la opción salir que se encuentra dentro del menú archivo de la aplicación o simplemente hacer click en la *X* de la ventana de la aplicación. 
