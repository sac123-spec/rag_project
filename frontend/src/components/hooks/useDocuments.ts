import { useState } from "react";

interface DocumentsListResponse {
  documents: string[];
}

export function useDocuments(apiBase: string = "http://localhost:8000") {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function listDocuments(): Promise<string[]> {
    try {
      setLoading(true);
      setError(null);

      const res = await fetch(`${apiBase}/documents`);
      const json: DocumentsListResponse = await res.json();

      return json.documents;
    } catch (err) {
      setError("Failed to load documents.");
      return [];
    } finally {
      setLoading(false);
    }
  }

  async function uploadDocuments(files: FileList): Promise<string[]> {
    const formData = new FormData();
    Array.from(files).forEach((file) => formData.append("files", file));

    try {
      setLoading(true);
      setError(null);

      const res = await fetch(`${apiBase}/documents/upload`, {
        method: "POST",
        body: formData
      });

      const json: DocumentsListResponse = await res.json();
      return json.documents;
    } catch (err) {
      setError("Failed to upload documents.");
      return [];
    } finally {
      setLoading(false);
    }
  }

  async function deleteDocument(filename: string): Promise<string[]> {
    try {
      setLoading(true);
      setError(null);

      const res = await fetch(`${apiBase}/documents/${filename}`, {
        method: "DELETE"
      });

      const json: DocumentsListResponse = await res.json();
      return json.documents;
    } catch (err) {
      setError("Failed to delete document.");
      return [];
    } finally {
      setLoading(false);
    }
  }

  async function reindex(): Promise<number> {
    try {
      setLoading(true);
      setError(null);

      const res = await fetch(`${apiBase}/documents/reindex`, {
        method: "POST"
      });

      const data = await res.json();
      return data.indexed_chunks || 0;
    } catch (err) {
      setError("Failed to reindex documents.");
      return 0;
    } finally {
      setLoading(false);
    }
  }

  return {
    loading,
    error,
    listDocuments,
    uploadDocuments,
    deleteDocument,
    reindex
  };
}
