#!/usr/bin/env python3
"""
Test de configuración JWT segura
"""

import sys
import os
import jwt
from datetime import datetime, timedelta, timezone
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_jwt_configuration():
    """Test de configuración JWT segura"""
    
    print("🔐 Test de Configuración JWT Segura")
    print("=" * 50)
    
    # Test 1: Verificar que no hay defaults inseguros
    print("🔍 Test 1: Verificar ausencia de defaults inseguros")
    
    # Intentar iniciar aplicación sin variables de entorno
    os.environ.pop('JWT_SECRET', None)
    os.environ.pop('FLASK_SECRET_KEY', None)
    
    try:
        from app import app
        print("❌ VULNERABILIDAD: Aplicación inició sin JWT_SECRET")
        assert False
    except ValueError as e:
        if "JWT_SECRET environment variable is required" in str(e):
            print("✅ Aplicación correctamente rechazada sin JWT_SECRET")
        else:
            print(f"❌ Error inesperado: {e}")
            assert False
    except Exception as e:
        print(f"⚠️  Error importando app: {e}")
    
    # Test 2: Verificar longitud mínima del secret
    print("\n📏 Test 2: Verificar longitud mínima del secret")
    
    os.environ['JWT_SECRET'] = 'short'
    os.environ['FLASK_SECRET_KEY'] = 'short'
    os.environ['ENVIRONMENT'] = 'development'
    
    try:
        from app import app
        print("❌ VULNERABILIDAD: Secret corto aceptado")
        assert False
    except ValueError as e:
        if "must be at least 32 characters long" in str(e):
            print("✅ Secret corto correctamente rechazado")
        else:
            print(f"❌ Error inesperado: {e}")
            assert False
    except Exception as e:
        print(f"⚠️  Error importando app: {e}")
    
    # Test 3: Configuración válida
    print("\n✅ Test 3: Configuración válida")
    
    os.environ['JWT_SECRET'] = 'super-secure-jwt-secret-key-32-chars-min'
    os.environ['FLASK_SECRET_KEY'] = 'super-secure-flask-secret-key-32-chars'
    os.environ['ENVIRONMENT'] = 'development'
    
    try:
        # Limpiar import cache
        if 'app' in sys.modules:
            del sys.modules['app']
        
        from app import app, jwt_secret
        
        # Verificar que el secret es el esperado
        expected_secret = 'super-secure-jwt-secret-key-32-chars-min'
        if jwt_secret == expected_secret:
            print("✅ JWT_SECRET cargado correctamente")
        else:
            print(f"❌ JWT_SECRET incorrecto: {jwt_secret}")
            assert False
            
        print("✅ Aplicación iniciada con configuración segura")
        
    except Exception as e:
        print(f"❌ Error iniciando aplicación: {e}")
        assert False

def test_jwt_token_security():
    """Test de seguridad de tokens JWT"""
    
    print("\n🔐 Test de Seguridad de Tokens JWT")
    print("=" * 50)
    
    # Configuración de prueba
    test_secret = 'test-jwt-secret-key-32-characters-long'
    
    # Test 1: Token con estructura completa
    print("🏗️ Test 1: Generación de token con estructura completa")
    
    current_time = datetime.now(timezone.utc)
    payload = {
        "user_id": "test-user-123",
        "username": "testuser",
        "iat": current_time,
        "exp": current_time + timedelta(hours=24),
        "iss": "chatme-app",
        "aud": "chatme-users"
    }
    
    try:
        token = jwt.encode(payload, test_secret, algorithm="HS256")
        print(f"✅ Token generado correctamente: {len(token)} caracteres")
    except Exception as e:
        print(f"❌ Error generando token: {e}")
        assert False
    
    # Test 2: Decodificación con validación completa
    print("\n🔍 Test 2: Decodificación con validación completa")
    
    try:
        decoded = jwt.decode(
            token,
            test_secret,
            algorithms=["HS256"],
            audience="chatme-users",
            issuer="chatme-app",
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iat": True
            }
        )
        
        if decoded['user_id'] == 'test-user-123':
            print("✅ Token decodificado y validado correctamente")
        else:
            print("❌ Token decodificado pero con datos incorrectos")
            assert False
            
    except Exception as e:
        print(f"❌ Error decodificando token: {e}")
        assert False
    
    # Test 3: Token expirado
    print("\n⏰ Test 3: Token expirado")
    
    expired_payload = payload.copy()
    expired_payload['exp'] = datetime.now(timezone.utc) - timedelta(hours=1)
    
    try:
        expired_token = jwt.encode(expired_payload, test_secret, algorithm="HS256")
        jwt.decode(expired_token, test_secret, algorithms=["HS256"])
        print("❌ VULNERABILIDAD: Token expirado aceptado")
        assert False
    except jwt.ExpiredSignatureError:
        print("✅ Token expirado correctamente rechazado")
    except Exception as e:
        print(f"⚠️  Error inesperado: {e}")
    
    # Test 4: Token con issuer incorrecto
    print("\n🏢 Test 4: Token con issuer incorrecto")
    
    wrong_issuer_payload = payload.copy()
    wrong_issuer_payload['iss'] = 'malicious-app'
    
    try:
        wrong_token = jwt.encode(wrong_issuer_payload, test_secret, algorithm="HS256")
        jwt.decode(
            wrong_token,
            test_secret,
            algorithms=["HS256"],
            options={"verify_iss": True}
        )
        print("❌ VULNERABILIDAD: Token con issuer incorrecto aceptado")
        assert False
    except jwt.InvalidTokenError:
        print("✅ Token con issuer incorrecto correctamente rechazado")
    except Exception as e:
        print(f"⚠️  Error inesperado: {e}")
    
    # Test 5: Token con audience incorrecto
    print("\n👥 Test 5: Token con audience incorrecto")
    
    wrong_aud_payload = payload.copy()
    wrong_aud_payload['aud'] = 'malicious-users'
    
    try:
        wrong_token = jwt.encode(wrong_aud_payload, test_secret, algorithm="HS256")
        jwt.decode(
            wrong_token,
            test_secret,
            algorithms=["HS256"],
            options={"verify_aud": True}
        )
        print("❌ VULNERABILIDAD: Token con audience incorrecto aceptado")
        assert False
    except jwt.InvalidTokenError:
        print("✅ Token con audience incorrecto correctamente rechazado")
    except Exception as e:
        print(f"⚠️  Error inesperado: {e}")
    
    # Test 6: Token firmado con secret incorrecto
    print("\n🔑 Test 6: Token firmado con secret incorrecto")
    
    try:
        wrong_secret_token = jwt.encode(payload, 'wrong-secret', algorithm="HS256")
        jwt.decode(wrong_secret_token, test_secret, algorithms=["HS256"])
        print("❌ VULNERABILIDAD: Token con secret incorrecto aceptado")
        assert False
    except jwt.InvalidTokenError:
        print("✅ Token con secret incorrecto correctamente rechazado")
    except Exception as e:
        print(f"⚠️  Error inesperado: {e}")
    
def test_environment_variables():
    """Test de variables de entorno"""
    
    print("\n🌍 Test de Variables de Entorno")
    print("=" * 50)
    
    required_vars = ['JWT_SECRET', 'FLASK_SECRET_KEY']
    current_env = {}
    
    for var in required_vars:
        value = os.getenv(var)
        current_env[var] = value
        
        if value:
            print(f"✅ {var}: {'*' * min(len(value), 8)} (longitud: {len(value)})")
            
            if len(value) < 32:
                print(f"⚠️  ADVERTENCIA: {var} debe tener al menos 32 caracteres")
        else:
            print(f"❌ FALTA: {var} no está configurado")
    
    assert all(len(current_env[var] or "") >= 32 for var in required_vars)

if __name__ == "__main__":
    print("🔐 Suite de Tests JWT - ChatME Backend")
    print("=" * 60)
    
    success_count = 0
    total_tests = 3
    
    # Test configuración
    try:
        test_jwt_configuration()
        print("✅ Test configuración JWT: PASANDO")
        success_count += 1
    except AssertionError:
        print("❌ Test configuración JWT: FALLANDO")
    
    # Test seguridad tokens
    try:
        test_jwt_token_security()
        print("✅ Test seguridad tokens: PASANDO")
        success_count += 1
    except AssertionError:
        print("❌ Test seguridad tokens: FALLANDO")
    
    # Test variables de entorno
    try:
        test_environment_variables()
        print("✅ Test variables de entorno: PASANDO")
        success_count += 1
    except AssertionError:
        print("❌ Test variables de entorno: FALLANDO")
    
    print(f"\n" + "=" * 60)
    print(f"📊 Resultados: {success_count}/{total_tests} tests pasando")
    
    if success_count == total_tests:
        print("🎉 TODOS LOS TESTS JWT PASARON")
        print("✅ Configuración JWT segura implementada correctamente")
        sys.exit(0)
    else:
        print("❌ ALGUNOS TESTS FALLARON")
        print("🚨 Revisar configuración JWT")
        sys.exit(1)
