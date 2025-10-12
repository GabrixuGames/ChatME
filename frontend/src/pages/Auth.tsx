import { useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { useNavigate } from "react-router-dom";
import BubbleBackground from "@/components/BubbleBackground";
import { DarkModeToggle } from "@/components/DarkModeToggle";
import LoginForm from "@/components/LoginForm";
import RegisterForm from "../components/RegisterForm";

export default function AuthPage() {
  const { setUser, setToken } = useAuth();
  const [flipped, setFlipped] = useState<"none"|"login"|"register">("none");
  const [loginError, setLoginError] = useState("");
  const [loginLoading, setLoginLoading] = useState(false);
  const [registerError, setRegisterError] = useState("");
  const [registerLoading, setRegisterLoading] = useState(false);
  const navigate = useNavigate();

  return (
  <div className="min-h-screen flex flex-col items-center justify-center bg-background relative overflow-hidden px-2 sm:px-0">
    <div className="absolute top-4 right-4 z-30">
      <DarkModeToggle />
    </div>
      <BubbleBackground />
  <div className="flex flex-col items-center w-full max-w-md z-10 sm:mt-0 mt-4">
  <div className="perspective w-full">
          <div
            className="relative w-full max-w-md mx-auto"
            style={{ minHeight: "340px" }}
          >
            {/* Front face */}
            <div
              className={`absolute inset-0 flex flex-col justify-center items-center bg-white/80 dark:bg-zinc-900/80 shadow-2xl rounded-2xl p-4 sm:p-8 backdrop-blur-md transition-transform duration-700 ${flipped === "none" ? "z-20" : "z-10"}`}
              style={{
                backfaceVisibility: "hidden",
                transform: flipped === "none" ? "rotateY(0deg)" : "rotateY(180deg)"
              }}
            >
              <img src="/logo192.png" alt="ChatME! Logo" className="w-16 h-16 sm:w-20 sm:h-20 mb-4 drop-shadow-lg animate-bounce" />
              <h1 className="text-2xl sm:text-4xl font-extrabold mb-2 tracking-tight text-center">
                <span className="text-foreground">Bienvenido a </span>
                <span className="text-purple-700 dark:text-purple-300">ChatME<span>!</span></span>
              </h1>
              <p className="text-muted-foreground mb-6 text-center text-base sm:text-lg">Conéctate, chatea y haz nuevos amigos en una plataforma moderna, divertida y segura.</p>
              <div className="flex flex-col sm:flex-row gap-2 sm:gap-4 w-full mb-4">
                <button
                  className="flex-1 py-3 px-4 rounded-lg bg-purple-600 text-white dark:bg-purple-700 dark:text-purple-100 font-semibold shadow-lg hover:bg-purple-700 hover:scale-105 transition-all duration-150 text-base sm:text-lg"
                  onClick={() => setFlipped("login")}
                >
                  Iniciar sesión
                </button>
                <button
                  className="flex-1 py-3 px-4 rounded-lg bg-white text-purple-600 dark:bg-zinc-900 dark:text-purple-300 font-semibold border border-purple-600 dark:border-purple-300 shadow-lg hover:bg-purple-50 dark:hover:bg-zinc-800 hover:scale-105 transition-all duration-150 text-base sm:text-lg"
                  onClick={() => setFlipped("register")}
                >
                  Registrarse
                </button>
              </div>
            </div>
            {/* Back face */}
            <div
              className={`absolute inset-0 flex flex-col justify-center items-center bg-white/80 dark:bg-zinc-900/80 shadow-2xl rounded-2xl p-8 backdrop-blur-md transition-transform duration-700 ${flipped !== "none" ? "z-20" : "z-10"}`}
              style={{
                backfaceVisibility: "hidden",
                transform: flipped !== "none" ? "rotateY(0deg)" : "rotateY(180deg)"
              }}
            >
              {flipped === "login" && (
                <>
                  <LoginForm
                    onSubmit={async (username, password) => {
                      setLoginLoading(true);
                      setLoginError("");
                      try {
                        const res = await fetch("/procesar_login", {
                          method: "POST",
                          headers: { "Content-Type": "application/json" },
                          body: JSON.stringify({ username, password })
                        });
                        const data = await res.json();
                        if (res.ok && data.token) {
                          sessionStorage.setItem("jwt_token", data.token);
                          sessionStorage.setItem("username", data.username);
                          setUser(data.username);
                          setToken(data.token);
                          navigate(`/chat/${data.username}`);
                        } else {
                          setLoginError(data.error || "Error de login");
                        }
                      } catch (e) {
                        setLoginError("Error de conexión");
                      } finally {
                        setLoginLoading(false);
                      }
                    }}
                    error={loginError}
                    isLoading={loginLoading}
                    onBack={() => setFlipped("none")}
                  />
                </>
              )}
              {flipped === "register" && (
                <>
                  <RegisterForm
                    onSubmit={async (username, email, password) => {
                      setRegisterLoading(true);
                      setRegisterError("");
                      try {
                        const res = await fetch("/register", {
                          method: "POST",
                          headers: { "Content-Type": "application/json" },
                          body: JSON.stringify({ username, email, password })
                        });
                        const data = await res.json();
                        if (res.ok && data.user_id) {
                          // Registro exitoso, loguear automáticamente
                          const loginRes = await fetch("/procesar_login", {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({ username, password })
                          });
                          const loginData = await loginRes.json();
                          if (loginRes.ok && loginData.token) {
                            sessionStorage.setItem("jwt_token", loginData.token);
                            sessionStorage.setItem("username", loginData.username);
                            setUser(loginData.username);
                            setToken(loginData.token);
                            navigate(`/chat/${loginData.username}`);
                          } else {
                            setRegisterError(loginData.error || "Error al iniciar sesión tras registro");
                          }
                        } else {
                          setRegisterError(data.error || "Error de registro");
                        }
                      } catch (e) {
                        setRegisterError("Error de conexión");
                      } finally {
                        setRegisterLoading(false);
                      }
                    }}
                    error={registerError}
                    isLoading={registerLoading}
                    onBack={() => setFlipped("none")}
                  />
                </>
              )}
            </div>
          </div>
        </div>
        <div className="mt-8 text-purple-700 text-sm text-center z-10">
          <span>ChatME!</span> &copy; 2025 &mdash; Tu comunidad de chat favorita
        </div>
      </div>
    </div>
  );
}
