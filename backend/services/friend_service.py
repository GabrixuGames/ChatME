from repositories.friend_repository import FriendRepository

class FriendService:
    def remove_friend(self, user_id: str, friend_id: str) -> bool:
        return self.repo.remove_friend(user_id, friend_id)
    def __init__(self):
        self.repo = FriendRepository()

    def send_request(self, sender_id: str, receiver_id: str) -> str:
        return self.repo.send_request(sender_id, receiver_id)

    def respond_request(self, request_id: str, status: str) -> bool:
        return self.repo.respond_request(request_id, status)

    def get_pending_requests(self, user_id: str):
        return self.repo.get_pending_requests(user_id)

    def get_sent_requests(self, user_id: str):
        return self.repo.get_sent_requests(user_id)

    def get_friends(self, user_id: str):
        return self.repo.get_friends(user_id)

    def search_users(self, query_str: str, exclude_ids: list, limit: int = 10):
        return self.repo.search_users(query_str, exclude_ids, limit)
