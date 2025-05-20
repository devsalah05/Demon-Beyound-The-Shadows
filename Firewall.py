import tkinter as tk
from tkinter import scrolledtext
import threading
import queue
import time
import random

class FirewallAI:
    def __init__(self, strengthen=True):
        self.blocked_commands = set()
        self.log = []
        self.command_history = []  # (timestamp, command, server_id)
        self.rate_limit_window = 5  # seconds
        self.max_commands_per_window = 5
        # Stronger, more comprehensive suspicious patterns
        self.suspicious_patterns = [
            'rm -rf', 'format', 'shutdown', 'attack', 'hack', 'ddos', 'delete', 'drop', 'malware',
            'reboot', 'kill', 'fork', 'os.system', 'subprocess', 'eval', 'exec', 'wget', 'curl',
            'powershell', 'nc ', 'ncat', 'netcat', 'python', 'perl', 'bash', 'sh ', 'cmd ', 'ftp',
            'scp', 'sftp', 'nmap', 'hydra', 'brute', 'exploit', 'sqlmap', 'msfconsole', 'meterpreter',
            'reverse shell', 'bind shell', 'virus', 'trojan', 'worm', 'keylogger', 'scan', 'flood',
            'overflow', 'inject', 'root', 'admin', 'sudo', 'su ', 'proxy', 'obfuscate', 'encode',
            'decode', 'bypass', 'disable', 'firewall', 'iptables', 'ufw', 'netsh', 'reg add',
            'reg delete', 'schtasks', 'at ', 'crontab', 'service', 'systemctl'
        ]

    def analyze_command(self, command, server_id=None):
        now = time.time()
        # Rate limiting per server
        if server_id is not None:
            recent = [h for h in self.command_history if h[2] == server_id and now - h[0] < self.rate_limit_window]
            if len(recent) >= self.max_commands_per_window:
                self.blocked_commands.add(command)
                self.log.append(f"[BLOCKED] {command} (Reason: Rate limit exceeded for server {server_id})")
                return False
        # Suspicious pattern detection (stronger)
        for pattern in self.suspicious_patterns:
            if pattern in command.lower():
                self.blocked_commands.add(command)
                self.log.append(f"[BLOCKED] {command} (Reason: Suspicious pattern '{pattern}')")
                return False
        # Repeated suspicious command detection
        recent_cmds = [h[1] for h in self.command_history[-20:]]
        if recent_cmds.count(command) > 1:
            self.blocked_commands.add(command)
            self.log.append(f"[BLOCKED] {command} (Reason: Repeated suspicious command)")
            return False
        # Simulate random advanced detection (more strict)
        if random.random() < 0.10:
            self.blocked_commands.add(command)
            self.log.append(f"[BLOCKED] {command} (Reason: AI anomaly detected)")
            return False
        self.log.append(f"[ALLOWED] {command}")
        self.command_history.append((now, command, server_id))
        return True

    def get_log(self):
        return self.log[-100:]  # Show last 100 events

class FirewallGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Pro AI Firewall for Fake Servers")
        self.root.geometry("600x400")
        self.root.config(bg="#181818")
        self.firewall = FirewallAI()

        self.title_label = tk.Label(root, text="Pro AI Firewall", bg="#282828", fg="#fff", font=("Segoe UI", 14, "bold"))
        self.title_label.pack(fill=tk.X, pady=(10, 0))

        self.command_label = tk.Label(root, text="Test Command:", bg="#181818", fg="#fff", font=("Segoe UI", 10))
        self.command_label.pack(pady=(20, 0))
        self.command_entry = tk.Entry(root, width=40, font=("Consolas", 11), bg="#232323", fg="#fff", insertbackground="#fff", borderwidth=2, relief="groove")
        self.command_entry.pack(pady=5)
        self.test_button = tk.Button(root, text="Analyze Command", command=self.test_command, bg="#444", fg="#fff", font=("Segoe UI", 10, "bold"), activebackground="#222", activeforeground="#0f0", borderwidth=0, padx=10, pady=2)
        self.test_button.pack(pady=5)

        self.log_text = scrolledtext.ScrolledText(root, width=70, height=15, state='disabled', bg='#1a1a1a', fg='#0ff', font=('Consolas', 11), borderwidth=2, relief="groove")
        self.log_text.pack(pady=10)

        self.update_log()

    def test_command(self):
        command = self.command_entry.get()
        if command:
            allowed = self.firewall.analyze_command(command)
            self.command_entry.delete(0, tk.END)
            self.update_log()

    def update_log(self):
        logs = self.firewall.get_log()
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        for entry in logs:
            self.log_text.insert(tk.END, entry + '\n')
        self.log_text.config(state='disabled')
        self.log_text.see(tk.END)
        self.root.after(1000, self.update_log)

if __name__ == "__main__":
    root = tk.Tk()
    app = FirewallGUI(root)
    root.mainloop()
