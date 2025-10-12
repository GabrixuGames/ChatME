import { useNavigate } from "react-router-dom";
import BubbleBackground from "@/components/BubbleBackground";

export default function Home() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-purple-100 to-purple-300 relative overflow-hidden">
      <BubbleBackground />
  <div className="bg-white/80 shadow-2xl rounded-2xl p-8 flex flex-col items-center w-full max-w-md z-10 backdrop-blur-md">
        <img src="/logo192.png" alt="ChatME! Logo" className="w-20 h-20 mb-4 drop-shadow-lg animate-bounce" />
        <h1 className="text-4xl font-extrabold mb-2 tracking-tight text-center">
          <span className="text-gray-900">Bienvenido a </span>
          <span className="text-purple-700">ChatME<span>!</span></span>
        </h1>
        <style>{`
          h1 span.text-purple-700 span {
            color: #a21caf;
          }
        `}</style>
        <p className="text-gray-600 mb-6 text-center text-lg">Conéctate, chatea y haz nuevos amigos en una plataforma moderna, divertida y segura.</p>
        <div className="flex gap-4 w-full">
          <button
            className="flex-1 py-2 px-4 rounded-lg bg-purple-600 text-white font-semibold shadow-lg hover:bg-purple-700 hover:scale-105 transition-all duration-150"
            onClick={() => navigate("/login")}
          >
            Iniciar sesión
          </button>
          <button
            className="flex-1 py-2 px-4 rounded-lg bg-white text-purple-600 font-semibold border border-purple-600 shadow-lg hover:bg-purple-50 hover:scale-105 transition-all duration-150"
            onClick={() => navigate("/register")}
          >
            Registrarse
          </button>
        </div>
      </div>
      <div className="mt-8 text-purple-700 text-sm text-center z-10">
        <span>ChatME!</span> &copy; 2025 &mdash; Tu comunidad de chat favorita
      </div>
    </div>
  );
}
