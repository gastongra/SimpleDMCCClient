import tkinter as tk
from tkinter import ttk, messagebox
import configparser
import subprocess
import os

CONFIG_FILE = 'config.ini'

class ConfigApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('SimpleDMCCClient Config & Runner')
        self.geometry('400x400')
        self.resizable(False, False)
        self.config_parser = configparser.ConfigParser()
        self.fields = {}
        self.create_widgets()
        self.load_config()

    def create_widgets(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        self.frames = {}
        for section in ['AES', 'DialingExtension', 'DialedExtension']:
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=section)
            self.frames[section] = frame
            self.fields[section] = {}

        # Add fields for each section
        self.add_section_fields('AES', ['ip', 'port', 'hostname', 'switch_conn_name', 'switch_name'])
        self.add_section_fields('DialingExtension', ['extension', 'password'])
        self.add_section_fields('DialedExtension', ['extension'])

        # Save, Run, and Exit buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text='Save Config', command=self.save_config).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='Run MakeTestCall.py', command=self.run_script).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='Exit', command=self.exit_app).pack(side='left', padx=5)
    def exit_app(self):
        self.destroy()

    def add_section_fields(self, section, keys):
        frame = self.frames[section]
        for i, key in enumerate(keys):
            ttk.Label(frame, text=key).grid(row=i, column=0, sticky='e', padx=5, pady=5)
            entry = ttk.Entry(frame, width=30)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.fields[section][key] = entry

    def load_config(self):
        if not os.path.exists(CONFIG_FILE):
            messagebox.showerror('Error', f'{CONFIG_FILE} not found!')
            return
        self.config_parser.read(CONFIG_FILE)
        for section in self.fields:
            for key, entry in self.fields[section].items():
                value = self.config_parser.get(section, key, fallback='')
                entry.delete(0, tk.END)
                entry.insert(0, value)

    def save_config(self):
        for section in self.fields:
            if not self.config_parser.has_section(section):
                self.config_parser.add_section(section)
            for key, entry in self.fields[section].items():
                self.config_parser.set(section, key, entry.get())
        with open(CONFIG_FILE, 'w') as f:
            self.config_parser.write(f)
        messagebox.showinfo('Saved', 'Configuration saved successfully!')

    def run_script(self):
        self.save_config()
        try:
            result = subprocess.run(['python', 'MakeTestCall.py'], capture_output=True, text=True, check=True)
            messagebox.showinfo('Script Output', result.stdout or 'Script executed successfully!')
        except subprocess.CalledProcessError as e:
            messagebox.showerror('Script Error', e.stderr or str(e))

if __name__ == '__main__':
    app = ConfigApp()
    app.mainloop()
