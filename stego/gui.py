import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError:
    DND_FILES = None
    TkinterDnD = None

from .crypto import encrypt_message, decrypt_message
from .header import HEADER_SIZE, create_header, parse_header
from .lsb import calculate_capacity, encode_data, extract_data


# ============================================================
# COLORS
# ============================================================

BG = "#07111F"
PANEL = "#0B1726"
PANEL_2 = "#0F2033"

BLUE = "#1769AA"
BLUE_HOVER = "#1E7BC4"

TEXT = "#EAF4FF"
TEXT_MUTED = "#8FA8BD"

SUCCESS = "#35C98A"
ERROR = "#FF5C5C"

ENTRY_BG = "#06101C"


# ============================================================
# GUI
# ============================================================

class SteganoGUI:

    def __init__(self, root):

        self.root = root

        self.root.title("SteganoTool")
        self.root.geometry("950x700")
        self.root.minsize(650, 550)

        self.root.configure(bg=BG)

        # Image state
        self.image_path = None
        self.image = None

        self.decode_image_path = None

        # Encoded image state
        self.encoded_image = None
        self.encoded_image_path = None

        # ImageTk references
        self.preview_photo = None
        self.encoded_preview_photo = None

        self.setup_style()
        self.build_ui()

    # ========================================================
    # STYLE
    # ========================================================

    def setup_style(self):

        style = ttk.Style()

        style.theme_use("clam")

        style.configure(
            "TFrame",
            background=BG
        )

        style.configure(
            "Panel.TFrame",
            background=PANEL
        )

        style.configure(
            "TLabel",
            background=BG,
            foreground=TEXT,
            font=("Segoe UI", 10)
        )

        style.configure(
            "Panel.TLabel",
            background=PANEL,
            foreground=TEXT,
            font=("Segoe UI", 10)
        )

        style.configure(
            "Title.TLabel",
            background=BG,
            foreground=TEXT,
            font=("Segoe UI", 24, "bold")
        )

        style.configure(
            "Subtitle.TLabel",
            background=BG,
            foreground=TEXT_MUTED,
            font=("Segoe UI", 10)
        )

        style.configure(
            "TButton",
            background=BLUE,
            foreground="#FFFFFF",
            borderwidth=0,
            padding=(16, 9),
            font=("Segoe UI", 10, "bold")
        )

        style.map(
            "TButton",
            background=[
                ("active", BLUE_HOVER)
            ]
        )

        # Notebook

        style.configure(
            "TNotebook",
            background=BG,
            borderwidth=0,
            tabmargins=0
        )

        style.configure(
            "TNotebook.Tab",
            background=PANEL,
            foreground=TEXT_MUTED,
            padding=(25, 11),
            borderwidth=0
        )

        style.map(
            "TNotebook.Tab",
            background=[
                ("selected", PANEL_2)
            ],
            foreground=[
                ("selected", TEXT)
            ]
        )

    # ========================================================
    # MAIN UI
    # ========================================================

    def build_ui(self):

        main = tk.Frame(
            self.root,
            bg=BG
        )

        main.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=20
        )

        # ----------------------------------------------------
        # Header
        # ----------------------------------------------------

        title = tk.Label(
            main,
            text="STEGANOTOOL",
            bg=BG,
            fg=TEXT,
            font=("Segoe UI", 24, "bold")
        )

        title.pack(
            anchor="w"
        )

        subtitle = tk.Label(
            main,
            text="Secure message hiding with LSB steganography",
            bg=BG,
            fg=TEXT_MUTED,
            font=("Segoe UI", 10)
        )

        subtitle.pack(
            anchor="w",
            pady=(0, 18)
        )

        # ----------------------------------------------------
        # Notebook
        # ----------------------------------------------------

        notebook = ttk.Notebook(main)

        notebook.pack(
            fill="both",
            expand=True
        )

        self.encode_tab = tk.Frame(
            notebook,
            bg=PANEL
        )

        self.decode_tab = tk.Frame(
            notebook,
            bg=PANEL
        )

        notebook.add(
            self.encode_tab,
            text="  ENCODE  "
        )

        notebook.add(
            self.decode_tab,
            text="  DECODE  "
        )

        self.build_encode_tab()
        self.build_decode_tab()

    # ========================================================
    # SCROLLABLE FRAME
    # ========================================================

    def create_scrollable_frame(self, parent):

        container = tk.Frame(
            parent,
            bg=PANEL
        )

        canvas = tk.Canvas(
            container,
            bg=PANEL,
            highlightthickness=0
        )

        scrollbar = ttk.Scrollbar(
            container,
            orient="vertical",
            command=canvas.yview
        )

        content = tk.Frame(
            canvas,
            bg=PANEL
        )

        content_window = canvas.create_window(
            (0, 0),
            window=content,
            anchor="nw"
        )

        def update_scroll_region(event=None):

            canvas.configure(
                scrollregion=canvas.bbox("all")
            )

        content.bind(
            "<Configure>",
            update_scroll_region
        )

        def resize_content(event):

            canvas.itemconfig(
                content_window,
                width=event.width
            )

        canvas.bind(
            "<Configure>",
            resize_content
        )

        canvas.configure(
            yscrollcommand=scrollbar.set
        )

        canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        return container, content

    # ========================================================
    # ENCODE TAB
    # ========================================================

    def build_encode_tab(self):

        container, frame = self.create_scrollable_frame(
            self.encode_tab
        )

        container.pack(
            fill="both",
            expand=True
        )

        frame.configure(
            padx=25,
            pady=25
        )

        # ----------------------------------------------------
        # Cover Image
        # ----------------------------------------------------

        self.section_title(
            frame,
            "Cover Image"
        )

        self.encode_image_box = tk.Frame(
            frame,
            bg=PANEL_2,
            height=180
        )

        self.encode_image_box.pack(
            fill="x",
            pady=(8, 10)
        )

        self.encode_image_box.pack_propagate(
            False
        )

        self.encode_image_label = tk.Label(
            self.encode_image_box,
            text="Click or drop an image here",
            bg=PANEL_2,
            fg=TEXT_MUTED,
            font=("Segoe UI", 11)
        )

        self.encode_image_label.pack(
            fill="both",
            expand=True
        )

        self.encode_image_label.bind(
            "<Button-1>",
            lambda event: self.select_encode_image()
        )

        if DND_FILES:

            self.encode_image_label.drop_target_register(
                DND_FILES
            )

            self.encode_image_label.dnd_bind(
                "<<Drop>>",
                self.drop_encode_image
            )

        self.blue_button(
            frame,
            "Select Image",
            self.select_encode_image
        ).pack(
            anchor="w"
        )

        # ----------------------------------------------------
        # Capacity
        # ----------------------------------------------------

        self.capacity_label = tk.Label(
            frame,
            text="Capacity: --",
            bg=PANEL,
            fg=TEXT_MUTED,
            font=("Segoe UI", 9)
        )

        self.capacity_label.pack(
            anchor="w",
            pady=(8, 0)
        )

        # ----------------------------------------------------
        # Message
        # ----------------------------------------------------

        self.section_title(
            frame,
            "Secret Message"
        )

        self.message_text = tk.Text(
            frame,
            height=7,
            bg=ENTRY_BG,
            fg=TEXT,
            insertbackground=TEXT,
            selectbackground=BLUE,
            relief="flat",
            borderwidth=0,
            font=("Consolas", 10),
            padx=10,
            pady=10
        )

        self.message_text.pack(
            fill="x",
            pady=(8, 0)
        )

        # ----------------------------------------------------
        # Password
        # ----------------------------------------------------

        self.section_title(
            frame,
            "Password"
        )

        self.encode_password = tk.Entry(
            frame,
            bg=ENTRY_BG,
            fg=TEXT,
            insertbackground=TEXT,
            selectbackground=BLUE,
            show="*",
            relief="flat",
            borderwidth=0,
            font=("Segoe UI", 10)
        )

        self.encode_password.pack(
            fill="x",
            ipady=9,
            pady=(8, 0)
        )

        # ----------------------------------------------------
        # Encode Button
        # ----------------------------------------------------

        self.blue_button(
            frame,
            "🔒  Encrypt & Hide",
            self.encode
        ).pack(
            anchor="e",
            pady=18
        )

        # ----------------------------------------------------
        # Encoded Preview
        # ----------------------------------------------------

        self.section_title(
            frame,
            "Encoded Image"
        )

        self.encoded_image_box = tk.Frame(
            frame,
            bg=PANEL_2,
            height=220
        )

        self.encoded_image_box.pack(
            fill="x",
            pady=(8, 8)
        )

        self.encoded_image_box.pack_propagate(
            False
        )

        self.encoded_image_label = tk.Label(
            self.encoded_image_box,
            text="Encoded image will appear here",
            bg=PANEL_2,
            fg=TEXT_MUTED,
            font=("Segoe UI", 10)
        )

        self.encoded_image_label.pack(
            fill="both",
            expand=True
        )

        self.encoded_path_label = tk.Label(
            frame,
            text="Not saved yet",
            bg=PANEL,
            fg=TEXT_MUTED,
            anchor="w"
        )

        self.encoded_path_label.pack(
            fill="x"
        )

        button_frame = tk.Frame(
            frame,
            bg=PANEL
        )

        button_frame.pack(
            anchor="e",
            pady=12
        )

        self.blue_button(
            button_frame,
            "Save As",
            self.save_encoded_image
        ).pack(
            side="left",
            padx=5
        )

        self.blue_button(
            button_frame,
            "Open Image",
            self.open_encoded_image
        ).pack(
            side="left"
        )

    # ========================================================
    # DECODE TAB
    # ========================================================

    def build_decode_tab(self):

        container, frame = self.create_scrollable_frame(
            self.decode_tab
        )

        container.pack(
            fill="both",
            expand=True
        )

        frame.configure(
            padx=25,
            pady=25
        )

        self.section_title(
            frame,
            "Encoded Image"
        )

        self.decode_image_box = tk.Frame(
            frame,
            bg=PANEL_2,
            height=200
        )

        self.decode_image_box.pack(
            fill="x",
            pady=(8, 10)
        )

        self.decode_image_box.pack_propagate(
            False
        )

        self.decode_image_label = tk.Label(
            self.decode_image_box,
            text="Click or drop an encoded image here",
            bg=PANEL_2,
            fg=TEXT_MUTED,
            font=("Segoe UI", 11)
        )

        self.decode_image_label.pack(
            fill="both",
            expand=True
        )

        self.decode_image_label.bind(
            "<Button-1>",
            lambda event: self.select_decode_image()
        )

        if DND_FILES:

            self.decode_image_label.drop_target_register(
                DND_FILES
            )

            self.decode_image_label.dnd_bind(
                "<<Drop>>",
                self.drop_decode_image
            )

        self.blue_button(
            frame,
            "Select Image",
            self.select_decode_image
        ).pack(
            anchor="w"
        )

        self.section_title(
            frame,
            "Password"
        )

        self.decode_password = tk.Entry(
            frame,
            bg=ENTRY_BG,
            fg=TEXT,
            insertbackground=TEXT,
            selectbackground=BLUE,
            show="*",
            relief="flat",
            borderwidth=0,
            font=("Segoe UI", 10)
        )

        self.decode_password.pack(
            fill="x",
            ipady=9,
            pady=(8, 0)
        )

        self.blue_button(
            frame,
            "🔓  Extract Message",
            self.decode
        ).pack(
            anchor="e",
            pady=18
        )

        self.section_title(
            frame,
            "Extracted Message"
        )

        self.output_text = tk.Text(
            frame,
            height=10,
            bg=ENTRY_BG,
            fg=TEXT,
            insertbackground=TEXT,
            selectbackground=BLUE,
            relief="flat",
            borderwidth=0,
            font=("Consolas", 10),
            padx=10,
            pady=10
        )

        self.output_text.pack(
            fill="x"
        )

        self.blue_button(
            frame,
            "Save Message",
            self.save_message
        ).pack(
            anchor="e",
            pady=12
        )

    # ========================================================
    # HELPERS
    # ========================================================

    def section_title(self, parent, text):

        label = tk.Label(
            parent,
            text=text,
            bg=PANEL,
            fg=TEXT,
            font=("Segoe UI", 11, "bold")
        )

        label.pack(
            anchor="w",
            pady=(16, 0)
        )

    def blue_button(self, parent, text, command):

        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=BLUE,
            fg="white",
            activebackground=BLUE_HOVER,
            activeforeground="white",
            relief="flat",
            borderwidth=0,
            padx=16,
            pady=9,
            cursor="hand2",
            font=("Segoe UI", 10, "bold")
        )

    # ========================================================
    # IMAGE SELECTION
    # ========================================================

    def select_encode_image(self):

        path = filedialog.askopenfilename(
            filetypes=[
                (
                    "Image files",
                    "*.png *.bmp *.jpg *.jpeg *.webp"
                ),
                ("All files", "*.*")
            ]
        )

        if path:
            self.set_encode_image(path)

    def select_decode_image(self):

        path = filedialog.askopenfilename(
            filetypes=[
                (
                    "Image files",
                    "*.png *.bmp *.jpg *.jpeg *.webp"
                ),
                ("All files", "*.*")
            ]
        )

        if path:
            self.set_decode_image(path)

    def set_encode_image(self, path):

        try:

            image = Image.open(path).convert("RGB")

            self.image_path = path
            self.image = image

            capacity = calculate_capacity(image)

            self.capacity_label.config(
                text=f"Raw capacity: {capacity:,} bytes"
            )

            self.show_preview(
                image,
                self.encode_image_label
            )

        except Exception as exc:

            messagebox.showerror(
                "Error",
                str(exc)
            )

    def set_decode_image(self, path):

        try:

            image = Image.open(path).convert("RGB")

            self.decode_image_path = path

            self.show_preview(
                image,
                self.decode_image_label
            )

        except Exception as exc:

            messagebox.showerror(
                "Error",
                str(exc)
            )

    # ========================================================
    # DRAG & DROP
    # ========================================================

    def drop_encode_image(self, event):

        path = event.data.strip("{}")

        self.set_encode_image(path)

    def drop_decode_image(self, event):

        path = event.data.strip("{}")

        self.set_decode_image(path)

    # ========================================================
    # IMAGE PREVIEW
    # ========================================================

    def show_preview(self, image, label):

        preview = image.copy()

        preview.thumbnail((700, 170))

        photo = ImageTk.PhotoImage(preview)

        label.configure(
            image=photo,
            text=""
        )

        label.image = photo

    def show_encoded_preview(self, image):

        preview = image.copy()

        preview.thumbnail((700, 210))

        self.encoded_preview_photo = ImageTk.PhotoImage(
            preview
        )

        self.encoded_image_label.configure(
            image=self.encoded_preview_photo,
            text=""
        )

    # ========================================================
    # ENCODE
    # ========================================================

    def encode(self):

        if self.image is None:

            messagebox.showerror(
                "Error",
                "Please select an image."
            )

            return

        message = self.message_text.get(
            "1.0",
            "end-1c"
        )

        password = self.encode_password.get()

        if not message:

            messagebox.showerror(
                "Error",
                "Message cannot be empty."
            )

            return

        if not password:

            messagebox.showerror(
                "Error",
                "Password cannot be empty."
            )

            return

        try:

            message_bytes = message.encode(
                "utf-8"
            )

            ciphertext, salt, nonce = encrypt_message(
                message_bytes,
                password
            )

            header = create_header(
                salt,
                nonce,
                len(ciphertext)
            )

            payload = header + ciphertext

            capacity = calculate_capacity(
                self.image
            )

            if len(payload) > capacity:

                messagebox.showerror(
                    "Capacity Error",
                    "✗ Message is too large for this image."
                )

                return

            encoded_image = encode_data(
                self.image.copy(),
                payload
            )

            self.encoded_image = encoded_image
            self.encoded_image_path = None

            self.show_encoded_preview(
                encoded_image
            )

            self.encoded_path_label.config(
                text="✓ Encoded image ready — click Save As"
            )

            messagebox.showinfo(
                "Success",
                "✓ Message successfully hidden!"
            )

        except Exception as exc:

            messagebox.showerror(
                "Encode Error",
                str(exc)
            )

    # ========================================================
    # SAVE ENCODED IMAGE
    # ========================================================

    def save_encoded_image(self):

        if self.encoded_image is None:

            messagebox.showerror(
                "Error",
                "There is no encoded image to save."
            )

            return

        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG image", "*.png")
            ]
        )

        if not path:
            return

        self.encoded_image.save(
            path,
            format="PNG"
        )

        self.encoded_image_path = path

        self.encoded_path_label.config(
            text=f"✓ Saved: {path}"
        )

    # ========================================================
    # OPEN ENCODED IMAGE
    # ========================================================

    def open_encoded_image(self):

        if not self.encoded_image_path:

            messagebox.showerror(
                "Error",
                "Save the encoded image first."
            )

            return

        os.startfile(
            os.path.abspath(
                self.encoded_image_path
            )
        )

    # ========================================================
    # DECODE
    # ========================================================

    def decode(self):

        if not self.decode_image_path:

            messagebox.showerror(
                "Error",
                "Please select an encoded image."
            )

            return

        password = self.decode_password.get()

        if not password:

            messagebox.showerror(
                "Error",
                "Password cannot be empty."
            )

            return

        try:

            image = Image.open(
                self.decode_image_path
            ).convert("RGB")

            header_bytes = extract_data(
                image,
                HEADER_SIZE
            )

            header = parse_header(
                header_bytes
            )

            ciphertext_length = header[
                "ciphertext_length"
            ]

            total_length = (
                HEADER_SIZE +
                ciphertext_length
            )

            payload = extract_data(
                image,
                total_length
            )

            ciphertext = payload[
                HEADER_SIZE:
            ]

            message_bytes = decrypt_message(
                ciphertext,
                password,
                header["salt"],
                header["nonce"]
            )

            message = message_bytes.decode(
                "utf-8"
            )

            self.output_text.delete(
                "1.0",
                "end"
            )

            self.output_text.insert(
                "1.0",
                message
            )

            messagebox.showinfo(
                "Success",
                "✓ Message extracted successfully.\n"
                "✓ Integrity verified."
            )

        except Exception as exc:

            messagebox.showerror(
                "Decode Error",
                str(exc)
            )

    # ========================================================
    # SAVE DECODED MESSAGE
    # ========================================================

    def save_message(self):

        message = self.output_text.get(
            "1.0",
            "end-1c"
        )

        if not message:
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("Text file", "*.txt")
            ]
        )

        if not path:
            return

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(message)

        messagebox.showinfo(
            "Saved",
            "Message saved successfully."
        )


# ============================================================
# RUN
# ============================================================

def run():

    if TkinterDnD:

        root = TkinterDnD.Tk()

    else:

        root = tk.Tk()

    SteganoGUI(root)

    root.mainloop()