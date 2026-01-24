import { useRef, useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { useChat } from "@/contexts/ChatContext";
import { ChatMessage } from "@/components/ChatMessage";
import { TypingIndicator } from "@/components/TypingIndicator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { MessageCircle, X } from "lucide-react";
import { useIsMobile } from "@/hooks/use-mobile";

type ChatRoomProps = {
  openSidebar?: () => void;
  roomId?: string | null;
  autoSelect?: boolean;
  onCloseWindow?: () => void;
};

export function ChatRoom({ openSidebar = () => {}, roomId, autoSelect = true, onCloseWindow }: ChatRoomProps) {
  const { user } = useAuth();
  const { messages, currentRoom, setCurrentRoom, rooms, typingUsers, hideRoom } = useChat();
  const isMobile = useIsMobile();
  
  // Usar currentRoom si coincide con roomId, sino buscar en rooms
  const room = roomId 
    ? (currentRoom?.id === roomId ? currentRoom : rooms.find(r => r.id === roomId))
    : null;
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Get typing users for current room (exclude current user)
  const roomTypingUsers = room ? (typingUsers[room.id] || []).filter(u => u !== user) : [];

  // Filtrar mensajes para la sala actual
  const roomMessages = messages.filter(
    (message) => message.roomId === room?.id || message.room === room?.id
  );

  // Función para hacer scroll hacia abajo
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // Hacer scroll hacia abajo cuando los mensajes cambian
  useEffect(() => {
    scrollToBottom();
    // Pequeño delay para asegurar que los mensajes se hayan cargado
    setTimeout(scrollToBottom, 100);
  }, [roomMessages, currentRoom]);
  
  // Join room when roomId changes
  useEffect(() => {
    if (!autoSelect) return;
    if (roomId && currentRoom?.id !== roomId) {
      setCurrentRoom(roomId);
    }
  }, [roomId, currentRoom?.id, setCurrentRoom, autoSelect]);

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
    <div className="flex flex-col h-full w-full min-h-0">
      <div className="border-b p-2 sm:p-4 sticky top-0 bg-white dark:bg-background z-10 flex items-center justify-between">
        <div className="flex items-center gap-2">
          {/* Botón menú flotante solo en móvil/tablet */}
          {isMobile && (
            <button
              className="bg-purple-600 text-white rounded-full p-2 shadow-lg"
              onClick={openSidebar}
            >
              <span className="sr-only">Abrir menú</span>
              <MessageCircle className="h-5 w-5" />
            </button>
          )}
          <div>
            <h2 className="font-semibold text-base sm:text-lg">{room.name}</h2>
            <p className="text-xs sm:text-sm text-muted-foreground">{room.description}</p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          {/* Botón ocultar chat (solo para chats individuales) */}
          {room.room_type === 'individual' && (
            <Button
              variant="ghost"
              size="icon"
              onClick={() => {
                if (window.confirm('¿Ocultar este chat? Podrás volver a abrirlo desde tu lista de amigos.')) {
                  hideRoom(room.id);
                }
              }}
              className="text-muted-foreground hover:text-foreground"
            >
              <X className="h-5 w-5" />
            </Button>
          )}
          {onCloseWindow && (
            <Button
              variant="ghost"
              size="icon"
              onClick={onCloseWindow}
              className="text-muted-foreground hover:text-foreground"
              aria-label="Cerrar ventana"
            >
              <X className="h-5 w-5" />
            </Button>
          )}
        </div>
      </div>

      {/* Mensajes scrollables, usando ScrollArea para compatibilidad móvil/tablet */}
      <ScrollArea className="flex-1 min-h-0 w-full px-1 sm:px-4 py-0 max-h-full overflow-y-auto" style={{touchAction: 'pan-y', overscrollBehavior: 'contain'}}>
        <div className="space-y-3 sm:space-y-4">
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
          {/* Typing indicator */}
          <TypingIndicator usernames={roomTypingUsers} />
          {/* Elemento invisible para hacer scroll automático */}
          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>
    </div>
  );
}
