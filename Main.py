import customtkinter as ctk
from customtkinter import CTkImage
import threading
import queue
import subprocess
import sys
from Firewall import FirewallAI
from PIL import Image
import os

# --- Login Window ---
class LoginWindow:
    def __init__(self, root, on_success):
        self.root = root
        self.on_success = on_success
        self.root.geometry("350x320")
        self.root.title("DBTS")
        self.root.configure(bg="#111")

        self.frame = ctk.CTkFrame(root, fg_color="#181818", border_width=0, corner_radius=18)
        self.frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

        # Logo
        logo_path = os.path.join(os.path.dirname(__file__), 'LOGO.png')
        try:
            logo_img = Image.open(logo_path)
            logo_img = logo_img.resize((80, 80), Image.LANCZOS)
            self.logo = CTkImage(light_image=logo_img, dark_image=logo_img, size=(80, 80))
            logo_label = ctk.CTkLabel(self.frame, image=self.logo, text="", fg_color="#181818")
            logo_label.pack(pady=(10, 0))
        except Exception:
            logo_label = ctk.CTkLabel(self.frame, text="[Logo]", fg_color="#181818", text_color="#fff", font=("Segoe UI", 16, "bold"))
            logo_label.pack(pady=(10, 0))

        ctk.CTkLabel(self.frame, text="Login", fg_color="#181818", text_color="#ff3333", font=("Segoe UI", 18, "bold")).pack(pady=(8, 8))
        ctk.CTkLabel(self.frame, text="Username", fg_color="#181818", text_color="#ff5555", font=("Segoe UI", 11)).pack(pady=(0, 2))
        self.username = ctk.CTkEntry(self.frame, width=180, font=("Segoe UI", 12), fg_color="#222", text_color="#fff", border_width=2, border_color="#ff2222", corner_radius=10)
        self.username.pack(pady=(0, 8))
        ctk.CTkLabel(self.frame, text="Password", fg_color="#181818", text_color="#ff5555", font=("Segoe UI", 11)).pack(pady=(0, 2))
        self.password = ctk.CTkEntry(self.frame, width=180, font=("Segoe UI", 12), fg_color="#222", text_color="#fff", border_width=2, border_color="#ff2222", corner_radius=10, show="*")
        self.password.pack(pady=(0, 12))
        self.login_btn = ctk.CTkButton(self.frame, text="Login", command=self.try_login, fg_color="#ff2222", text_color="#fff", font=("Segoe UI", 12, "bold"), hover_color="#b30000", corner_radius=10, border_width=0)
        self.login_btn.pack(pady=(0, 10))
        self.status = ctk.CTkLabel(self.frame, text="", fg_color="#181818", text_color="#ff3333", font=("Segoe UI", 10))
        self.status.pack()

    def try_login(self):
        user = self.username.get()
        pwd = self.password.get()
        if user == "DKA" and pwd == "DBTS":
            self.root.destroy()
            self.on_success()
        else:
            self.status.configure(text="Invalid username or password.")

# --- Main App ---
class FakeServer(threading.Thread):
    def __init__(self, server_id, command_queue, output_queue):
        super().__init__(daemon=True)
        self.server_id = server_id
        self.command_queue = command_queue
        self.output_queue = output_queue
        self.running = True

    def run(self):
        while self.running:
            try:
                command = self.command_queue.get(timeout=0.1)
                # Expect command to be a tuple: (ip, port, duration, threads)
                ip, port, duration, threads = command
                # Run Command.py as a subprocess
                result = subprocess.run([
                    sys.executable, 'Command.py', ip, str(port), str(duration), str(threads)
                ], capture_output=True, text=True)
                output = result.stdout + result.stderr
                self.output_queue.put(f"Server {self.server_id}:\n" + output)
            except queue.Empty:
                continue

    def stop(self):
        self.running = False

class ServerManager:
    def __init__(self, num_servers=5):
        self.command_queues = [queue.Queue() for _ in range(num_servers)]
        self.output_queue = queue.Queue()
        self.servers = [FakeServer(i+1, self.command_queues[i], self.output_queue) for i in range(num_servers)]
        for server in self.servers:
            server.start()

    def send_command(self, ip, port, duration, threads):
        for q in self.command_queues:
            q.put((ip, port, duration, threads))

    def get_output(self):
        outputs = []
        while not self.output_queue.empty():
            outputs.append(self.output_queue.get())
        return outputs

    def stop_all(self):
        for server in self.servers:
            server.stop()

class CustomTkApp:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)
        self.root.geometry("670x440")
        self.root.configure(bg="#111")
        self.root.title("DBTS")
        self.manager = ServerManager()
        self.firewall = FirewallAI(strengthen=True)
        self._after_id = None  # Store after callback id

        # Custom title bar with logo at top left
        self.title_bar = ctk.CTkFrame(root, fg_color="#181818", height=44, corner_radius=0, border_width=0)
        self.title_bar.pack(fill=ctk.X, side=ctk.TOP)
        logo_path = os.path.join(os.path.dirname(__file__), 'LOGO.png')
        try:
            logo_img = Image.open(logo_path)
            logo_img = logo_img.resize((32, 32), Image.LANCZOS)
            self.logo_main = CTkImage(light_image=logo_img, dark_image=logo_img, size=(32, 32))
            logo_label = ctk.CTkLabel(self.title_bar, image=self.logo_main, text="", fg_color="#181818")
            logo_label.pack(side=ctk.LEFT, padx=(8, 4), pady=4)
        except Exception:
            logo_label = ctk.CTkLabel(self.title_bar, text="[Logo]", fg_color="#181818", text_color="#fff", font=("Segoe UI", 10, "bold"))
            logo_label.pack(side=ctk.LEFT, padx=(8, 4), pady=4)
        self.title_label = ctk.CTkLabel(self.title_bar, text="  Server Management", fg_color="#181818", text_color="#ff3333", font=("Segoe UI", 15, "bold"))
        self.title_label.pack(side=ctk.LEFT, padx=8)
        self.close_button = ctk.CTkButton(self.title_bar, text="✕", fg_color="#181818", text_color="#fff", font=("Segoe UI", 13), command=self.on_close, hover_color="#ff2222", width=36, height=32, corner_radius=10, border_width=0)
        self.close_button.pack(side=ctk.RIGHT, padx=8)
        self.log_button = ctk.CTkButton(self.title_bar, text="Firewall Log", fg_color="#181818", text_color="#ff3333", font=("Segoe UI", 11), command=self.show_firewall_log, hover_color="#222", width=100, height=32, corner_radius=10, border_width=0)
        self.log_button.pack(side=ctk.RIGHT, padx=8)
        self.title_bar.bind('<B1-Motion>', self.move_window)
        self.title_bar.bind('<Button-1>', self.get_pos)
        self.title_label.bind('<B1-Motion>', self.move_window)
        self.title_label.bind('<Button-1>', self.get_pos)

        # Command entry area
        self.command_frame = ctk.CTkFrame(root, fg_color="#181818", corner_radius=14, border_width=0)
        self.command_frame.pack(pady=(22, 5))
        self.command_label = ctk.CTkLabel(self.command_frame, text="Enter Command:", fg_color="#181818", text_color="#fff", font=("Segoe UI", 11, "bold"))
        self.command_label.pack(side=ctk.LEFT, padx=(0, 8))
        self.command_entry = ctk.CTkEntry(self.command_frame, width=320, font=("Consolas", 12), fg_color="#222", text_color="#fff", border_width=2, border_color="#ff2222", corner_radius=10)
        self.command_entry.pack(side=ctk.LEFT)
        self.send_button = ctk.CTkButton(self.command_frame, text="Send to All Servers", command=self.send_command, fg_color="#ff2222", text_color="#fff", font=("Segoe UI", 11, "bold"), hover_color="#b30000", corner_radius=10, border_width=0)
        self.send_button.pack(side=ctk.LEFT, padx=(8, 0))

        # DDOS Attack button
        self.ddos_button = ctk.CTkButton(self.command_frame, text="Start DDOS Attack", command=self.start_ddos_attack, fg_color="#0ff", text_color="#111", font=("Segoe UI", 11, "bold"), hover_color="#0cc", corner_radius=10, border_width=0)
        self.ddos_button.pack(side=ctk.LEFT, padx=(8, 0))

        # Server control buttons
        self.button_frame = ctk.CTkFrame(root, fg_color="#181818", corner_radius=14, border_width=0)
        self.button_frame.pack(pady=(0, 10))
        self.start_button = ctk.CTkButton(self.button_frame, text="Start Servers", command=self.start_servers, fg_color="#ff2222", text_color="#fff", font=("Segoe UI", 11, "bold"), hover_color="#b30000", corner_radius=10, border_width=0)
        self.start_button.pack(side=ctk.LEFT, padx=8)
        self.shutdown_button = ctk.CTkButton(self.button_frame, text="Shutdown Servers", command=self.shutdown_servers, fg_color="#b30000", text_color="#fff", font=("Segoe UI", 11, "bold"), hover_color="#ff2222", corner_radius=10, border_width=0)
        self.shutdown_button.pack(side=ctk.LEFT, padx=8)
        self.servers_running = True

        # DDOS parameters area
        self.param_frame = ctk.CTkFrame(root, fg_color="#181818", corner_radius=14, border_width=0)
        self.param_frame.pack(pady=(8, 0))
        ctk.CTkLabel(self.param_frame, text="Target IP:", fg_color="#181818", text_color="#fff", font=("Segoe UI", 10, "bold")).pack(side=ctk.LEFT, padx=(0, 4))
        self.ip_entry = ctk.CTkEntry(self.param_frame, width=90, font=("Consolas", 11), fg_color="#222", text_color="#fff", border_width=2, border_color="#ff2222", corner_radius=10)
        self.ip_entry.pack(side=ctk.LEFT, padx=(0, 8))
        ctk.CTkLabel(self.param_frame, text="Port:", fg_color="#181818", text_color="#fff", font=("Segoe UI", 10, "bold")).pack(side=ctk.LEFT, padx=(0, 4))
        self.port_entry = ctk.CTkEntry(self.param_frame, width=50, font=("Consolas", 11), fg_color="#222", text_color="#fff", border_width=2, border_color="#ff2222", corner_radius=10)
        self.port_entry.pack(side=ctk.LEFT, padx=(0, 8))
        ctk.CTkLabel(self.param_frame, text="Duration:", fg_color="#181818", text_color="#fff", font=("Segoe UI", 10, "bold")).pack(side=ctk.LEFT, padx=(0, 4))
        self.duration_entry = ctk.CTkEntry(self.param_frame, width=50, font=("Consolas", 11), fg_color="#222", text_color="#fff", border_width=2, border_color="#ff2222", corner_radius=10)
        self.duration_entry.pack(side=ctk.LEFT, padx=(0, 8))
        ctk.CTkLabel(self.param_frame, text="Threads:", fg_color="#181818", text_color="#fff", font=("Segoe UI", 10, "bold")).pack(side=ctk.LEFT, padx=(0, 4))
        self.threads_entry = ctk.CTkEntry(self.param_frame, width=50, font=("Consolas", 11), fg_color="#222", text_color="#fff", border_width=2, border_color="#ff2222", corner_radius=10)
        self.threads_entry.pack(side=ctk.LEFT, padx=(0, 8))
        # Set defaults
        self.ip_entry.insert(0, "127.0.0.1")
        self.port_entry.insert(0, "80")
        self.duration_entry.insert(0, "5")
        self.threads_entry.insert(0, "10")

        # Output area
        self.output_text = ctk.CTkTextbox(root, width=650, height=260, fg_color='#181818', text_color='#ff3333', font=('Consolas', 12), border_width=2, border_color="#ff2222", corner_radius=14)
        self.output_text.pack(pady=(10, 0), padx=10)
        self.output_text.configure(state='disabled')

        # Footer for copyright
        self.footer = ctk.CTkLabel(root, text="All rights reserved © DEVsalah", fg_color="#181818", text_color="#ff3333", font=("Segoe UI", 10, "bold"))
        self.footer.pack(side=ctk.BOTTOM, pady=(0, 2))

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.update_output()
        self.setup_terminal(root)

    def get_pos(self, event):
        self.xwin = event.x
        self.ywin = event.y

    def move_window(self, event):
        self.root.geometry(f'+{event.x_root - self.xwin}+{event.y_root - self.ywin}')

    def send_command(self):
        ip = self.ip_entry.get()
        port = self.port_entry.get()
        duration = self.duration_entry.get()
        threads = self.threads_entry.get()
        command = self.command_entry.get()
        if ip and port and duration and threads:
            # Firewall AI checks command before sending
            allowed = self.firewall.analyze_command(command, server_id=None)
            if allowed:
                self.manager.send_command(ip, int(port), int(duration), int(threads))
                self.command_entry.delete(0, 1000)
            else:
                self.output_text.configure(state='normal')
                self.output_text.insert('end', f"[FIREWALL BLOCKED] {command}\n")
                self.output_text.configure(state='disabled')
                self.output_text.see('end')

    def start_ddos_attack(self):
        ip = self.ip_entry.get()
        port = self.port_entry.get()
        duration = self.duration_entry.get()
        threads = self.threads_entry.get()
        if ip and port and duration and threads:
            # Enhanced DDOS: double thread count and duration for more power
            enhanced_threads = int(threads) * 2
            enhanced_duration = int(duration) * 2
            self.manager.send_command(ip, int(port), enhanced_duration, enhanced_threads)
            self.output_text.configure(state='normal')
            self.output_text.insert('end', f"[DDOS] Enhanced attack started on {ip}:{port} for {enhanced_duration}s with {enhanced_threads} threads.\n")
            self.output_text.configure(state='disabled')
            self.output_text.see('end')

    def show_firewall_log(self):
        log_window = ctk.CTkToplevel(self.root)
        log_window.title("DBTS")
        log_window.geometry("600x350")
        log_text = ctk.CTkTextbox(log_window, width=570, height=300, fg_color='#181818', text_color='#0ff', font=('Consolas', 12), border_width=2, border_color="#ff2222", corner_radius=14)
        log_text.pack(pady=10, padx=10)
        logs = self.firewall.get_log()
        for entry in logs:
            log_text.insert('end', entry + '\n')
        log_text.configure(state='disabled')

    def start_servers(self):
        if not self.servers_running:
            self.manager = ServerManager()
            self.servers_running = True
            self.output_text.configure(state='normal')
            self.output_text.insert('end', 'Servers started.\n')
            self.output_text.configure(state='disabled')
            self.output_text.see('end')

    def shutdown_servers(self):
        if self.servers_running:
            self.manager.stop_all()
            self.servers_running = False
            self.output_text.configure(state='normal')
            self.output_text.insert('end', 'Servers shut down.\n')
            self.output_text.configure(state='disabled')
            self.output_text.see('end')

    def update_output(self):
        if not hasattr(self, 'root') or not self.root.winfo_exists():
            return  # Window destroyed, do not update
        outputs = self.manager.get_output()
        if outputs:
            self.output_text.configure(state='normal')
            for line in outputs:
                self.output_text.insert('end', line + '\n')
            self.output_text.configure(state='disabled')
            self.output_text.see('end')
        self._after_id = self.root.after(100, self.update_output)

    def on_close(self):
        if hasattr(self, '_after_id') and self._after_id is not None:
            try:
                self.root.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None
        self.manager.stop_all()
        self.root.destroy()

    def setup_terminal(self, parent):
        self.terminal_frame = ctk.CTkFrame(parent, fg_color="#181818", corner_radius=14, border_width=0)
        self.terminal_frame.pack(pady=(8, 0), padx=10, fill="x")
        self.terminal_label = ctk.CTkLabel(self.terminal_frame, text="DBTS Terminal:", fg_color="#181818", text_color="#0ff", font=("Consolas", 11, "bold"))
        self.terminal_label.pack(anchor="w", padx=6, pady=(4, 0))
        self.terminal_output = ctk.CTkTextbox(self.terminal_frame, width=630, height=80, fg_color='#111', text_color='#fff', font=('Consolas', 11), border_width=2, border_color="#0ff", corner_radius=10)
        self.terminal_output.pack(padx=6, pady=(0, 4))
        self.terminal_output.configure(state='disabled')
        self.terminal_entry = ctk.CTkEntry(self.terminal_frame, width=600, font=("Consolas", 11), fg_color="#222", text_color="#fff", border_width=2, border_color="#0ff", corner_radius=10)
        self.terminal_entry.pack(padx=6, pady=(0, 8), side="left")
        self.terminal_entry.bind('<Return>', self.handle_terminal_command)
        self.terminal_send = ctk.CTkButton(self.terminal_frame, text="Send", command=self.handle_terminal_command, fg_color="#0ff", text_color="#111", font=("Segoe UI", 10, "bold"), hover_color="#0cc", corner_radius=8, border_width=0, width=60)
        self.terminal_send.pack(padx=(4, 0), pady=(0, 8), side="left")

    def handle_terminal_command(self, event=None):
        cmd = self.terminal_entry.get().strip()
        if not cmd:
            return
        self.terminal_entry.delete(0, 'end')
        self.terminal_output.configure(state='normal')
        if not cmd.startswith('dbts'):
            self.terminal_output.insert('end', '[ERROR] All commands must start with "dbts".\n')
        else:
            args = cmd.split()
            if args[0] == 'dbts':
                if len(args) == 1 or args[1] == '-h':
                    self.terminal_output.insert('end', self.get_dbts_help())
                elif args[1] == 'status':
                    self.terminal_output.insert('end', self.get_dbts_status())
                elif args[1] == 'firewall-log':
                    self.terminal_output.insert('end', self.get_dbts_firewall_log())
                elif args[1] == 'servers':
                    self.terminal_output.insert('end', self.get_dbts_servers())
                else:
                    self.terminal_output.insert('end', f'[ERROR] Unknown dbts command: {" ".join(args[1:])}\n')
            else:
                self.terminal_output.insert('end', '[ERROR] Invalid command.\n')
        self.terminal_output.configure(state='disabled')
        self.terminal_output.see('end')

    def get_dbts_help(self):
        return (
            "DBTS Terminal Help:\n"
            "  dbts -h                Show this help menu\n"
            "  dbts status            Show server and firewall status\n"
            "  dbts firewall-log      Show recent firewall log\n"
            "  dbts servers           Show running servers\n"
        )

    def get_dbts_status(self):
        status = f"Servers running: {self.servers_running}\n"
        status += f"Firewall log entries: {len(self.firewall.get_log())}\n"
        return status

    def get_dbts_firewall_log(self):
        logs = self.firewall.get_log()
        return '\n'.join(logs[-10:]) + '\n' if logs else 'No firewall log entries.\n'

    def get_dbts_servers(self):
        return f"Number of fake servers: {len(self.manager.servers)}\n"

# --- App Launcher ---
def launch_main():
    root = ctk.CTk()
    app = CustomTkApp(root)
    root.mainloop()

if __name__ == "__main__":
    login_root = ctk.CTk()
    LoginWindow(login_root, on_success=launch_main)
    login_root.mainloop()