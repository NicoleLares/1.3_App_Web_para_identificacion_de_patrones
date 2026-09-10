import base64
import binascii
import json
import os

from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

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
# HANDLER PRINCIPAL
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
    # VALIDAR ORIGEN
    # ======================================

    def origin_is_allowed(self):

        if not ALLOWED_ORIGIN:
            return True

        origin = self.headers.get(
            "Origin",
            ""
        )

        return origin == ALLOWED_ORIGIN


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
            # LEER CONTENT-LENGTH
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
            # VALIDAR TAMAÑO
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
            # CONVERTIR A JSON
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
            # IMAGEN BASE64
            # ==================================

            image = str(
                data.get(
                    "image"
                )
                or ""
            ).strip()


            # ==================================
            # URL DE IMAGEN
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
            # VALIDAR QUE EXISTA IMAGEN
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
            # FUENTE QUE SE ENVIARÁ A OPENAI
            # ==================================

            image_source = None


            # ==================================
            # OPCIÓN 1:
            # IMAGEN SUBIDA EN BASE64
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
            # OPCIÓN 2:
            # IMAGEN MEDIANTE URL
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
            # CLIENTE DE OPENAI
            # ==================================

            client = OpenAI(
                api_key=api_key
            )


            # ==================================
            # INSTRUCCIONES PARA LA IA
            # ==================================

            instructions = """
Eres un sistema especializado en análisis visual
e identificación de patrones.

Analiza únicamente la imagen proporcionada.

Devuelve SOLAMENTE un objeto JSON válido.

No utilices Markdown.
No utilices bloques de código.
No escribas texto antes ni después del JSON.

La respuesta debe tener exactamente esta estructura:

{
    "descripcion": "string",

    "patrones": [
        "string"
    ],

    "personas": [
        {
            "descripcion": "string",
            "ubicacion": "string",
            "actividad": "string"
        }
    ],

    "objetos": [
        {
            "nombre": "string",
            "cantidad": 1,
            "ubicacion": "string"
        }
    ],

    "texto_visible": [
        "string"
    ]
}

REGLAS:

1. Describe brevemente la escena.

2. Identifica patrones visuales relevantes como:
   elementos repetidos,
   colores predominantes,
   formas,
   distribuciones,
   agrupaciones,
   simetrías
   o estructuras visuales.

3. Detecta si existen personas.

4. Para las personas describe únicamente:
   vestimenta,
   postura,
   actividad
   y ubicación aproximada.

5. No intentes identificar el nombre
   o identidad de personas reales.

6. No infieras atributos sensibles.

7. Identifica los principales objetos.

8. Agrupa objetos iguales cuando sea posible.

9. La cantidad de objetos debe ser
   un número entero positivo.

10. Usa ubicaciones aproximadas como:
    izquierda,
    derecha,
    centro,
    parte superior
    o parte inferior.

11. Detecta texto solamente cuando
    sea claramente legible.

12. Si una categoría no tiene resultados,
    devuelve un arreglo vacío [].

13. No inventes información.

14. Responde siempre en español.
"""


            # ==================================
            # PETICIÓN A OPENAI
            # ==================================

            response = client.responses.create(

                model=MODEL,

                instructions=instructions,

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
                                    image_source
                            }

                        ]
                    }
                ],

                max_output_tokens=1200,

                store=False
            )


            # ==================================
            # OBTENER RESPUESTA
            # ==================================

            output_text = (
                response.output_text
                or ""
            ).strip()


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
            # LIMPIAR BLOQUE DE CÓDIGO
            # POR SI EL MODELO LO UTILIZA
            # ==================================

            if output_text.startswith(
                "```"
            ):

                output_text = (
                    output_text
                    .strip("`")
                    .strip()
                )


                if output_text.lower().startswith(
                    "json"
                ):

                    output_text = (
                        output_text[4:]
                        .strip()
                    )


            # ==================================
            # CONVERTIR RESPUESTA A JSON
            # ==================================

            try:

                analysis = json.loads(
                    output_text
                )

            except json.JSONDecodeError:

                print(
                    "Respuesta recibida de OpenAI:"
                )

                print(
                    output_text
                )


                self.send_json(
                    500,
                    {
                        "error":
                            "La IA respondió, pero el resultado "
                            "no pudo convertirse a JSON."
                    }
                )

                return


            # ==================================
            # VALIDAR CAMPOS ESPERADOS
            # ==================================

            expected_keys = {

                "descripcion",

                "patrones",

                "personas",

                "objetos",

                "texto_visible"

            }


            if not expected_keys.issubset(
                analysis.keys()
            ):

                self.send_json(
                    500,
                    {
                        "error":
                            "La respuesta de la IA no contiene "
                            "todos los campos esperados."
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