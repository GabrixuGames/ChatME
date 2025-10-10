from utils.database import db_manager

try:
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    # Buscar el mensaje específico que acabamos de crear
    message_id = "d9bd2dc8-e31b-49e2-a708-d9ccfa96f232"
    
    cursor.execute("""
        SELECT m.id, m.content, m.created_at, u.username, m.room_id 
        FROM messages m 
        LEFT JOIN users u ON m.user_id = u.id 
        WHERE m.id = %s
    """, (message_id,))
    
    message = cursor.fetchone()
    
    if message:
        print("✅ Mensaje encontrado:")
        print(f"   ID: {message[0]}")
        print(f"   Contenido: {message[1]}")
        print(f"   Usuario: {message[3]}")
        print(f"   Sala: {message[4]}")
        print(f"   Fecha: {message[2]}")
    else:
        print("❌ Mensaje NO encontrado en la BD")
    
    # Verificar últimos 5 mensajes sin filtro
    print("\n=== ÚLTIMOS 5 MENSAJES (SIN FILTRO) ===")
    cursor.execute("""
        SELECT m.id, m.content, m.created_at, u.username, m.room_id 
        FROM messages m 
        LEFT JOIN users u ON m.user_id = u.id 
        ORDER BY m.created_at DESC 
        LIMIT 5
    """)
    
    recent = cursor.fetchall()
    for msg in recent:
        print(f"ID: {msg[0][:8]}... | Usuario: {msg[3]} | Sala: {msg[4]} | Contenido: {msg[1]}")
    
    db_manager.return_connection(conn)
except Exception as e:
    print(f'Error: {e}')