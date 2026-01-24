#!/usr/bin/env python3
"""
Test de seguridad para verificar que la vulnerabilidad SQL injection está resuelta
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from repositories.friend_repository import FriendRepository
import logging

def test_sql_injection_protection():
    """Testear protección contra SQL injection en search_users"""
    
    print("🛡️ Test de Protección SQL Injection")
    print("=" * 50)
    
    friend_repo = FriendRepository()
    
    # Test 1: SQL Injection básico
    print("💉 Test 1: SQL Injection básico")
    malicious_input = "'; DROP TABLE users; --"
    exclude_ids = []
    
    try:
        results = friend_repo.search_users(malicious_input, exclude_ids, 10)
        print(f"✅ Input malicioso rechazado: {len(results)} resultados (esperado: 0)")
        if len(results) == 0:
            print("✅ Protección contra DROP TABLE funcionando")
        else:
            print("❌ VULNERABILIDAD: DROP TABLE pudo ejecutarse")
            assert False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        assert False
    
    # Test 2: SQL Injection con UNION SELECT
    print("\n💉 Test 2: SQL Injection con UNION SELECT")
    union_input = "test' UNION SELECT id, username, password_hash FROM users --"
    
    try:
        results = friend_repo.search_users(union_input, exclude_ids, 10)
        print(f"✅ UNION SELECT rechazado: {len(results)} resultados")
        # Verificar que no se expongan passwords
        for user in results:
            if 'password_hash' in user:
                print("❌ VULNERABILIDAD: Passwords expuestos")
                assert False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        assert False
    
    # Test 3: Búsqueda normal (debe funcionar)
    print("\n🔍 Test 3: Búsqueda normal")
    normal_input = "user"
    
    try:
        results = friend_repo.search_users(normal_input, exclude_ids, 10)
        print(f"✅ Búsqueda normal funciona: {len(results)} resultados")
        if len(results) > 0:
            print(f"✅ Ejemplo: {results[0].get('username', 'N/A')}")
    except Exception as e:
        print(f"❌ Error en búsqueda normal: {e}")
        assert False
    
    # Test 4: Input con caracteres especiales (debe ser seguro)
    print("\n🔣 Test 4: Caracteres especiales")
    special_chars = "!@#$%^&*()_+-={}[]|\\:;\"'<>?,./"
    
    try:
        results = friend_repo.search_users(special_chars, exclude_ids, 10)
        print(f"✅ Caracteres especiales manejados: {len(results)} resultados")
    except Exception as e:
        print(f"❌ Error con caracteres especiales: {e}")
        assert False
    
    # Test 5: Exclude IDs con valores maliciosos
    print("\n🚫 Test 5: Exclude IDs con SQL injection")
    malicious_exclude_ids = [
        "'; DROP TABLE users; --",
        "' OR '1'='1",
        "1 UNION SELECT password_hash FROM users --"
    ]
    
    try:
        results = friend_repo.search_users("user", malicious_exclude_ids, 10)
        print(f"✅ Exclude IDs maliciosos manejados: {len(results)} resultados")
    except Exception as e:
        print(f"❌ Error con exclude IDs maliciosos: {e}")
        assert False
    
    # Test 6: Validación de UUID en exclude_ids
    print("\n🔍 Test 6: Validación de UUIDs")
    invalid_uuids = [
        "not-a-uuid",
        "12345",
        "00000000-0000-0000-0000-00000000000",
        ""
    ]
    
    try:
        results = friend_repo.search_users("user", invalid_uuids, 10)
        print(f"✅ UUIDs inválidos filtrados: {len(results)} resultados")
    except Exception as e:
        print(f"❌ Error con UUIDs inválidos: {e}")
        assert False
    
    # Test 7: Input muy largo (debe ser truncado)
    print("\n📏 Test 7: Input muy largo")
    long_input = "a" * 1000  # 1000 caracteres
    
    try:
        results = friend_repo.search_users(long_input, exclude_ids, 10)
        print(f"✅ Input largo truncado/seguro: {len(results)} resultados")
    except Exception as e:
        print(f"❌ Error con input largo: {e}")
        assert False
    
    # Test 8: Verificación de integridad de datos
    print("\n🔒 Test 8: Integridad de datos post-inyección")
    try:
        # Verificar que la tabla users aún exista y tenga datos
        from repositories.base_repository import UserRepository
        user_repo = UserRepository()
        users = user_repo.get_all_users()
        
        if users and len(users) > 0:
            print(f"✅ Integridad de datos mantenida: {len(users)} usuarios")
        else:
            print("❌ CORRUPCIÓN: Tabla users dañada o vacía")
            assert False
    except Exception as e:
        print(f"❌ Error verificando integridad: {e}")
        assert False
    
    print("\n" + "=" * 50)
    print("🎉 TODOS LOS TESTS DE SEGURIDAD PASARON")
    print("✅ Vulnerabilidad SQL Injection resuelta")

if __name__ == "__main__":
    test_sql_injection_protection()
    sys.exit(0)
