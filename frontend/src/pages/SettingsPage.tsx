import React, { useEffect, useState } from "react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent
} from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";

const SettingsPage: React.FC = () => {
  const [backendUrl, setBackendUrl] = useState("");
  const [openaiKey, setOpenaiKey] = useState("");
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const storedBackend = localStorage.getItem("backend_url");
    const storedKey = localStorage.getItem("openai_key");

    setBackendUrl(storedBackend || "http://localhost:8000");
    setOpenaiKey(storedKey || "");
  }, []);

  const saveSettings = () => {
    localStorage.setItem("backend_url", backendUrl);
    localStorage.setItem("openai_key", openaiKey);

    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const toggleDark = () => {
    document.documentElement.classList.toggle("dark");
  };

  return (
    <div className="max-w-2xl space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>API Configuration</CardTitle>
        </CardHeader>

        <CardContent className="space-y-4">
          <div>
            <label className="text-sm font-medium">Backend URL</label>
            <Input
              placeholder="http://localhost:8000"
              value={backendUrl}
              onChange={(e) => setBackendUrl(e.target.value)}
            />
          </div>

          <div>
            <label className="text-sm font-medium">OpenAI API Key</label>
            <Input
              type="password"
              placeholder="sk-..."
              value={openaiKey}
              onChange={(e) => setOpenaiKey(e.target.value)}
            />
          </div>

          <Button className="w-full" onClick={saveSettings}>
            Save Settings
          </Button>

          {saved && (
            <p className="text-sm text-muted-foreground mt-2">
              Settings saved ✔
            </p>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Appearance</CardTitle>
        </CardHeader>
        <CardContent>
          <Button variant="secondary" onClick={toggleDark}>
            Toggle Dark Mode
          </Button>
        </CardContent>
      </Card>
    </div>
  );
};

export default SettingsPage;
