import { useState, useEffect, useRef } from "react";
import { io } from "socket.io-client";
import { useAuth } from "@/contexts/AuthContext";
import { ChatMessage } from "@/components/ChatMessage";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { MessageCircle } from "lucide-react";

const SOCKET_URL = import.meta.env.VITE_SOCKET_URL || "http://localhost:5000";

export function ChatRoomWindow({ room, openSidebar, onClose }) {
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const messagesEndRef = useRef(null);
  const socketRef = useRef(null);

  useEffect(() => {
    // Crear socket para esta ventana
    socketRef.current = io(SOCKET_URL);
    const socket = socketRef.current;

    // Join room
    if (room) {
      socket.emit("join", {
        room: room.id,
        roomId: room.id,
        username: user || "Invitado"
      });
    }

    // Recibir mensajes
    socket.on("message", (message) => {
      if (message.roomId === room.id || message.room === room.id) {
        setMessages((prev) => [...prev, message]);
      }
    });
    socket.on("previous_messages", (previousMessages) => {
      setMessages(previousMessages);
    });

    return () => {
      socket.disconnect();
    };
  }, [room, user]);

  // Scroll automático
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
    setTimeout(() => {
      if (messagesEndRef.current) {
        messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
      }
    }, 100);
  }, [messages]);

  if (!room) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="text-center max-w-md">
          <div className="mb-6">
            <MessageCircle className="h-16 w-16 mx-auto text-muted-foreground mb-4" />
            <h2 className="text-2xl font-bold text-foreground mb-2">
              ¡Bienvenido a ChatME!
            </h2>
            <p className="text-muted-foreground mb-6">
              Selecciona una sala del panel izquierdo para comenzar a chatear
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full w-full min-h-0">
  <div className="border-b p-2 sm:p-4 sticky top-0 bg-background z-10 flex items-center relative">
        {/* Botón menú flotante solo en móvil/tablet */}
        {typeof window !== "undefined" && window.innerWidth < 640 && (
          <button
            className="mr-2 bg-purple-600 text-white rounded-full p-2 shadow-lg"
            onClick={openSidebar}
          >
            <span className="sr-only">Abrir menú</span>
            <MessageCircle className="h-5 w-5" />
          </button>
        )}
        <h2 className="font-semibold text-base sm:text-lg">{room.name}</h2>
        <p className="text-xs sm:text-sm text-muted-foreground ml-2">{room.description}</p>
        {onClose && (
          <button
            className="absolute top-2 right-8 z-20 text-xl text-purple-600 hover:text-purple-800 font-bold bg-background rounded-full shadow-lg p-1 transition-colors"
            onClick={onClose}
            title="Cerrar chat"
            style={{minWidth: '32px', minHeight: '32px'}}
          >
            ×
          </button>
        )}
      </div>
      <ScrollArea className="flex-1 min-h-0 w-full px-1 sm:px-4 py-0 max-h-full overflow-y-auto" style={{touchAction: 'pan-y', overscrollBehavior: 'contain'}}>
        <div className="space-y-3 sm:space-y-4">
          {messages.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <p className="text-muted-foreground">No messages yet. Start the conversation!</p>
            </div>
          ) : (
            messages.map((message) => (
              <ChatMessage
                key={message.id}
                message={message}
                isCurrentUser={message.username === user}
              />
            ))
          )}
          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>
    </div>
  );
}
