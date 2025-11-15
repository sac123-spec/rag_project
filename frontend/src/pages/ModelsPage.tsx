import React, { useState } from "react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Textarea } from "@/components/ui/Textarea";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent
} from "@/components/ui/Card";
import { Brain } from "lucide-react";

const ModelsPage: React.FC = () => {
  const [query, setQuery] = useState("");
  const [positive, setPositive] = useState("");
  const [negative, setNegative] = useState("");
  const [epochs, setEpochs] = useState(1);
  const [batch, setBatch] = useState(8);
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const trainModel = async () => {
    const openaiKey = localStorage.getItem("openai_key") || "";
    const backendUrl = localStorage.getItem("backend_url") || "http://localhost:8000";

    const payload = {
      samples: [
        {
          query,
          positive_passages: positive.split("\n").filter(Boolean),
          negative_passages: negative.split("\n").filter(Boolean)
        }
      ],
      num_epochs: epochs,
      batch_size: batch,
      openai_api_key: openaiKey
    };

    setLoading(true);
    setStatus("Training model…");

    const res = await fetch(`${backendUrl}/train-reranker`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const json = await res.json();
    if (res.ok) setStatus(`Model trained: ${json.model_path}`);
    else setStatus(`Error: ${json.detail}`);

    setLoading(false);
  };

  return (
    <div className="max-w-3xl space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Train Reranker Model</CardTitle>
        </CardHeader>

        <CardContent className="space-y-4">
          <Input
            placeholder="Query text…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />

          <Textarea
            placeholder="Positive passages (one per line)"
            value={positive}
            onChange={(e) => setPositive(e.target.value)}
          />

          <Textarea
            placeholder="Negative passages (one per line)"
            value={negative}
            onChange={(e) => setNegative(e.target.value)}
          />

          <div className="grid grid-cols-2 gap-4">
            <Input
              type="number"
              value={epochs}
              onChange={(e) => setEpochs(Number(e.target.value))}
              placeholder="Epochs"
            />
            <Input
              type="number"
              value={batch}
              onChange={(e) => setBatch(Number(e.target.value))}
              placeholder="Batch Size"
            />
          </div>

          <Button className="w-full" onClick={trainModel} isLoading={loading}>
            <Brain className="h-4 w-4 mr-2" />
            Train Model
          </Button>

          {status && <p className="text-sm text-muted-foreground">{status}</p>}
        </CardContent>
      </Card>
    </div>
  );
};

export default ModelsPage;
