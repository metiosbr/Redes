import socket
import threading
import os

clients = []

def main():
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        server.bind(('', 7777))
        server.listen()
        print('ouvindo')
    except:
        return print('\nNão foi possível iniciar o servidor\n')
    
    while True:
        client, addr = server.accept()
        clients.append(client)
        
        thread = threading.Thread(target=messagesTreatment, args=[client])
        thread.start()
        
def messagesTreatment(client):
    while True:
        try:
            msg = client.recv(2048)
            brodcast(msg, client)
            
        except:
            deleteClient(client)

def receive_file(client, filename):
    with open(filename, 'wb') as f:
        while True:
            data = client.recv(1024)
            if not data:
                break
            f.write(data)
    print(f'Arquivo {filename} recebido com sucesso.')


def brodcast(msg, client):
    for clientItem in clients:
        if clientItem != client:
            try:
                clientItem.send(msg)
            except:
                deleteClient(clientItem)

def deleteClient(client):
    clients.remove(client)
    
    
    
    
main()        