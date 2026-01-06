import React from "react";
import { useFriends } from "@/contexts/FriendsContext";
import { useChat } from "@/contexts/ChatContext";
import { Button } from "@/components/ui/button";
import { AddFriendDialog } from "./AddFriendDialog";
import { Check, X, Trash2, MessageCircle } from "lucide-react";

interface FriendsPanelProps {
  collapsed?: boolean;
}

export const FriendsPanel: React.FC<FriendsPanelProps & { onRoomSelect?: (roomId: string) => void }> = ({ collapsed, onRoomSelect }) => {
  const { friends, pendingRequests, respondRequest, removeFriend, refresh } = useFriends();
  const { openIndividualChat, rooms, currentRoom, setCurrentRoom } = useChat();

  return (
  <div className={collapsed ? "space-y-2 flex flex-col" : "space-y-4"}>
      {/* Lista de amigos */}
      <div className="space-y-1">
        {friends.length === 0 && <div className="text-xs px-2 py-1 text-muted-foreground">No tienes amigos aún.</div>}
        {friends.map((f) => {
          // Buscar el chat room correspondiente a este amigo
          const friendRoom = rooms.find(r => r.room_type === 'individual' && r.name.includes(f.username));
          const isActive = currentRoom?.id === friendRoom?.id;
          // Solo mostrar badge si hay mensajes no leídos Y la ventana NO está activa
          const hasUnread = ((friendRoom?.unread_count ?? 0) > 0) && !isActive;
          
          return (
          <div
            key={f.id}
            role="button"
            className={`w-full flex flex-col px-2 py-2 rounded-xl transition text-sidebar-foreground justify-start border border-sidebar-border/30 bg-transparent hover:bg-sidebar-accent hover:text-sidebar-accent-foreground focus:bg-sidebar-accent focus:text-sidebar-accent-foreground focus:outline-none cursor-pointer ${isActive ? 'bg-sidebar-accent text-sidebar-accent-foreground' : ''} ${hasUnread ? 'font-semibold' : ''}`}
            style={{ backdropFilter: 'blur(2px)', WebkitBackdropFilter: 'blur(2px)' }}
            title={`Abrir chat con ${f.username}`}
            tabIndex={0}
            onClick={async e => {
              if ((e.target as HTMLElement).closest('.delete-friend-btn')) return;
              
              console.log("🟢 Click en amigo:", f.username);
              console.log("🟢 friendRoom encontrado:", friendRoom);
              console.log("🟢 onRoomSelect existe:", !!onRoomSelect);
              
              // Si ya existe el room, abrirlo directamente
              if (friendRoom) {
                console.log("🟢 Abriendo room existente:", friendRoom.id);
                setCurrentRoom(friendRoom.id);
                if (onRoomSelect) {
                  console.log("🟢 Llamando a onRoomSelect con:", friendRoom.id);
                  onRoomSelect(friendRoom.id);
                }
                return;
              }
              
              // Si no existe, crearlo
              console.log("🟢 Room no existe, creando...");
              const roomId = await openIndividualChat(f.username);
              console.log("🟢 Room creado con ID:", roomId);
              if (roomId) {
                setCurrentRoom(roomId);
                if (onRoomSelect) {
                  console.log("🟢 Llamando a onRoomSelect con nuevo room:", roomId);
                  onRoomSelect(roomId);
                }
              }
            }}
            onKeyDown={async e => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                if ((e.target as HTMLElement).closest('.delete-friend-btn')) return;
                
                if (friendRoom) {
                  setCurrentRoom(friendRoom.id);
                  if (onRoomSelect) onRoomSelect(friendRoom.id);
                  return;
                }
                
                const roomId = await openIndividualChat(f.username);
                if (roomId) {
                  setCurrentRoom(roomId);
                  if (onRoomSelect) onRoomSelect(roomId);
                }
              }
            }}
          >
            <div className="flex items-center justify-between w-full">
              <div className="flex items-center gap-2 flex-1 min-w-0">
                <MessageCircle className="h-4 w-4 shrink-0" />
                <span className="text-sm truncate">{f.username}</span>
                {hasUnread && (
                  <span className="bg-primary text-primary-foreground rounded-full px-2 py-0.5 text-xs font-bold shrink-0">
                    {friendRoom.unread_count}
                  </span>
                )}
              </div>
              <Button
                variant="ghost"
                size="icon"
                className="h-7 w-7 delete-friend-btn shrink-0"
                onClick={(e) => {
                  e.stopPropagation();
                  if (window.confirm(`¿Eliminar a ${f.username} de tus amigos?`)) {
                    removeFriend(f.id).then(() => refresh());
                  }
                }}
              >
                <Trash2 className="h-4 w-4 text-destructive" />
              </Button>
            </div>
            {friendRoom?.last_message && (
              <div className="text-xs text-white/80 dark:text-muted-foreground mt-1 truncate w-full">
                {friendRoom.last_message_username && `${friendRoom.last_message_username}: `}
                {friendRoom.last_message}
              </div>
            )}
          </div>
          );
        })}
      </div>
      
      {/* Solicitudes pendientes */}
      {pendingRequests.length > 0 && (
        <div>
          <div className="text-xs px-2 py-1 font-semibold text-sidebar-foreground">Solicitudes pendientes</div>
          {pendingRequests.map((req) => (
            <div
              key={req.id}
              className="w-full flex items-center justify-between px-2 py-2 rounded-xl transition text-sidebar-foreground border border-sidebar-border/30 bg-transparent mb-1"
              style={{ backdropFilter: 'blur(2px)', WebkitBackdropFilter: 'blur(2px)' }}
            >
              <span className="text-sm truncate flex-1">{req.sender_username}</span>
              <div className="flex items-center gap-1">
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-7 w-7 text-green-500 hover:text-green-600 hover:bg-green-50 dark:hover:bg-green-950"
                  onClick={() => respondRequest(req.id, 'accepted').then(() => refresh())}
                >
                  <Check className="h-4 w-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-7 w-7 text-destructive hover:bg-destructive/10"
                  onClick={() => respondRequest(req.id, 'rejected').then(() => refresh())}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}
      
      {/* Botón añadir amigo */}
      <AddFriendDialog />
    </div>
  );
};
