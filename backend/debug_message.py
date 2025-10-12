from services.chat_service import ChatService
from repositories.base_repository import UserRepository, RoomRepository
import logging

# Configurar logging para ver más detalles
logging.basicConfig(level=logging.DEBUG)

def test_send_message():
    print("=== INICIANDO PRUEBA DE ENVÍO DE MENSAJE ===")
    
    chat_service = ChatService()
    user_repo = UserRepository()
    room_repo = RoomRepository()
    
    # Verificar que existan el usuario y la sala
    username = "user1"
    room_id = "R1"
    content = "Mensaje de prueba debug"
    
    print(f"1. Verificando usuario: {username}")
    user = user_repo.find_by_username(username)
    if user:
        print(f"   ✅ Usuario encontrado: {user}")
    else:
        print(f"   ❌ Usuario NO encontrado")
        # Crear usuario si no existe
        print(f"   Creando usuario...")
        user_id = user_repo.create_user(username, "password", "user1@test.com")
        if user_id:
            print(f"   ✅ Usuario creado con ID: {user_id}")
            user = user_repo.find_by_username(username)
        else:
            print(f"   ❌ Error creando usuario")
            return
    
    print(f"2. Verificando sala: {room_id}")
    room = room_repo.find_by_id(room_id)
    if room:
        print(f"   ✅ Sala encontrada: {room}")
    else:
        print(f"   ❌ Sala NO encontrada")
        return
    
    print(f"3. Intentando enviar mensaje...")
    result = chat_service.send_message(username, room_id, content)
    
    if result:
        print(f"   ✅ Mensaje enviado exitosamente:")
        print(f"   ID: {result['id']}")
        print(f"   Contenido: {result['content']}")
        print(f"   Usuario: {result['username']}")
        print(f"   Sala: {result['roomId']}")
    else:
        print(f"   ❌ Error enviando mensaje")

if __name__ == "__main__":
    test_send_message()