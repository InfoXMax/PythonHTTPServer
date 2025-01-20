import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import threading
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler

class CustomHTTPRequestHandler(SimpleHTTPRequestHandler):
    app = None

    def log_message(self, format, *args):
        message = f"{self.client_address[0]} - - [{self.log_date_time_string()}] {format % args}"
        if CustomHTTPRequestHandler.app:
            CustomHTTPRequestHandler.app.log_message(message)
        else:
            print(message)

    def do_GET(self):
        self.log_message("GET request for %s", self.path)
        super().do_GET()

    def list_directory(self, path):
        try:
            file_list = os.listdir(path)
        except OSError:
            self.send_error(404, "No permission to list directory")
            return None

        self.log_message("Directory listing requested for %s", self.path)

        file_list.sort(key=lambda a: a.lower())
        display_path = os.path.basename(path)
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
        <link rel="shortcut icon" href="logo.ico">
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Local HTTP Server {display_path}</title>
            <style>
                html,body {{
                            height: 100%;
            margin: 0;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(to bottom right, #f0f4f8, #d9e2ec);
                    
                    
                    
                }}
                header {{
                    background-color: #003366;
                    color: white;
                    padding: 1em 2em;
                    text-align: center;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                }}
                .directory-list {{
                    max-width: 50%;
                    margin: 2em auto;
                    padding: 0;
                    list-style: none;
                }}
                .directory-list li {{
                    background: white;
                    margin: 0.5em 0;
                    padding: 1em;
                    border-radius: 8px;
                    box-shadow: 0 1px 6px rgba(0, 0, 0, 0.1);
                    transition: background-color 0.3s;
                }}
                .directory-list li:hover {{
                    background-color: #e0f7fa;
                }}
                .directory-list li a {{
                    text-decoration: none;
                    color: #00796b;
                    font-weight: bold;
                }}
                .directory-list li a:hover {{
                    color: #004d40;
                }}

            </style>
        </head>
        <body>
            <header>
                <h1>My Local Http Server {display_path}</h1>
            </header>
            <ul class="directory-list">
        """
        for name in file_list:
            fullname = os.path.join(path, name)
            display_name = name
            link_name = name

            if os.path.isdir(fullname):
                display_name += "/"
                link_name += "/"

            html += f'<li><a href="{link_name}">{display_name}</a></li>'
            self.log_message("File listed: %s", display_name)

        html += """
            </ul>
                        <footer style="text-align: center; padding: 20px; font-size: 14px; color: #555;">
        Made with <span style="color: red;">♥</span> by <a href="https://github.com/InfoXMax" target="_blank" style="color: #4CAF50; text-decoration: none;">InfoXMax</a>
    </footer>
        </body>

        </html>
        """

        encoded = html.encode("utf-8", "surrogateescape")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)
        return None

class HTTPServerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("My Local HTTP Server")
        self.server_thread = None
        self.server = None
        self.port = 8000
        self.directory = os.getcwd()  # Default directory to the current working directory

        self.root.iconbitmap('logo.ico')  # Make sure to provide the correct path to your .ico file

        # Disable window resizing and maximize
        self.root.resizable(False, False)

        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self.root, text="Port:").grid(row=0, column=0, padx=10, pady=5)
        self.port_entry = ttk.Entry(self.root, width=10)
        self.port_entry.insert(0, str(self.port))
        self.port_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        ttk.Label(self.root, text="Folder:").grid(row=1, column=0, padx=10, pady=5)
        self.folder_label = ttk.Label(self.root, text=self.directory, anchor="w", width=40, background="white", relief="sunken")
        self.folder_label.grid(row=1, column=1, columnspan=2, padx=10, pady=5, sticky="w")

        self.browse_button = ttk.Button(self.root, text="Browse", command=self.browse_folder)
        self.browse_button.grid(row=1, column=3, padx=10, pady=5)

        self.start_button = ttk.Button(self.root, text="Start Server", command=self.start_server)
        self.start_button.grid(row=2, column=0, padx=10, pady=10)

        self.stop_button = ttk.Button(self.root, text="Stop Server", command=self.stop_server, state=tk.DISABLED)
        self.stop_button.grid(row=2, column=1, padx=10, pady=10)

        self.open_browser_button = ttk.Button(self.root, text="Open in Browser", command=self.open_browser, state=tk.DISABLED)
        self.open_browser_button.grid(row=2, column=2, padx=10, pady=10)

        self.log_text = tk.Text(self.root, height=15, width=60, state=tk.DISABLED)
        self.log_text.grid(row=3, column=0, columnspan=4, padx=10, pady=10)

        log_frame = tk.Frame(self.root)
        log_frame.grid(row=3, column=0, columnspan=4, padx=10, pady=10)

        self.log_text = tk.Text(log_frame, height=15, width=60, state=tk.DISABLED)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(log_frame, command=self.log_text.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=self.scrollbar.set)
        
    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.directory = folder
            self.folder_label.config(text=self.directory)

    def log_message(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def start_server(self):
        try:
            self.port = int(self.port_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Port must be an integer.")
            return

        if self.server_thread is not None and self.server_thread.is_alive():
            messagebox.showwarning("Warning", "Server is already running.")
            return

        os.chdir(self.directory)
        CustomHTTPRequestHandler.app = self
        self.server = HTTPServer(("", self.port), CustomHTTPRequestHandler)
        self.server_thread = threading.Thread(target=self.run_server, daemon=True)
        self.server_thread.start()

        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.open_browser_button.config(state=tk.NORMAL)
        self.log_message(f"Server started at http://localhost:{self.port}/ serving folder: {self.directory}")

    def run_server(self):
        self.server.serve_forever()

    def stop_server(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.server_thread = None
            self.server = None

        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.open_browser_button.config(state=tk.DISABLED)
        self.log_message("Server stopped.")

    def open_browser(self):
        webbrowser.open(f"http://localhost:{self.port}/")

    def on_close(self):
        if self.server_thread and self.server_thread.is_alive():
            self.stop_server()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = HTTPServerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
