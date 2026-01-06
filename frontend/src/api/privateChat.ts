// API para chat privado
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export async function createPrivateChat(user1_username: string, user2_username: string, is_temporary = true) {
  const token = localStorage.getItem('token');
  const res = await fetch(`${API_URL}/private-chats`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {})
    },
    body: JSON.stringify({ user1_username, user2_username, is_temporary }),
    credentials: 'include'
  });
  return res.json();
}

export async function getPrivateChat(chat_id: string) {
  const token = localStorage.getItem('token');
  const res = await fetch(`${API_URL}/private-chats/${chat_id}`, {
    headers: {
      ...(token ? { 'Authorization': `Bearer ${token}` } : {})
    },
    credentials: 'include'
  });
  return res.json();
}

export async function findChatBetweenUsers(user1_username: string, user2_username: string) {
  const token = localStorage.getItem('token');
  const res = await fetch(`${API_URL}/private-chats/between/${user1_username}/${user2_username}`, {
    headers: {
      ...(token ? { 'Authorization': `Bearer ${token}` } : {})
    },
    credentials: 'include'
  });
  return res.json();
}

export async function sendPrivateMessage(chat_id: string, sender_id: string, content: string) {
  const token = localStorage.getItem('token');
  const res = await fetch(`${API_URL}/private-messages`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {})
    },
    body: JSON.stringify({ chat_id, sender_id, content }),
    credentials: 'include'
  });
  return res.json();
}

export async function getPrivateMessages(chat_id: string, limit = 50, offset = 0) {
  const token = localStorage.getItem('token');
  const res = await fetch(`${API_URL}/private-messages/${chat_id}?limit=${limit}&offset=${offset}`, {
    headers: {
      ...(token ? { 'Authorization': `Bearer ${token}` } : {})
    },
    credentials: 'include'
  });
  return res.json();
}
