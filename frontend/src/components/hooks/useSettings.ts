import { useEffect, useState } from "react";

export interface AppSettings {
  backendUrl: string;
  openaiKey: string;
  darkMode: boolean;
}

export function useSettings() {
  const [settings, setSettings] = useState<AppSettings>({
    backendUrl: "http://localhost:8000",
    openaiKey: "",
    darkMode: false
  });

  const [saved, setSaved] = useState(false);

  // Load from localStorage on mount
  useEffect(() => {
    const backendUrl = localStorage.getItem("backend_url");
    const openaiKey = localStorage.getItem("openai_key");
    const darkMode = localStorage.getItem("dark_mode") === "true";

    setSettings({
      backendUrl: backendUrl || "http://localhost:8000",
      openaiKey: openaiKey || "",
      darkMode
    });

    if (darkMode) {
      document.documentElement.classList.add("dark");
    }
  }, []);

  const saveSettings = () => {
    localStorage.setItem("backend_url", settings.backendUrl);
    localStorage.setItem("openai_key", settings.openaiKey);
    localStorage.setItem("dark_mode", settings.darkMode ? "true" : "false");

    setSaved(true);
    setTimeout(() => setSaved(false), 1500);
  };

  const toggleDarkMode = () => {
    const newValue = !settings.darkMode;

    setSettings((s) => ({ ...s, darkMode: newValue }));
    localStorage.setItem("dark_mode", newValue ? "true" : "false");

    if (newValue) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  };

  return {
    settings,
    setSettings,
    saveSettings,
    toggleDarkMode,
    saved
  };
}
