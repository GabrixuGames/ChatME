import socketio

# Crear cliente de test
sio = socketio.Client()

@sio.event
def connect():
    print("Conectado al servidor!")
    # Unirse a sala R1
    sio.emit('join', {'room': 'R1', 'username': 'test_user'})

@sio.event
def message(data):
    print(f"Mensaje recibido: {data}")

@sio.event
def previous_messages(data):
    print(f"Mensajes previos: {data}")

@sio.event
def disconnect():
    print("Desconectado!")

if __name__ == '__main__':
    try:
        # Conectar al servidor
        sio.connect('http://localhost:5000')
        
        # Enviar mensaje de prueba
        import time
        time.sleep(1)
        sio.emit('message', {
            'username': 'test_user',
            'roomId': 'R1',
            'content': 'Mensaje de prueba desde script!'
        })
        
        # Mantener conexión
        sio.wait()
        
    except Exception as e:
        print(f"Error: {e}")