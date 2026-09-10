import base64
import binascii
import json
import os

from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

from openai import OpenAI


# ==========================================
# CONFIGURACIÓN CORS
# ==========================================

# Tu GitHub Pages
DEFAULT_ORIGIN = "https://nicolelares.github.io"


# Orígenes permitidos
ALLOWED_ORIGINS = {
    DEFAULT_ORIGIN,

    # También permitimos pruebas locales
    "http://127.0.0.1:5500",
    "http://localhost:5500",
}


# Si existe ALLOWED_ORIGIN en Vercel,
# también se agrega automáticamente.
configured_origins = os.environ.get(
    "ALLOWED_ORIGIN",
    ""
)


for configured_origin in configured_origins.split(","):

    configured_origin = (
        configured_origin
        .strip()
        .rstrip("/")
    )

    if configured_origin:

        ALLOWED_ORIGINS.add(
            configured_origin
        )


# ==========================================
# MODELO
# ==========================================

MODEL = "gpt-5.6-luna"


# ==========================================
# TAMAÑO MÁXIMO DE LA PETICIÓN
# ==========================================

MAX_BODY_BYTES = 3_500_000


# ==========================================
# HANDLER PRINCIPAL
# ==========================================

class handler(BaseHTTPRequestHandler):


    # ======================================
    # OBTENER ORIGEN
    # ======================================

    def get_request_origin(self):

        return self.headers.get(
            "Origin",
            ""
        ).rstrip("/")


    # ======================================
    # VALIDAR ORIGEN
    # ======================================

    def origin_is_allowed(self):

        origin = self.get_request_origin()

        return (
            origin in ALLOWED_ORIGINS
        )


    # ======================================
    # AGREGAR HEADERS CORS
    # ======================================

    def add_cors_headers(self):

        origin = self.get_request_origin()


        if origin in ALLOWED_ORIGINS:

            self.send_header(
                "Access-Control-Allow-Origin",
                origin
            )

            self.send_header(
                "Vary",
                "Origin"
            )


    # ======================================
    # RESPUESTA JSON
    # ======================================

    def send_json(
        self,
        status_code,
        data
    ):

        body = json.dumps(
            data,
            ensure_ascii=False
        ).encode(
            "utf-8"
        )


        self.send_response(
            status_code
        )


        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )


        self.add_cors_headers()


        self.send_header(
            "Content-Length",
            str(len(body))
        )


        self.end_headers()


        self.wfile.write(
            body
        )


    # ======================================
    # OPTIONS
    # PREFLIGHT DE CORS
    # ======================================

    def do_OPTIONS(self):

        origin = self.get_request_origin()


        if origin not in ALLOWED_ORIGINS:

            self.send_response(
                403
            )

            self.end_headers()

            return


        self.send_response(
            204
        )


        self.send_header(
            "Access-Control-Allow-Origin",
            origin
        )


        self.send_header(
            "Access-Control-Allow-Methods",
            "POST, OPTIONS"
        )


        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type"
        )


        self.send_header(
            "Access-Control-Max-Age",
            "86400"
        )


        self.send_header(
            "Vary",
            "Origin"
        )


        self.end_headers()


    # ======================================
    # GET
    # ======================================

    def do_GET(self):

        self.send_json(
            405,
            {
                "error":
                    "Este endpoint solamente acepta POST."
            }
        )


    # ======================================
    # POST
    # ======================================

    def do_POST(self):

        try:

            # ==================================
            # VALIDAR ORIGEN
            # ==================================

            if not self.origin_is_allowed():

                self.send_json(
                    403,
                    {
                        "error":
                            "Origen no autorizado."
                    }
                )

                return


            # ==================================
            # CONTENT LENGTH
            # ==================================

            try:

                content_length = int(
                    self.headers.get(
                        "Content-Length",
                        "0"
                    )
                )

            except ValueError:

                self.send_json(
                    400,
                    {
                        "error":
                            "Content-Length no válido."
                    }
                )

                return


            # ==================================
            # VALIDAR PETICIÓN
            # ==================================

            if content_length <= 0:

                self.send_json(
                    400,
                    {
                        "error":
                            "La petición está vacía."
                    }
                )

                return


            if content_length > MAX_BODY_BYTES:

                self.send_json(
                    413,
                    {
                        "error":
                            "La imagen es demasiado grande."
                    }
                )

                return


            # ==================================
            # LEER BODY
            # ==================================

            raw_body = self.rfile.read(
                content_length
            )


            # ==================================
            # CONVERTIR BODY A JSON
            # ==================================

            try:

                data = json.loads(
                    raw_body.decode(
                        "utf-8"
                    )
                )

            except (
                json.JSONDecodeError,
                UnicodeDecodeError
            ):

                self.send_json(
                    400,
                    {
                        "error":
                            "La petición no contiene JSON válido."
                    }
                )

                return


            # ==================================
            # MENSAJE
            # ==================================

            message = str(
                data.get(
                    "message"
                )
                or ""
            ).strip()


            # ==================================
            # IMAGEN SUBIDA
            # ==================================

            image = str(
                data.get(
                    "image"
                )
                or ""
            ).strip()


            # ==================================
            # URL DE INTERNET
            # ==================================

            image_url = str(
                data.get(
                    "image_url"
                )
                or ""
            ).strip()


            # ==================================
            # MENSAJE PREDETERMINADO
            # ==================================

            if not message:

                message = (
                    "Analiza esta imagen e identifica "
                    "los patrones y elementos visibles."
                )


            # ==================================
            # VALIDAR TEXTO
            # ==================================

            if len(message) > 500:

                self.send_json(
                    400,
                    {
                        "error":
                            "La consulta supera los 500 caracteres."
                    }
                )

                return


            # ==================================
            # VALIDAR FUENTE DE IMAGEN
            # ==================================

            if (
                not image
                and
                not image_url
            ):

                self.send_json(
                    400,
                    {
                        "error":
                            "Debes seleccionar una imagen "
                            "o proporcionar una URL."
                    }
                )

                return


            # ==================================
            # FUENTE FINAL PARA OPENAI
            # ==================================

            image_source = None


            # ==================================
            # OPCIÓN 1
            # IMAGEN BASE64
            # ==================================

            if image:

                valid_prefixes = (
                    "data:image/jpeg;base64,",
                    "data:image/png;base64,",
                    "data:image/webp;base64,"
                )


                if not image.startswith(
                    valid_prefixes
                ):

                    self.send_json(
                        400,
                        {
                            "error":
                                "El formato de la imagen "
                                "no es válido."
                        }
                    )

                    return


                # ==============================
                # VALIDAR BASE64
                # ==============================

                try:

                    base64_data = image.split(
                        ",",
                        1
                    )[1]


                    base64.b64decode(
                        base64_data,
                        validate=True
                    )


                except (
                    IndexError,
                    ValueError,
                    binascii.Error
                ):

                    self.send_json(
                        400,
                        {
                            "error":
                                "Los datos Base64 de la imagen "
                                "no son válidos."
                        }
                    )

                    return


                image_source = image


            # ==================================
            # OPCIÓN 2
            # URL DE INTERNET
            # ==================================

            else:

                parsed_url = urlparse(
                    image_url
                )


                if (
                    parsed_url.scheme != "https"
                    or
                    not parsed_url.netloc
                ):

                    self.send_json(
                        400,
                        {
                            "error":
                                "La URL debe ser una dirección "
                                "HTTPS válida."
                        }
                    )

                    return


                image_source = image_url


            # ==================================
            # API KEY
            # ==================================

            api_key = os.environ.get(
                "OPENAI_API_KEY"
            )


            if not api_key:

                self.send_json(
                    500,
                    {
                        "error":
                            "OPENAI_API_KEY no está configurada."
                    }
                )

                return


            # ==================================
            # CLIENTE OPENAI
            # ==================================

            client = OpenAI(
                api_key=api_key
            )


            # ==================================
            # INSTRUCCIONES
            # ==================================

            instructions = """
Eres un sistema especializado en análisis visual
e identificación de patrones dentro de imágenes.

Analiza únicamente la información visible en la imagen.

Debes realizar las siguientes tareas:

1. Dar una descripción general breve de la imagen.

2. Identificar patrones visuales relevantes como:
   - elementos repetidos,
   - colores predominantes,
   - formas similares,
   - agrupaciones,
   - distribuciones,
   - simetrías,
   - estructuras visuales.

3. Detectar la presencia de personas.

4. Para cada persona describe únicamente
   características visibles y apropiadas como:
   - vestimenta,
   - postura,
   - actividad,
   - ubicación aproximada.

5. No identifiques ni intentes proporcionar
   la identidad de personas reales.

6. No infieras atributos sensibles de las personas.

7. Identifica los principales objetos visibles.

8. Agrupa objetos iguales cuando sea razonable.

9. Indica una cantidad aproximada de cada objeto.

10. Indica la ubicación aproximada utilizando:
    - izquierda,
    - derecha,
    - centro,
    - parte superior,
    - parte inferior.

11. Detecta texto solamente cuando sea
    claramente legible.

12. No inventes información que no sea visible.

13. Si existe incertidumbre, utiliza una descripción
    prudente.

14. Responde siempre en español.
"""


            # ==================================
            # ESQUEMA JSON
            # ==================================

            response_schema = {

                "type":
                    "object",


                "properties": {


                    # ==========================
                    # DESCRIPCIÓN
                    # ==========================

                    "descripcion": {

                        "type":
                            "string"

                    },


                    # ==========================
                    # PATRONES
                    # ==========================

                    "patrones": {

                        "type":
                            "array",

                        "items": {

                            "type":
                                "string"

                        }

                    },


                    # ==========================
                    # PERSONAS
                    # ==========================

                    "personas": {

                        "type":
                            "array",

                        "items": {

                            "type":
                                "object",


                            "properties": {


                                "descripcion": {

                                    "type":
                                        "string"

                                },


                                "ubicacion": {

                                    "type":
                                        "string"

                                },


                                "actividad": {

                                    "type":
                                        "string"

                                }

                            },


                            "required": [

                                "descripcion",

                                "ubicacion",

                                "actividad"

                            ],


                            "additionalProperties":
                                False

                        }

                    },


                    # ==========================
                    # OBJETOS
                    # ==========================

                    "objetos": {

                        "type":
                            "array",

                        "items": {

                            "type":
                                "object",


                            "properties": {


                                "nombre": {

                                    "type":
                                        "string"

                                },


                                "cantidad": {

                                    "type":
                                        "integer"

                                },


                                "ubicacion": {

                                    "type":
                                        "string"

                                }

                            },


                            "required": [

                                "nombre",

                                "cantidad",

                                "ubicacion"

                            ],


                            "additionalProperties":
                                False

                        }

                    },


                    # ==========================
                    # TEXTO VISIBLE
                    # ==========================

                    "texto_visible": {

                        "type":
                            "array",

                        "items": {

                            "type":
                                "string"

                        }

                    }

                },


                "required": [

                    "descripcion",

                    "patrones",

                    "personas",

                    "objetos",

                    "texto_visible"

                ],


                "additionalProperties":
                    False

            }


            # ==================================
            # PETICIÓN A RESPONSES API
            # ==================================

            response = client.responses.create(

                model=MODEL,


                instructions=instructions,


                input=[
                    {

                        "role":
                            "user",


                        "content": [


                            # ==================
                            # TEXTO
                            # ==================

                            {

                                "type":
                                    "input_text",

                                "text":
                                    message

                            },


                            # ==================
                            # IMAGEN
                            # ==================

                            {

                                "type":
                                    "input_image",

                                "image_url":
                                    image_source,

                                "detail":
                                    "high"

                            }

                        ]

                    }
                ],


                # ==================================
                # RESPUESTA ESTRUCTURADA JSON
                # ==================================

                text={

                    "format": {

                        "type":
                            "json_schema",

                        "name":
                            "analisis_visual",

                        "strict":
                            True,

                        "schema":
                            response_schema

                    }

                },


                # ==================================
                # RAZONAMIENTO
                # ==================================

                reasoning={

                    "effort":
                        "none"

                },


                max_output_tokens=
                    1400,


                store=
                    False

            )


            # ==================================
            # OBTENER TEXTO DE RESPUESTA
            # ==================================

            output_text = (
                response.output_text
                or ""
            ).strip()


            # ==================================
            # VALIDAR RESPUESTA
            # ==================================

            if not output_text:

                self.send_json(
                    500,
                    {
                        "error":
                            "La IA no devolvió resultados."
                    }
                )

                return


            # ==================================
            # CONVERTIR RESPUESTA A JSON
            # ==================================

            try:

                analysis = json.loads(
                    output_text
                )


            except json.JSONDecodeError:

                print(
                    "Respuesta no válida de OpenAI:"
                )

                print(
                    output_text
                )


                self.send_json(
                    500,
                    {
                        "error":
                            "No fue posible interpretar "
                            "el análisis generado por la IA."
                    }
                )

                return


            # ==================================
            # RESPUESTA AL FRONTEND
            # ==================================

            self.send_json(
                200,
                {

                    "analysis":
                        analysis

                }
            )


        # ======================================
        # ERROR GENERAL
        # ======================================

        except Exception as error:

            print(
                f"Error en /api/chat: "
                f"{type(error).__name__}: "
                f"{error}"
            )


            self.send_json(
                500,
                {
                    "error":
                        "No fue posible analizar la imagen."
                }
            )