#!/usr/bin/env python3
"""
Test de integración completa del sistema de autenticación con bcrypt
"""

import sys
import os
import uuid
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.auth_service import AuthService
from repositories.base_repository import UserRepository

def test_complete_auth_flow():
    """Test completo del flujo de autenticación"""
    
    print("🔐 Test Completo de Autenticación con Bcrypt")
    print("=" * 50)
    
    auth_service = AuthService()
    user_repo = UserRepository()
    
    # Test 1: Crear nuevo usuario
    print("📝 Test 1: Creación de usuario")
    test_username = f"test_auth_{uuid.uuid4().hex[:8]}"
    test_email = f"{test_username}@auth.com"
    test_password = "SecurePassword123!"
    
    # Verificar si usuario ya existe y eliminarlo
    existing_user = user_repo.find_by_username(test_username)
    if existing_user:
        print(f"⚠️  Usuario {test_username} ya existe, eliminando...")
        # Marcar como inactivo en lugar de eliminar
        user_repo.execute_query("UPDATE users SET is_active = false WHERE username = %s", (test_username,))
    
    # Crear nuevo usuario
    user_id = auth_service.register_user(test_username, test_email, test_password)
    
    if user_id:
        print(f"✅ Usuario creado exitosamente con ID: {user_id}")
    else:
        print("❌ Error creando usuario")
        assert False
    
    # Test 2: Autenticación con password correcto
    print("\n🔑 Test 2: Autenticación con password correcto")
    auth_result = auth_service.authenticate_user(test_username, test_password)
    
    if auth_result:
        print(f"✅ Autenticación exitosa: {auth_result['username']}")
    else:
        print("❌ Error en autenticación con password correcto")
        assert False
    
    # Test 3: Autenticación con password incorrecto
    print("\n❌ Test 3: Autenticación con password incorrecto")
    wrong_result = auth_service.authenticate_user(test_username, "WrongPassword!")
    
    if not wrong_result:
        print("✅ Autenticación incorrecta rechazada correctamente")
    else:
        print("❌ Autenticación con password incorrecto debería fallar")
        assert False
    
    # Test 4: Verificar que el password está hasheado en BD
    print("\n🔍 Test 4: Verificación de hash en base de datos")
    stored_user = user_repo.find_by_username(test_username)
    
    if stored_user:
        stored_hash = stored_user['password_hash']
        if stored_hash.startswith('$2b$'):
            print("✅ Password almacenado como hash bcrypt")
        else:
            print("❌ Password no está hasheado correctamente")
            assert False
    else:
        print("❌ No se encontró el usuario almacenado")
        assert False
    
    # Test 5: Verificar que el hash original coincide
    print("\n🔐 Test 5: Verificación directa de hash")
    hash_matches = AuthService._verify_password(test_password, stored_hash)
    
    if hash_matches:
        print("✅ Verificación directa de hash exitosa")
    else:
        print("❌ Error en verificación directa de hash")
        assert False
    
    # Test 6: Intentar crear usuario duplicado
    print("\n🚫 Test 6: Creación de usuario duplicado")
    duplicate_id = auth_service.register_user(test_username, "other@user.com", "AnotherPassword!")
    
    if duplicate_id is None:
        print("✅ Usuario duplicado correctamente rechazado")
    else:
        print("❌ No se permitió crear usuario duplicado")
        assert False
    
    # Limpiar: marcar usuario como inactivo
    print("\n🧹 Test 7: Limpieza de datos de prueba")
    cleanup_success = user_repo.execute_query(
        "UPDATE users SET is_active = false WHERE username = %s", 
        (test_username,)
    )
    
    if cleanup_success is not None:
        print("✅ Datos de prueba limpiados correctamente")
    else:
        print("⚠️  No se pudo limpiar datos de prueba")
    
    print("\n" + "=" * 50)
    print("🎉 TODOS LOS TESTS DE AUTENTICACIÓN PASARON")
    print("✅ Sistema de password hashing con bcrypt implementado correctamente")

if __name__ == "__main__":
    test_complete_auth_flow()
    sys.exit(0)
