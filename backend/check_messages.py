from utils.database import db_manager

try:
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    # Obtener mensajes de una sala específica con información de usuario
    cursor.execute("""
        SELECT m.id, m.content, m.created_at, u.username, m.room_id 
        FROM messages m 
        JOIN users u ON m.user_id = u.id 
        WHERE m.room_id = 'R1' 
        ORDER BY m.created_at DESC 
        LIMIT 10
    """)
    messages = cursor.fetchall()
    
    print("=== MENSAJES EN SALA R1 ===")
    for msg in messages:
        print(f"ID: {msg[0]}")
        print(f"Contenido: {msg[1]}")
        print(f"Usuario: {msg[3]}")
        print(f"Sala: {msg[4]}")
        print(f"Fecha: {msg[2]}")
        print("---")
    
    db_manager.return_connection(conn)
except Exception as e:
    print(f'Error: {e}')