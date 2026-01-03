import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

# Cấu hình kết nối
HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

class ClientGUI:
    def __init__(self):
        # 1. Khởi tạo cửa sổ
        self.window = tk.Tk()
        self.window.title("Socket Chat Client")
        self.window.geometry("500x500")

        # 2. Khung hiển thị tin nhắn (ScrolledText)
        self.chat_label = tk.Label(self.window, text="Chat Log:", font=("Arial", 12))
        self.chat_label.pack(pady=5)

        self.text_area = scrolledtext.ScrolledText(self.window, wrap=tk.WORD, height=15)
        self.text_area.pack(padx=20, pady=5)
        self.text_area.config(state='disabled') # Không cho người dùng gõ trực tiếp vào log

        # 3. Khung nhập liệu
        self.msg_label = tk.Label(self.window, text="Message:", font=("Arial", 12))
        self.msg_label.pack(pady=5)

        self.input_field = tk.Entry(self.window, font=("Arial", 12), width=40)
        self.input_field.pack(padx=20, pady=5)
        self.input_field.bind("<Return>", lambda event: self.send_message()) # Nhấn Enter để gửi

        # 4. Nút gửi
        self.send_button = tk.Button(self.window, text="Send", command=self.send_message, bg="#4CAF50", fg="white")
        self.send_button.pack(pady=10)

        # 5. Kết nối Socket
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect(ADDR)

            # Chạy một luồng riêng để nhận tin nhắn từ server mà không làm treo GUI
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True # Tự động đóng thread khi đóng cửa sổ
            receive_thread.start()
        except Exception as e:
            print(f"Lỗi kết nối: {e}")

        self.window.mainloop()

    def send_message(self):
        msg = self.input_field.get()
        if not msg: return

        self.input_field.delete(0, tk.END) # Xóa ô nhập sau khi lấy tin nhắn

        message = msg.encode(FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))

        self.client.send(send_length)
        self.client.send(message)

        self.update_chat(f"You: {msg}")

        if msg == DISCONNECT_MESSAGE:
            self.client.close()
            self.window.destroy()

    def receive_messages(self):
        while True:
            try:
                # Lưu ý: Code server của bạn đang gửi phản hồi sau mỗi lần nhận tin
                response = self.client.recv(2048).decode(FORMAT)
                if response:
                    self.update_chat(f"Server: {response}")
            except:
                break

    def update_chat(self, msg):
        # Hàm cập nhật tin nhắn vào Text Area một cách an toàn
        self.text_area.config(state='normal')
        self.text_area.insert(tk.END, msg + "\n")
        self.text_area.config(state='disabled')
        self.text_area.yview(tk.END) # Tự động cuộn xuống dưới cùng

if __name__ == "__main__":
    ClientGUI()