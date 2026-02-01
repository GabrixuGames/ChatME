import { createContext, useContext, useState, ReactNode, useEffect, useCallback } from "react";
import { io, Socket } from "socket.io-client";
import { useAuth } from "./AuthContext";

// Define la estructura del mensaje
export interface Message {
  id: string;
  roomId: string;
  room?: string; // Por compatibilidad con backend legacy
  userId: string;
  username: string;
  content: string;
  timestamp: Date | string; // Puede venir como string del backend
}

// Define la estructura de la sala
export interface Room {
  id: string;
  name: string;
  description: string;
  room_type?: string;
  is_temporary?: boolean;
  other_username?: string;
  other_user_id?: string;
  last_message?: string;
  last_message_at?: string;
  last_message_username?: string;
  unread_count?: number;
  friend_removed_by?: string | null; // username de quien eliminó la amistad, null si son amigos
}

interface ChatContextType {
  messages: Message[];
  rooms: Room[];
  currentRoom: Room | null;
  sendMessage: (content: string, username: string, roomId?: string) => void;
  setCurrentRoom: (roomId: string) => void;
  goToWelcome: () => void;
  openIndividualChat: (friendUsername: string, isTemporary?: boolean) => Promise<string | undefined>;
  markRoomAsRead: (roomId: string) => Promise<void>;
  hideRoom: (roomId: string) => Promise<void>;
  typingUsers: Record<string, string[]>; // roomId -> [usernames]
  sendTyping: (roomId: string, username: string) => void;
  sendStopTyping: (roomId: string, username: string) => void;
  refreshRooms: () => Promise<void>;
  joinRoom: (roomId: string) => void;
  inactiveFriendships: Set<string>; // Set de room_ids con amistades inactivas
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

// Configura la conexión con Socket.IO usando variables de entorno
const SOCKET_URL = import.meta.env.VITE_SOCKET_URL || "";
let socket: Socket | null = null;

export function ChatProvider({ children }: { children: ReactNode }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [rooms, setRooms] = useState<Room[]>([]);
  const [currentRoom, setCurrentRoomState] = useState<Room | null>(null);
  const [typingUsers, setTypingUsers] = useState<Record<string, string[]>>({});
  const [inactiveFriendships, setInactiveFriendships] = useState<Set<string>>(new Set());
  const { user, token } = useAuth();
  const API_URL = import.meta.env.VITE_API_URL ?? "";

  const refreshRooms = useCallback(async () => {
    if (!token) return;
    
    try {
      const res = await fetch(`${API_URL}/chat/rooms`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
      });
      const data = await res.json();
      setRooms(data.rooms || []);
    } catch (err) {
      console.error("Error al cargar rooms:", err);
    }
  }, [token, API_URL]);

  const joinRoom = useCallback((roomId: string) => {
    if (socket && user) {
      socket.emit("join", { room: roomId, username: user });
    }
  }, [user]);

  // Conectar Socket.IO cuando el usuario está autenticado
  useEffect(() => {
    if (!user) return;

    if (!socket) {
      socket = io(SOCKET_URL, {
        query: { username: user }
      });

      socket.on("message", (message) => {
        // Convertir timestamp si viene como string
        if (typeof message.timestamp === 'string') {
          message.timestamp = new Date(message.timestamp);
        }

        setMessages((prev) => [...prev, message]);
        
        // Actualizar última mensaje en rooms
        refreshRooms();
      });

      socket.on("previous_messages", (msgs) => {
        const formattedMsgs = msgs.map((msg: Message) => ({
          ...msg,
          timestamp: typeof msg.timestamp === 'string' ? new Date(msg.timestamp) : msg.timestamp
        }));
        const roomId = formattedMsgs[0]?.roomId || formattedMsgs[0]?.room;
        if (!roomId) {
          setMessages(formattedMsgs);
          return;
        }
        setMessages((prev) => {
          const filtered = prev.filter(
            (message) => message.roomId !== roomId && message.room !== roomId
          );
          return [...filtered, ...formattedMsgs];
        });
      });

      // Nuevo evento: cuando se crea un chat individual
      socket.on("new_individual_chat", (data) => {
        if (data.room) {
          setRooms((prevRooms) => {
            const exists = prevRooms.some(r => r.id === data.room.id);
            if (!exists) {
              return [...prevRooms, data.room];
            }
            return prevRooms;
          });
          
          // Auto-join a la sala
          joinRoom(data.room.id);
        }
      });

      // Typing indicators
      socket.on("user_typing", (data) => {
        const { username, room } = data;
        setTypingUsers((prev) => {
          const current = prev[room] || [];
          if (!current.includes(username)) {
            return { ...prev, [room]: [...current, username] };
          }
          return prev;
        });
      });

      socket.on("user_stop_typing", (data) => {
        const { username, room } = data;
        setTypingUsers((prev) => {
          const current = prev[room] || [];
          return { ...prev, [room]: current.filter(u => u !== username) };
        });
      });

      // Eventos de solicitudes de amistad
      socket.on("friend_request_received", (data) => {
        // Disparar evento personalizado para que FriendsContext lo escuche
        window.dispatchEvent(new CustomEvent('friendRequestReceived', { detail: data }));
      });

      socket.on("friend_request_accepted", (data) => {
        // Disparar evento personalizado para que FriendsContext lo escuche
        window.dispatchEvent(new CustomEvent('friendRequestAccepted', { detail: data }));
      });

      socket.on("friendship_ended", (data) => {
        // Marcar este room como con amistad inactiva
        if (data.room_id) {
          setInactiveFriendships(prev => {
            const newSet = new Set(prev);
            newSet.add(data.room_id);
            return newSet;
          });
        }
      });

      socket.on("error", (error) => {
        console.error("❌ Socket.IO error:", error);
      });
    }

    return () => {
      if (socket) {
        socket.disconnect();
        socket = null;
      }
    };
  }, [user, refreshRooms, joinRoom]);

  // Cargar rooms al iniciar
  useEffect(() => {
    if (user && token) {
      refreshRooms();
    }
  }, [user, token, refreshRooms]);

  const switchRoom = (roomId: string) => {
    const room = rooms.find((r) => r.id === roomId);
    if (room) {
      setCurrentRoomState(room);

      joinRoom(roomId);
      
      // Marcar como leído
      markRoomAsRead(roomId);
    }
  };

  const openIndividualChat = async (friendUsername: string, isTemporary: boolean = false) => {
    try {
      const res = await fetch(`${API_URL}/chat/individual/create`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ username_2: friendUsername, is_temporary: isTemporary })
      });
      const data = await res.json();
      if (data.room) {
        await refreshRooms();
        switchRoom(data.room.id);
        return data.room.id;
      }
      return undefined;
    } catch (err) {
      console.error("Error abriendo chat individual:", err);
      return undefined;
    }
  };

  const sendMessage = (content: string, username: string, roomId?: string) => {
    if (!socket) {
      console.error("Socket no conectado");
      return;
    }

    const targetRoom = roomId || currentRoom?.id;
    if (!targetRoom) {
      console.error("No hay sala seleccionada");
      return;
    }

    socket.emit("message", {
      username,
      room: targetRoom,
      message: content,
    });
  };

  const sendTyping = (roomId: string, username: string) => {
    if (socket) {
      socket.emit("typing", { room: roomId, username });
    }
  };

  const sendStopTyping = (roomId: string, username: string) => {
    if (socket) {
      socket.emit("stop_typing", { room: roomId, username });
    }
  };

  const markRoomAsRead = async (roomId: string) => {
    if (!token) {
      console.warn("⚠️ No token disponible para marcar como leído");
      return;
    }
    
    try {
      const response = await fetch(`${API_URL}/chat/mark_read`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ room_id: roomId })
      });
      
      if (!response.ok) {
        console.error(`❌ Error HTTP ${response.status} al marcar como leído`);
        return;
      }
      
      // Actualizar contador local solo si la petición fue exitosa
      setRooms(prev => prev.map(r => 
        r.id === roomId ? { ...r, unread_count: 0 } : r
      ));
    } catch (err) {
      console.error("❌ Error marcando como leído:", err);
      // No relanzar el error para evitar romper el flujo
    }
  };

  const hideRoom = async (roomId: string) => {
    if (!token) return;
    
    try {
      await fetch(`${API_URL}/chat/hide_room`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ room_id: roomId })
      });
      
      // Remover de la lista local
      setRooms(prev => prev.filter(r => r.id !== roomId));
      
      if (currentRoom?.id === roomId) {
        setCurrentRoomState(null);
      }
      
      // Refrescar rooms para asegurar sincronización con backend
      await refreshRooms();
    } catch (err) {
      console.error("Error ocultando sala:", err);
    }
  };

  const setCurrentRoom = (roomId: string) => {
    switchRoom(roomId);
  };

  const goToWelcome = () => {
    setCurrentRoomState(null);
    setMessages([]);
  };

  return (
    <ChatContext.Provider
      value={{
        messages,
        rooms,
        currentRoom,
        sendMessage,
        setCurrentRoom,
        goToWelcome,
        openIndividualChat,
        markRoomAsRead,
        hideRoom,
        typingUsers,
        sendTyping,
        sendStopTyping,
        refreshRooms,
        joinRoom,
        inactiveFriendships
      }}
    >
      {children}
    </ChatContext.Provider>
  );
}

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) throw new Error("useChat must be used within a ChatProvider");
  return context;
};
