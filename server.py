import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

# Cấu hình hệ thống
HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

class ServerGUI:
    def __init__(self):
        # 1. Khởi tạo cửa sổ GUI
        self.window = tk.Tk()
        self.window.title(f"Server Control Panel - {SERVER}")
        self.window.geometry("600x500")

        # 2. Khung hiển thị nội dung chat (Log)
        self.log_area = scrolledtext.ScrolledText(self.window, wrap=tk.WORD, height=15)
        self.log_area.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        self.log_area.config(state='disabled')

        # 3. Khung nhập liệu để Server nhắn tin cho Client
        self.input_frame = tk.Frame(self.window)
        self.input_frame.pack(padx=20, pady=10, fill=tk.X)

        self.msg_entry = tk.Entry(self.input_frame, font=("Arial", 12))
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.msg_entry.bind("<Return>", lambda event: self.send_to_all()) # Nhấn Enter để gửi

        self.send_button = tk.Button(
            self.input_frame, 
            text="Gửi Client", 
            command=self.send_to_all,
            bg="#2196F3", 
            fg="white",
            font=("Arial", 10, "bold")
        )
        self.send_button.pack(side=tk.RIGHT)

        # 4. Quản lý danh sách kết nối
        self.clients = {} # Lưu trữ dưới dạng {addr: conn}

        # 5. Khởi động Socket Server trong một Thread riêng để không làm treo GUI
        server_thread = threading.Thread(target=self.start_socket_server, daemon=True)
        server_thread.start()

        self.window.mainloop()

    def write_to_log(self, message):
        """Hàm cập nhật tin nhắn lên màn hình GUI"""
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.config(state='disabled')
        self.log_area.yview(tk.END)

    def send_to_all(self):
        """Hàm lấy dữ liệu từ ô nhập và gửi cho tất cả Client đang kết nối"""
        msg = self.msg_entry.get()
        if not msg:
            return
        
        self.msg_entry.delete(0, tk.END)
        
        # Duyệt qua danh sách các Client đang online để gửi tin
        for addr, conn in list(self.clients.items()):
            try:
                # Gửi tin nhắn trực tiếp (Client của bạn dùng recv(2048) để nhận phản hồi)
                conn.send(msg.encode(FORMAT))
            except Exception as e:
                self.write_to_log(f"[LỖI] Không thể gửi tới {addr}: {e}")
                del self.clients[addr]

        self.write_to_log(f"[SERVER]: {msg}")

    def start_socket_server(self):
        """Hàm thiết lập socket và lắng nghe kết nối"""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(ADDR)
        server.listen()
        self.write_to_log(f"[LISTENING] Server đang chạy trên {SERVER}")

        while True:
            conn, addr = server.accept()
            self.clients[addr] = conn
            # Mỗi Client mới lại được xử lý trong một Thread riêng
            thread = threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True)
            thread.start()
            self.write_to_log(f"[NEW CONNECTION] {addr} connected.")

    def handle_client(self, conn, addr):
        """Hàm xử lý nhận tin nhắn từ Client (Thay thế code cũ của bạn)"""
        connected = True
        while connected:
            try:
                # Nhận HEADER để biết độ dài tin nhắn
                msg_length_raw = conn.recv(HEADER).decode(FORMAT)
                if msg_length_raw:
                    msg_length = int(msg_length_raw.strip())
                    # Nhận nội dung tin nhắn thực tế
                    msg = conn.recv(msg_length).decode(FORMAT)

                    if msg == DISCONNECT_MESSAGE:
                        connected = False
                        self.write_to_log(f"[{addr}] Ngắt kết nối.")
                    else:
                        self.write_to_log(f"[{addr}]: {msg}")
                        # Ở ĐÂY KHÔNG DÙNG input() NỮA
                else:
                    connected = False
            except:
                connected = False

        conn.close()
        if addr in self.clients:
            del self.clients[addr]

if __name__ == "__main__":
    ServerGUI()