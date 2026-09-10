import base64
import binascii
import json
import os

from http.server import BaseHTTPRequestHandler

from openai import OpenAI


# ==========================================
# CONFIGURACIÓN
# ==========================================

ALLOWED_ORIGIN = os.environ.get(
    "ALLOWED_ORIGIN",
    ""
).rstrip("/")


# ==========================================
# TAMAÑO MÁXIMO DE LA PETICIÓN
# ==========================================

MAX_BODY_BYTES = 3_500_000


# ==========================================
# MODELO
# ==========================================

MODEL = "gpt-5.6-luna"


# ==========================================
# HANDLER
# ==========================================

class handler(BaseHTTPRequestHandler):


    # ======================================
    # AGREGAR HEADERS CORS
    # ======================================

    def add_cors_headers(self):

        origin = self.headers.get(
            "Origin",
            ""
        )


        if (
            ALLOWED_ORIGIN
            and
            origin == ALLOWED_ORIGIN
        ):

            self.send_header(
                "Access-Control-Allow-Origin",
                origin
            )


            self.send_header(
                "Vary",
                "Origin"
            )


    # ======================================
    # ENVIAR RESPUESTA JSON
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
            str(
                len(body)
            )
        )


        self.end_headers()


        self.wfile.write(
            body
        )


    # ======================================
    # VALIDAR ORIGEN
    # ======================================

    def origin_is_allowed(self):

        origin = self.headers.get(
            "Origin",
            ""
        )


        if not ALLOWED_ORIGIN:

            return True


        return (
            origin ==
            ALLOWED_ORIGIN
        )


    # ======================================
    # OPTIONS
    # ======================================

    def do_OPTIONS(self):

        if not self.origin_is_allowed():

            self.send_response(
                403
            )


            self.end_headers()


            return


        self.send_response(
            204
        )


        self.add_cors_headers()


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


        self.end_headers()


    # ======================================
    # GET
    # ======================================

    def do_GET(self):

        self.send_json(
            405,
            {
                "error":
                    "Este endpoint solamente acepta peticiones POST."
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
                        0
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
            # VALIDAR BODY
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


            if (
                content_length >
                MAX_BODY_BYTES
            ):

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
            # CONVERTIR JSON
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
                    "message",
                    ""
                )
            ).strip()


            # ==================================
            # IMAGEN
            # ==================================

            image = str(
                data.get(
                    "image",
                    ""
                )
            ).strip()


            # ==================================
            # VALIDAR MENSAJE
            # ==================================

            if not message:

                message = (
                    "Analiza la imagen e identifica "
                    "los elementos y patrones visibles."
                )


            if len(message) > 500:

                self.send_json(
                    400,
                    {
                        "error":
                            "La pregunta supera los 500 caracteres."
                    }
                )


                return


            # ==================================
            # VALIDAR IMAGEN
            # ==================================

            if not image:

                self.send_json(
                    400,
                    {
                        "error":
                            "Es necesario seleccionar una imagen."
                    }
                )


                return


            # ==================================
            # FORMATOS ADMITIDOS
            # ==================================

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
                            "El formato de la imagen no es válido."
                    }
                )


                return


            # ==================================
            # VALIDAR BASE64
            # ==================================

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
                            "Los datos de la imagen no son válidos."
                    }
                )


                return


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
Eres un sistema especializado en análisis visual e
identificación de patrones dentro de imágenes.

Debes analizar únicamente la información visible en la
imagen proporcionada.

Tu análisis debe:

1. Generar una descripción general de la escena.

2. Detectar la presencia de personas.

3. Para cada persona visible, describe solamente
características observables y apropiadas como:
ropa, postura, actividad y posición aproximada.

4. No identifiques ni intentes proporcionar el nombre
o identidad de una persona real.

5. No infieras características sensibles de las personas.

6. Identifica los principales objetos presentes.

7. Agrupa objetos iguales cuando sea posible.

8. Indica una cantidad aproximada de cada objeto.

9. Indica la ubicación aproximada de los elementos usando
términos como izquierda, derecha, centro, parte superior
o parte inferior.

10. Identifica patrones visuales relevantes como elementos
repetidos, distribuciones, formas o colores cuando ayuden
a comprender la imagen.

11. Detecta texto solamente cuando sea suficientemente
legible.

12. No inventes objetos, personas ni texto que no puedas
observar con suficiente claridad.

13. Cuando exista incertidumbre, indícalo mediante una
descripción prudente.

Responde siempre en español.
"""


            # ==================================
            # ESQUEMA JSON
            # ==================================

            response_schema = {

                "type":
                    "object",

                "properties": {

                    "descripcion": {

                        "type":
                            "string"

                    },


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
                                        "integer",

                                    "minimum":
                                        1

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
                    "personas",
                    "objetos",
                    "texto_visible"

                ],


                "additionalProperties":
                    False

            }


            # ==================================
            # PETICIÓN A OPENAI
            # ==================================

            response = client.responses.create(

                model=
                    MODEL,


                instructions=
                    instructions,


                input=[
                    {

                        "role":
                            "user",


                        "content": [

                            {

                                "type":
                                    "input_text",


                                "text":
                                    message

                            },


                            {

                                "type":
                                    "input_image",


                                "image_url":
                                    image

                            }

                        ]

                    }
                ],


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


                reasoning={

                    "effort":
                        "none"

                },


                max_output_tokens=
                    1200,


                store=
                    False

            )


            # ==================================
            # VALIDAR RESPUESTA
            # ==================================

            output_text = response.output_text


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
            # CONVERTIR RESPUESTA JSON
            # ==================================

            try:

                analysis = json.loads(
                        output_text
                    )


            except json.JSONDecodeError:

                print(
                    "La respuesta del modelo "
                    "no pudo convertirse a JSON."
                )


                self.send_json(
                    500,
                    {
                        "error":
                            "No fue posible interpretar el análisis de la IA."
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