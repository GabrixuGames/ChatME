
import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { ChatSidebar } from "@/components/ChatSidebar";
import { ChatRoom } from "@/components/ChatRoom";
import { ChatInput } from "@/components/ChatInput";

 const Chat = () => {
  const { isAuthenticated } = useAuth();
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
  const [openSidebar, setOpenSidebar] = React.useState(false);
  return (
  <div className="fixed inset-0 flex flex-col sm:flex-row overflow-hidden" style={{height: '100dvh', width: '100vw'}}>
      <ChatSidebar showMobileMenu={openSidebar} setShowMobileMenu={setOpenSidebar} />
      <div className="flex-1 flex flex-col bg-white/90 sm:bg-transparent h-full min-h-0">
        <div className="flex-1 min-h-0 px-0 py-0 sm:px-4 sm:py-4">
          <ChatRoom openSidebar={() => setOpenSidebar(true)} />
        </div>
        <div className="p-0 sm:p-4 bg-white/95" style={{borderTop: 'none', marginBottom: 0}}>
          <ChatInput />
        </div>
      </div>
    </div>
  );
};

export default Chat;
