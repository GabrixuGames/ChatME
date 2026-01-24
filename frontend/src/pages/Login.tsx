import { useState } from "react";
import BubbleBackground from "@/components/BubbleBackground";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import LoginForm from "@/components/LoginForm";

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
      setError("");
      const userData = await login(username, password);
      navigate(`/chat/${userData.username}`);
    } catch (err) {
      setError("Credenciales incorrectas. Por favor verifica tus datos.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-purple-100 to-purple-300 relative overflow-hidden">
      <BubbleBackground />
      <LoginForm onSubmit={handleLogin} error={error} isLoading={isLoading} />
    </div>
  );
}
