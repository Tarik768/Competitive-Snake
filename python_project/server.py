import socket
import threading
import pickle
import random
import time

from common import *

# --- SUNUCU AYARLARI ---
SERVER_IP = "0.0.0.0" # Tüm IP'lerden gelen isteklere açık
PORT = 5555

# Aktif odaları tutan sözlük
games = {} 

def server_game_loop():
    while True:
        try:
            active_games = list(games.values())
            for game in active_games:
                if game.ready:
                    game.update_game_state()
            time.sleep(0.015) 
        except Exception as e:
            print(f"Server Loop Hatası: {e}")

def handle_client(conn, p_id, game_id):
    global games
    conn.send(str.encode(str(p_id)))

    while True:
        try:
            data = conn.recv(2048).decode()
            if game_id in games:
                game = games[game_id]
                if not data: break
                
                if data == "REMATCH":
                    print(f"Oyuncu {p_id} yeniden oynamak istiyor.") # <-- BU SATIRI EKLE
                    with game.lock:
                        if p_id == 0: game.p1_rematch = True
                        else: game.p2_rematch = True
                        
                        # İkisi de hazırsa oyunu sıfırla!
                        if game.p1_rematch and game.p2_rematch:
                            print(f"Oda {game_id} sıfırlanıyor...") # <-- BU SATIRI EKLE
                            game.reset_game()

                elif data != "get":
                    # KİLİT MEKANİZMASI: Yön değiştirirken sunucu update yapmasın
                    with game.lock:
                        if p_id == 0:
                            if game.p1_can_turn: 
                                updated = False
                                if data == "UP" and game.p1_dir != "DOWN": game.p1_dir = "UP"; updated = True
                                elif data == "DOWN" and game.p1_dir != "UP": game.p1_dir = "DOWN"; updated = True
                                elif data == "LEFT" and game.p1_dir != "RIGHT": game.p1_dir = "LEFT"; updated = True
                                elif data == "RIGHT" and game.p1_dir != "LEFT": game.p1_dir = "RIGHT"; updated = True
                                if updated: game.p1_can_turn = False
                        else:
                            if game.p2_can_turn:
                                updated = False
                                if data == "UP" and game.p2_dir != "DOWN": game.p2_dir = "UP"; updated = True
                                elif data == "DOWN" and game.p2_dir != "UP": game.p2_dir = "DOWN"; updated = True
                                elif data == "LEFT" and game.p2_dir != "RIGHT": game.p2_dir = "LEFT"; updated = True
                                elif data == "RIGHT" and game.p2_dir != "LEFT": game.p2_dir = "RIGHT"; updated = True
                                if updated: game.p2_can_turn = False

                conn.sendall(pickle.dumps(game))
            else:
                break
        except:
            break
    
    try:
        del games[game_id]
    except:
        pass
    conn.close()

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind((SERVER_IP, PORT))
    except socket.error as e:
        print(str(e))
        return

    s.listen()
    print("Sunucu Başlatıldı (Skor Fix + Thread Safe Sürüm)...")

    threading.Thread(target=server_game_loop).start()

    while True:
        conn, addr = s.accept()
        try:
            data = conn.recv(1024).decode()
        except:
            continue

        if data == "MAKE":
            room_id = random.randint(1000, 9999)
            while room_id in games: room_id = random.randint(1000, 9999)
            games[room_id] = Game(room_id)
            print(f"Oda: {room_id}")
            conn.send(str.encode(str(room_id)))
            threading.Thread(target=handle_client, args=(conn, 0, room_id)).start()

        elif data.startswith("JOIN"):
            try:
                split_data = data.split(" ")
                room_id = int(split_data[1])
                if room_id in games:
                    game = games[room_id]
                    if not game.ready:
                        game.ready = True
                        game.start_ticks = time.time()
                        conn.send(str.encode("OK"))
                        threading.Thread(target=handle_client, args=(conn, 1, room_id)).start()
                    else:
                        conn.send(str.encode("FULL"))
                        conn.close()
                else:
                    conn.send(str.encode("FAIL"))
                    conn.close()
            except:
                conn.close()
        else:
            conn.close()

if __name__ == "__main__":
    main()