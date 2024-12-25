import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import zlib
import base64
import json

def decode_blueprint(blueprint_string):
    """
    Decodes a Factorio blueprint string into a JSON-like structure.
    """
    encoded_data = blueprint_string[1:]  # Remove version prefix
    decoded_data = zlib.decompress(base64.b64decode(encoded_data))
    return json.loads(decoded_data)

def encode_blueprint(blueprint_data):
    """
    Encodes a JSON-like structure into a Factorio blueprint string.
    """
    compressed_data = zlib.compress(json.dumps(blueprint_data).encode("utf-8"))
    return "0" + base64.b64encode(compressed_data).decode("utf-8")

def decode_action():
    blueprint_string = blueprint_input.get("1.0", tk.END).strip()
    if not blueprint_string.startswith("0"):
        messagebox.showerror("Error", "Invalid Factorio blueprint string.")
        return
    try:
        decoded_data = decode_blueprint(blueprint_string)
        json_output.delete("1.0", tk.END)
        json_output.insert("1.0", json.dumps(decoded_data, indent=4))
        messagebox.showinfo("Success", "Blueprint decoded successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to decode blueprint: {e}")

def encode_action():
    try:
        json_data = json.loads(json_output.get("1.0", tk.END).strip())
        encoded_string = encode_blueprint(json_data)
        blueprint_input.delete("1.0", tk.END)
        blueprint_input.insert("1.0", encoded_string)
        messagebox.showinfo("Success", "Blueprint encoded successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to encode blueprint: {e}")

def save_json():
    json_data = json_output.get("1.0", tk.END).strip()
    if not json_data:
        messagebox.showerror("Error", "No decoded blueprint to save.")
        return
    filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if filepath:
        with open(filepath, "w") as file:
            file.write(json_data)
        messagebox.showinfo("Success", f"Decoded JSON saved to {filepath}.")

def load_json():
    filepath = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if filepath:
        with open(filepath, "r") as file:
            json_data = file.read()
        json_output.delete("1.0", tk.END)
        json_output.insert("1.0", json_data)
        messagebox.showinfo("Success", f"JSON loaded from {filepath}.")

# GUI Setup
root = tk.Tk()
root.title("Factorio Blueprint Tool")

# Blueprint Input
tk.Label(root, text="Blueprint String:").pack()
blueprint_input = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=8)
blueprint_input.pack(fill=tk.BOTH, expand=True)

# Decode/Encode Buttons
btn_frame = tk.Frame(root)
btn_frame.pack(fill=tk.X)
tk.Button(btn_frame, text="Decode", command=decode_action).pack(side=tk.LEFT, padx=5, pady=5)
tk.Button(btn_frame, text="Encode", command=encode_action).pack(side=tk.LEFT, padx=5, pady=5)
tk.Button(btn_frame, text="Save JSON", command=save_json).pack(side=tk.LEFT, padx=5, pady=5)
tk.Button(btn_frame, text="Load JSON", command=load_json).pack(side=tk.LEFT, padx=5, pady=5)

# JSON Output
tk.Label(root, text="Decoded JSON:").pack()
json_output = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=20)
json_output.pack(fill=tk.BOTH, expand=True)

# Start GUI
root.mainloop()
