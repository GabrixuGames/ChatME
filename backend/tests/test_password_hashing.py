#!/usr/bin/env python3
"""
Test de verificación de implementación de password hashing con bcrypt
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.auth_service import AuthService

def test_password_hashing():
    """Test completo de password hashing y verificación"""
    
    print("🧪 Test de Password Hashing con Bcrypt")
    print("=" * 50)
    
    # Test 1: Hashing de password
    password_original = "TestPassword123!"
    print(f"📝 Password original: {password_original}")
    
    password_hasheado = AuthService._hash_password(password_original)
    print(f"🔒 Password hasheado: {password_hasheado[:20]}...")
    
    # Test 2: Verificación correcta
    es_valido = AuthService._verify_password(password_original, password_hasheado)
    print(f"✅ Verificación password correcto: {es_valido}")
    
    # Test 3: Verificación incorrecta
    password_incorrecto = "PasswordIncorrecto"
    es_invalido = AuthService._verify_password(password_incorrecto, password_hasheado)
    print(f"❌ Verificación password incorrecto: {es_invalido}")
    
    # Test 4: Hashes únicos (mismo password, hashes diferentes)
    password_repetido = "MismoPassword"
    hash1 = AuthService._hash_password(password_repetido)
    hash2 = AuthService._hash_password(password_repetido)
    
    son_diferentes = hash1 != hash2
    print(f"🔄 Hashes únicos para mismo password: {son_diferentes}")
    
    # Test 5: Verificación de ambos hashes contra mismo password
    verify1 = AuthService._verify_password(password_repetido, hash1)
    verify2 = AuthService._verify_password(password_repetido, hash2)
    
    print(f"✅ Verificación hash1: {verify1}")
    print(f"✅ Verificación hash2: {verify2}")
    
    print("\n" + "=" * 50)
    print("🎉 Resultados de los Tests:")
    
    todos_correctos = (
        es_valido and 
        not es_invalido and 
        son_diferentes and 
        verify1 and 
        verify2
    )
    
    if todos_correctos:
        print("✅ TODOS LOS TESTS PASARON - Implementación segura de bcrypt")
        assert True
    else:
        print("❌ ALGUNOS TESTS FALLARON - Revisar implementación")
        assert False

if __name__ == "__main__":
    test_password_hashing()
    sys.exit(0)
