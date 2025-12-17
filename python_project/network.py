import socket
import pickle

class Network:
    def __init__(self, action, room_id=None):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # --- BURAYA SUNUCU IP ADRESİNİ YAZ ---
        # Localhost test için: "localhost" veya "127.0.0.1"
        # Gerçek sunucu için: "45.xxx.xxx.xxx"
        self.server = "core.kectr.tech" 
        self.port = 5555
        self.addr = (self.server, self.port)
        
        # Bağlantı sonucunda alacağımız veriler
        self.p = None # Oyuncu ID (0 veya 1)
        self.game_id = None # Oda ID
        
        # Bağlanmayı dene
        self.connect(action, room_id)

    def connect(self, action, room_id):
        try:
            self.client.connect(self.addr)
            
            # 1. Komutu Gönder
            if action == "MAKE":
                self.client.send(str.encode("MAKE"))
                # Yanıt olarak ODA ID'si gelecek
                response = self.client.recv(2048).decode()
                self.game_id = response
                
                # İkinci adım: Kendi Player ID'ni al (handle_client'tan gelir)
                self.p = int(self.client.recv(2048).decode())
                
            elif action == "JOIN":
                self.client.send(str.encode(f"JOIN {room_id}"))
                # Yanıt olarak "OK", "FAIL" veya "FULL" gelecek
                response = self.client.recv(2048).decode()
                
                if response == "OK":
                    self.game_id = room_id
                    # İkinci adım: Kendi Player ID'ni al
                    self.p = int(self.client.recv(2048).decode())
                else:
                    # Başarısız olursa bağlantıyı kes
                    print(f"Bağlantı Hatası: {response}")
                    self.client = None
                    
        except Exception as e:
            print(f"Network Hatası: {e}")
            self.client = None

    def send(self, data):
        """Sunucuya tuş verisi atar, yeni Game objesini alır"""
        if self.client is None: return None
        try:
            self.client.send(str.encode(data))
            return pickle.loads(self.client.recv(2048*4))
        except socket.error as e:
            print(e)
            return None