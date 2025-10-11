import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useAuth } from "@/contexts/AuthContext";
import { io } from "socket.io-client";
import { MessageCircle } from "lucide-react";

const SOCKET_URL = import.meta.env.VITE_SOCKET_URL || "http://localhost:5000";

export function ChatInputWindow({ room }) {
  const [message, setMessage] = useState("");
  const { user } = useAuth();
  const socketRef = useRef(null);

  useEffect(() => {
    socketRef.current = io(SOCKET_URL);
    return () => {
      socketRef.current.disconnect();
    };
  }, [room]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!message.trim() || !user || !room) return;
    socketRef.current.emit("message", {
      username: user,
      room: room.id,
      message: message.trim(),
      timestamp: new Date().toISOString()
    });
    setMessage("");
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const isMobile = typeof window !== "undefined" && window.innerWidth < 640;
  const textareaRef = useRef(null);
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 3 * 24)}px`;
    }
  }, [message]);

  return (
    <form
      onSubmit={handleSubmit}
      className={isMobile ? "border-t p-2 bg-background w-full sticky bottom-0 z-20" : "border-t p-2 sm:p-4 bg-background"}
      style={isMobile ? {maxWidth: '100vw'} : {}}
    >
      <div className="flex items-end gap-2 w-full">
        <Textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={room ? "Escribe tu mensaje..." : "Selecciona una sala para enviar mensajes"}
          rows={1}
          className={isMobile ? "min-h-[40px] max-h-[72px] resize-none bg-background text-foreground text-base leading-tight w-full" : "min-h-[48px] sm:min-h-[80px] resize-none bg-background text-foreground text-base sm:text-lg w-full"}
          style={isMobile ? {overflow: 'hidden'} : {}}
          disabled={!room}
        />
        <Button
          type="submit"
          size="icon"
          className={isMobile ? "h-9 w-9 rounded-full" : "h-10 w-10 sm:h-12 sm:w-12 rounded-full"}
          disabled={!message.trim() || !room}
        >
          <MessageCircle className="h-5 w-5 sm:h-6 sm:w-6" />
        </Button>
      </div>
      <p className={isMobile ? "text-[10px] text-muted-foreground mt-1" : "text-xs sm:text-sm text-muted-foreground mt-2"}>
        {room ? "Pulsa Enter para enviar, Shift+Enter para nueva línea" : "Selecciona una sala para chatear"}
      </p>
    </form>
  );
}
