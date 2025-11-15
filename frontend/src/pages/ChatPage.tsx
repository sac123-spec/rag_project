import React, { useState, useRef } from "react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Card, CardContent } from "@/components/ui/Card";
import { ScrollArea } from "@/components/ui/ScrollArea";
import { MessageSquare } from "lucide-react";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  sources?: any[];
}

const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  const scrollToBottom = () => {
    setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: "smooth" }), 50);
  };

  const sendMessage = async () => {
    if (!query.trim() || loading) return;

    const backendUrl =
      localStorage.getItem("backend_url") || "http://localhost:8000";

    const userMessage: ChatMessage = {
      role: "user",
      content: query,
    };

    // Add user message + placeholder assistant message
    setMessages((prev) => [
      ...prev,
      userMessage,
      { role: "assistant", content: "", sources: [] },
    ]);
    setQuery("");
    setLoading(true);
    scrollToBottom();

    try {
      const response = await fetch(`${backendUrl}/query-stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, top_k: 5 }),
      });

      if (!response.ok || !response.body) {
        const err = await response.text();
        setMessages((prev) => [
          ...prev.slice(0, -1),
          {
            role: "assistant",
            content: `Server error: ${response.status} ${err}`,
          },
        ]);
        setLoading(false);
        return;
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed) continue;

          let evt: any;
          try {
            evt = JSON.parse(trimmed);
          } catch {
            continue;
          }

          if (evt.type === "token") {
            const token: string = evt.content || "";
            if (!token) continue;

            setMessages((prev) => {
              const updated = [...prev];
              const last = updated[updated.length - 1];
              if (!last || last.role !== "assistant") return prev;
              last.content += token;
              return updated;
            });

            scrollToBottom();
          } else if (evt.type === "meta") {
            const sources = evt.sources || [];
            setMessages((prev) => {
              const updated = [...prev];
              const last = updated[updated.length - 1];
              if (!last || last.role !== "assistant") return prev;
              last.sources = sources;
              return updated;
            });
          }
        }
      }

      // Flush any remaining buffered line
      const finalLine = buffer.trim();
      if (finalLine) {
        try {
          const evt = JSON.parse(finalLine);
          if (evt.type === "meta") {
            const sources = evt.sources || [];
            setMessages((prev) => {
              const updated = [...prev];
              const last = updated[updated.length - 1];
              if (!last || last.role !== "assistant") return prev;
              last.sources = sources;
              return updated;
            });
          }
        } catch {
          // ignore
        }
      }
    } catch (error) {
      setMessages((prev) => [
        ...prev.slice(0, -1),
        {
          role: "assistant",
          content: "⚠️ Failed to reach backend.",
        },
      ]);
    } finally {
      setLoading(false);
      scrollToBottom();
    }
  };

  return (
    <div className="flex flex-col h-full">
      <ScrollArea className="flex-1 bg-white p-6 rounded-xl shadow-soft">
        <div className="space-y-6">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex ${
                msg.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <Card
                className={`max-w-lg ${
                  msg.role === "user"
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted"
                }`}
              >
                <CardContent>
                  <p className="whitespace-pre-wrap">{msg.content}</p>

                  {msg.sources && msg.sources.length > 0 && (
                    <div className="mt-3 text-xs text-muted-foreground">
                      <div className="font-semibold mb-1">Sources:</div>
                      <ul className="list-disc ml-4 space-y-1">
                        {msg.sources.map((s: any, i: number) => (
                          <li key={i}>
                            {s.source} — chunk {s.chunk_index}{" "}
                            {typeof s.score === "number" &&
                              `(score ${s.score.toFixed(3)})`}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          ))}
          <div ref={bottomRef} />
        </div>
      </ScrollArea>

      <div className="mt-4 flex gap-3">
        <Input
          placeholder="Ask something…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !loading && sendMessage()}
        />
        <Button onClick={sendMessage} disabled={loading}>
          <MessageSquare className="h-4 w-4 mr-2" />
          {loading ? "Thinking..." : "Ask"}
        </Button>
      </div>
    </div>
  );
};

export default ChatPage;
