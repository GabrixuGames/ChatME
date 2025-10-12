import { Button } from "@/components/ui/button";
import { Sun, Moon } from "lucide-react";
import { cn } from "@/lib/utils";
import { useDarkMode } from "../hooks/useDarkMode.tsx";

export function DarkModeToggle({ className }: { className?: string }) {
  const darkMode = useDarkMode();
  return (
    <Button
      variant="ghost"
      className={cn(
        "flex items-center gap-2 px-3 py-2 rounded-full border border-border transition",
        darkMode.dark
          ? "bg-zinc-900 text-purple-200 hover:bg-zinc-800 border-zinc-700"
          : "bg-white text-purple-700 hover:bg-purple-50 border-purple-200 shadow",
        className
      )}
      onClick={darkMode.toggle}
      aria-label="Toggle dark mode"
    >
      {darkMode.dark ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
      <span className={darkMode.dark ? "text-purple-200 font-medium" : "text-purple-700 font-medium"}>
        {darkMode.dark ? "Modo claro" : "Modo oscuro"}
      </span>
    </Button>
  );
}
