#!/usr/bin/env python3
"""
Test funcional completo del FriendRepository después de la refactorización
"""

import sys
import os
import uuid
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from repositories.friend_repository import FriendRepository
from repositories.base_repository import UserRepository

def test_friend_repository_functionality():
    """Test completo de funcionalidad del FriendRepository"""
    
    print("🧪 Test Funcional FriendRepository Refactorizado")
    print("=" * 50)
    
    friend_repo = FriendRepository()
    user_repo = UserRepository()
    
    # Crear usuarios de prueba
    print("👥 Preparando usuarios de prueba...")
    usernames = [f"test_friend_{uuid.uuid4().hex[:8]}" for i in range(3)]
    user_ids = []
    
    for username in usernames:
        # Crear nuevo usuario con nombre único
        try:
            user_id = user_repo.create_user(username, f"{username}@test.com", "TestPassword123!")
            user_ids.append(user_id)
            print(f"✅ Usuario creado: {username}")
        except Exception as e:
            print(f"⚠️  Error creando usuario {username}: {e}")
            assert False
    
    print(f"✅ Usuarios de prueba: {len(user_ids)} creados/encontrados")
    
    try:
        # Test 1: Enviar solicitud de amistad
        print("\n📨 Test 1: Enviar solicitud de amistad")
        request_id = friend_repo.send_request(user_ids[0], user_ids[1])
        
        if request_id:
            print(f"✅ Solicitud enviada: {request_id}")
        else:
            print("❌ Error enviando solicitud")
            assert False
        
        # Test 2: Verificar duplicado de solicitud
        print("\n🚫 Test 2: Evitar duplicado de solicitud")
        duplicate_id = friend_repo.send_request(user_ids[0], user_ids[1])
        
        if duplicate_id is None:
            print("✅ Duplicado correctamente evitado")
        else:
            print("❌ Se permitió duplicar solicitud")
            assert False
        
        # Test 3: Obtener solicitudes pendientes
        print("\n📬 Test 3: Obtener solicitudes pendientes")
        pending = friend_repo.get_pending_requests(user_ids[1])
        
        if pending and len(pending) > 0:
            print(f"✅ Solicitudes pendientes: {len(pending)}")
            print(f"✅ De: {pending[0]['sender_username']}")
        else:
            print("❌ No se encontraron solicitudes pendientes")
            assert False
        
        # Test 4: Obtener solicitudes enviadas
        print("\n📤 Test 4: Obtener solicitudes enviadas")
        sent = friend_repo.get_sent_requests(user_ids[0])
        
        if sent and len(sent) > 0:
            print(f"✅ Solicitudes enviadas: {len(sent)}")
        else:
            print("❌ No se encontraron solicitudes enviadas")
            assert False
        
        # Test 5: Verificar estado de solicitud
        print("\n🔍 Test 5: Verificar estado de solicitud")
        status = friend_repo.get_request_status(user_ids[0], user_ids[1])
        
        if status == 'pending':
            print(f"✅ Estado correcto: {status}")
        else:
            print(f"❌ Estado incorrecto: {status}")
            assert False
        
        # Test 6: Aceptar solicitud
        print("\n✅ Test 6: Aceptar solicitud")
        accept_result = friend_repo.respond_request(request_id, 'accepted')
        
        if accept_result:
            print("✅ Solicitud aceptada correctamente")
        else:
            print("❌ Error aceptando solicitud")
            assert False
        
        # Test 7: Verificar amistad
        print("\n🤝 Test 7: Verificar amistad establecida")
        are_friends = friend_repo.are_friends(user_ids[0], user_ids[1])
        
        if are_friends:
            print("✅ Amistad verificada correctamente")
        else:
            print("❌ Amistad no establecida")
            assert False
        
        # Test 8: Obtener lista de amigos
        print("\n👥 Test 8: Obtener lista de amigos")
        friends = friend_repo.get_friends(user_ids[0])
        
        if friends and len(friends) > 0:
            print(f"✅ Amigos encontrados: {len(friends)}")
            print(f"✅ Amigo: {friends[0]['username']}")
        else:
            print("❌ No se encontraron amigos")
            assert False
        
        # Test 9: Buscar usuarios
        print("\n🔍 Test 9: Buscar usuarios")
        search_results = friend_repo.search_users("test_friend", [user_ids[0]], 10)
        
        if search_results and len(search_results) > 0:
            print(f"✅ Resultados búsqueda: {len(search_results)}")
            # Verificar que user_ids[0] esté excluido
            excluded_found = any(user['id'] == user_ids[0] for user in search_results)
            if not excluded_found:
                print("✅ Exclusión de ID funcionando")
            else:
                print("❌ Exclusión de ID no funcionando")
                assert False
        else:
            print("❌ Error en búsqueda")
            assert False
        
        # Test 10: Remover amigo
        print("\n🗑️ Test 10: Remover amigo")
        remove_result = friend_repo.remove_friend(user_ids[0], user_ids[1])
        
        if remove_result:
            print("✅ Amigo removido correctamente")
        else:
            print("❌ Error removiendo amigo")
            assert False
        
        # Test 11: Verificar que ya no son amigos
        print("\n❌ Test 11: Verificar amistad eliminada")
        still_friends = friend_repo.are_friends(user_ids[0], user_ids[1])
        
        if not still_friends:
            print("✅ Amistad correctamente eliminada")
        else:
            print("❌ Amistad persiste después de eliminación")
            assert False
        
        print("\n" + "=" * 50)
        print("🎉 TODOS LOS TESTS FUNCIONALES PASARON")
        print("✅ FriendRepository refactorizado funciona correctamente")
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        assert False
    
    finally:
        # Limpiar datos de prueba
        print("\n🧹 Limpiando datos de prueba...")
        for i, username in enumerate(usernames):
            if i < len(user_ids):
                try:
                    user_repo.execute_query(
                        "UPDATE users SET is_active = false WHERE id = %s", 
                        (user_ids[i],)
                    )
                    print(f"✅ Usuario {username} desactivado")
                except Exception as e:
                    print(f"⚠️  Error limpiando {username}: {e}")

if __name__ == "__main__":
    test_friend_repository_functionality()
    sys.exit(0)
