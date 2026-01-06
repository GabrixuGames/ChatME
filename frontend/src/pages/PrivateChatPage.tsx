import React, { useEffect, useState } from 'react';
import { createPrivateChat, findChatBetweenUsers } from '../api/privateChat';
import { PrivateChatWindow } from '../components/PrivateChatWindow';


interface PrivateChatPageProps {
  user1Username: string; // Username actual
  user2Username: string; // Username con quien se inicia el chat
}


const PrivateChatPage: React.FC<PrivateChatPageProps> = ({ user1Username, user2Username }) => {
  const [chatId, setChatId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initChat = async () => {
      // Buscar si ya existe un chat entre los usuarios
      let chat = await findChatBetweenUsers(user1Username, user2Username);
      if (!chat || chat.error) {
        // Si no existe, crear uno nuevo
        chat = await createPrivateChat(user1Username, user2Username);
      }
      setChatId(chat.chat_id || chat.id || null);
      setLoading(false);
    };
    initChat();
  }, [user1Username, user2Username]);

  if (loading) return <div>Cargando chat...</div>;
  if (!chatId) return <div>No se pudo crear el chat privado.</div>;

  return (
    <div className="private-chat-page">
      <PrivateChatWindow chatId={chatId} currentUserId={user1Username} otherUsername={user2Username} />
    </div>
  );
};

export default PrivateChatPage;
