
import { useState, FormEvent, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useAuth } from "@/contexts/AuthContext";
import { useChat } from "@/contexts/ChatContext";
import { MessageCircle } from "lucide-react";
import { useIsMobile } from "@/hooks/use-mobile";

type ChatInputProps = {
  roomId?: string | null;
};

export function ChatInput({ roomId }: ChatInputProps) {
  const [message, setMessage] = useState("");
  const { user } = useAuth();
  const { sendMessage, currentRoom, rooms, sendTyping, sendStopTyping, inactiveFriendships, hideRoom } = useChat();
  const room = roomId ? rooms.find(r => r.id === roomId) : currentRoom;
  const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const isTypingRef = useRef(false);
  const isMobile = useIsMobile();

  // Detectar si esta sala tiene una amistad inactiva
  const isInactive = room && inactiveFriendships.has(room.id);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!message.trim() || !user || !room) return;
    
    // Dejar de escribir antes de enviar
    if (isTypingRef.current && user && room) {
      sendStopTyping(room.id, user);
      isTypingRef.current = false;
    }
    
    sendMessage(message.trim(), user, room.id);
    setMessage("");
  };
  
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };
  
  // Manejo de typing indicators con debounce
  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value;
    setMessage(newValue);
    
    if (!user || !room) return;
    
    // Enviar typing si no se había enviado
    if (!isTypingRef.current && newValue.length > 0) {
      sendTyping(room.id, user);
      isTypingRef.current = true;
    }
    
    // Reiniciar timeout para stop_typing
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }
    
    // Dejar de escribir después de 2 segundos de inactividad
    if (newValue.length > 0) {
      typingTimeoutRef.current = setTimeout(() => {
        if (isTypingRef.current && user && room) {
          sendStopTyping(room.id, user);
          isTypingRef.current = false;
        }
      }, 2000);
    } else {
      // Si borró todo el texto, enviar stop_typing inmediatamente
      if (isTypingRef.current) {
        sendStopTyping(room.id, user);
        isTypingRef.current = false;
      }
    }
  };
  
  // Cleanup al desmontar
  useEffect(() => {
    return () => {
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
      if (isTypingRef.current && user && room) {
        sendStopTyping(room.id, user);
      }
    };
  }, [room, user, sendStopTyping]);
  
  // Auto-expand textarea hasta 3 líneas
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 3 * 24)}px`;
    }
  }, [message]);

  // Si la amistad está inactiva y es un chat individual, mostrar mensaje especial
  if (isInactive && room?.room_type === 'individual') {
    return (
      <div className={isMobile ? "border-t p-2 bg-background w-full sticky bottom-0 z-20" : "border-t p-2 sm:p-4 bg-background"}>
        <div className="flex flex-col items-center gap-3 p-4 bg-muted rounded-lg">
          <p className="text-sm text-muted-foreground text-center">
            Ya no sois amigos
          </p>
          <Button 
            variant="destructive" 
            size="sm"
            onClick={() => {
              if (room) {
                hideRoom(room.id);
              }
            }}
          >
            Eliminar chat
          </Button>
        </div>
      </div>
    );
  }

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
          onChange={handleChange}
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

