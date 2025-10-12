from repositories.base_repository import UserRepository
import datetime

user_repo = UserRepository()

for i in range(1, 11):
    username = f"user{i}"
    email = f"{username}@test.com"
    password = username  # La contraseña es igual al nombre
    created_id = user_repo.create_user(username, email, password)
    print(f"Usuario creado: {username} (ID: {created_id})")
