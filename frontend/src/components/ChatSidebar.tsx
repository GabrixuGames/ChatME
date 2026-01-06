import React from "react";
import { useNavigate } from "react-router-dom";
import { useChat } from "../contexts/ChatContext";
import { useAuth } from "../contexts/AuthContext";
import { useIsMobile } from "../hooks/use-mobile";
import { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider } from "@/components/ui/tooltip";
import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from "@/components/ui/accordion";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { Sun, Moon, MessageCircle, User, Users, LogIn } from "lucide-react";
import { FriendsPanel } from "./FriendsPanel";
import { SidebarPopover } from "./SidebarPopover";
import { useDarkMode } from "../hooks/useDarkMode.tsx";

type ChatSidebarProps = {
  showMobileMenu?: boolean;
  setShowMobileMenu?: (open: boolean) => void;
  initialCollapsed?: boolean;
  onRoomSelect?: (roomId: string) => void;
};

function DarkModeToggle({ collapsed }: { collapsed: boolean }) {
  const darkMode = useDarkMode();
  return (
    <Button
      variant="ghost"
      className={cn(
        "w-full text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
        collapsed ? "flex items-center justify-center px-0 h-10" : "justify-start"
      )}
      onClick={darkMode.toggle}
      aria-label="Toggle dark mode"
    >
      {darkMode.dark
        ? <Sun className={cn("h-5 w-5", !collapsed && "mr-2")} />
        : <Moon className={cn("h-5 w-5", !collapsed && "mr-2")} />}
      {!collapsed && <span>{darkMode.dark ? "Modo claro" : "Modo oscuro"}</span>}
    </Button>
  );
}

export function ChatSidebar({ showMobileMenu = false, setShowMobileMenu = () => {}, initialCollapsed = false, onRoomSelect }: ChatSidebarProps) {
  const navigate = useNavigate();
  const { rooms, currentRoom, setCurrentRoom, goToWelcome } = useChat();
  const { user, logout } = useAuth();
  const isMobile = useIsMobile();
  const [collapsed, setCollapsed] = React.useState(isMobile || initialCollapsed);

  const handleLogout = () => {
    logout();
    navigate("/");
  };
  // El botón flotante se moverá al header del chat, así que lo eliminamos aquí
  // Recibe un prop para abrir el menú desde ChatRoom
  return (
    <>
      {/* Sidebar normal en desktop, flotante en móvil */}
      <div
        data-sidebar-mobile
        className={cn(
          isMobile
            ? `fixed top-0 left-0 h-full w-64 bg-sidebar z-50 shadow-2xl transition-transform duration-300 ${showMobileMenu ? 'translate-x-0' : '-translate-x-full'}`
            : collapsed
              ? "flex flex-col h-full bg-sidebar transition-all duration-300 border-r border-sidebar-border w-14 min-h-screen"
              : "flex flex-col h-full bg-sidebar transition-all duration-300 border-r border-sidebar-border w-64 min-h-screen"
        )}
        style={isMobile ? { touchAction: 'none' } : {}}
      >
        {/* Cierre en móvil */}
        {isMobile && (
          <button
            className="absolute top-4 right-4 w-8 h-8 flex items-center justify-center text-purple-700 bg-white rounded-full p-0 shadow border border-purple-200 hover:bg-purple-50 transition"
            onClick={() => setShowMobileMenu(false)}
            aria-label="Cerrar menú"
          >
            <span className="sr-only">Cerrar menú</span>
            <span className="text-2xl font-bold">✕</span>
          </button>
        )}
        {/* Header */}
        <div className="flex items-center justify-between p-4">
          {!collapsed && (
            <Button
              variant="ghost"
              className="p-0 h-auto hover:bg-transparent"
              onClick={goToWelcome}
            >
              <h1 className="text-xl font-bold text-sidebar-foreground hover:text-sidebar-accent-foreground transition-colors">
                ChatME!
              </h1>
            </Button>
          )}
          <Button 
            variant="ghost" 
            size="icon" 
            onClick={() => setCollapsed(!collapsed)}
            className="text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
          >
            {collapsed ? (
              <MessageCircle className="h-5 w-5" />
            ) : (
              <span className="text-xl">☰</span>
            )}
          </Button>
        </div>

        <div className={cn("px-4 py-3 flex items-center justify-center", !collapsed && "justify-start")}> 
          <Tooltip>
            <TooltipTrigger asChild>
              <div className="flex items-center justify-center w-8 h-8 rounded-full bg-sidebar-accent text-sidebar-accent-foreground">
                <User className="h-4 w-4" />
              </div>
            </TooltipTrigger>
            <TooltipContent side="right">Perfil</TooltipContent>
          </Tooltip>
          {!collapsed && (
            <div className="overflow-hidden ml-3">
              <p className="text-sm font-medium text-sidebar-foreground truncate">
                {user || "Usuario"}
              </p>
            </div>
          )}
        </div>

        {/* Accordion for Rooms and Friends o solo iconos con popover si está retraído */}
        <div className={cn("flex-1 overflow-auto py-2", collapsed && "px-0 flex flex-col items-center gap-4")}> 
          {!collapsed ? (
            <Accordion type="multiple" className={cn("py-2", "px-2")}> 
              <AccordionItem value="rooms">
                <AccordionTrigger className="px-2">
                  <span className="flex items-center gap-2"> <MessageCircle className="h-4 w-4" /> Salas Públicas </span>
                </AccordionTrigger>
                <AccordionContent>
                  <div className="space-y-1"> 
                    {rooms.filter(r => r.room_type !== 'individual').map((room) => {
                      const isActive = currentRoom?.id === room.id;
                      const hasUnread = ((room.unread_count ?? 0) > 0) && !isActive;
                      
                      return (
                        <div key={room.id} className="relative">
                          <Button
                            variant={currentRoom?.id === room.id ? "secondary" : "ghost"}
                            className={cn(
                              "w-full text-left h-auto py-2 px-2 flex flex-col items-start",
                              "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
                              currentRoom?.id === room.id && "bg-sidebar-accent text-sidebar-accent-foreground",
                              hasUnread && "font-semibold"
                            )}
                            draggable
                            onDragStart={e => {
                              e.dataTransfer.setData('roomId', room.id);
                            }}
                            onClick={() => onRoomSelect ? onRoomSelect(room.id) : setCurrentRoom(room.id)}
                          >
                            <div className="flex items-center gap-2 w-full">
                              <MessageCircle className="h-4 w-4 shrink-0" />
                              <span className="flex-1 truncate text-sm">{room.name}</span>
                              {hasUnread && (
                                <span className="bg-primary text-primary-foreground rounded-full px-2 py-0.5 text-xs font-bold">
                                  {room.unread_count}
                                </span>
                              )}
                            </div>
                            {room.last_message && (
                              <div className="text-xs text-white/80 dark:text-muted-foreground mt-1 truncate w-full pl-6">
                                {room.last_message_username && `${room.last_message_username}: `}
                                {room.last_message}
                              </div>
                            )}
                          </Button>
                        </div>
                      );
                    })}
                  </div>
                </AccordionContent>
              </AccordionItem>
              {/* Friends Accordion */}
              <AccordionItem value="friends">
                <AccordionTrigger className="px-2">
                  <span className="flex items-center gap-2"> <Users className="h-4 w-4" /> Amigos </span>
                </AccordionTrigger>
                <AccordionContent>
                  <FriendsPanel collapsed={collapsed} onRoomSelect={onRoomSelect} />
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          ) : (
            <>
              <SidebarPopover icon={<MessageCircle className="h-6 w-6" />} label="Salas Públicas">
                <div className="space-y-1 min-w-[220px] max-w-[280px]">
                  {rooms.filter(r => r.room_type !== 'individual').map((room) => {
                    const isActive = currentRoom?.id === room.id;
                    const hasUnread = ((room.unread_count ?? 0) > 0) && !isActive;
                    
                    return (
                      <div key={room.id} className="relative">
                        <Button
                          variant={currentRoom?.id === room.id ? "secondary" : "ghost"}
                          className={cn(
                            "w-full text-left h-auto py-2 px-2 flex flex-col items-start",
                            "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
                            currentRoom?.id === room.id && "bg-sidebar-accent text-sidebar-accent-foreground",
                            hasUnread && "font-semibold"
                          )}
                          onClick={() => setCurrentRoom(room.id)}
                        >
                          <div className="flex items-center gap-2 w-full">
                            <MessageCircle className="h-4 w-4 shrink-0" />
                            <span className="flex-1 truncate text-sm">{room.name}</span>
                            {hasUnread && (
                              <span className="bg-primary text-primary-foreground rounded-full px-2 py-0.5 text-xs font-bold">
                                {room.unread_count}
                              </span>
                            )}
                          </div>
                          {room.last_message && (
                            <div className="text-xs text-white/80 dark:text-muted-foreground mt-1 truncate w-full pl-6">
                              {room.last_message_username && `${room.last_message_username}: `}
                              {room.last_message}
                            </div>
                          )}
                        </Button>
                      </div>
                    );
                  })}
                </div>
              </SidebarPopover>
              <SidebarPopover icon={<Users className="h-6 w-6" />} label="Amigos">
                <div className="min-w-[180px]">
                  <FriendsPanel collapsed={collapsed} onRoomSelect={onRoomSelect} />
                </div>
              </SidebarPopover>
            </>
          )}
        </div>

        {/* Footer */}
        <div className={cn("p-4 flex flex-col gap-2", collapsed && "items-center justify-center")}> 
          {/* Dark mode toggle */}
          <DarkModeToggle collapsed={collapsed} />
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                className={cn("w-full justify-start text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground", collapsed && "justify-center px-0")}
                onClick={handleLogout}
              >
                <LogIn className="h-4 w-4 mr-2 rotate-180" />
                {!collapsed && <span>Logout</span>}
              </Button>
            </TooltipTrigger>
            <TooltipContent side="right">Logout</TooltipContent>
          </Tooltip>
        </div>
      </div>
    </>
  );
}
