from utils.database import db_manager

try:
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    # Verificar tablas existentes
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    tables = cursor.fetchall()
    print('Tablas en la BD:', [t[0] for t in tables])
    
    # Verificar si hay datos en la tabla messages
    if any('messages' in str(t[0]) for t in tables):
        cursor.execute("SELECT COUNT(*) FROM messages")
        count = cursor.fetchone()[0]
        print(f'Cantidad de mensajes en BD: {count}')
        
        # Mostrar últimos 5 mensajes
        cursor.execute("SELECT id, content, created_at FROM messages ORDER BY created_at DESC LIMIT 5")
        recent = cursor.fetchall()
        print('Últimos mensajes:', recent)
    
    db_manager.return_connection(conn)
except Exception as e:
    print(f'Error: {e}')