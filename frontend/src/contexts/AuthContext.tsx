import { createContext, useContext, useState, useEffect } from "react";
import axios from "axios";
import React from "react";

// Tipo para los datos del usuario
interface UserData {
  username: string;
  token: string;
}

// Tipo del contexto
export type AuthContextType = {
  login: (username: string, password: string) => Promise<UserData>;
  logout: () => void;
  user: string | null;
  token: string | null;
  setUser: React.Dispatch<React.SetStateAction<string | null>>;
  setToken: React.Dispatch<React.SetStateAction<string | null>>;
  isAuthenticated: boolean;
};

// Crear el contexto
const AuthContext = React.createContext<AuthContextType | undefined>(undefined);

// Hook personalizado
// eslint-disable-next-line react-refresh/only-export-components
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within an AuthProvider");
  return context;
};

// Proveedor
export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<string | null>(null);
  const [token, setToken] = useState<string | null>(null);

  // Configurar URL base desde variables de entorno
  const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";

  const login = async (username: string, password: string): Promise<UserData> => {
    const response = await fetch(`${API_URL}/procesar_login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: username, password })
    });

    if (!response.ok) throw new Error("Credenciales incorrectas");

    const data: UserData = await response.json();
    setUser(data.username);
    setToken(data.token);
    sessionStorage.setItem("username", data.username);
    sessionStorage.setItem("jwt_token", data.token);
    return data;
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    sessionStorage.removeItem("username");
    sessionStorage.removeItem("jwt_token");
  };

  const verificarSesion = async () => {
    const storedToken = sessionStorage.getItem("jwt_token");
    const storedUsername = sessionStorage.getItem("username");
    if (storedToken && storedUsername) {
      setToken(storedToken);
      setUser(storedUsername);
    } else {
      setToken(null);
      setUser(null);
    }
  };

  useEffect(() => {
    verificarSesion();
  }, []);

  const isAuthenticated = !!user; // ✅ Lo añadimos aquí

  return (
    <AuthContext.Provider value={{ login, logout, user, token, setUser, setToken, isAuthenticated }}>
      {children}
    </AuthContext.Provider>
  );
};

export type { UserData };
