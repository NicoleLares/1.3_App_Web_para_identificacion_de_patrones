# 1.3 App Web para Identificación de Patrones

Aplicación web desarrollada para la identificación de patrones
y elementos presentes en imágenes mediante Inteligencia Artificial.

El sistema permite seleccionar una imagen desde el dispositivo
del usuario, visualizarla dentro de la aplicación y enviarla a
un modelo de Inteligencia Artificial para realizar un análisis
de su contenido.

---

## Objetivo

Desarrollar una aplicación web que utilice Inteligencia Artificial
para analizar imágenes e identificar diferentes patrones y
elementos presentes en ellas.

La aplicación busca demostrar el uso de modelos multimodales
capaces de procesar información visual y generar una descripción
estructurada de los elementos encontrados.

---

## Funcionalidades

La aplicación permite:

- Seleccionar una imagen desde el dispositivo.
- Mostrar una previsualización de la imagen seleccionada.
- Analizar imágenes mediante Inteligencia Artificial.
- Identificar objetos presentes en la imagen.
- Detectar la presencia de personas.
- Describir características visuales de las personas.
- Determinar la cantidad aproximada de algunos objetos.
- Identificar la ubicación aproximada de los elementos.
- Detectar texto visible dentro de una imagen.
- Generar una descripción general de la escena.
- Realizar preguntas relacionadas con la imagen.
- Reiniciar el análisis para seleccionar una nueva imagen.

---

## Tecnologías utilizadas

### Frontend

- HTML5
- CSS3
- JavaScript

### Backend

- Python
- Vercel Serverless Functions

### Inteligencia Artificial

- OpenAI API
- Responses API
- Modelos multimodales
- Análisis de imágenes

### Control de versiones

- Git
- GitHub

### Despliegue

- GitHub Pages
- Vercel

---

## Estructura del proyecto

```text
1.3_App_Web_Identificacion_Patrones/
│
├── api/
│   └── chat.py
│
├── assets/
│   │
│   ├── css/
│   │   └── styles.css
│   │
│   └── js/
│       └── app.js
│
├── .gitignore
├── .python-version
├── index.html
├── README.md
├── requirements.txt
└── vercel.json
```

---

## Funcionamiento

El funcionamiento general de la aplicación es el siguiente:

1. El usuario selecciona una imagen desde su dispositivo.

2. JavaScript obtiene el archivo seleccionado.

3. La imagen se muestra dentro de la aplicación mediante
   una previsualización.

4. JavaScript prepara y comprime la imagen para enviarla
   al servidor.

5. El frontend realiza una petición HTTP al backend.

6. El backend desarrollado en Python recibe la imagen.

7. Python utiliza la API de OpenAI para enviar la imagen
   a un modelo multimodal.

8. El modelo analiza el contenido visual de la imagen.

9. La Inteligencia Artificial genera información estructurada
   sobre los patrones y elementos encontrados.

10. El backend devuelve los resultados en formato JSON.

11. JavaScript procesa la respuesta.

12. Los resultados son mostrados dentro de la interfaz.

---

## Flujo de la aplicación

```text
Usuario
   │
   ▼
Seleccionar imagen
   │
   ▼
Previsualización
   │
   ▼
JavaScript
   │
   ▼
Petición HTTP
   │
   ▼
Vercel
/api/chat
   │
   ▼
Python
   │
   ▼
OpenAI API
   │
   ▼
Modelo multimodal
   │
   ▼
Identificación de patrones
   │
   ▼
Respuesta JSON
   │
   ▼
JavaScript
   │
   ▼
Resultados en pantalla
```

---

## Identificación de patrones

La aplicación analiza diferentes elementos presentes
dentro de una imagen.

### Descripción general

La Inteligencia Artificial genera una descripción breve
de la escena observada.

Ejemplo:

```text
Se observa una persona trabajando frente a una computadora
sobre un escritorio que contiene diferentes objetos.
```

---

### Personas detectadas

Cuando existen personas en la imagen, la aplicación puede
describir características visuales como:

- Vestimenta.
- Posición.
- Postura.
- Actividad.
- Ubicación aproximada dentro de la imagen.

El sistema no intenta identificar la identidad real
de las personas.

---

### Objetos identificados

La aplicación puede reconocer diferentes objetos visibles.

Por ejemplo:

```text
Computadora
Cantidad: 1
Ubicación: centro

Taza
Cantidad: 1
Ubicación: derecha

Silla
Cantidad: 2
Ubicación: parte inferior
```

---

### Texto visible

La Inteligencia Artificial también puede identificar
texto claramente visible dentro de la imagen.

Por ejemplo:

```text
OPEN
SALIDA
Tecnológico Nacional de México
```

---

## Formatos de imagen

La aplicación admite los siguientes formatos:

```text
JPG
JPEG
PNG
WEBP
```

---

## API

La aplicación utiliza la API de OpenAI mediante el backend
desarrollado en Python.

El frontend realiza una petición hacia:

```text
/api/chat
```

Cuando el backend está desplegado en Vercel, la dirección
tendrá una estructura similar a:

```text
https://nombre-del-proyecto.vercel.app/api/chat
```

---

## Datos enviados al backend

El frontend envía información similar a:

```json
{
    "message": "Identifica los elementos de esta imagen",
    "image": "data:image/jpeg;base64,..."
}
```

La propiedad `message` contiene la instrucción proporcionada
por el usuario.

La propiedad `image` contiene la imagen preparada para ser
analizada.

---

## Respuesta del servidor

El backend puede devolver información estructurada similar a:

```json
{
    "analysis": {

        "descripcion":
            "Se observa una persona trabajando frente a una computadora.",

        "personas": [
            {
                "descripcion":
                    "Persona con ropa oscura sentada frente al escritorio.",

                "ubicacion":
                    "Centro de la imagen",

                "actividad":
                    "Utilizando una computadora"
            }
        ],

        "objetos": [
            {
                "nombre":
                    "computadora",

                "cantidad":
                    1,

                "ubicacion":
                    "centro"
            },

            {
                "nombre":
                    "taza",

                "cantidad":
                    1,

                "ubicacion":
                    "derecha"
            }
        ],

        "texto_visible": [
            "OPENAI"
        ]
    }
}
```

---

## Variables de entorno

El backend necesita las siguientes variables de entorno:

```text
OPENAI_API_KEY
ALLOWED_ORIGIN
```

---

### OPENAI_API_KEY

Contiene la clave utilizada para realizar peticiones
a la API de OpenAI.

Esta variable debe configurarse dentro de Vercel.

Nunca debe colocarse directamente dentro de:

```text
index.html
app.js
chat.py
README.md
```

ni debe almacenarse en un repositorio público.

---

### ALLOWED_ORIGIN

Define qué sitio web tiene permiso para comunicarse
con el backend.

Por ejemplo:

```text
https://usuario.github.io
```

Esta configuración se utiliza para controlar las
peticiones mediante CORS.

---

## Seguridad

La API Key de OpenAI solamente es utilizada desde
el backend desarrollado en Python.

El navegador nunca recibe directamente la clave.

El flujo es:

```text
Navegador
    │
    ▼
JavaScript
    │
    ▼
Servidor de Vercel
    │
    ├── OPENAI_API_KEY
    │
    ▼
OpenAI API
```

Esto evita exponer la clave directamente dentro
del código frontend.

---

## Despliegue

El proyecto utiliza dos servicios principales.

### GitHub Pages

Se utiliza para publicar el frontend:

```text
HTML
CSS
JavaScript
```

### Vercel

Se utiliza para ejecutar el backend:

```text
Python
/api/chat
```

---

## Resultado

La práctica permite demostrar cómo una aplicación web
puede integrar modelos de Inteligencia Artificial capaces
de analizar tanto texto como imágenes.

A partir de una imagen proporcionada por el usuario,
el sistema puede identificar diferentes patrones y
elementos visuales, procesar la información y presentar
los resultados dentro de una interfaz web organizada.

---

## Autor

Nicole Dayana Esparza Lares

No. Control: 22200208

TecNM Campus Pachuca

Inteligencia Artificial aplicada a las TIC

Práctica 1.3 - App Web para Identificación de Patrones