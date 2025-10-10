
import { useState, FormEvent } from "react";
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
  
  return (
    <form onSubmit={handleSubmit} className="border-t p-4 bg-background">
      <div className="flex items-end gap-2">
        <Textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={currentRoom ? "Type your message..." : "Selecciona una sala para enviar mensajes"}
          className="min-h-[80px] resize-none bg-white"
          disabled={!currentRoom}
        />
        <Button 
          type="submit" 
          size="icon" 
          className="h-10 w-10 rounded-full"
          disabled={!message.trim() || !currentRoom}
        >
          <MessageCircle className="h-5 w-5" />
        </Button>
      </div>
      <p className="text-xs text-muted-foreground mt-2">
        {currentRoom ? "Press Enter to send, Shift+Enter for a new line" : "Selecciona una sala para chatear"}
      </p>
    </form>
  );
}
