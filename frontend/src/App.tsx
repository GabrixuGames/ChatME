import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate, useLocation } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import { ChatProvider } from "./contexts/ChatContext";
import Chat from "./pages/Chat";
import NotFound from "./pages/NotFound";
import AuthPage from "./pages/Auth";
import BubbleBackgroundGlobal from "@/components/BubbleBackgroundGlobal";

const queryClient = new QueryClient();

import { FriendsProvider } from "./contexts/FriendsContext";

import { useState } from "react";
import { DarkModeProvider } from "./hooks/useDarkMode.tsx";

function AppContent() {
  const location = useLocation();
  const showBubbles = location.pathname === "/" || location.pathname === "/login";
  return (
    <div className="relative min-h-screen">
      {showBubbles && <BubbleBackgroundGlobal />}
      <Routes>
        <Route path="/" element={<AuthPage />} />
        <Route path="/chat/:username" element={<Chat />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </div>
  );
}

const App = () => {
  return (
    <DarkModeProvider>
      <QueryClientProvider client={queryClient}>
        <TooltipProvider>
          <Toaster />
          <Sonner />
          <AuthProvider>
            <ChatProvider>
              <FriendsProvider>
                <BrowserRouter>
                  <AppContent />
                </BrowserRouter>
              </FriendsProvider>
            </ChatProvider>
          </AuthProvider>
        </TooltipProvider>
      </QueryClientProvider>
    </DarkModeProvider>
  );
};

export default App;
