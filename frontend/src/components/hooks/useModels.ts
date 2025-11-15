import { useState } from "react";

interface TrainRerankerRequest {
  samples: Array<{
    query: string;
    positive_passages: string[];
    negative_passages: string[];
  }>;
  num_epochs: number;
  batch_size: number;
}

interface TrainRerankerResponse {
  status: string;
  model_path: string;
}

export function useModels(apiBase: string = "http://localhost:8000") {
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function trainReranker(request: TrainRerankerRequest): Promise<TrainRerankerResponse | null> {
    try {
      setLoading(true);
      setError(null);
      setStatus("Training reranker model…");

      const res = await fetch(`${apiBase}/train-reranker`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(request)
      });

      const json: TrainRerankerResponse | { detail: string } = await res.json();

      if (!res.ok) {
        setError((json as any).detail || "Training failed.");
        setStatus(null);
        return null;
      }

      setStatus("Training completed successfully.");
      return json as TrainRerankerResponse;
    } catch (err) {
      setError("Failed to reach the server.");
      return null;
    } finally {
      setLoading(false);
    }
  }

  return {
    loading,
    status,
    error,
    trainReranker
  };
}
