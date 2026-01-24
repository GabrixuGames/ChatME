import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import axios from "axios";
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

  const refresh = useCallback(async () => {
    if (!token) {
      console.warn('⚠️ No hay token disponible, no se pueden cargar amigos');
      return;
    }
    
    const authHeader = { Authorization: `Bearer ${token}` };
    
    try {
      const [friendsRes, pendingRes, sentRes] = await Promise.all([
        axios.get(`${API_URL}/friends/list`, { headers: authHeader }),
        axios.get(`${API_URL}/friends/pending`, { headers: authHeader }),
        axios.get(`${API_URL}/friends/sent`, { headers: authHeader })
      ]);
      setFriends(friendsRes.data.friends || []);
      setPendingRequests(pendingRes.data.pending_requests || []);
      setSentRequests(sentRes.data.sent_requests || []);
    } catch (error) {
      console.error('❌ Error al actualizar amigos:', error);
    }
  }, [token, API_URL]);

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
    const authHeader = token ? { Authorization: `Bearer ${token}` } : {};
    await axios.post(`${API_URL}/friends/send_request`, { receiver_id }, { headers: authHeader });
    await refresh();
  };

  const respondRequest = async (request_id: string, status: string) => {
    const authHeader = token ? { Authorization: `Bearer ${token}` } : {};
    await axios.post(`${API_URL}/friends/respond_request`, { request_id, status }, { headers: authHeader });
    await refresh();
  };

  const removeFriend = async (friend_id: string) => {
    const authHeader = token ? { Authorization: `Bearer ${token}` } : {};
    await axios.post(`${API_URL}/friends/remove`, { friend_id }, { headers: authHeader });
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
