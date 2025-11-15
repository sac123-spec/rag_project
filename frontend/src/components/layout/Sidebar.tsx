import React from "react";
import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  MessageSquare,
  FileText,
  Settings,
  Brain
} from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  {
    label: "Dashboard",
    href: "/dashboard",
    icon: <LayoutDashboard className="h-5 w-5" />
  },
  {
    label: "Chat",
    href: "/chat",
    icon: <MessageSquare className="h-5 w-5" />
  },
  {
    label: "Documents",
    href: "/documents",
    icon: <FileText className="h-5 w-5" />
  },
  {
    label: "Models",
    href: "/models",
    icon: <Brain className="h-5 w-5" />
  },
  {
    label: "Settings",
    href: "/settings",
    icon: <Settings className="h-5 w-5" />
  }
];

export const Sidebar: React.FC = () => {
  return (
    <aside className="hidden md:flex h-full w-64 flex-col border-r bg-white shadow-sm">
      <div className="p-6 text-xl font-semibold tracking-tight">
        Enterprise RAG
      </div>

      <nav className="flex-1 px-4 space-y-2 mt-2">
        {navItems.map((item) => (
          <NavLink
            key={item.href}
            to={item.href}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 px-3 py-2 rounded-xl text-sm font-medium transition-colors",
                "hover:bg-accent hover:text-accent-foreground",
                isActive ? "bg-accent text-accent-foreground" : "text-muted-foreground"
              )
            }
          >
            {item.icon}
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="p-4 mt-auto text-xs text-muted-foreground">
        © {new Date().getFullYear()} Enterprise RAG
      </div>
    </aside>
  );
};
