import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { useAuth } from "@/contexts/AuthContext";

export interface Friend {
  id: string;
  username: string;
  profile_pic?: string;
}

export interface FriendRequest {
  id: string;
  sender_id: string;
  receiver_id: string;
  status: string;
  created_at: string;
  responded_at?: string;
  sender_username?: string;
}

interface FriendsContextType {
  friends: Friend[];
  pendingRequests: FriendRequest[];
  sentRequests: FriendRequest[];
  sendRequest: (receiver_id: string) => Promise<void>;
  respondRequest: (request_id: string, status: string) => Promise<void>;
  removeFriend: (friend_id: string) => Promise<void>;
  refresh: () => void;
}

const FriendsContext = createContext<FriendsContextType | undefined>(undefined);

export const FriendsProvider = ({ children }: { children: React.ReactNode }) => {
  const [friends, setFriends] = useState<Friend[]>([]);
  const [pendingRequests, setPendingRequests] = useState<FriendRequest[]>([]);
  const [sentRequests, setSentRequests] = useState<FriendRequest[]>([]);
  const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";
  const { token } = useAuth();

  const fetchWithAuth = useCallback(
    async (path: string, options: RequestInit = {}) => {
      if (!token) {
        throw new Error("No token disponible");
      }
      const res = await fetch(`${API_URL}${path}`, {
        ...options,
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
          ...(options.headers || {})
        }
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data?.error || "Error de red");
      }
      return data;
    },
    [API_URL, token]
  );

  const refresh = useCallback(async () => {
    if (!token) {
      console.warn('⚠️ No hay token disponible, no se pueden cargar amigos');
      return;
    }
    
    try {
      const [friendsData, pendingData, sentData] = await Promise.all([
        fetchWithAuth("/friends/list"),
        fetchWithAuth("/friends/pending"),
        fetchWithAuth("/friends/sent")
      ]);
      setFriends(friendsData.friends || []);
      setPendingRequests(pendingData.pending_requests || []);
      setSentRequests(sentData.sent_requests || []);
    } catch (error) {
      console.error('❌ Error al actualizar amigos:', error);
    }
  }, [token, fetchWithAuth]);

  useEffect(() => { refresh(); }, [token, refresh]);

  // Escuchar eventos personalizados de window (disparados desde ChatContext)
  useEffect(() => {
    const handleFriendRequestAccepted = (event: Event) => {
      const data = (event as CustomEvent).detail;
      refresh();
    };

    const handleFriendRequestReceived = (event: Event) => {
      const data = (event as CustomEvent).detail;
      refresh();
    };

    window.addEventListener('friendRequestAccepted', handleFriendRequestAccepted);
    window.addEventListener('friendRequestReceived', handleFriendRequestReceived);

    return () => {
      window.removeEventListener('friendRequestAccepted', handleFriendRequestAccepted);
      window.removeEventListener('friendRequestReceived', handleFriendRequestReceived);
    };
  }, [refresh]);

  const sendRequest = async (receiver_id: string) => {
    await fetchWithAuth("/friends/send_request", {
      method: "POST",
      body: JSON.stringify({ receiver_id })
    });
    await refresh();
  };

  const respondRequest = async (request_id: string, status: string) => {
    await fetchWithAuth("/friends/respond_request", {
      method: "POST",
      body: JSON.stringify({ request_id, status })
    });
    await refresh();
  };

  const removeFriend = async (friend_id: string) => {
    await fetchWithAuth("/friends/remove", {
      method: "POST",
      body: JSON.stringify({ friend_id })
    });
    await refresh();
  };

  return (
    <FriendsContext.Provider value={{ friends, pendingRequests, sentRequests, sendRequest, respondRequest, removeFriend, refresh }}>
      {children}
    </FriendsContext.Provider>
  );
};

export const useFriends = () => {
  const context = useContext(FriendsContext);
  if (!context) throw new Error("useFriends must be used within a FriendsProvider");
  return context;
};
