import { useCallback, useState } from "react";

type UseDualChatWindowsOptions = {
  onSingleRoom?: (roomId: string) => void;
  openIndividualChat: (friendUsername: string) => Promise<string | undefined>;
};

export function useDualChatWindows({ onSingleRoom, openIndividualChat }: UseDualChatWindowsOptions) {
  const [openRooms, setOpenRooms] = useState<string[]>([]);
  const [lastActiveIdx, setLastActiveIdx] = useState(0);

  const handleRoomSelect = useCallback((roomId: string) => {
    setOpenRooms((prev) => {
      if (prev.includes(roomId)) {
        return prev;
      }
      if (prev.length === 0) {
        return [roomId];
      }
      if (prev.length === 1) {
        return [roomId];
      }
      const newRooms = [...prev];
      newRooms[lastActiveIdx] = roomId;
      return newRooms;
    });
  }, [lastActiveIdx]);

  const handleDrop = useCallback(async (windowIdx: number, e: React.DragEvent) => {
    e.preventDefault();
    const roomId = e.dataTransfer.getData("roomId");
    let targetRoomId = roomId;
    if (!targetRoomId) {
      const friendUsername = e.dataTransfer.getData("friendUsername");
      if (friendUsername) {
        targetRoomId = await openIndividualChat(friendUsername);
      }
    }
    if (!targetRoomId) return;
    setLastActiveIdx(windowIdx);
    setOpenRooms((prev) => {
      if (prev.length === 0) return [targetRoomId];
      if (prev.length === 1 && windowIdx === 1) return [prev[0], targetRoomId];
      const newRooms = [...prev];
      newRooms[windowIdx] = targetRoomId;
      return newRooms;
    });
  }, [openIndividualChat]);

  const handleCloseWindow = useCallback((windowIdx: number) => {
    setOpenRooms((prev) => {
      const newRooms = [...prev];
      newRooms.splice(windowIdx, 1);
      if (newRooms.length === 1 && onSingleRoom) {
        onSingleRoom(newRooms[0]);
      }
      return newRooms.length ? newRooms : [];
    });
  }, [onSingleRoom]);

  return {
    openRooms,
    lastActiveIdx,
    setLastActiveIdx,
    handleRoomSelect,
    handleDrop,
    handleCloseWindow,
  };
}
