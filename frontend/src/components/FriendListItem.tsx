import React from 'react';

interface FriendListItemProps {
  friendId: string;
  friendName: string;
  avatarUrl?: string;
  onStartPrivateChat: (friendId: string) => void;
}

const FriendListItem: React.FC<FriendListItemProps> = ({ friendId, friendName, avatarUrl, onStartPrivateChat }) => {
  return (
    <button className="friend-list-item" onClick={() => onStartPrivateChat(friendId)}>
      <img src={avatarUrl || '/default-avatar.png'} alt={friendName} className="avatar" />
      <span className="friend-name">{friendName}</span>
    </button>
  );
};

export default FriendListItem;
