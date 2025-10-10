import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import LoginForm from "@/components/LoginForm"; // Asegúrate de importar LoginForm correctamente

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleLogin = async (username: string, password: string) => {
    if (!username || !password) {
      setError("Por favor ingresa tanto usuario como contraseña.");
      return;
    }

    try {
      setIsLoading(true);
      setError(""); // Limpiar errores previos
      const userData = await login(username, password);
      navigate(`/chat/${userData.username}`); // Redirige a la página de chat usando el nombre de usuario
    } catch (err) {
      setError("Credenciales incorrectas. Por favor verifica tus datos.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <h1>Bienvenido a ChatME!</h1>
      <LoginForm onSubmit={handleLogin} error={error} isLoading={isLoading} />
    </div>
  );
}
