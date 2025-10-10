import { useRef, useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { useChat } from "@/contexts/ChatContext";
import { ChatMessage } from "@/components/ChatMessage";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { MessageCircle } from "lucide-react";

export function ChatRoom() {
  const { user } = useAuth();
  const { messages, currentRoom, setCurrentRoom, rooms } = useChat();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Filtrar mensajes para la sala actual
  const roomMessages = messages.filter(
    (message) => message.roomId === currentRoom?.id || message.room === currentRoom?.id
  );
  
  // Función para hacer scroll hacia abajo
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // Hacer scroll hacia abajo cuando los mensajes cambian
  useEffect(() => {
    scrollToBottom();
  }, [roomMessages]);

  // También hacer scroll cuando se cambia de sala
  useEffect(() => {
    if (currentRoom) {
      // Pequeño delay para asegurar que los mensajes se hayan cargado
      setTimeout(scrollToBottom, 100);
    }
  }, [currentRoom]);
  
  if (!currentRoom) {
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
          
          <div className="space-y-3">
            {rooms.map((room) => (
              <Button
                key={room.id}
                variant="outline"
                className="w-full p-4 h-auto flex flex-col items-start hover:bg-accent"
                onClick={() => setCurrentRoom(room.id)}
              >
                <h3 className="font-semibold text-sm">
                  {room.id === "R1" && "💬"} 
                  {room.id === "R2" && "🚀"} 
                  {room.id === "R3" && "🎲"} 
                  {" " + room.name}
                </h3>
                <p className="text-xs text-muted-foreground">{room.description}</p>
              </Button>
            ))}
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="flex flex-col h-full">
      <div className="border-b p-4">
        <h2 className="font-semibold text-lg">{currentRoom.name}</h2>
        <p className="text-sm text-muted-foreground">{currentRoom.description}</p>
      </div>
      
      <ScrollArea className="flex-1 p-4">
        <div className="space-y-4">
          {roomMessages.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <p className="text-muted-foreground">No messages yet. Start the conversation!</p>
            </div>
          ) : (
            roomMessages.map((message) => (
              <ChatMessage
                key={message.id}
                message={message}
                isCurrentUser={message.username === user}
              />
            ))
          )}
          {/* Elemento invisible para hacer scroll automático */}
          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>
    </div>
  );
}
