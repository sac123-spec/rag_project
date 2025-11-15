import React, { useEffect, useState } from "react";
import { Button } from "@/components/ui/Button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { formatBytes } from "@/lib/utils";
import { FileText, Upload, Trash2, RefreshCw } from "lucide-react";

const API_BASE = "http://localhost:8000";

interface DocumentListResponse {
  documents: string[];
}

const DocumentsPage: React.FC = () => {
  const [docs, setDocs] = useState<string[]>([]);
  const [files, setFiles] = useState<FileList | null>(null);
  const [uploading, setUploading] = useState(false);
  const [reindexing, setReindexing] = useState(false);

  const loadDocs = async () => {
    const res = await fetch(`${API_BASE}/documents`);
    const data: DocumentListResponse = await res.json();
    setDocs(data.documents);
  };

  useEffect(() => {
    loadDocs();
  }, []);

  const uploadFiles = async () => {
    if (!files || files.length === 0) return;

    const formData = new FormData();
    for (const f of Array.from(files)) {
      formData.append("files", f);
    }

    setUploading(true);
    const res = await fetch(`${API_BASE}/documents/upload`, {
      method: "POST",
      body: formData
    });

    const data = await res.json();
    setDocs(data.documents);
    setUploading(false);
    setFiles(null);
  };

  const deleteDoc = async (filename: string) => {
    const res = await fetch(`${API_BASE}/documents/${filename}`, {
      method: "DELETE"
    });

    const data = await res.json();
    setDocs(data.documents);
  };

  const reindex = async () => {
    setReindexing(true);
    await fetch(`${API_BASE}/documents/reindex`, { method: "POST" });
    setReindexing(false);
  };

  return (
    <div className="max-w-3xl space-y-6">

      <Card>
        <CardHeader>
          <CardTitle>Upload PDF Documents</CardTitle>
        </CardHeader>

        <CardContent className="space-y-4">
          <Input
            type="file"
            accept="application/pdf"
            multiple
            onChange={(e) => setFiles(e.target.files)}
          />

          <Button isLoading={uploading} onClick={uploadFiles}>
            <Upload className="h-4 w-4 mr-2" />
            Upload PDFs
          </Button>

          {files && (
            <div className="text-sm text-muted-foreground">
              {Array.from(files).map((f) => (
                <div key={f.name}>
                  {f.name} — {formatBytes(f.size)}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Stored Documents</CardTitle>
        </CardHeader>

        <CardContent>
          {docs.length === 0 ? (
            <p className="text-sm text-muted-foreground">No documents uploaded yet.</p>
          ) : (
            <ul className="space-y-2">
              {docs.map((d) => (
                <li
                  key={d}
                  className="flex items-center justify-between bg-muted p-3 rounded-xl"
                >
                  <div className="flex items-center gap-2">
                    <FileText className="h-5 w-5 text-primary" />
                    <span>{d}</span>
                  </div>

                  <button
                    className="text-destructive hover:text-destructive/80"
                    onClick={() => deleteDoc(d)}
                  >
                    <Trash2 className="h-5 w-5" />
                  </button>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>

      <Button onClick={reindex} isLoading={reindexing} className="w-full">
        <RefreshCw className="h-4 w-4 mr-2" />
        Reindex All Documents
      </Button>
    </div>
  );
};

export default DocumentsPage;
