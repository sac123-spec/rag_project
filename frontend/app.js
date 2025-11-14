// ===============================
//  FRONTEND LOGIC FOR RAG SYSTEM
// ===============================

// All endpoints relative to FastAPI root
const API_BASE = "";

// ---------- Utility ----------
function $(id) {
    return document.getElementById(id);
}

function showMessage(target, msg, isError = false) {
    target.innerHTML = msg;
    target.style.color = isError ? "red" : "green";
    target.style.display = "block";
}

// --------------------------------------
// 1. INGEST PDF DOCUMENTS
// --------------------------------------
$("ingestBtn").addEventListener("click", async () => {
    const ingestStatus = $("ingestStatus");
    showMessage(ingestStatus, "Starting ingestion...");

    try {
        const response = await fetch(`${API_BASE}/ingest`, {
            method: "POST"
        });

        const data = await response.json();
        showMessage(
            ingestStatus,
            `Ingestion complete. Processed: ${data.docs} docs, ${data.chunks} chunks.`
        );
    } catch (err) {
        showMessage(ingestStatus, "Ingestion failed: " + err.message, true);
    }
});


// --------------------------------------
// 2. ASK QUESTION → FASTAPI → LLM ANSWER
// --------------------------------------
$("askBtn").addEventListener("click", async () => {
    const query = $("userQuery").value.trim();
    const answerBox = $("answerBox");

    if (!query) {
        showMessage(answerBox, "Please enter a question.", true);
        return;
    }

    showMessage(answerBox, "Thinking...");

    try {
        const response = await fetch(`${API_BASE}/query`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ query })
        });

        const data = await response.json();

        answerBox.innerHTML = `
            <h3>Answer:</h3>
            <p>${data.answer}</p>
            <h4>Context Used:</h4>
            <pre>${data.context}</pre>
        `;
    } catch (err) {
        showMessage(answerBox, "Query failed: " + err.message, true);
    }
});


// --------------------------------------
// 3. TRAIN RERANKER — NEW UI BUTTON
// --------------------------------------
$("trainBtn").addEventListener("click", async () => {
    const trainStatus = $("trainStatus");

    showMessage(trainStatus, "Training started... please wait.");

    try {
        const response = await fetch(`${API_BASE}/train/reranker`, {
            method: "POST"
        });

        const data = await response.json();

        // Display final training status
        trainStatus.innerHTML = `
            <h3>Training Complete 🎉</h3>
            <p><strong>Message:</strong> ${data.message}</p>
            <p><strong>Saved Model Path:</strong> ${data.model_path}</p>
        `;
        trainStatus.style.color = "green";
    } catch (err) {
        showMessage(trainStatus, "Training failed: " + err.message, true);
    }
});


// --------------------------------------
// 4. Upload PDFs via UI (optional)
// --------------------------------------
$("uploadBtn")?.addEventListener("click", async () => {
    const fileInput = $("pdfUpload");
    const uploadStatus = $("uploadStatus");

    if (!fileInput.files.length) {
        showMessage(uploadStatus, "Please select a PDF.", true);
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    showMessage(uploadStatus, "Uploading...");

    try {
        const response = await fetch(`${API_BASE}/upload/pdf`, {
            method: "POST",
            body: formData
        });

        const data = await response.json();
        showMessage(uploadStatus, `Uploaded: ${data.filename}`);
    } catch (err) {
        showMessage(uploadStatus, "Upload failed: " + err.message, true);
    }
});
