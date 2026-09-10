// ==========================================
// URL DEL BACKEND
// ==========================================

/*
    CAMBIA ESTA URL cuando Vercel te dé
    la URL definitiva del proyecto 1.3.
*/

const API_URL =
    "https://1-3-app-web-para-identificacion-de.vercel.app/api/chat";


// ==========================================
// CONFIGURACIÓN
// ==========================================

const MAX_IMAGE_DIMENSION =
    1280;


const MAX_DATA_URL_LENGTH =
    2400000;


// ==========================================
// ELEMENTOS HTML
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


const imageUrlInput =
    document.getElementById(
        "imageUrlInput"
    );


const loadUrlButton =
    document.getElementById(
        "loadUrlButton"
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


const patternsResult =
    document.getElementById(
        "patternsResult"
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
// FUENTE ACTUAL DE LA IMAGEN
// ==========================================

let currentImage =
    null;


let currentImageUrl =
    null;


// ==========================================
// FORMATEAR TAMAÑO
// ==========================================

function formatFileSize(
    bytes
) {

    if (
        bytes < 1024
    ) {

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
// LEER ARCHIVO
// ==========================================

function loadImageFile(
    file
) {

    return new Promise(
        (
            resolve,
            reject
        ) => {

            const reader =
                new FileReader();


            reader.onload =
                () => {

                    const image =
                        new Image();


                    image.onload =
                        () => {

                            resolve(
                                image
                            );

                        };


                    image.onerror =
                        () => {

                            reject(
                                new Error(
                                    "No fue posible cargar la imagen."
                                )
                            );

                        };


                    image.src =
                        reader.result;

                };


            reader.onerror =
                () => {

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

async function compressImage(
    file
) {

    const image =
        await loadImageFile(
            file
        );


    let scale =
        Math.min(
            1,

            MAX_IMAGE_DIMENSION /
            Math.max(
                image.width,
                image.height
            )
        );


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
                "El navegador no pudo procesar la imagen."
            );

        }


        // Fondo blanco para PNG transparente

        context.fillStyle =
            "#ffffff";


        context.fillRect(
            0,
            0,
            width,
            height
        );


        context.drawImage(
            image,
            0,
            0,
            width,
            height
        );


        const quality =
            Math.max(
                0.50,
                0.86 -
                (
                    attempt *
                    0.07
                )
            );


        const dataURL =
            canvas.toDataURL(
                "image/jpeg",
                quality
            );


        if (
            dataURL.length <=
            MAX_DATA_URL_LENGTH
        ) {

            return dataURL;

        }


        scale *=
            0.78;

    }


    throw new Error(
        "La imagen es demasiado grande para ser procesada."
    );

}


// ==========================================
// VALIDAR URL
// ==========================================

function isValidImageUrl(
    value
) {

    try {

        const url =
            new URL(
                value
            );


        return (
            url.protocol ===
            "https:"
        );

    }

    catch {

        return false;

    }

}


// ==========================================
// SELECCIONAR ARCHIVO LOCAL
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


        // Desactivar URL

        currentImageUrl =
            null;


        imageUrlInput.value =
            "";


        currentImage =
            null;


        // Estado preparando

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


        resetAnalysis();


        try {

            currentImage =
                await compressImage(
                    file
                );


            previewImage.onerror =
                null;


            previewImage.onload =
                null;


            previewImage.src =
                currentImage;


            previewImage.hidden =
                false;


            previewPlaceholder.hidden =
                true;


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
// USAR URL
// ==========================================

loadUrlButton.addEventListener(
    "click",

    () => {

        loadImageFromUrl();

    }
);


// ==========================================
// ENTER EN EL CAMPO URL
// ==========================================

imageUrlInput.addEventListener(
    "keydown",

    (event) => {

        if (
            event.key ===
            "Enter"
        ) {

            event.preventDefault();


            loadImageFromUrl();

        }

    }
);


// ==========================================
// CARGAR IMAGEN DESDE URL
// ==========================================

function loadImageFromUrl() {

    hideError();


    const url =
        imageUrlInput.value.trim();


    if (!url) {

        showError(
            "Escribe la URL de una imagen."
        );


        return;

    }


    if (
        !isValidImageUrl(
            url
        )
    ) {

        showError(
            "La dirección debe ser una URL HTTPS válida."
        );


        return;

    }


    // Desactivar archivo local

    currentImage =
        null;


    imageInput.value =
        "";


    currentImageUrl =
        url;


    resetAnalysis();


    // Estado cargando preview

    previewPlaceholder.hidden =
        false;


    previewPlaceholder.innerHTML = `
        <div class="preview-icon">
            ⏳
        </div>

        <p>
            Cargando imagen...
        </p>

        <span>
            Obteniendo imagen desde Internet
        </span>
    `;


    previewImage.hidden =
        true;


    fileInfo.hidden =
        true;


    // ======================================
    // PREVIEW
    // ======================================

    previewImage.onload =
        () => {

            previewImage.hidden =
                false;


            previewPlaceholder.hidden =
                true;


            fileName.textContent =
                "Imagen desde Internet";


            fileSize.textContent =
                "URL externa";


            fileInfo.hidden =
                false;


            hideError();

        };


    previewImage.onerror =
        () => {

            previewImage.hidden =
                true;


            restorePreviewPlaceholder();


            showError(
                "No fue posible mostrar la imagen. Verifica que la URL sea pública y apunte directamente a una imagen."
            );

        };


    previewImage.src =
        url;

}


// ==========================================
// ENVIAR A LA API
// ==========================================

form.addEventListener(
    "submit",

    async (event) => {

        event.preventDefault();


        hideError();


        // ==================================
        // VALIDAR FUENTE
        // ==================================

        if (
            !currentImage &&
            !currentImageUrl
        ) {

            showError(
                "Selecciona una imagen o proporciona una URL."
            );


            return;

        }


        // ==================================
        // MENSAJE
        // ==================================

        let message =
            messageInput.value.trim();


        if (!message) {

            message =
                "Analiza esta imagen e identifica los patrones visuales, objetos, personas y texto visible.";

        }


        if (
            message.length >
            500
        ) {

            showError(
                "La consulta no puede superar los 500 caracteres."
            );


            return;

        }


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
                                        currentImage,

                                    image_url:
                                        currentImageUrl

                                }
                            )

                    }
                );


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


            if (!response.ok) {

                throw new Error(
                    data.error ||
                    "Ocurrió un error al analizar la imagen."
                );

            }


            if (!data.analysis) {

                throw new Error(
                    "No se recibieron resultados del análisis."
                );

            }


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

    analysisEmpty.hidden =
        true;


    analysisLoading.hidden =
        true;


    analysisResult.hidden =
        false;


    descriptionResult.textContent =
        analysis.descripcion ||
        "No se generó una descripción.";


    renderPatterns(
        analysis.patrones
    );


    renderPeople(
        analysis.personas
    );


    renderObjects(
        analysis.objetos
    );


    renderVisibleText(
        analysis.texto_visible
    );

}


// ==========================================
// PATRONES
// ==========================================

function renderPatterns(
    patterns
) {

    patternsResult.innerHTML =
        "";


    if (
        !Array.isArray(
            patterns
        )
        ||
        patterns.length === 0
    ) {

        addEmptyResult(
            patternsResult,
            "No se identificaron patrones visuales relevantes."
        );


        return;

    }


    patterns.forEach(
        (pattern) => {

            const card =
                document.createElement(
                    "div"
                );


            card.className =
                "pattern-card";


            card.textContent =
                pattern;


            patternsResult.appendChild(
                card
            );

        }
    );

}


// ==========================================
// PERSONAS
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


            const title =
                document.createElement(
                    "strong"
                );


            title.textContent =
                `Persona ${index + 1}`;


            const description =
                document.createElement(
                    "p"
                );


            description.textContent =
                person.descripcion ||
                "Sin descripción.";


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
// OBJETOS
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


            const title =
                document.createElement(
                    "strong"
                );


            title.textContent =
                object.nombre ||
                "Objeto";


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
// TEXTO VISIBLE
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
// CARGANDO
// ==========================================

function setLoading(
    loading
) {

    messageInput.disabled =
        loading;


    imageInput.disabled =
        loading;


    imageUrlInput.disabled =
        loading;


    loadUrlButton.disabled =
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


    patternsResult.innerHTML =
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

        currentImage =
            null;


        currentImageUrl =
            null;


        imageInput.value =
            "";


        imageUrlInput.value =
            "";


        previewImage.onload =
            null;


        previewImage.onerror =
            null;


        previewImage.src =
            "";


        previewImage.hidden =
            true;


        fileInfo.hidden =
            true;


        fileName.textContent =
            "";


        fileSize.textContent =
            "";


        messageInput.value =
            "";


        restorePreviewPlaceholder();


        resetAnalysis();


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
            Puedes subir JPG, PNG o WEBP
            <br>
            o proporcionar una URL pública
        </span>
    `;


    previewPlaceholder.hidden =
        false;

}


// ==========================================
// ERROR
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