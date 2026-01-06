import React, { useState } from 'react';
import { sendPrivateMessage } from '../api/privateChat';

interface PrivateChatInputProps {
  chatId: string;
  onSend: () => void;
}

const PrivateChatInput: React.FC<PrivateChatInputProps> = ({ chatId, onSend }) => {
  const [content, setContent] = useState('');

  const handleSend = async () => {
    if (!content.trim()) return;
    // TODO: Obtener sender_id del contexto de usuario
    const sender_id = localStorage.getItem('user_id') || '';
    await sendPrivateMessage(chatId, sender_id, content);
    setContent('');
    onSend();
  };

  return (
    <div className="private-chat-input">
      <input
        type="text"
        value={content}
        onChange={e => setContent(e.target.value)}
        placeholder="Escribe un mensaje..."
      />
      <button onClick={handleSend}>Enviar</button>
    </div>
  );
};

export default PrivateChatInput;
