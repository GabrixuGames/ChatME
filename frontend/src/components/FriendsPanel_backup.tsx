import React from "react";
import { useFriends } from "@/contexts/FriendsContext";
import { useChat } from "@/contexts/ChatContext";
import { useCallback } from "react";
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
      <div className="space-y-1">
        {friends.length === 0 && <div className="text-xs px-2 py-1 text-muted-foreground">No tienes amigos aún.</div>}
        {friends.map((f) => {
          // Buscar el chat room correspondiente a este amigo
          const friendRoom = rooms.find(r => r.room_type === 'individual' && r.name.includes(f.username));
          const hasUnread = friendRoom?.unread_count && friendRoom.unread_count > 0;
          const isActive = currentRoom?.id === friendRoom?.id;
          
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
              
              // Si ya existe el room, abrirlo directamente
              if (friendRoom) {
                setCurrentRoom(friendRoom.id);
                return;
              }
              
              // Si no existe, crearlo
              const roomId = await openIndividualChat(f.username);
              if (roomId) {
                let tries = 0;
                const maxTries = 30;
                while (!rooms.find(r => r.id === roomId) && tries < maxTries) {
                  console.log(`[FriendsPanel] Esperando sala ${roomId} en rooms... intento ${tries}`);
                  await new Promise(res => setTimeout(res, 100));
                  tries++;
                }
                if (!rooms.find(r => r.id === roomId)) {
                  // Forzar fetch manual de salas si no aparece
                  try {
                    const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";
                    const token = sessionStorage.getItem("jwt_token");
                    const res = await fetch(`${API_URL}/chat/rooms`, {
                      method: "GET",
                      headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${token}`,
                      },
                    });
                    const data = await res.json();
                    console.log("[FriendsPanel] Recarga manual de rooms:", data.rooms);
                  } catch (err) {
                    console.error("[FriendsPanel] Error forzando fetch de rooms:", err);
                  }
                }
                if (onRoomSelect && rooms.find(r => r.id === roomId)) onRoomSelect(roomId);
                else if (onRoomSelect) {
                  const foundRoom = rooms.find(r => r.name.includes(f.username));
                  if (foundRoom) onRoomSelect(foundRoom.id);
                }
              } else if (onRoomSelect) {
                const foundRoom = rooms.find(r => r.name.includes(f.username));
                if (foundRoom) onRoomSelect(foundRoom.id);
              }
            }}
            onKeyDown={async e => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                const roomId = await openIndividualChat(f.username);
                if (roomId) {
                  let tries = 0;
                  const maxTries = 30;
                  while (!rooms.find(r => r.id === roomId) && tries < maxTries) {
                    console.log(`[FriendsPanel] Esperando sala ${roomId} en rooms... intento ${tries}`);
                    await new Promise(res => setTimeout(res, 100));
                    tries++;
                  }
                  if (!rooms.find(r => r.id === roomId)) {
                    try {
                      const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";
                      const token = sessionStorage.getItem("jwt_token");
                      const res = await fetch(`${API_URL}/chat/rooms`, {
                        method: "GET",
                        headers: {
                          "Content-Type": "application/json",
                          "Authorization": `Bearer ${token}`,
                        },
                      });
                      const data = await res.json();
                      console.log("[FriendsPanel] Recarga manual de rooms:", data.rooms);
                    } catch (err) {
                      console.error("[FriendsPanel] Error forzando fetch de rooms:", err);
                    }
                  }
                  if (onRoomSelect && rooms.find(r => r.id === roomId)) onRoomSelect(roomId);
                  else if (onRoomSelect) {
                    const foundRoom = rooms.find(r => r.name.includes(f.username));
                    if (foundRoom) onRoomSelect(foundRoom.id);
                  }
                } else if (onRoomSelect) {
                  const foundRoom = rooms.find(r => r.name.includes(f.username));
                  if (foundRoom) onRoomSelect(foundRoom.id);
                }
              }
            }}
          >
            {f.profile_pic ? (
              <img src={f.profile_pic} alt={f.username} className="w-7 h-7 rounded-full object-cover mr-2 border border-sidebar-border" />
            ) : (
              <div className="w-7 h-7 rounded-full bg-sidebar-accent text-white flex items-center justify-center mr-2 border border-sidebar-border">
                {f.username.charAt(0).toUpperCase()}
              </div>
            )}
            <span className="truncate text-sidebar-foreground text-left font-medium flex-1">{f.username}</span>
            <MessageCircle className="h-4 w-4 text-purple-700 mr-2" />
            <Button
              size="icon"
              variant="ghost"
              className="delete-friend-btn bg-red-100 text-red-700 hover:bg-red-200 p-1 h-6 w-6 ml-2"
              title="Eliminar amigo"
              onClick={e => {
                e.stopPropagation();
                removeFriend(f.id);
              }}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        ))}
      </div>
      <div>
        {pendingRequests.map((r) => (
          <div key={r.id} className="flex items-center px-2 py-1 text-sidebar-foreground bg-sidebar rounded w-full">
            <span className="truncate text-sidebar-foreground text-left flex-1">{r.sender_username || r.sender_id}</span>
            <div className="flex gap-1 ml-auto justify-end">
              <Button size="icon" variant="ghost" className="bg-green-100 text-green-700 hover:bg-green-200 p-1 h-6 w-6" onClick={() => respondRequest(r.id, "accepted")}> <Check className="h-4 w-4" /> </Button>
              <Button size="icon" variant="ghost" className="bg-red-100 text-red-700 hover:bg-red-200 p-1 h-6 w-6" onClick={() => respondRequest(r.id, "rejected")}> <X className="h-4 w-4" /> </Button>
            </div>
          </div>
        ))}
      </div>
      <div className="px-2 py-2 mt-2 flex justify-center">
        <AddFriendDialog />
      </div>
    </div>
  );
};
