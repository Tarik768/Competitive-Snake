import socket
import threading
import pickle
import random

SERVER_IP = "0.0.0.0"
PORT = 5555

# Aktif odaları tutan sözlük
games = {} 

class Game:
    def __init__(self, room_id):
        self.id = room_id
        self.ready = False
        # Mantıksal Çözünürlük: 1920x1080
        self.snake1 = [[400, 400], [375, 400], [350, 400]]
        self.snake2 = [[1500, 400], [1525, 400], [1550, 400]]
        self.foods = [[960, 540]]
        self.score = [0, 0]
        self.p1_dir = "RIGHT" # Yılanların anlık yönü
        self.p2_dir = "LEFT"
        self.winner = None

    def move_snakes(self):
        # Yılan hareket matematiği buraya gelecek (ileride ekleyeceğiz)
        pass

def handle_client(conn, p_id, game_id):
    """
    Oyun başladıktan sonraki veri trafiğini yönetir.
    """
    global games
    conn.send(str.encode(str(p_id))) # Oyuncuya kim olduğunu söyle (0 veya 1)

    while True:
        try:
            data = conn.recv(2048).decode()

            if game_id in games:
                game = games[game_id]

                if not data:
                    break
                else:
                    # Gelen tuş verisine göre sunucudaki yönü güncelle
                    if data != "get":
                        if p_id == 0:
                            game.p1_dir = data # Örn: "UP"
                        else:
                            game.p2_dir = data

                    # Oyunun son halini (Game nesnesini) paketleyip yolla
                    conn.sendall(pickle.dumps(game))
            else:
                break
        except:
            break

    print(f"Bağlantı koptu: Oda {game_id}")
    try:
        del games[game_id]
        print(f"Oda {game_id} kapatıldı.")
    except:
        pass
    conn.close()

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((SERVER_IP, PORT))
    except socket.error as e:
        print(str(e))

    s.listen()
    print("Sunucu Başlatıldı (Oda Sistemi Aktif)...")

    while True:
        conn, addr = s.accept()
        print("Biri bağlandı:", addr)

        # --- HANDSHAKE (EL SIKIŞMA) BÖLÜMÜ ---
        # İstemciden ilk komutu bekle: "MAKE" veya "JOIN <ID>"
        try:
            data = conn.recv(1024).decode()
        except:
            continue

        if data == "MAKE":
            # 1. Yeni Oda Oluştur
            room_id = random.randint(1000, 9999)
            # Eğer şans eseri aynı ID varsa tekrar üret
            while room_id in games:
                room_id = random.randint(1000, 9999)
            
            games[room_id] = Game(room_id)
            print(f"Oda oluşturuldu: {room_id}")
            
            # İstemciye oluşturulan ID'yi gönder
            conn.send(str.encode(str(room_id)))
            
            # Oyuncuyu P1 (id=0) olarak oyuna al
            threading.Thread(target=handle_client, args=(conn, 0, room_id)).start()

        elif data.startswith("JOIN"):
            # 2. Odaya Katıl
            try:
                # Mesaj "JOIN 4512" şeklinde gelir, parçala
                split_data = data.split(" ")
                room_id = int(split_data[1])
                
                if room_id in games:
                    game = games[room_id]
                    if not game.ready: # Oda dolu değilse
                        game.ready = True # Artık oyun başlayabilir
                        conn.send(str.encode("OK")) # Onay yolla
                        print(f"Odaya katılım başarılı: {room_id}")
                        # Oyuncuyu P2 (id=1) olarak oyuna al
                        threading.Thread(target=handle_client, args=(conn, 1, room_id)).start()
                    else:
                        conn.send(str.encode("FULL")) # Oda dolu
                        conn.close()
                else:
                    conn.send(str.encode("FAIL")) # Oda bulunamadı
                    conn.close()
            except:
                conn.close()
        
        else:
            # Geçersiz komut
            conn.close()

if __name__ == "__main__":
    main()