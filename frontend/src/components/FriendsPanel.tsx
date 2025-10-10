import React from "react";
import { useFriends } from "@/contexts/FriendsContext";
import { Button } from "@/components/ui/button";
import { AddFriendDialog } from "./AddFriendDialog";
import { Check, X, Trash2 } from "lucide-react";

interface FriendsPanelProps {
  collapsed?: boolean;
}

export const FriendsPanel: React.FC<FriendsPanelProps> = ({ collapsed }) => {
  const { friends, pendingRequests, respondRequest, removeFriend, refresh } = useFriends();

  return (
  <div className={collapsed ? "space-y-2 flex flex-col" : "space-y-4"}>
      <div>
        {friends.length === 0 && <div className="text-xs px-2 py-1 text-muted-foreground">No tienes amigos aún.</div>}
        {friends.map((f) => (
          <div key={f.id} className="flex items-center px-2 py-1 text-sidebar-foreground bg-sidebar rounded w-full">
            <div className="flex items-center min-w-0 flex-1">
              {f.profile_pic ? (
                <img src={f.profile_pic} alt={f.username} className="w-7 h-7 rounded-full object-cover mr-2 border border-sidebar-border" />
              ) : (
                <div className="w-7 h-7 rounded-full bg-sidebar-accent text-white flex items-center justify-center mr-2 border border-sidebar-border">
                  {f.username.charAt(0).toUpperCase()}
                </div>
              )}
              <span className="truncate text-sidebar-foreground text-left">{f.username}</span>
            </div>
            <Button size="icon" variant="ghost" className="bg-red-100 text-red-700 hover:bg-red-200 p-1 h-6 w-6 ml-2" onClick={() => removeFriend(f.id)}>
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
