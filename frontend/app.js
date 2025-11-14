// Use same origin as the page (works for localhost:8000)
const API_URL = window.location.origin;

let totalQueries = 0;
let logs = [];
let filesToUpload = [];

// ---------- Helpers ----------
function $(id) {
  return document.getElementById(id);
}

function addLogEntry(text) {
  const timestamp = new Date().toLocaleTimeString();
  logs.unshift(`[${timestamp}] ${text}`);
  if (logs.length > 200) logs.pop();
  renderLogs();
}

function renderLogs() {
  const c = $("logs-container");
  c.innerHTML = "";
  if (!logs.length) {
    c.innerHTML = `<span class="text-slate-500">No activity yet.</span>`;
    return;
  }
  logs.forEach((log) => {
    const d = document.createElement("div");
    d.className =
      "border border-slate-800 rounded-lg p-2 text-slate-300 text-xs bg-slate-950/80";
    d.textContent = log;
    c.appendChild(d);
  });
}

// ---------- Health ----------
async function checkHealth() {
  try {
    const res = await fetch(`${API_URL}/health`);
    const data = await res.json();
    if (data.status === "ok") {
      $("status-indicator").textContent = "Online";
      $("status-indicator").className = "ml-1 font-semibold text-emerald-400";
    } else {
      $("status-indicator").textContent = "Issues";
      $("status-indicator").className = "ml-1 font-semibold text-amber-400";
    }
  } catch {
    $("status-indicator").textContent = "Offline";
    $("status-indicator").className = "ml-1 font-semibold text-red-400";
  }
}

// ---------- Upload ----------
function setupUploadArea() {
  const dropzone = $("upload-dropzone");
  const fileInput = $("file-input");

  dropzone.addEventListener("click", () => fileInput.click());

  fileInput.addEventListener("change", (e) => {
    filesToUpload = [...e.target.files];
    $("upload-status").textContent = `${filesToUpload.length} file(s) ready`;
  });

  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("border-brand-500", "shadow", "shadow-brand-500/40");
  });

  dropzone.addEventListener("dragleave", () => {
    dropzone.classList.remove("border-brand-500", "shadow", "shadow-brand-500/40");
  });

  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("border-brand-500", "shadow", "shadow-brand-500/40");
    filesToUpload = [...e.dataTransfer.files].filter(
      (f) => f.type === "application/pdf"
    );
    $("upload-status").textContent = `${filesToUpload.length} file(s) ready`;
  });
}

async function uploadFiles() {
  if (!filesToUpload.length) {
    $("upload-status").innerHTML =
      `<span class="text-amber-400">No files selected.</span>`;
    return;
  }

  $("btn-upload").disabled = true;
  $("btn-upload-label").textContent = "Uploading...";
  $("btn-upload-spinner").classList.remove("hidden");

  const form = new FormData();
  filesToUpload.forEach((f) => form.append("files", f));

  try {
    const res = await fetch(`${API_URL}/upload`, {
      method: "POST",
      body: form,
    });
    const data = await res.json();

    $("upload-status").innerHTML = `
      <span class="text-emerald-400">Uploaded:</span>
      <pre class="text-xs mt-1 whitespace-pre-wrap">${JSON.stringify(
        data.saved,
        null,
        2
      )}</pre>
    `;
    addLogEntry(`Uploaded ${data.saved.length} file(s).`);

    await loadAdminFiles();
  } catch (err) {
    $("upload-status").innerHTML =
      `<span class="text-red-400">Upload failed: ${err.message}</span>`;
    addLogEntry(`Upload failed: ${err.message}`);
  } finally {
    $("btn-upload").disabled = false;
    $("btn-upload-label").textContent = "Upload Files";
    $("btn-upload-spinner").classList.add("hidden");
  }
}

// ---------- Ingestion ----------
async function runIngestion() {
  $("btn-ingest").disabled = true;
  $("btn-ingest-label").textContent = "Ingesting...";
  $("btn-ingest-spinner").classList.remove("hidden");
  $("ingest-status").textContent = "";

  try {
    const res = await fetch(`${API_URL}/ingest`, { method: "POST" });

    if (!res.ok) {
      const txt = await res.text();
      $("ingest-status").innerHTML =
        `<span class="text-red-400">${txt}</span>`;
      addLogEntry(`Ingestion failed: HTTP ${res.status}`);
      return;
    }

    const data = await res.json();
    $("ingest-status").innerHTML = `
      <span class="text-emerald-400">Ingestion complete.</span>
      <div class="mt-1 text-xs">
        ${data.num_raw_docs} docs → ${data.num_chunks} chunks.
      </div>
    `;
    addLogEntry(
      `Ingested ${data.num_raw_docs} docs into ${data.num_chunks} chunks.`
    );
  } catch (err) {
    $("ingest-status").innerHTML =
      `<span class="text-red-400">${err.message}</span>`;
    addLogEntry(`Ingestion error: ${err.message}`);
  } finally {
    $("btn-ingest").disabled = false;
    $("btn-ingest-label").textContent = "Run Ingestion";
    $("btn-ingest-spinner").classList.add("hidden");
  }
}

// ---------- Search / Query ----------
async function runSearch() {
  const question = $("input-query").value.trim();
  if (!question) {
    alert("Please enter a question.");
    return;
  }

  const topK = parseInt($("input-topk").value || "5", 10);
  const useReranker = $("checkbox-reranker").checked;

  const payload = {
    question,
    top_k: topK,
    use_reranker: useReranker,
  };

  $("btn-search").disabled = true;
  $("btn-search-label").textContent = "Searching...";
  $("btn-search-spinner").classList.remove("hidden");

  const start = performance.now();

  try {
    const res = await fetch(`${API_URL}/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const latency = Math.round(performance.now() - start);
    $("stat-last-latency").textContent = `${latency}`;

    if (!res.ok) {
      const txt = await res.text();
      $("answer-box").innerHTML =
        `<div class="text-red-400 text-sm">Error ${res.status}</div>
         <pre class="text-xs mt-1 whitespace-pre-wrap">${txt}</pre>`;
      $("stat-last-status").textContent = "Error";
      $("stat-last-status").className =
        "text-red-400 text-2xl font-semibold";
      addLogEntry(`Query error: HTTP ${res.status}`);
      return;
    }

    const data = await res.json();

    $("answer-box").innerHTML =
      `<div class="whitespace-pre-wrap text-sm">${data.answer}</div>`;

    renderSources(data.sources);

    totalQueries += 1;
    $("stat-total-queries").textContent = String(totalQueries);
    $("stat-last-status").textContent = "OK";
    $("stat-last-status").className =
      "text-emerald-400 text-2xl font-semibold";

    addLogEntry(`Query OK (${latency} ms): ${question}`);
  } catch (err) {
    $("answer-box").innerHTML =
      `<div class="text-red-400 text-sm">${err.message}</div>`;
    $("stat-last-status").textContent = "Error";
    $("stat-last-status").className =
      "text-red-400 text-2xl font-semibold";
    addLogEntry(`Query error: ${err.message}`);
  } finally {
    $("btn-search").disabled = false;
    $("btn-search-label").textContent = "Run Search";
    $("btn-search-spinner").classList.add("hidden");
  }
}

function renderSources(sources) {
  const c = $("sources-container");
  c.innerHTML = "";

  if (!sources || !sources.length) {
    c.innerHTML =
      `<span class="text-slate-500 text-xs">No sources returned.</span>`;
    return;
  }

  sources.forEach((src, idx) => {
    const div = document.createElement("div");
    div.className =
      "border border-slate-800 bg-slate-950/80 p-3 rounded-xl hover:border-brand-500/60 transition";

    const meta =
      src.metadata && src.metadata.source ? src.metadata.source : "Unknown";

    div.innerHTML = `
      <div class="flex justify-between mb-1 text-[11px] text-slate-400">
        <span>Source #${idx + 1}</span>
        <span>${meta}</span>
      </div>
      <div class="text-[11px] whitespace-pre-wrap text-slate-100">${src.content}</div>
    `;
    c.appendChild(div);
  });
}

// ---------- Admin: list, delete, rebuild ----------
async function loadAdminFiles() {
  const container = $("admin-files-container");
  container.innerHTML =
    `<span class="text-slate-500 text-xs">Loading…</span>`;
  $("admin-status").textContent = "";

  try {
    const res = await fetch(`${API_URL}/admin/files`);
    const data = await res.json();

    const files = data.files || [];
    container.innerHTML = "";

    if (!files.length) {
      container.innerHTML =
        `<span class="text-slate-500 text-xs">No PDF files in data/raw.</span>`;
      return;
    }

    files.forEach((f) => {
      const row = document.createElement("div");
      row.className =
        "flex items-center justify-between text-[11px] text-slate-200";

      row.innerHTML = `
        <label class="flex items-center space-x-2">
          <input type="checkbox"
                 class="admin-file-checkbox accent-brand-500"
                 data-filename="${f.name}" />
          <span>${f.name}</span>
        </label>
        <span class="text-slate-500">${Math.round(f.size / 1024)} KB</span>
      `;
      container.appendChild(row);
    });
  } catch (err) {
    container.innerHTML =
      `<span class="text-red-400 text-xs">Failed to load files: ${err.message}</span>`;
  }
}

async function deleteSelectedFiles() {
  const checkboxes = document.querySelectorAll(
    ".admin-file-checkbox:checked"
  );
  const filenames = [...checkboxes].map((cb) =>
    cb.getAttribute("data-filename")
  );

  if (!filenames.length) {
    $("admin-status").innerHTML =
      `<span class="text-amber-400 text-xs">No files selected to delete.</span>`;
    return;
  }

  $("admin-status").innerHTML =
    `<span class="text-slate-300 text-xs">Deleting…</span>`;

  try {
    const res = await fetch(`${API_URL}/admin/delete`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ filenames }),
    });

    const data = await res.json();
    $("admin-status").innerHTML =
      `<span class="text-emerald-400 text-xs">Deleted: ${data.deleted.join(
        ", "
      ) || "none"}; Missing: ${data.missing.join(", ") || "none"}</span>`;
    addLogEntry(`Deleted PDFs: ${data.deleted.join(", ") || "none"}`);

    await loadAdminFiles();
  } catch (err) {
    $("admin-status").innerHTML =
      `<span class="text-red-400 text-xs">Delete failed: ${err.message}</span>`;
    addLogEntry(`Delete error: ${err.message}`);
  }
}

async function rebuildVectorstore() {
  $("admin-status").innerHTML =
    `<span class="text-slate-300 text-xs">Rebuilding vector store…</span>`;
  addLogEntry("Rebuild triggered.");

  try {
    const res = await fetch(`${API_URL}/admin/rebuild`, {
      method: "POST",
    });

    if (!res.ok) {
      const txt = await res.text();
      $("admin-status").innerHTML =
        `<span class="text-red-400 text-xs">Rebuild failed: ${txt}</span>`;
      addLogEntry(`Rebuild failed: HTTP ${res.status}`);
      return;
    }

    const data = await res.json();
    $("admin-status").innerHTML =
      `<span class="text-emerald-400 text-xs">Rebuilt: ${data.num_raw_docs} docs → ${data.num_chunks} chunks.</span>`;
    addLogEntry(
      `Rebuilt vector store: ${data.num_raw_docs} docs, ${data.num_chunks} chunks.`
    );
  } catch (err) {
    $("admin-status").innerHTML =
      `<span class="text-red-400 text-xs">Rebuild error: ${err.message}</span>`;
    addLogEntry(`Rebuild error: ${err.message}`);
  }
}

// ---------- Navigation ----------
function setupNav() {
  $("nav-search").addEventListener("click", () => {
    $("input-query").scrollIntoView({ behavior: "smooth", block: "center" });
    $("input-query").focus();
  });
  $("nav-upload").addEventListener("click", () => {
    $("upload-dropzone").scrollIntoView({
      behavior: "smooth",
      block: "center",
    });
  });
  $("nav-ingest").addEventListener("click", () => {
    $("btn-ingest").scrollIntoView({ behavior: "smooth", block: "center" });
  });
  $("nav-admin").addEventListener("click", () => {
    $("admin-files-container").scrollIntoView({
      behavior: "smooth",
      block: "center",
    });
  });
}

// ---------- Init ----------
document.addEventListener("DOMContentLoaded", () => {
  checkHealth();
  setupUploadArea();
  setupNav();

  $("btn-upload").addEventListener("click", uploadFiles);
  $("btn-ingest").addEventListener("click", runIngestion);
  $("btn-search").addEventListener("click", runSearch);

  $("btn-admin-refresh").addEventListener("click", loadAdminFiles);
  $("btn-admin-delete").addEventListener("click", deleteSelectedFiles);
  $("btn-admin-rebuild").addEventListener("click", rebuildVectorstore);

  $("input-query").addEventListener("keydown", (e) => {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
      runSearch();
    }
  });

  loadAdminFiles();
});
