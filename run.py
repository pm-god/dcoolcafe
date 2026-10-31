import os
import socket
from app import app

def find_free_port(starting_port=5000):
    port = starting_port
    while port < 65535:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)) != 0:
                return port
            port += 1
    return 5000

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # If standard 5000 is occupied, auto-detect next available port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(('127.0.0.1', port)) == 0:
            port = find_free_port(5001)

    print("=" * 60)
    print(" ☕  D COOL CAFE - OFFICIAL WEBSITE (Burla, Odisha)  ☕")
    print(f" 🌐  Server running at: http://127.0.0.1:{port}")
    print(f" 📱  Instagram Profile: https://www.instagram.com/d_cool_cafe/")
    print(f" 🔑  Admin Dashboard:   http://127.0.0.1:{port}/admin (admin / dcool123)")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=port, debug=True)
