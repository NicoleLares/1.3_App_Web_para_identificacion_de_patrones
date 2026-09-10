// ==========================================
// URL DEL BACKEND
// ==========================================

/*
    IMPORTANTE:

    Después de desplegar este nuevo proyecto
    en Vercel, reemplaza esta dirección por
    la URL correspondiente a tu proyecto 1.3.

    Ejemplo:

    https://mi-proyecto.vercel.app/api/chat
*/

const API_URL =
    "https://TU-PROYECTO.vercel.app/api/chat";


// ==========================================
// CONFIGURACIÓN DE IMAGEN
// ==========================================

const MAX_IMAGE_DIMENSION = 1280;

const MAX_DATA_URL_LENGTH = 2400000;


// ==========================================
// ELEMENTOS DEL HTML
// ==========================================

const form =
    document.getElementById(
        "chatForm"
    );


const messageInput =
    document.getElementById(
        "messageInput"
    );


const imageInput =
    document.getElementById(
        "imageInput"
    );


const previewImage =
    document.getElementById(
        "previewImage"
    );


const previewPlaceholder =
    document.getElementById(
        "previewPlaceholder"
    );


const fileInfo =
    document.getElementById(
        "fileInfo"
    );


const fileName =
    document.getElementById(
        "fileName"
    );


const fileSize =
    document.getElementById(
        "fileSize"
    );


const sendButton =
    document.getElementById(
        "sendButton"
    );


const newChatButton =
    document.getElementById(
        "newChatButton"
    );


const analysisEmpty =
    document.getElementById(
        "analysisEmpty"
    );


const analysisLoading =
    document.getElementById(
        "analysisLoading"
    );


const analysisResult =
    document.getElementById(
        "analysisResult"
    );


const descriptionResult =
    document.getElementById(
        "descriptionResult"
    );


const peopleResult =
    document.getElementById(
        "peopleResult"
    );


const objectsResult =
    document.getElementById(
        "objectsResult"
    );


const textResult =
    document.getElementById(
        "textResult"
    );


const errorMessage =
    document.getElementById(
        "errorMessage"
    );


// ==========================================
// IMAGEN ACTUAL
// ==========================================

let currentImage = null;


// ==========================================
// FORMATEAR TAMAÑO DEL ARCHIVO
// ==========================================

function formatFileSize(bytes) {

    if (bytes < 1024) {

        return (
            bytes +
            " B"
        );

    }


    if (
        bytes <
        1024 * 1024
    ) {

        return (
            (
                bytes /
                1024
            ).toFixed(1)
            +
            " KB"
        );

    }


    return (
        (
            bytes /
            (
                1024 *
                1024
            )
        ).toFixed(2)
        +
        " MB"
    );

}


// ==========================================
// LEER ARCHIVO COMO IMAGEN
// ==========================================

function loadImageFile(file) {

    return new Promise(
        (
            resolve,
            reject
        ) => {

            const reader =
                new FileReader();


            reader.onload = () => {

                const image =
                    new Image();


                image.onload = () => {

                    resolve(
                        image
                    );

                };


                image.onerror = () => {

                    reject(
                        new Error(
                            "No fue posible cargar la imagen."
                        )
                    );

                };


                image.src =
                    reader.result;

            };


            reader.onerror = () => {

                reject(
                    new Error(
                        "No fue posible leer el archivo."
                    )
                );

            };


            reader.readAsDataURL(
                file
            );

        }
    );

}


// ==========================================
// COMPRIMIR IMAGEN
// ==========================================

async function compressImage(file) {

    const image =
        await loadImageFile(
            file
        );


    // ======================================
    // CALCULAR ESCALA
    // ======================================

    let scale =
        Math.min(
            1,
            MAX_IMAGE_DIMENSION /
            Math.max(
                image.width,
                image.height
            )
        );


    /*
        Hacemos varios intentos.

        Si la imagen sigue siendo grande,
        disminuimos calidad y resolución.
    */

    for (
        let attempt = 0;
        attempt < 6;
        attempt++
    ) {

        const width =
            Math.max(
                1,
                Math.round(
                    image.width *
                    scale
                )
            );


        const height =
            Math.max(
                1,
                Math.round(
                    image.height *
                    scale
                )
            );


        // ==================================
        // CANVAS
        // ==================================

        const canvas =
            document.createElement(
                "canvas"
            );


        canvas.width =
            width;

        canvas.height =
            height;


        const context =
            canvas.getContext(
                "2d"
            );


        if (!context) {

            throw new Error(
                "El navegador no permite procesar la imagen."
            );

        }


        // ==================================
        // FONDO BLANCO
        // ==================================

        /*
            Esto evita que imágenes PNG
            transparentes se conviertan
            a un fondo negro.
        */

        context.fillStyle =
            "#ffffff";


        context.fillRect(
            0,
            0,
            width,
            height
        );


        // ==================================
        // DIBUJAR IMAGEN
        // ==================================

        context.drawImage(
            image,
            0,
            0,
            width,
            height
        );


        // ==================================
        // CALIDAD
        // ==================================

        const quality =
            Math.max(
                0.5,
                0.86 -
                (
                    attempt *
                    0.07
                )
            );


        // ==================================
        // CONVERTIR A JPEG BASE64
        // ==================================

        const dataURL =
            canvas.toDataURL(
                "image/jpeg",
                quality
            );


        // ==================================
        // VALIDAR TAMAÑO
        // ==================================

        if (
            dataURL.length <=
            MAX_DATA_URL_LENGTH
        ) {

            return dataURL;

        }


        // ==================================
        // REDUCIR PARA SIGUIENTE INTENTO
        // ==================================

        scale *=
            0.78;

    }


    throw new Error(
        "La imagen es demasiado grande para ser procesada."
    );

}


// ==========================================
// CAMBIO DE IMAGEN
// ==========================================

imageInput.addEventListener(
    "change",
    async () => {

        hideError();


        const file =
            imageInput.files[0];


        if (!file) {

            return;

        }


        // ==================================
        // VALIDAR TIPO
        // ==================================

        const allowedTypes = [
            "image/jpeg",
            "image/png",
            "image/webp"
        ];


        if (
            !allowedTypes.includes(
                file.type
            )
        ) {

            imageInput.value =
                "";


            showError(
                "Selecciona una imagen JPG, PNG o WEBP."
            );


            return;

        }


        // ==================================
        // MOSTRAR PROCESANDO
        // ==================================

        previewImage.hidden =
            true;


        previewPlaceholder.hidden =
            false;


        previewPlaceholder.innerHTML = `
            <div class="preview-icon">
                ⏳
            </div>

            <p>
                Preparando imagen...
            </p>

            <span>
                Espera un momento
            </span>
        `;


        fileInfo.hidden =
            true;


        currentImage =
            null;


        resetAnalysis();


        try {

            // ==================================
            // COMPRIMIR
            // ==================================

            currentImage =
                await compressImage(
                    file
                );


            // ==================================
            // MOSTRAR IMAGEN
            // ==================================

            previewImage.src =
                currentImage;


            previewImage.hidden =
                false;


            previewPlaceholder.hidden =
                true;


            // ==================================
            // INFORMACIÓN
            // ==================================

            fileName.textContent =
                file.name;


            fileSize.textContent =
                formatFileSize(
                    file.size
                );


            fileInfo.hidden =
                false;


        }

        catch (error) {

            currentImage =
                null;


            restorePreviewPlaceholder();


            showError(
                error.message
            );

        }

    }
);


// ==========================================
// ENVIAR IMAGEN
// ==========================================

form.addEventListener(
    "submit",
    async (event) => {

        event.preventDefault();


        hideError();


        // ==================================
        // VALIDAR IMAGEN
        // ==================================

        if (!currentImage) {

            showError(
                "Primero selecciona una imagen."
            );


            return;

        }


        // ==================================
        // PREGUNTA
        // ==================================

        let message =
            messageInput.value.trim();


        // ==================================
        // PREGUNTA PREDETERMINADA
        // ==================================

        if (!message) {

            message =
                "Analiza esta imagen e identifica los patrones, objetos, personas y texto visible.";

        }


        // ==================================
        // VALIDAR LONGITUD
        // ==================================

        if (
            message.length >
            500
        ) {

            showError(
                "La pregunta no puede superar los 500 caracteres."
            );


            return;

        }


        // ==================================
        // CARGANDO
        // ==================================

        setLoading(
            true
        );


        try {

            // ==================================
            // PETICIÓN
            // ==================================

            const response =
                await fetch(
                    API_URL,
                    {

                        method:
                            "POST",

                        headers: {

                            "Content-Type":
                                "application/json"

                        },

                        body:
                            JSON.stringify(
                                {

                                    message:
                                        message,

                                    image:
                                        currentImage

                                }
                            )

                    }
                );


            // ==================================
            // VALIDAR RESPUESTA JSON
            // ==================================

            const contentType =
                response.headers.get(
                    "content-type"
                );


            if (
                !contentType ||
                !contentType.includes(
                    "application/json"
                )
            ) {

                throw new Error(
                    "El servidor no devolvió una respuesta JSON válida."
                );

            }


            const data =
                await response.json();


            // ==================================
            // ERROR HTTP
            // ==================================

            if (!response.ok) {

                throw new Error(
                    data.error ||
                    "Ocurrió un error al analizar la imagen."
                );

            }


            // ==================================
            // VALIDAR ANÁLISIS
            // ==================================

            if (!data.analysis) {

                throw new Error(
                    "El servidor no devolvió los resultados del análisis."
                );

            }


            // ==================================
            // MOSTRAR RESULTADOS
            // ==================================

            renderAnalysis(
                data.analysis
            );


        }

        catch (error) {

            analysisResult.hidden =
                true;


            analysisEmpty.hidden =
                false;


            showError(
                error.message
            );


        }

        finally {

            setLoading(
                false
            );

        }

    }
);


// ==========================================
// MOSTRAR ANÁLISIS
// ==========================================

function renderAnalysis(
    analysis
) {

    // ======================================
    // CAMBIAR VISTA
    // ======================================

    analysisEmpty.hidden =
        true;


    analysisLoading.hidden =
        true;


    analysisResult.hidden =
        false;


    // ======================================
    // DESCRIPCIÓN
    // ======================================

    descriptionResult.textContent =
        analysis.descripcion ||
        "No se generó una descripción.";


    // ======================================
    // PERSONAS
    // ======================================

    renderPeople(
        analysis.personas
    );


    // ======================================
    // OBJETOS
    // ======================================

    renderObjects(
        analysis.objetos
    );


    // ======================================
    // TEXTO
    // ======================================

    renderVisibleText(
        analysis.texto_visible
    );

}


// ==========================================
// MOSTRAR PERSONAS
// ==========================================

function renderPeople(
    people
) {

    peopleResult.innerHTML =
        "";


    if (
        !Array.isArray(
            people
        )
        ||
        people.length === 0
    ) {

        addEmptyResult(
            peopleResult,
            "No se detectaron personas."
        );


        return;

    }


    people.forEach(
        (
            person,
            index
        ) => {

            const card =
                document.createElement(
                    "div"
                );


            card.className =
                "result-card";


            // ==================================
            // TÍTULO
            // ==================================

            const title =
                document.createElement(
                    "strong"
                );


            title.textContent =
                `Persona ${index + 1}`;


            // ==================================
            // DESCRIPCIÓN
            // ==================================

            const description =
                document.createElement(
                    "p"
                );


            description.textContent =
                person.descripcion ||
                "Sin descripción.";


            // ==================================
            // UBICACIÓN
            // ==================================

            const location =
                document.createElement(
                    "span"
                );


            location.textContent =
                "Ubicación: " +
                (
                    person.ubicacion ||
                    "No determinada"
                );


            // ==================================
            // ACTIVIDAD
            // ==================================

            const activity =
                document.createElement(
                    "span"
                );


            activity.textContent =
                "Actividad: " +
                (
                    person.actividad ||
                    "No determinada"
                );


            // ==================================
            // AGREGAR
            // ==================================

            card.appendChild(
                title
            );


            card.appendChild(
                description
            );


            card.appendChild(
                location
            );


            card.appendChild(
                activity
            );


            peopleResult.appendChild(
                card
            );

        }
    );

}


// ==========================================
// MOSTRAR OBJETOS
// ==========================================

function renderObjects(
    objects
) {

    objectsResult.innerHTML =
        "";


    if (
        !Array.isArray(
            objects
        )
        ||
        objects.length === 0
    ) {

        addEmptyResult(
            objectsResult,
            "No se identificaron objetos."
        );


        return;

    }


    objects.forEach(
        (object) => {

            const card =
                document.createElement(
                    "div"
                );


            card.className =
                "result-card";


            // ==================================
            // NOMBRE
            // ==================================

            const title =
                document.createElement(
                    "strong"
                );


            title.textContent =
                object.nombre ||
                "Objeto";


            // ==================================
            // CANTIDAD
            // ==================================

            const amount =
                document.createElement(
                    "p"
                );


            amount.textContent =
                "Cantidad aproximada: " +
                (
                    object.cantidad ??
                    "No determinada"
                );


            // ==================================
            // UBICACIÓN
            // ==================================

            const location =
                document.createElement(
                    "span"
                );


            location.textContent =
                "Ubicación: " +
                (
                    object.ubicacion ||
                    "No determinada"
                );


            // ==================================
            // AGREGAR
            // ==================================

            card.appendChild(
                title
            );


            card.appendChild(
                amount
            );


            card.appendChild(
                location
            );


            objectsResult.appendChild(
                card
            );

        }
    );

}


// ==========================================
// MOSTRAR TEXTO VISIBLE
// ==========================================

function renderVisibleText(
    texts
) {

    textResult.innerHTML =
        "";


    if (
        !Array.isArray(
            texts
        )
        ||
        texts.length === 0
    ) {

        addEmptyResult(
            textResult,
            "No se detectó texto legible."
        );


        return;

    }


    texts.forEach(
        (text) => {

            const card =
                document.createElement(
                    "div"
                );


            card.className =
                "text-card";


            card.textContent =
                text;


            textResult.appendChild(
                card
            );

        }
    );

}


// ==========================================
// RESULTADO VACÍO
// ==========================================

function addEmptyResult(
    container,
    message
) {

    const element =
        document.createElement(
            "p"
        );


    element.className =
        "empty-result";


    element.textContent =
        message;


    container.appendChild(
        element
    );

}


// ==========================================
// ESTADO DE CARGA
// ==========================================

function setLoading(
    loading
) {

    messageInput.disabled =
        loading;


    imageInput.disabled =
        loading;


    sendButton.disabled =
        loading;


    newChatButton.disabled =
        loading;


    if (loading) {

        analysisEmpty.hidden =
            true;


        analysisResult.hidden =
            true;


        analysisLoading.hidden =
            false;


        sendButton.textContent =
            "Analizando...";

    }

    else {

        analysisLoading.hidden =
            true;


        sendButton.textContent =
            "Analizar imagen";

    }

}


// ==========================================
// REINICIAR ANÁLISIS
// ==========================================

function resetAnalysis() {

    analysisResult.hidden =
        true;


    analysisLoading.hidden =
        true;


    analysisEmpty.hidden =
        false;


    descriptionResult.textContent =
        "";


    peopleResult.innerHTML =
        "";


    objectsResult.innerHTML =
        "";


    textResult.innerHTML =
        "";

}


// ==========================================
// NUEVA IMAGEN
// ==========================================

newChatButton.addEventListener(
    "click",
    () => {

        // ==================================
        // BORRAR IMAGEN
        // ==================================

        currentImage =
            null;


        imageInput.value =
            "";


        previewImage.src =
            "";


        previewImage.hidden =
            true;


        // ==================================
        // RESTAURAR PLACEHOLDER
        // ==================================

        restorePreviewPlaceholder();


        // ==================================
        // ARCHIVO
        // ==================================

        fileInfo.hidden =
            true;


        fileName.textContent =
            "";


        fileSize.textContent =
            "";


        // ==================================
        // PREGUNTA
        // ==================================

        messageInput.value =
            "";


        // ==================================
        // RESULTADOS
        // ==================================

        resetAnalysis();


        // ==================================
        // ERROR
        // ==================================

        hideError();

    }
);


// ==========================================
// RESTAURAR PREVIEW
// ==========================================

function restorePreviewPlaceholder() {

    previewPlaceholder.innerHTML = `
        <div class="preview-icon">
            🖼️
        </div>

        <p>
            Aquí aparecerá la imagen
        </p>

        <span>
            Formatos permitidos:
            JPG, PNG y WEBP
        </span>
    `;


    previewPlaceholder.hidden =
        false;

}


// ==========================================
// MOSTRAR ERROR
// ==========================================

function showError(
    message
) {

    errorMessage.textContent =
        message;


    errorMessage.hidden =
        false;

}


// ==========================================
// OCULTAR ERROR
// ==========================================

function hideError() {

    errorMessage.textContent =
        "";


    errorMessage.hidden =
        true;

}