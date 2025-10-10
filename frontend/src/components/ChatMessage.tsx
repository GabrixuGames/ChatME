import { Message } from "@/contexts/ChatContext";
import { cn } from "@/lib/utils";
import { format } from "date-fns";
import { User } from "lucide-react";

interface ChatMessageProps {
  message: Message;
  isCurrentUser: boolean;
}

export function ChatMessage({ message, isCurrentUser }: ChatMessageProps) {
  const { username, content, timestamp } = message;  // 'content' es el mensaje
  
  const formattedTime = format(new Date(timestamp), 'h:mm a');
  const formattedDate = format(new Date(timestamp), 'MMM d');
  
  const isSystem = message.username === "system";  // Comprobación para mensaje del sistema

  // Estilo para el mensaje del sistema
  if (isSystem) {
    return (
      <div className="flex justify-center my-4">
        <div className="bg-muted rounded-md py-2 px-4 text-sm text-muted-foreground max-w-md">
          {content}
        </div>
      </div>
    );
  }

  return (
    <div
      className={cn(
        "flex items-start gap-2 group mb-4",
        isCurrentUser ? "justify-end" : "justify-start"
      )}
    >
      {!isCurrentUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary flex items-center justify-center text-primary-foreground">
          <User className="w-4 h-4" />
        </div>
      )}
      
      <div className="flex flex-col max-w-[70%]">
        {!isCurrentUser && (
          <span className="text-xs font-medium text-foreground mb-1">{username}</span>
        )}
        
        <div
          className={cn(
            "rounded-lg py-2 px-3",
            isCurrentUser
              ? "bg-secondary text-secondary-foreground rounded-tr-none"
              : "bg-accent bg-opacity-20 text-foreground rounded-tl-none"
          )}
        >
          <p className="text-sm">{content}</p>
        </div>
        
        <span className="text-xs text-muted-foreground mt-1 opacity-70">
          {formattedTime} · {formattedDate}
        </span>
      </div>
      
      {isCurrentUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-secondary flex items-center justify-center text-secondary-foreground">
          <User className="w-4 h-4" />
        </div>
      )}
    </div>
  );
}
