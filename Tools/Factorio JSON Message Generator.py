import tkinter as tk
from tkinter import ttk, messagebox
import json
import math

# Default colors for each group
default_colors = [
    "255,0,0",        # Red for 1st group (0 to 10)
    "255,255,255",    # White for 2nd group (10 to 100)
    "255,165,0",      # Orange for 3rd group (100 to 1,000)
    "255,255,0",      # Yellow for 4th group (1,000 to 10,000)
    "0,255,0",        # Green for 5th group (10,000 to 100,000)
    "0,255,255",      # Cyan for 6th group (100,000 to 1,000,000)
    "127,127,255"     # Purple for 7th group (1,000,000 to 10,000,000)
]

# Assign distinct colors to each group based on user input
def generate_color(group_index, user_colors):
    return user_colors[group_index]

# Format text for large numbers, including decimals for mid-values
def format_text(value):
    if value >= 1000000:
        return f"{value / 1000000:.1f}M" if value % 1000000 != 0 else f"{value // 1000000}M"
    elif value >= 1000:
        return f"{value / 1000:.1f}K" if value % 1000 != 0 else f"{value // 1000}K"
    return str(value)

# Group definitions for steps (ordered bottom to top)
GROUPS = {
    "1st group (0 to 10)": list(range(0, 11)),
    "2nd group (10 to 100)": list(range(15, 101, 5)),
    "3rd group (100 to 1,000)": list(range(100, 1001, 50)),
    "4th group (1,000 to 10,000)": list(range(1000, 10001, 500)),
    "5th group (10,000 to 100,000)": list(range(10000, 100001, 10000)),
    "6th group (100,000 to 1,000,000)": list(range(100000, 1000001, 100000)),
    "7th group (1,000,000 to 10,000,000)": list(range(1000000, 10000001, 1000000))
}

# Function to generate JSON code with quality and extra code
def generate_json_with_quality(selected_quality, extra_top, extra_bottom, user_colors, zero_color):
    messages = []

    # Add 0 with its specific color
    formatted_zero_color = f"[color={zero_color}]"
    messages.append({
        "condition": {
            "first_signal": {"name": "parameter-0"},
            "constant": 0,
            "comparator": "\u2265"
        },
        "icon": {
            "name": "parameter-0"
        },
        "text": f"{formatted_zero_color}0[/color]"
    })

    # Reverse the groups and their values to start from the largest
    for group_index, (group_name, values) in enumerate(reversed(list(GROUPS.items()))):
        group_color = generate_color(len(GROUPS) - group_index - 1, user_colors)  # Match color to original group order
        for value in reversed(values):
            if value == 0:  # Skip 0, already added
                continue
            formatted_color = f"[color={group_color}]"
            formatted_text = format_text(value)
            message = {
                "condition": {
                    "first_signal": {"name": "parameter-0"},
                    "constant": value,
                    "comparator": "\u2265"
                },
                "icon": {
                    "name": "parameter-0"
                },
                "text": f"{formatted_color}{formatted_text}[/color]"
            }
            if selected_quality and selected_quality != "Normal":
                message["condition"]["first_signal"]["quality"] = selected_quality
                message["icon"]["quality"] = selected_quality

            messages.append(message)

    final_result = extra_top + "\n" + json.dumps(messages, indent=4) + "\n" + extra_bottom
    return final_result, len(messages)

# GUI Application
def create_gui():
    def process_json():
        try:
            selected_quality = next((q for q, var in quality_vars.items() if var.get()), "Normal")
            extra_top = extra_top_text.get("1.0", tk.END).strip()
            extra_bottom = extra_bottom_text.get("1.0", tk.END).strip()

            # Get user-defined colors
            user_colors = [color_entries[i].get() for i in range(len(color_entries))]
            zero_color = zero_color_entry.get()

            json_output, message_count = generate_json_with_quality(selected_quality, extra_top, extra_bottom, user_colors, zero_color)

            output_text.delete("1.0", tk.END)
            output_text.insert("1.0", json_output)

            message_count_label.config(text=f"Total Messages: {message_count}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def toggle_quality(selected):
        for quality, var in quality_vars.items():
            if quality != selected:
                var.set(False)

    # Main window
    root = tk.Tk()
    root.title("JSON Code Generator with Quality")

    # Extra code areas
    extra_top_frame = ttk.LabelFrame(root, text="Extra Top Code")
    extra_top_frame.pack(fill="both", expand=True, padx=10, pady=5)
    extra_top_text = tk.Text(extra_top_frame, height=5)
    extra_top_text.pack(fill="both", expand=True, padx=5, pady=5)

    settings_frame = ttk.LabelFrame(root, text="Settings")
    settings_frame.pack(fill="x", padx=10, pady=5)

    # Quality radio buttons
    quality_frame = ttk.LabelFrame(settings_frame, text="Select Quality")
    quality_frame.grid(row=0, column=0, columnspan=2, pady=10, sticky="w")

    qualities = ["Normal", "uncommon", "rare", "epic", "legendary"]
    quality_vars = {quality: tk.BooleanVar(value=(quality == "Normal")) for quality in qualities}

    def on_quality_change(selected):
        toggle_quality(selected)

    for idx, quality in enumerate(qualities):
        chk = ttk.Checkbutton(
            quality_frame,
            text=quality.capitalize(),
            variable=quality_vars[quality],
            command=lambda q=quality: on_quality_change(q)
        )
        chk.grid(row=0, column=idx, padx=5, pady=5)

    # Color settings
    color_frame = ttk.LabelFrame(settings_frame, text="Group Colors")
    color_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky="w")

    zero_color_label = ttk.Label(color_frame, text="Color for 0:")
    zero_color_label.grid(row=0, column=0, padx=5, pady=2, sticky="w")
    zero_color_entry = ttk.Entry(color_frame, width=20)
    zero_color_entry.insert(0, "255,0,0")  # Default red for 0
    zero_color_entry.grid(row=0, column=1, padx=5, pady=2)

    color_entries = []
    for i, group_name in enumerate(GROUPS.keys()):
        ttk.Label(color_frame, text=group_name).grid(row=i + 1, column=0, padx=5, pady=2, sticky="w")
        color_entry = ttk.Entry(color_frame, width=20)
        color_entry.insert(0, default_colors[i])
        color_entry.grid(row=i + 1, column=1, padx=5, pady=2)
        color_entries.append(color_entry)

    # Output frame
    output_frame = ttk.LabelFrame(root, text="Generated JSON")
    output_frame.pack(fill="both", expand=True, padx=10, pady=10)

    output_text = tk.Text(output_frame, height=20)
    output_text.pack(fill="both", expand=True, padx=5, pady=5)

    # Extra bottom code area
    extra_bottom_frame = ttk.LabelFrame(root, text="Extra Bottom Code")
    extra_bottom_frame.pack(fill="both", expand=True, padx=10, pady=5)
    extra_bottom_text = tk.Text(extra_bottom_frame, height=5)
    extra_bottom_text.pack(fill="both", expand=True, padx=5, pady=5)

    # Message count
    message_count_label = ttk.Label(root, text="Total Messages: 0")
    message_count_label.pack(pady=5)

    # Buttons
    process_button = ttk.Button(root, text="Generate JSON", command=process_json)
    process_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
