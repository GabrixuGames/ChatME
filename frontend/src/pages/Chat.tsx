
import React, { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { ChatSidebar } from "@/components/ChatSidebar";
import { ChatRoom } from "@/components/ChatRoom";
import { ChatInput } from "@/components/ChatInput";
import { Room, useChat } from "@/contexts/ChatContext";
import { useDualChatWindows } from "@/hooks/useDualChatWindows";
import { useIsMobile } from "@/hooks/use-mobile";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Button } from "@/components/ui/button";
import { FriendsPanel } from "@/components/FriendsPanel";

const Chat = () => {
  const { isAuthenticated, user } = useAuth();
  const navigate = useNavigate();
  const { rooms, openIndividualChat, setCurrentRoom, joinRoom } = useChat();
  const isMobile = useIsMobile();

  const [openSidebar, setOpenSidebar] = useState(false);
  const {
    openRooms,
    lastActiveIdx,
    setLastActiveIdx,
    handleRoomSelect,
    handleDrop,
    handleCloseWindow,
  } = useDualChatWindows({
    onSingleRoom: setCurrentRoom,
    openIndividualChat,
  });

  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/");
    }
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    openRooms.forEach((roomId) => joinRoom(roomId));
  }, [openRooms, joinRoom]);


  const publicRooms = useMemo(
    () => rooms.filter((room) => room.room_type !== "individual"),
    [rooms]
  );
  const initials = user ? user.slice(0, 1).toUpperCase() : "U";

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="fixed inset-0 flex flex-col sm:flex-row overflow-hidden" style={{height: '100dvh', width: '100vw'}}>
      <ChatSidebar
        showMobileMenu={openSidebar}
        setShowMobileMenu={setOpenSidebar}
        onRoomSelect={(roomId) => {
          setOpenSidebar(false);
          handleRoomSelect(roomId);
        }}
      />
      {openRooms.length === 1 && (
        <div
          className="flex-1 flex flex-col relative w-full h-full"
          onDragOver={e => e.preventDefault()}
          onDrop={e => void handleDrop(1, e)}
          onClick={() => setLastActiveIdx(0)}
        >
          <ChatRoom
            roomId={openRooms[0]}
            openSidebar={() => setOpenSidebar(true)}
          />
          <ChatInput roomId={openRooms[0]} />
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
                onDrop={e => void handleDrop(idx, e)}
                onClick={() => setLastActiveIdx(idx)}
              >
                <ChatRoom
                  roomId={roomId}
                  openSidebar={() => setOpenSidebar(true)}
                  autoSelect={false}
                  onCloseWindow={() => handleCloseWindow(idx)}
                />
                <ChatInput roomId={roomId} />
              </div>
            </div>
          ))}
        </>
      )}
      {openRooms.length === 0 && (
        <div className="flex-1 flex items-center justify-center text-gray-400 px-4">
          <ProfilePanel
            isMobile={isMobile}
            initials={initials}
            username={user || "Usuario"}
            publicRooms={publicRooms}
            onRoomSelect={handleRoomSelect}
          />
        </div>
      )}
    </div>
  );
}

export default Chat;

type ProfilePanelProps = {
  isMobile: boolean;
  initials: string;
  username: string;
  publicRooms: Room[];
  onRoomSelect: (roomId: string) => void;
};

function ProfilePanel({ isMobile, initials, username, publicRooms, onRoomSelect }: ProfilePanelProps) {
  if (isMobile) {
    return (
      <div className="w-full max-w-md text-foreground">
        <div className="relative overflow-hidden rounded-3xl border border-border bg-card shadow-xl">
          <div className="absolute -top-12 -right-10 h-32 w-32 rounded-full bg-emerald-400/20 blur-2xl" />
          <div className="absolute -bottom-12 -left-10 h-32 w-32 rounded-full bg-sky-400/20 blur-2xl" />
          <div className="px-6 pt-8 pb-6 text-center">
            <div className="mx-auto h-20 w-20 rounded-full bg-gradient-to-br from-emerald-500 to-sky-500 text-white flex items-center justify-center text-2xl font-semibold shadow-lg">
              {initials}
            </div>
            <div className="mt-3 text-lg font-semibold">{username}</div>
            <div className="text-xs text-muted-foreground">Perfil</div>
          </div>
        </div>
        <div className="mt-5 rounded-2xl border border-border bg-card p-4 shadow-sm">
          <Accordion type="single" collapsible className="w-full">
            <AccordionItem value="friends">
              <AccordionTrigger>Amigos</AccordionTrigger>
              <AccordionContent>
                <FriendsPanel onRoomSelect={onRoomSelect} />
              </AccordionContent>
            </AccordionItem>
            <AccordionItem value="rooms">
              <AccordionTrigger>Salas públicas</AccordionTrigger>
              <AccordionContent>
                <div className="space-y-2">
                  {publicRooms.map((room) => (
                    <Button
                      key={room.id}
                      variant="ghost"
                      className="w-full justify-between"
                      onClick={() => onRoomSelect(room.id)}
                    >
                      <span className="truncate">{room.name}</span>
                      {room.unread_count ? (
                        <span className="bg-emerald-500 text-white rounded-full px-2 py-0.5 text-xs font-bold">
                          {room.unread_count}
                        </span>
                      ) : null}
                    </Button>
                  ))}
                </div>
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-3xl text-foreground">
      <div className="relative overflow-hidden rounded-3xl border border-border bg-card shadow-xl">
        <div className="absolute -top-16 -right-12 h-40 w-40 rounded-full bg-emerald-500/20 blur-3xl" />
        <div className="absolute -bottom-16 -left-12 h-40 w-40 rounded-full bg-amber-400/20 blur-3xl" />
        <div className="flex items-center gap-6 p-10">
          <div className="h-24 w-24 rounded-full bg-gradient-to-br from-emerald-500 to-sky-500 text-white flex items-center justify-center text-3xl font-semibold shadow-lg">
            {initials}
          </div>
          <div>
            <div className="text-3xl font-semibold">{username}</div>
            <div className="text-sm text-muted-foreground">Perfil del usuario</div>
            <div className="mt-4 text-sm text-muted-foreground max-w-xl">
              Selecciona una sala o un amigo desde el panel izquierdo para empezar a chatear.
            </div>
          </div>
        </div>
        <div className="px-10 pb-10">
          <div className="grid grid-cols-2 gap-4">
            <div className="rounded-2xl border border-border bg-background/60 p-4">
              <div className="text-xs text-muted-foreground">Estado</div>
              <div className="mt-1 text-sm font-semibold">Disponible</div>
            </div>
            <div className="rounded-2xl border border-border bg-background/60 p-4">
              <div className="text-xs text-muted-foreground">Actividad</div>
              <div className="mt-1 text-sm font-semibold">Listo para chatear</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
