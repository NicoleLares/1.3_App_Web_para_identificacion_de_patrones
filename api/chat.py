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

DEFAULT_ORIGIN = "https://nicolelares.github.io"


ALLOWED_ORIGINS = {

    DEFAULT_ORIGIN,

    "http://127.0.0.1:5500",

    "http://localhost:5500",

}


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
# TAMAÑO MÁXIMO
# ==========================================

MAX_BODY_BYTES = 3_500_000


# ==========================================
# HANDLER
# ==========================================

class handler(BaseHTTPRequestHandler):


    # ======================================
    # ORIGEN DE LA PETICIÓN
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
    # CORS
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
    # ENVIAR JSON
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
            # CORS
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
            # BODY
            # ==================================

            raw_body = self.rfile.read(
                content_length
            )


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
            # URL
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
                    "Analiza la imagen, cuenta las personas "
                    "e identifica objetos, texto y patrones."
                )


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
            # VALIDAR FUENTE
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


            image_source = None


            # ==================================
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
            # URL
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
            # CLIENTE
            # ==================================

            client = OpenAI(
                api_key=api_key
            )


            # ==================================
            # INSTRUCCIONES
            # ==================================

            instructions = """
Eres un sistema especializado en análisis visual
e identificación de patrones en imágenes.

Analiza exclusivamente la información que sea
razonablemente visible en la imagen.

TAREAS:

1. Genera una descripción general breve de la imagen.

2. Cuenta todas las personas razonablemente visibles.

3. Coloca el número total de personas en el campo
   total_personas.

4. Si no hay personas visibles:
   total_personas debe ser 0.

5. Evita contar dos veces a la misma persona.

6. Describe a las personas claramente visibles mediante:
   - vestimenta,
   - postura,
   - actividad,
   - ubicación aproximada.

7. Si existe un grupo muy grande de personas,
   cuenta a todas las personas razonablemente visibles,
   pero describe individualmente solamente hasta
   12 de las personas más claras.

8. NO identifiques a ninguna persona por su nombre.

9. NO identifiques famosos, celebridades, deportistas,
   políticos, artistas o cualquier otra persona real,
   aunque creas reconocerla.

10. No realices reconocimiento facial.

11. No infieras atributos sensibles como:
    - religión,
    - origen étnico,
    - orientación sexual,
    - condición médica,
    - afiliación política.

12. Identifica los principales objetos visibles.

13. Agrupa objetos iguales cuando sea razonable.

14. Indica una cantidad aproximada de cada objeto.

15. Indica la ubicación aproximada de los objetos,
    usando términos como:
    - izquierda,
    - derecha,
    - centro,
    - parte superior,
    - parte inferior.

16. Identifica patrones visuales relevantes como:
    - elementos repetidos,
    - colores predominantes,
    - formas similares,
    - agrupaciones,
    - distribuciones,
    - simetrías,
    - estructuras visuales.

17. Detecta texto únicamente cuando sea
    claramente legible.

18. No inventes objetos, personas, texto o patrones.

19. Si existe incertidumbre, utiliza lenguaje prudente.

20. Responde siempre en español.
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
                    # TOTAL PERSONAS
                    # ==========================

                    "total_personas": {

                        "type":
                            "integer",

                        "minimum":
                            0

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


                    # ==========================
                    # TEXTO
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


                # ==================================
                # CAMPOS OBLIGATORIOS
                # ==================================

                "required": [

                    "descripcion",

                    "total_personas",

                    "patrones",

                    "personas",

                    "objetos",

                    "texto_visible"

                ],


                "additionalProperties":
                    False

            }


            # ==================================
            # OPENAI
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
                                    image_source,

                                "detail":
                                    "high"
                            }

                        ]

                    }
                ],


                # ==================================
                # JSON ESTRUCTURADO
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


                reasoning={

                    "effort":
                        "none"

                },


                max_output_tokens=
                    1600,


                store=
                    False

            )


            # ==================================
            # RESPUESTA
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
            # CONVERTIR JSON
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
            # RESPONDER
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