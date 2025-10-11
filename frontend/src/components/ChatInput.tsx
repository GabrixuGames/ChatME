
import { useState, FormEvent, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useAuth } from "@/contexts/AuthContext";
import { useChat } from "@/contexts/ChatContext";
import { MessageCircle } from "lucide-react";

export function ChatInput() {
  const [message, setMessage] = useState("");
  const { user } = useAuth();
  const { sendMessage, currentRoom } = useChat();
  
  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    
    if (!message.trim() || !user || !currentRoom) return;
    
    // Usar solo el username, que es lo que tenemos disponible
    sendMessage(message.trim(), user); // Cambiar para pasar solo el username
    setMessage("");
  };
  
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };
  
  // Detectar si es móvil
  const isMobile = window.innerWidth < 640;

  // Auto-expand textarea hasta 3 líneas
  const textareaRef = useRef<HTMLTextAreaElement>(null);
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
          placeholder={currentRoom ? "Escribe tu mensaje..." : "Selecciona una sala para enviar mensajes"}
          rows={1}
          className={isMobile ? "min-h-[40px] max-h-[72px] resize-none bg-white text-base leading-tight w-full" : "min-h-[48px] sm:min-h-[80px] resize-none bg-white text-base sm:text-lg w-full"}
          style={isMobile ? {overflow: 'hidden'} : {}}
          disabled={!currentRoom}
        />
        <Button
          type="submit"
          size="icon"
          className={isMobile ? "h-9 w-9 rounded-full" : "h-10 w-10 sm:h-12 sm:w-12 rounded-full"}
          disabled={!message.trim() || !currentRoom}
        >
          <MessageCircle className="h-5 w-5 sm:h-6 sm:w-6" />
        </Button>
      </div>
      <p className={isMobile ? "text-[10px] text-muted-foreground mt-1" : "text-xs sm:text-sm text-muted-foreground mt-2"}>
        {currentRoom ? "Pulsa Enter para enviar, Shift+Enter para nueva línea" : "Selecciona una sala para chatear"}
      </p>
    </form>
  );
}
