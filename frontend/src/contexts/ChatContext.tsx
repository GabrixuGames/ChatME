import { createContext, useContext, useState, ReactNode, useEffect } from "react";
import { io } from "socket.io-client";

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
}

interface ChatContextType {
  messages: Message[];
  rooms: Room[];
  currentRoom: Room | null;
  sendMessage: (content: string, username: string) => void; // Cambiado para usar username
  setCurrentRoom: (roomId: string) => void;
  goToWelcome: () => void; // Nueva función para volver a la página de bienvenida
  currentUserId: string;  // Añadimos el campo currentUserId
}

// Crear las salas iniciales
const initialRooms: Room[] = [
  { id: "R1", name: "Sala General", description: "Conversación principal" },
  { id: "R2", name: "Sala Desarrollo", description: "Para hablar de código" },
  { id: "R3", name: "Sala Random", description: "Conversaciones casuales" }
];

const ChatContext = createContext<ChatContextType | undefined>(undefined);

// Configura la conexión con Socket.IO usando variables de entorno
const SOCKET_URL = import.meta.env.VITE_SOCKET_URL || "http://localhost:5000";
const socket = io(SOCKET_URL);

export function ChatProvider({ children }: { children: ReactNode }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [rooms] = useState<Room[]>(initialRooms);
  const [currentRoom, setCurrentRoom] = useState<Room | null>(null); // Cambiar a null
  const [currentUserId] = useState<string>(sessionStorage.getItem("userId") || "defaultUserId");

  useEffect(() => {
    // Establece la conexión para recibir mensajes en tiempo real
    socket.on("connect", () => {
      console.log("Conexión establecida con el servidor Socket.IO");
    });

    socket.on("message", (message) => {
      console.log("=== MENSAJE RECIBIDO ===");
      console.log("Mensaje completo:", message);
      console.log("Sala del mensaje:", message.roomId || message.room);
      console.log("Sala actual:", currentRoom?.id);
      console.log("¿Es de la sala actual?", (message.roomId === currentRoom?.id || message.room === currentRoom?.id));
      
      // Convertir timestamp si viene como string
      if (typeof message.timestamp === 'string') {
        message.timestamp = new Date(message.timestamp);
      }
      
      // Agregar mensaje al estado
      setMessages((prevMessages) => {
        console.log("Mensajes antes de agregar:", prevMessages.length);
        
        // Evitar duplicados basados en ID o timestamp
        const isDuplicate = prevMessages.some(msg => 
          msg.id === message.id || 
          (msg.timestamp && message.timestamp && 
           Math.abs(new Date(msg.timestamp).getTime() - new Date(message.timestamp).getTime()) < 1000)
        );
        
        if (!isDuplicate) {
          console.log("Agregando mensaje nuevo:", message);
          const newMessages = [...prevMessages, message];
          console.log("Total mensajes después de agregar:", newMessages.length);
          return newMessages;
        }
        
        console.log("Mensaje duplicado, no se agrega:", message);
        return prevMessages;
      });
    });

    // Escucha los mensajes previos cuando el usuario entra en una sala
    socket.on("previous_messages", (previousMessages: Message[]) => {
      console.log("=== MENSAJES PREVIOS RECIBIDOS ===");
      console.log("Cantidad de mensajes:", previousMessages.length);
      console.log("Mensajes:", previousMessages);
      
      // Convertir timestamps
      const processedMessages = previousMessages.map(msg => ({
        ...msg,
        timestamp: typeof msg.timestamp === 'string' ? new Date(msg.timestamp) : msg.timestamp
      }));
      
      console.log("Mensajes procesados:", processedMessages);
      setMessages(processedMessages);
      console.log("Estado de mensajes actualizado");
    });

    // Escucha errores
    socket.on("error", (error) => {
      console.error("=== ERROR DE SOCKET.IO ===", error);
    });

    socket.on("connect_error", (error) => {
      console.error("=== ERROR DE CONEXIÓN ===", error);
    });

    // Cleanup function
    return () => {
      socket.off("message");
      socket.off("previous_messages");
      socket.off("connect");
      socket.off("error");
      socket.off("connect_error");
    };
  }, []); // Sin dependencias para que solo se ejecute una vez

  const sendMessage = (content: string, username: string) => {
    if (!currentRoom) {
      console.error("No hay sala actual seleccionada");
      return;
    }

    // Crear mensaje en formato que espera el backend
    const messageData = {
      username: username,
      room: currentRoom.id,      // Cambiar roomId por room
      message: content,          // Cambiar content por message
      timestamp: new Date().toISOString()
    };

    console.log("=== ENVIANDO MENSAJE ===");
    console.log("Sala actual:", currentRoom.id);
    console.log("Username:", username);
    console.log("Datos del mensaje:", messageData);
    console.log("Estado de socket conectado:", socket.connected);

    // Enviar el mensaje al servidor
    socket.emit("message", messageData);
    
    console.log("Mensaje enviado via socket.emit");
  };

  const switchRoom = (roomId: string) => {
    const room = rooms.find((r) => r.id === roomId);
    if (room) {
      console.log("=== CAMBIANDO DE SALA ===");
      console.log("Sala anterior:", currentRoom?.id);
      console.log("Nueva sala:", room.id);
      
      setCurrentRoom(room);
      // Limpiar mensajes actuales antes de cargar los nuevos
      setMessages([]);
      
      // Emitir join con formato correcto
      const joinData = {
        room: room.id,
        roomId: room.id, // Por compatibilidad
        username: sessionStorage.getItem("username") || "Invitado"
      };
      
      console.log("Enviando join con datos:", joinData);
      socket.emit("join", joinData);
      console.log("Join enviado");
    } else {
      console.error("Sala no encontrada:", roomId);
    }
  };

  // Función para volver a la página de bienvenida
  const goToWelcome = () => {
    setCurrentRoom(null);
  };

  return (
    <ChatContext.Provider
      value={{
        messages,
        rooms,
        currentRoom,
        sendMessage,
        setCurrentRoom: switchRoom,
        goToWelcome,
        currentUserId,  // Pasamos el currentUserId a los componentes que lo necesiten
      }}
    >
      {children}
    </ChatContext.Provider>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useChat() {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error("useChat must be used within a ChatProvider");
  }
  return context;
}
