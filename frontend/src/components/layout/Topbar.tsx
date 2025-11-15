import React from "react";
import { Menu } from "lucide-react";

export const Topbar: React.FC = () => {
  return (
    <header className="flex h-16 items-center justify-between bg-white shadow-sm px-4 md:px-6">
      <div className="flex items-center gap-3">
        <button className="md:hidden">
          <Menu className="h-6 w-6 text-gray-700" />
        </button>
        <h1 className="text-lg font-semibold text-gray-800">Enterprise RAG</h1>
      </div>

      <div className="flex items-center space-x-3">
        {/* Placeholder for future user menu or notifications */}
      </div>
    </header>
  );
};
