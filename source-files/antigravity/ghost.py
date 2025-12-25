import socket
import subprocess
import os
import threading
import sys

# GHOST PROTOCOL - SIMULATION
# "Slave-Agent" Listener
# Binds to local port to simulate a C2 connection

HOST = '127.0.0.1'
PORT = 1337

def handle_client(client_socket):
    client_socket.send(b"[+] GHOST PROTOCOL INITIATED. WAITING FOR COMMANDS...\n")
    client_socket.send(b"[+] TYPE 'exit' TO DISCONNECT.\n")
    
    while True:
        try:
            client_socket.send(b"GHOST> ")
            cmd = client_socket.recv(1024).decode('utf-8').strip()
            
            if not cmd:
                break
                
            if cmd.lower() == 'exit':
                break
            
            if cmd.lower().startswith('cd '):
                try:
                    os.chdir(cmd[3:])
                    client_socket.send(b"\n")
                except Exception as e:
                    client_socket.send(str(e).encode('utf-8') + b"\n")
                continue

            # Execute command
            output = subprocess.getoutput(cmd)
            client_socket.send(output.encode('utf-8') + b"\n")
            
        except Exception as e:
            print(f"[-] Error: {e}")
            break
            
    client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((HOST, PORT))
        server.listen(5)
        print(f"[*] LISTENING ON {HOST}:{PORT}")
        print("[*] WAITING FOR INCOMING CONNECTION...")
        
        while True:
            client, addr = server.accept()
            print(f"[*] CONNECTION FROM {addr[0]}:{addr[1]}")
            client_handler = threading.Thread(target=handle_client, args=(client,))
            client_handler.start()
            
    except Exception as e:
        print(f"[-] FAILED TO BIND: {e}")

if __name__ == "__main__":
    start_server()
