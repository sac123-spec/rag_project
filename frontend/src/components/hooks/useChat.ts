import { useState } from "react";

interface ChatResponse {
  answer: string;
  sources: Array<{
    id: string;
    source: string;
    page?: number;
    chunk_index?: number;
    score?: number;
  }>;
}

export function useChat(apiBase: string = "http://localhost:8000") {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function sendQuery(query: string, topK: number = 5): Promise<ChatResponse | null> {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${apiBase}/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, top_k: topK })
      });

      if (!response.ok) {
        setError("Query failed.");
        return null;
      }

      const json: ChatResponse = await response.json();
      return json;
    } catch (err) {
      setError("Failed to reach server.");
      return null;
    } finally {
      setLoading(false);
    }
  }

  return {
    loading,
    error,
    sendQuery
  };
}
