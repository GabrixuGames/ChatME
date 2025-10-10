
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { useChat } from "@/contexts/ChatContext";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { MessageCircle, LogIn, User, Users } from "lucide-react";
import { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider } from "@/components/ui/tooltip";
import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from "@/components/ui/accordion";
import { FriendsPanel } from "./FriendsPanel";
import { SidebarPopover } from "./SidebarPopover";

export function ChatSidebar() {
  const { user, logout } = useAuth();
  const { rooms, currentRoom, setCurrentRoom, goToWelcome } = useChat();
  const navigate = useNavigate();
  const [collapsed, setCollapsed] = useState(false);

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <TooltipProvider>
      <div
        className={cn(
          "flex flex-col h-full bg-sidebar transition-all duration-300 border-r border-sidebar-border",
          collapsed ? "w-16 items-center" : "w-64"
        )}
      >
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
                <span className="flex items-center gap-2"> <MessageCircle className="h-4 w-4" /> Salas </span>
              </AccordionTrigger>
              <AccordionContent>
                <div className="space-y-1"> 
                  {rooms.map((room) => (
                    <Button
                      key={room.id}
                      variant={currentRoom?.id === room.id ? "secondary" : "ghost"}
                      className={cn(
                        "w-full justify-start text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
                        currentRoom?.id === room.id && "bg-sidebar-accent text-sidebar-accent-foreground"
                      )}
                      onClick={() => setCurrentRoom(room.id)}
                    >
                      <MessageCircle className="h-4 w-4" />
                      <span className="ml-2">{room.name}</span>
                    </Button>
                  ))}
                </div>
              </AccordionContent>
            </AccordionItem>
            {/* Friends Accordion */}
            <AccordionItem value="friends">
              <AccordionTrigger className="px-2">
                <span className="flex items-center gap-2"> <Users className="h-4 w-4" /> Amigos </span>
              </AccordionTrigger>
              <AccordionContent>
                <FriendsPanel collapsed={collapsed} />
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        ) : (
          <>
            <SidebarPopover icon={<MessageCircle className="h-6 w-6" />} label="Salas">
              <div className="space-y-1 min-w-[180px]">
                {rooms.map((room) => (
                  <Button
                    key={room.id}
                    variant={currentRoom?.id === room.id ? "secondary" : "ghost"}
                    className={cn(
                      "w-full justify-start text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
                      currentRoom?.id === room.id && "bg-sidebar-accent text-sidebar-accent-foreground"
                    )}
                    onClick={() => setCurrentRoom(room.id)}
                  >
                    <MessageCircle className="h-4 w-4" />
                    <span className="ml-2">{room.name}</span>
                  </Button>
                ))}
              </div>
            </SidebarPopover>
            <SidebarPopover icon={<Users className="h-6 w-6" />} label="Amigos">
              <div className="min-w-[180px]">
                <FriendsPanel collapsed={collapsed} />
              </div>
            </SidebarPopover>
          </>
        )}
      </div>

      {/* Footer */}
      <div className={cn("p-4", collapsed && "flex justify-center")}> 
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
    </TooltipProvider>
  );
}
