import React, { useContext, createContext, useEffect, useState } from "react";

export const DarkModeContext = createContext({ dark: false, toggle: () => {} });

export function DarkModeProvider({ children }: { children: React.ReactNode }) {
  // Leer preferencia inicial de localStorage o media query
  const getInitial = () => {
    if (typeof window === "undefined") return false;
    const stored = localStorage.getItem("darkMode");
    if (stored !== null) return stored === "true";
    return window.matchMedia("(prefers-color-scheme: dark)").matches;
  };
  const [dark, setDark] = useState(getInitial);

  useEffect(() => {
    if (dark) {
      document.body.classList.add("dark");
    } else {
      document.body.classList.remove("dark");
    }
    localStorage.setItem("darkMode", dark ? "true" : "false");
  }, [dark]);

  const value = { dark, toggle: () => setDark(d => !d) };
  return <DarkModeContext.Provider value={value}>{children}</DarkModeContext.Provider>;
}

export function useDarkMode() {
  return useContext(DarkModeContext);
}
