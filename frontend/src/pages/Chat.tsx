
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { useChat } from "@/contexts/ChatContext";
import { ChatSidebar } from "@/components/ChatSidebar";
import { ChatRoomWindow } from "@/components/ChatRoomWindow";
import { ChatInputWindow } from "@/components/ChatInputWindow";

const Chat = () => {
  const { isAuthenticated } = useAuth();
  const { rooms } = useChat();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/");
    }
  }, [isAuthenticated, navigate]);

  if (!isAuthenticated) {
    return null;
  }

  // Estado para abrir el menú desde ChatRoom
  const [openSidebar, setOpenSidebar] = useState(false);

  // Dual chat logic (desktop only)
  // openRooms: array of room ids (max 2)
  const [openRooms, setOpenRooms] = useState<string[]>([]);
  // Track last active chat index (0 or 1)
  const [lastActiveIdx, setLastActiveIdx] = useState(0);

  // Open chat by click
  const handleRoomSelect = (roomId: string) => {
    setOpenRooms(prev => {
      if (prev.length === 0) return [roomId];
      if (prev.length === 1) return [roomId];
      // If two chats, replace last active (do not alternate)
      const newRooms = [...prev];
      newRooms[lastActiveIdx] = roomId;
      return newRooms;
    });
  };

  // Drag & drop: replace chat in any window
  const handleDrop = (windowIdx: number, e: React.DragEvent) => {
    e.preventDefault();
    const roomId = e.dataTransfer.getData("roomId");
    if (!roomId) return;
    setLastActiveIdx(windowIdx);
    setOpenRooms(prev => {
      if (prev.length === 0) return [roomId];
      if (prev.length === 1 && windowIdx === 1) return [prev[0], roomId];
      const newRooms = [...prev];
      newRooms[windowIdx] = roomId;
      return newRooms;
    });
  };

  // Close chat window, expand remaining chat
  const handleCloseWindow = (windowIdx: number) => {
    setOpenRooms(prev => {
      const newRooms = [...prev];
      newRooms.splice(windowIdx, 1);
      return newRooms.length ? newRooms : [];
    });
  };

  return (
    <div className="fixed inset-0 flex flex-col sm:flex-row overflow-hidden" style={{height: '100dvh', width: '100vw'}}>
      <ChatSidebar showMobileMenu={openSidebar} setShowMobileMenu={setOpenSidebar} onRoomSelect={handleRoomSelect} />
      {openRooms.length === 1 && (
        <div
          className="flex-1 flex flex-col relative w-full h-full"
          onDragOver={e => e.preventDefault()}
          onDrop={e => handleDrop(1, e)}
          onClick={() => setLastActiveIdx(0)}
        >
          <ChatRoomWindow
            room={rooms.find(r => r.id === openRooms[0])}
            openSidebar={() => setOpenSidebar(true)}
            onClose={() => setOpenRooms([])}
          />
          <ChatInputWindow room={rooms.find(r => r.id === openRooms[0])} />
        </div>
      )}
      {openRooms.length === 2 && (
        <>
          {openRooms.map((roomId, idx) => (
            <div key={roomId} className="flex-1 flex items-center justify-center w-1/2 h-full">
              <div
                className={`relative w-[95%] h-[95%] flex flex-col bg-background ${lastActiveIdx === idx ? 'ring-4 ring-purple-500 shadow-2xl rounded-2xl z-10' : ''}`}
                style={lastActiveIdx === idx ? {boxShadow: '0 8px 32px 0 rgba(128,0,128,0.25), 0 1.5px 0 0 #a855f7', borderRadius: '1.25rem'} : {}}
                onDragOver={e => e.preventDefault()}
                onDrop={e => handleDrop(idx, e)}
                onClick={() => setLastActiveIdx(idx)}
              >
                <ChatRoomWindow
                  room={rooms.find(r => r.id === roomId)}
                  openSidebar={() => setOpenSidebar(true)}
                  onClose={() => setOpenRooms(prev => {
                    const newRooms = [...prev];
                    newRooms.splice(idx, 1);
                    return newRooms;
                  })}
                />
                <ChatInputWindow room={rooms.find(r => r.id === roomId)} />
              </div>
            </div>
          ))}
        </>
      )}
      {openRooms.length === 0 && (
        <div className="flex-1 flex items-center justify-center text-gray-400">
          Selecciona una sala para empezar
        </div>
      )}
    </div>
  );
}

export default Chat;
