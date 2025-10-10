"""
Test Runner
Script para ejecutar todos los tests
"""
import unittest
import sys
import os

# Añadir path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_all_tests():
    """Ejecutar todos los tests de la aplicación"""
    # Descubrir y cargar todos los tests
    loader = unittest.TestLoader()
    test_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(test_dir, pattern='test_*.py')
    
    # Ejecutar tests con verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Retornar código de salida basado en el resultado
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    print("🧪 Ejecutando todos los tests de ChatApp...")
    print("=" * 50)
    exit_code = run_all_tests()
    print("=" * 50)
    if exit_code == 0:
        print("✅ Todos los tests pasaron exitosamente!")
    else:
        print("❌ Algunos tests fallaron.")
    sys.exit(exit_code)