
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { useChat } from "@/contexts/ChatContext";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { MessageCircle, LogIn, User } from "lucide-react";

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
    <div
      className={cn(
        "flex flex-col h-full bg-sidebar transition-all duration-300 border-r border-sidebar-border",
        collapsed ? "w-16" : "w-64"
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-sidebar-border">
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
            <span>☰</span>
          )}
        </Button>
      </div>

      {/* User info section - Entre ChatME! y las salas */}
      {!collapsed && (
        <div className="px-4 py-3 border-b border-sidebar-border">
          <div className="flex items-center">
            <div className="flex items-center justify-center w-8 h-8 rounded-full bg-sidebar-accent text-sidebar-accent-foreground mr-3">
              <User className="h-4 w-4" />
            </div>
            <div className="overflow-hidden">
              <p className="text-sm font-medium text-sidebar-foreground truncate">
                {user || "Usuario"}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Room list */}
      <div className="flex-1 overflow-auto py-2">
        <div className={cn("py-2", !collapsed && "px-2")}>
          {!collapsed && (
            <h2 className="text-xs font-semibold text-sidebar-foreground opacity-60 uppercase tracking-wider px-2 mb-2">
              Rooms
            </h2>
          )}
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
                <MessageCircle className="h-4 w-4 mr-2" />
                {!collapsed && <span>{room.name}</span>}
              </Button>
            ))}
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-sidebar-border">
        <Button
          variant="ghost"
          className="w-full justify-start text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
          onClick={handleLogout}
        >
          <LogIn className="h-4 w-4 mr-2 rotate-180" />
          {!collapsed && <span>Logout</span>}
        </Button>
      </div>
    </div>
  );
}
