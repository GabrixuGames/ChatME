
import { useState, useEffect, useRef } from "react";
import { io } from "socket.io-client";
import { useAuth } from "@/contexts/AuthContext";
import { ChatMessage } from "@/components/ChatMessage";
import { ScrollArea } from "@/components/ui/scroll-area";
import { MessageCircle } from "lucide-react";

const SOCKET_URL = import.meta.env.VITE_SOCKET_URL || "http://localhost:5000";

interface PrivateChatWindowProps {
  chatId: string;
  currentUserId: string;
  otherUsername?: string;
}

export function PrivateChatWindow({ chatId, currentUserId, otherUsername }: PrivateChatWindowProps) {
  const { user } = useAuth();
  const [messages, setMessages] = useState<any[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const socketRef = useRef<any>(null);

  useEffect(() => {
    socketRef.current = io(SOCKET_URL);
    const socket = socketRef.current;

    // Unirse al chat privado
    socket.emit("join_private", {
      chatId,
      username: user || currentUserId
    });

    socket.on("private_message", (message) => {
      setMessages((prev) => [...prev, message]);
    });
    socket.on("previous_private_messages", (previousMessages) => {
      setMessages(previousMessages);
    });

    return () => {
      socket.disconnect();
    };
  }, [chatId, user, currentUserId]);

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

  return (
    <div className="flex flex-col h-full w-full min-h-0">
      <div className="border-b p-2 sm:p-4 sticky top-0 bg-background z-10 flex items-center relative">
        <h2 className="font-semibold text-base sm:text-lg">{otherUsername ? otherUsername : 'Chat privado'}</h2>
      </div>
      <ScrollArea className="flex-1 min-h-0 w-full px-1 sm:px-4 py-0 max-h-full overflow-y-auto" style={{touchAction: 'pan-y', overscrollBehavior: 'contain'}}>
        <div className="space-y-3 sm:space-y-4">
          {messages.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <p className="text-muted-foreground">No hay mensajes aún. ¡Empieza la conversación!</p>
            </div>
          ) : (
            messages.map((message) => (
              <ChatMessage
                key={message.id}
                message={message}
                isCurrentUser={message.username === (user || currentUserId)}
              />
            ))
          )}
          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>
      {/* Aquí puedes añadir el input de mensajes igual que en ChatRoomWindow */}
      {/* ... */}
    </div>
  );
}
