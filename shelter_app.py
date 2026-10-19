import os
import sqlite3
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk


def init_db():
    conn = sqlite3.connect("shelter.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS animals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, species TEXT, breed TEXT, chip TEXT, 
            age TEXT, status TEXT, general_notes TEXT, medical_notes TEXT, image_path TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL, category TEXT, quantity REAL DEFAULT 0, unit TEXT, notes TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS finances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL, category TEXT, amount REAL NOT NULL, date_entry TEXT, description TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL, phone TEXT, address TEXT, email TEXT, notes TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier_name TEXT NOT NULL, contact_person TEXT, phone TEXT, email TEXT, category TEXT, notes TEXT
        )
    """)
    conn.commit()
    conn.close()


class ShelterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ολοκληρωμένο Σύστημα Διαχείρισης Καταφυγίου")
        self.root.geometry("1200x820")

        init_db()
        self.selected_image_path = ""
        self.dark_mode = True

        # Χρώματα Dark Mode
        self.bg_color = "#222222"
        self.card_bg = "#2b2b2b"
        self.fg_color = "#ffffff"
        self.entry_bg = "#3c3c3c"
        self.entry_fg = "#ffffff"
        self.btn_bg = "#444444"
        self.btn_fg = "#ffffff"

        self.root.config(bg=self.bg_color)

        # Top Bar για Theme Toggle
        self.top_bar = tk.Frame(root, height=40, bg=self.bg_color)
        self.top_bar.pack(fill="x", side="top")

        self.theme_btn = tk.Button(
            self.top_bar,
            text="☀️ Εναλλαγή σε Light Mode",
            font=("Arial", 9, "bold"),
            bg=self.btn_bg,
            fg=self.btn_fg,
            relief="flat",
            command=self.toggle_theme,
        )
        self.theme_btn.pack(side="right", padx=10, pady=5)

        # Style για TTK
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.apply_ttk_theme()

        # Notebook
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        self.tab_animals = tk.Frame(self.notebook, bg=self.bg_color)
        self.tab_inventory = tk.Frame(self.notebook, bg=self.bg_color)
        self.tab_finances = tk.Frame(self.notebook, bg=self.bg_color)
        self.tab_members = tk.Frame(self.notebook, bg=self.bg_color)
        self.tab_suppliers = tk.Frame(self.notebook, bg=self.bg_color)

        self.notebook.add(self.tab_animals, text="🐾 Ζώα Καταφυγίου")
        self.notebook.add(self.tab_inventory, text="📦 Αποθήκη")
        self.notebook.add(self.tab_finances, text="💰 Οικονομικά")
        self.notebook.add(self.tab_members, text="👥 Μέλη Συλλόγου")
        self.notebook.add(self.tab_suppliers, text="🚚 Προμηθευτές")

        self.setup_animals_tab()
        self.setup_inventory_tab()
        self.setup_finances_tab()
        self.setup_members_tab()
        self.setup_suppliers_tab()

    def apply_ttk_theme(self):
        if self.dark_mode:
            self.style.configure(".", background=self.bg_color, foreground=self.fg_color, fieldbackground=self.entry_bg)
            self.style.configure("TNotebook", background=self.bg_color)
            self.style.configure("TNotebook.Tab", background="#333333", foreground=self.fg_color, padding=[10, 5])
            self.style.map("TNotebook.Tab", background=[("selected", self.card_bg)], foreground=[("selected", "#ffffff")])
            
            self.style.configure("TCombobox", fieldbackground=self.entry_bg, background=self.card_bg, foreground=self.fg_color, arrowcolor=self.fg_color)
            self.style.map("TCombobox", fieldbackground=[("readonly", self.entry_bg)], foreground=[("readonly", self.fg_color)])
            
            self.style.configure("Treeview", background=self.card_bg, foreground=self.fg_color, fieldbackground=self.card_bg, rowheight=25)
            self.style.configure("Treeview.Heading", background="#3a3a3a", foreground=self.fg_color, font=("Arial", 9, "bold"))
            self.style.map("Treeview", background=[("selected", "#16a085")])
        else:
            self.style.configure(".", background="#f0f0f0", foreground="#000000", fieldbackground="#ffffff")
            self.style.configure("TNotebook", background="#f0f0f0")
            self.style.configure("TCombobox", fieldbackground="#ffffff")
            self.style.configure("Treeview", background="#ffffff", foreground="#000000", fieldbackground="#ffffff")

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.bg_color, self.card_bg, self.fg_color, self.entry_bg, self.entry_fg, self.btn_bg, self.btn_fg = (
                "#222222", "#2b2b2b", "#ffffff", "#3c3c3c", "#ffffff", "#444444", "#ffffff"
            )
            self.theme_btn.config(text="☀️ Εναλλαγή σε Light Mode", bg=self.btn_bg, fg=self.btn_fg)
        else:
            self.bg_color, self.card_bg, self.fg_color, self.entry_bg, self.entry_fg, self.btn_bg, self.btn_fg = (
                "#f0f0f0", "#f9f9f9", "#000000", "#ffffff", "#000000", "#e0e0e0", "#000000"
            )
            self.theme_btn.config(text="🌙 Εναλλαγή σε Dark Mode", bg=self.btn_bg, fg=self.btn_fg)

        self.root.config(bg=self.bg_color)
        self.top_bar.config(bg=self.bg_color)
        self.apply_ttk_theme()

        for tab in [self.tab_animals, self.tab_inventory, self.tab_finances, self.tab_members, self.tab_suppliers]:
            self.update_widget_colors(tab)

    def update_widget_colors(self, parent):
        parent.config(bg=self.bg_color)
        for widget in parent.winfo_children():
            w_class = widget.winfo_class()
            try:
                if w_class in ("Frame", "Labelframe"):
                    widget.config(bg=self.card_bg if w_class == "Labelframe" else self.bg_color)
                    if w_class == "Labelframe":
                        widget.config(fg=self.fg_color)
                    self.update_widget_colors(widget)
                elif w_class == "Label":
                    curr_fg = widget.cget("fg")
                    if curr_fg not in ("#8e44ad", "#27ae60", "#c0392b", "#2980b9", "#16a085", "#d35400", "gray"):
                        widget.config(fg=self.fg_color)
                    widget.config(bg=self.card_bg if widget.master.winfo_class() == "Labelframe" else self.bg_color)
                elif w_class in ("Entry", "Text"):
                    widget.config(bg=self.entry_bg, fg=self.entry_fg, insertbackground=self.fg_color)
                elif w_class == "Button":
                    current_bg = widget.cget("bg")
                    if current_bg in ("#27ae60", "#e74c3c", "#2980b9", "#8e44ad", "#16a085", "#d35400"):
                        continue
                    widget.config(bg=self.btn_bg, fg=self.btn_fg, activebackground="#555555")
            except Exception:
                pass

    # ==========================================
    # 1. ΚΑΡΤΕΛΑ ΖΩΩΝ
    # ==========================================
    def setup_animals_tab(self):
        form_frame = tk.LabelFrame(
            self.tab_animals, text=" Στοιχεία Καρτέλας Ζώου ", padx=10, pady=10, bg=self.card_bg, fg=self.fg_color
        )
        form_frame.pack(fill="x", padx=10, pady=5)

        # GRID ΔΙΑΤΑΞΗ ΜΕ ΣΩΣΤΕΣ ΑΝΑΛΟΓΙΕΣ ΣΤΗΛΩΝ
        form_frame.columnconfigure(0, weight=1)
        form_frame.columnconfigure(1, weight=0)

        left_sub_frame = tk.Frame(form_frame, bg=self.card_bg)
        left_sub_frame.grid(row=0, column=0, sticky="nsew")

        right_sub_frame = tk.Frame(form_frame, bg=self.card_bg, padx=10)
        right_sub_frame.grid(row=0, column=1, sticky="n")

        # ΑΡΙΣΤΕΡΑ: ΠΕΔΙΑ
        left_sub_frame.columnconfigure(1, weight=1)
        left_sub_frame.columnconfigure(3, weight=1)

        tk.Label(left_sub_frame, text="Όνομα:", bg=self.card_bg, fg=self.fg_color).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.ent_name = tk.Entry(left_sub_frame, bg=self.entry_bg, fg=self.entry_fg, insertbackground=self.fg_color)
        self.ent_name.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        tk.Label(left_sub_frame, text="Είδος:", bg=self.card_bg, fg=self.fg_color).grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.combo_species = ttk.Combobox(left_sub_frame, values=["Σκύλος", "Γάτα", "Άλλο"], state="readonly")
        self.combo_species.current(0)
        self.combo_species.grid(row=0, column=3, sticky="ew", padx=5, pady=5)

        tk.Label(left_sub_frame, text="Ράτσα:", bg=self.card_bg, fg=self.fg_color).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.ent_breed = tk.Entry(left_sub_frame, bg=self.entry_bg, fg=self.entry_fg, insertbackground=self.fg_color)
        self.ent_breed.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        tk.Label(left_sub_frame, text="Microchip:", bg=self.card_bg, fg=self.fg_color).grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.ent_chip = tk.Entry(left_sub_frame, bg=self.entry_bg, fg=self.entry_fg, insertbackground=self.fg_color)
        self.ent_chip.grid(row=1, column=3, sticky="ew", padx=5, pady=5)

        tk.Label(left_sub_frame, text="Ηλικία:", bg=self.card_bg, fg=self.fg_color).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.ent_age = tk.Entry(left_sub_frame, bg=self.entry_bg, fg=self.entry_fg, insertbackground=self.fg_color)
        self.ent_age.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        tk.Label(left_sub_frame, text="Κατάσταση:", bg=self.card_bg, fg=self.fg_color).grid(row=2, column=2, sticky="w", padx=5, pady=5)
        self.combo_status = ttk.Combobox(
            left_sub_frame, values=["Προς Υιοθεσία", "Σε Φιλοξενία", "Υιοθετήθηκε", "Σε Θεραπεία"], state="readonly"
        )
        self.combo_status.current(0)
        self.combo_status.grid(row=2, column=3, sticky="ew", padx=5, pady=5)

        tk.Label(left_sub_frame, text="Γενικές Παρατηρήσεις\n(Συμπεριφορά/Χαρακτήρας):", bg=self.card_bg, fg=self.fg_color).grid(row=3, column=0, sticky="nw", padx=5, pady=5)
        self.txt_general = tk.Text(left_sub_frame, height=3, width=20, bg=self.entry_bg, fg=self.entry_fg, insertbackground=self.fg_color)
        self.txt_general.grid(row=3, column=1, sticky="ew", padx=5, pady=5)

        tk.Label(left_sub_frame, text="🩺 Ιατρικές Σημειώσεις\n(Μόνο για Ιατρικό Προσωπικό):", bg=self.card_bg, fg="#8e44ad", font=("Arial", 9, "bold")).grid(row=3, column=2, sticky="nw", padx=5, pady=5)
        self.txt_medical = tk.Text(left_sub_frame, height=3, width=20, bg=self.entry_bg, fg=self.entry_fg, insertbackground=self.fg_color)
        self.txt_medical.grid(row=3, column=3, sticky="ew", padx=5, pady=5)

        tk.Label(left_sub_frame, text="Φωτογραφία:", bg=self.card_bg, fg=self.fg_color).grid(row=4, column=0, sticky="w", padx=5, pady=5)
        btn_img = tk.Button(left_sub_frame, text="📷 Επιλογή Εικόνας", bg=self.btn_bg, fg=self.btn_fg, relief="raised", command=self.select_image)
        btn_img.grid(row=4, column=1, sticky="w", padx=5, pady=5)

        self.lbl_img_path = tk.Label(left_sub_frame, text="Καμία εικόνα", bg=self.card_bg, fg="gray", font=("Arial", 9, "italic"))
        self.lbl_img_path.grid(row=4, column=2, columnspan=2, sticky="w", padx=5, pady=5)

        # ΔΕΞΙΑ: CANVAS ΠΡΟΕΠΙΣΚΟΠΗΣΗΣ (ΑΔΙΑΠΡΑΓΜΑΤΕΥΤΟ ΜΕΓΕΘΟΣ)
        tk.Label(right_sub_frame, text="Προεπισκόπηση", bg=self.card_bg, fg=self.fg_color, font=("Arial", 9, "bold")).pack(pady=(0, 5))
        
        self.img_canvas = tk.Canvas(
            right_sub_frame, width=150, height=150, bg="#1a1a1a", highlightthickness=1, highlightbackground="#555555"
        )
        self.img_canvas.pack()
        self.img_canvas_text = self.img_canvas.create_text(75, 75, text="[ Χωρίς Εικόνα ]", fill="white", font=("Arial", 9))

        save_btn = tk.Button(
            form_frame, text="💾 Αποθήκευση Ζώου", bg="#27ae60", fg="white", font=("Arial", 10, "bold"), command=self.add_animal
        )
        save_btn.grid(row=1, column=0, columnspan=2, pady=(10, 0), sticky="ew")

        table_frame = tk.Frame(self.tab_animals, bg=self.bg_color)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        cols = ("ID", "Όνομα", "Είδος", "Ράτσα", "Microchip", "Ηλικία", "Κατάσταση", "Γενικές Σημειώσεις", "Ιατρικό Ιστορικό")
        self.tree_animals = ttk.Treeview(table_frame, columns=cols, show="headings")
        for col in cols:
            self.tree_animals.heading(col, text=col)
            self.tree_animals.column(col, width=100)
        self.tree_animals.column("ID", width=35)

        sb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_animals.yview)
        self.tree_animals.configure(yscrollcommand=sb.set)
        self.tree_animals.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tree_animals.bind("<<TreeviewSelect>>", self.on_select_animal_row)

        del_btn = tk.Button(self.tab_animals, text="❌ Διαγραφή Επιλεγμένου Ζώου", bg="#e74c3c", fg="white", command=self.delete_animal)
        del_btn.pack(pady=5)
        self.load_animals()

    def select_image(self):
        fp = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")])
        if fp:
            self.selected_image_path = fp
            self.lbl_img_path.config(text=os.path.basename(fp), fg=self.fg_color, font=("Arial", 9, "normal"))
            self.show_image_preview(fp)

    def show_image_preview(self, img_path):
        self.img_canvas.delete("all")
        if img_path and os.path.exists(img_path):
            try:
                img = Image.open(img_path)
                img.thumbnail((145, 145), Image.Resampling.LANCZOS)
                self.preview_photo = ImageTk.PhotoImage(img)
                self.img_canvas.create_image(75, 75, image=self.preview_photo, anchor="center")
            except Exception:
                self.img_canvas.create_text(75, 75, text="[Σφάλμα]", fill="red", font=("Arial", 9))
        else:
            self.img_canvas.create_text(75, 75, text="[ Χωρίς Εικόνα ]", fill="white", font=("Arial", 9))

    def add_animal(self):
        name = self.ent_name.get().strip()
        if not name:
            messagebox.showerror("Σφάλμα", "Το όνομα του ζώου είναι υποχρεωτικό!")
            return
        conn = sqlite3.connect("shelter.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO animals (name, species, breed, chip, age, status, general_notes, medical_notes, image_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name, self.combo_species.get(), self.ent_breed.get(), self.ent_chip.get(),
            self.ent_age.get(), self.combo_status.get(), self.txt_general.get("1.0", tk.END).strip(),
            self.txt_medical.get("1.0", tk.END).strip(), self.selected_image_path
        ))
        conn.commit()
        conn.close()
        messagebox.showinfo("Επιτυχία", "Η καρτέλα του ζώου καταχωρήθηκε!")
        self.clear_animal_form()
        self.load_animals()

    def clear_animal_form(self):
        self.ent_name.delete(0, tk.END)
        self.ent_breed.delete(0, tk.END)
        self.ent_chip.delete(0, tk.END)
        self.ent_age.delete(0, tk.END)
        self.txt_general.delete("1.0", tk.END)
        self.txt_medical.delete("1.0", tk.END)
        self.selected_image_path = ""
        self.lbl_img_path.config(text="Καμία εικόνα", fg="gray", font=("Arial", 9, "italic"))
        self.show_image_preview("")

    def load_animals(self):
        for r in self.tree_animals.get_children():
            self.tree_animals.delete(r)
        conn = sqlite3.connect("shelter.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, species, breed, chip, age, status, general_notes, medical_notes FROM animals")
        for r in cursor.fetchall():
            self.tree_animals.insert("", "end", values=r)
        conn.close()

    def on_select_animal_row(self, event):
        sel = self.tree_animals.selection()
        if not sel:
            return
        aid = self.tree_animals.item(sel)["values"][0]
        conn = sqlite3.connect("shelter.db")
        cursor = conn.cursor()
        cursor.execute("SELECT image_path FROM animals WHERE id = ?", (aid,))
        res = cursor.fetchone()
        conn.close()
        if res and res[0]:
            self.show_image_preview(res[0])
        else:
            self.show_image_preview("")

    def delete_animal(self):
        sel = self.tree_animals.selection()
        if not sel:
            messagebox.showwarning("Προσοχή", "Επιλέξτε ένα ζώο από τη λίστα για διαγραφή.")
            return
        if messagebox.askyesno("Επιβεβαίωση", "Διαγραφή επιλεγμένης καρτέλας;"):
            aid = self.tree_animals.item(sel)["values"][0]
            conn = sqlite3.connect("shelter.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM animals WHERE id = ?", (aid,))
            conn.commit()
            conn.close()
            self.show_image_preview("")
            self.load_animals()

    # ==========================================
    # 2. ΚΑΡΤΕΛΑ ΑΠΟΘΗΚΗΣ
    # ==========================================
    def setup_inventory_tab(self):
        form_frame = tk.LabelFrame(self.tab_inventory, text=" Διαχείριση Υλικών & Τροφών ", padx=10, pady=10, bg=self.card_bg, fg=self.fg_color)
        form_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(form_frame, text="Όνομα Υλικού:", bg=self.card_bg, fg=self.fg_color).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.ent_inv_name = tk.Entry(form_frame, bg=self.entry_bg, fg=self.entry_fg, insertbackground=self.fg_color)
        self.ent_inv_name.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        tk.Label(form_frame, text="Κατηγορία:", bg=self.card_bg, fg=self.fg_color).grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.combo_inv_cat = ttk.Combobox(form_frame, values=["Ζωοτροφή", "Φάρμακα / Ιατρικά", "Είδη Καθαρισμού", "Εξοπλισμός / Άλλο"], state="readonly")
        self.combo_inv_cat.current(0)
        self.combo_inv_cat.grid(row=0, column=3, sticky="ew", padx=5, pady=5)

        tk.Label(form_frame, text="Ποσότητα:", bg=self.card_bg, fg=self.fg_color).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.ent_inv_qty = tk.Entry(form_frame, bg=self.entry_bg, fg=self.entry_fg, insertbackground=self.fg_color)
        self.ent_inv_qty.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        tk.Label(form_frame, text="Μονάδα Μέτρησης:", bg=self.card_bg, fg=self.fg_color).grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.combo_inv_unit = ttk.Combobox(form_frame, values=["Κιλά (Kg)", "Τεμάχια", "Κουτιά", "Λίτρα (L)"], state="readonly")
        self.combo_inv_unit.current(0)
        self.combo_inv_unit.grid(row=1, column=3, sticky="ew", padx=5, pady=5)

        tk.Label(form_frame, text="Σημειώσεις:", bg=self.card_bg, fg=self.fg_color).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.ent_inv_notes = tk.Entry(form_frame, bg=self.entry_bg, fg=self.entry_fg, insertbackground=self.fg_color)
        self.ent_inv_notes.grid(row=2, column=1, columnspan=3, sticky="ew", padx=5, pady=5)

        save_btn = tk.Button(form_frame, text="📦 Προσθήκη Υλικού στην Αποθήκη", bg="#2980b9", fg="white", font=("Arial", 10, "bold"), command=self.add_inventory_item)
        save_btn.grid(row=3, column=0, columnspan=4, pady=10, sticky="ew")

        table_frame = tk.Frame(self.tab_inventory, bg=self.bg_color)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        cols = ("ID", "Όνομα Υλικού", "Κατηγορία", "Ποσότητα", "Μονάδα", "Σημειώσεις")
        self.tree_inv = ttk.Treeview(table_frame, columns=cols, show="headings")
        for col in cols:
            self.tree_inv.heading(col, text=col)
            self.tree_inv.column(col, width=120)
        self.tree_inv.column("ID", width=35)

        sb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_inv.yview)
        self.tree_inv.configure(yscrollcommand=sb.set)
        self.tree_inv.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        del_btn = tk.Button(self.tab_inventory, text="❌ Διαγραφή Υλικού", bg="#e74c3c", fg="white", command=self.delete_inventory_item)
        del_btn.pack(pady=5)
        self.load_inventory()

    def add_inventory_item(self):
        name = self.ent_inv_name.get().strip()
        qty_str = self.ent_inv_qty.get().strip()
        if not name or not qty_str:
            messagebox.showerror("Σφάλμα", "Το όνομα και η ποσότητα είναι υποχρεωτικά!")
            return
        try:
            qty = float(qty_str)
        except ValueError:
            messagebox.showerror("Σφάλμα", "Η ποσότητα πρέπει να είναι αριθμός!")
            return

        conn = sqlite3.connect("shelter.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO inventory (item_name, category, quantity, unit, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (name, self.combo_inv_cat.get(), qty, self.combo_inv_unit.get(), self.ent_inv_notes.get()))
        conn.commit()
        conn.close()
        messagebox.showinfo("Επιτυχία", "Το υλικό προστέθηκε στην αποθήκη!")
        self.ent_inv_name.delete(0, tk.END)
        self.ent_inv_qty.delete(0, tk.END)
        self.ent_inv_notes.delete(0, tk.END)
        self.load_inventory()

    def load_inventory(self):
        for r in self.tree_inv.get_children():
            self.tree_inv.delete(r)
        conn = sqlite3.connect("shelter.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventory")
        for r in cursor.fetchall():
            self.tree_inv.insert("", "end", values=r)
        conn.close()

    def delete_inventory_item(self):
        sel = self.tree_inv.selection()
        if not sel:
            messagebox.showwarning("Προσοχή", "Επιλέξτε ένα υλικό για διαγραφή.")
            return
        if messagebox.askyesno("Επιβεβαίωση", "Διαγραφή επιλεγμένου υλικού;"):
            iid = self.tree_inv.item(sel)["values"][0]
            conn = sqlite3.connect("shelter.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM inventory WHERE id = ?", (iid,))
            conn.commit()
            conn.close()
            self.load_inventory()

    # ==========================================
    # 3. ΚΑΡΤΕΛΑ ΟΙΚΟΝΟΜΙΚΩΝ
    # ==========================================
    def setup_finances_tab(self):
        balance_frame = tk.LabelFrame(self.tab_finances, text=" 📊 Ταμείο Καταφυγίου ", padx=10, pady=10, bg=self.card_bg, fg=self.fg_color)
        balance_frame.pack(fill="x", padx=10, pady=5)

        self.lbl_income = tk.Label(balance_frame, text="Συνολικά Έσοδα: 0.00 €", bg=self.card_bg, fg="#27ae60", font=("Arial", 11, "bold"))
        self.lbl_income.grid(row=0, column=0, padx=20, pady=5)

        self.lbl_expense = tk.Label(balance_frame, text="Συνολικά Έξοδα: 0.00 €", bg=self.card_bg, fg="#c0392b", font=("Arial", 11, "bold"))
        self.lbl_expense.grid(row=0, column=1, padx=20, pady=5)

        self.lbl_balance = tk.Label(balance_frame, text="Υπόλοιπο Ταμείου: 0.00 €", bg=self.card_bg, fg="#2980b9", font=("Arial", 12, "bold"))
        self.lbl_balance.grid(row=0, column=2, padx=20, pady=5)

        form_frame = tk.LabelFrame(self.tab_finances, text=" Καταγραφή Νέας Συναλλαγής ", padx=10, pady=10, bg=self.card_bg, fg=self.fg_color)
        form_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(form_frame, text="Τύπος:", bg=self.card_bg, fg=self.fg_color).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.combo_fin_type = ttk.Combobox(form_frame, values=["Έσοδο", "Έξοδο"], state="readonly")
        self.combo_fin_type.current(0)
        self.combo_fin_type.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        tk.Label(form_frame, text="Κατηγορία:", bg=self.card_bg, fg=self.fg_color).grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.combo_fin_cat = ttk.Combobox(
            form_frame, values=["Δωρεά / Χορηγία", "Ιατρικά Έξοδα / Κτηνίατρος", "Αγορά Τροφών / Υλικών", "Λογαριασμοί / Πάγια", "Άλλο"], state="readonly"
        )
        self.combo_fin_cat.current(0)
        self.combo_fin_cat.grid(row=0, column=3, sticky="ew", padx=5, pady=5)

        tk.Label(form_frame, text="Ποσό (€):", bg=self.card_bg, fg=self.fg_color).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.ent_fin_amount = tk.Entry(form_frame, bg=self.entry_bg, fg=self.entry_fg, insertbackground=self.fg_color)
        self.ent_fin_amount.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        tk.Label(form_frame, text="Ημερομηνία:", bg=self.card_bg, fg=self.fg_color).grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.ent_fin_date = tk.Entry(form_frame, bg=self.entry_bg, fg=self.entry_fg, insertbackground=self.fg_color)
        self.ent_fin_date.grid(row=1, column=3, sticky="ew", padx=5, pady=5)

        tk.Label(form_frame, text="Περιγραφή:", bg=self.card_bg, fg=self.fg_color).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.ent_fin_desc = tk.Entry(form_frame, bg=self.entry_bg, fg=self.entry_fg, insertbackground=self.fg_color)
        self.ent_fin_desc.grid(row=2, column=1, columnspan=3, sticky="ew", padx=5, pady=5)

        save_btn = tk.Button(form_frame, text="💰 Καταχώρηση Συναλλαγής", bg="#8e44ad", fg="white", font=("Arial", 10, "bold"), command=self.add_finance_entry)
        save_btn.grid(row=3, column=0, columnspan=4, pady=10, sticky="ew")

        table_frame = tk.Frame(self.tab_finances, bg=self.bg_color)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        cols = ("ID", "Τύπος", "Κατηγορία", "Ποσό (€)", "Ημερομηνία", "Περιγραφή")
        self.tree_fin = ttk.Treeview(table_frame, columns=cols, show="headings")
        for col in cols:
            self.tree_fin.heading(col, text=col)
            self.tree_fin.column(col, width=120)
        self.tree_fin.column("ID", width=35)

        sb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_fin.yview)
        self.tree_fin.configure(yscrollcommand=sb.set)
        self.tree_fin.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        del_btn = tk.Button(self.tab_finances, text="❌ Διαγραφή Συναλλαγής", bg="#e74c3c", fg="white", command=self.delete_finance_entry)
        del_btn.pack(pady=5)
        self.load_finances()

    def add_finance_entry(self):
        amount_str = self.ent_fin_amount.get().strip()
        if not amount_str:
            messagebox.showerror("Σφάλμα", "Το ποσό είναι υποχρεωτικό!")
            return
        try:
            amount = float(amount_str)
        except ValueError:
            messagebox.showerror("Σφάλμα", "Το ποσό πρέπει να είναι αριθμός!")
            return
        conn = sqlite3.connect("shelter.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO finances (type, category, amount, date_entry, description)
            VALUES (?, ?, ?, ?, ?)
        """, (self.combo_fin_type.get(), self.combo_fin_cat.get(), amount, self.ent_fin_date.get(), self.ent_fin_desc.get()))
        conn.commit()
        conn.close()
        messagebox.showinfo("Επιτυχία", "Η συναλλαγή καταχωρήθηκε!")
        self.ent_fin_amount.delete(0, tk.END)
        self.ent_fin_date.delete(0, tk.END)
        self.ent_fin_desc.delete(0, tk.END)
        self.load_finances()

    def load_finances(self):
        for r in self.tree_fin.get_children():
            self.tree_fin.delete(r)
        conn = sqlite3.connect("shelter.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM finances")
        rows = cursor.fetchall()
        total_income = 0.0
        total_expense = 0.0
        for r in rows:
            self.tree_fin.insert("", "end", values=r)
            if r[1] == "Έσοδο":
                total_income += r[3]
            else:
                total_expense += r[3]
        conn.close()
        balance = total_income - total_expense
        self.lbl_income.config(text=f"Συνολικά Έσοδα: {total_income:.2f} €")
        self.lbl_expense.config(text=f"Συνολικά Έξοδα: {total_expense:.2f} €")
        self.lbl_balance.config(text=f"Υπόλοιπο Ταμείου: {balance:.2f} €")

    def delete_finance_entry(self):
        sel = self.tree_fin.selection()
        if not sel:
            messagebox.showwarning("Προσοχή", "Επιλέξτε μια συναλλαγή για διαγραφή.")
            return
        if messagebox.askyesno("Επιβεβαίωση", "Διαγραφή επιλεγμένης συναλλαγής;"):
            fid = self.tree_fin.item(sel)["values"][0]
            conn = sqlite3.connect("shelter.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM finances WHERE id = ?", (fid,))
            conn.commit()
            conn.close()
            self.load_finances()

    # ==========================================
    # 4. ΚΑΡΤΕΛΑ ΜΕΛΩΝ ΣΥΛΛΟΓΟΥ
    # ==========================================
    def setup_members_tab(self):
        form_frame = tk.LabelFrame(self.tab_members, text=" Διαχείριση Μελών & Εθελοντών ", padx=10, pady=10, bg=self.card_bg, fg=self.fg_color)
        form_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(form_frame, text="Ονοματεπώνυμο:", bg=self.card_bg, fg=self.fg_color).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.ent_mem_name = tk.Entry(form_frame, bg=self.entry_bg, fg=self.entry_fg, insertbackground=self.fg_color)
        self.ent_mem_name.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        tk.Label(form_frame, text="Τηλέφωνο:", bg=self.card_bg, fg=self.fg_color).grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.ent_mem_phone = tk.Entry(form_frame, bg=self.entry_bg, fg=self.entry_fg, insertbackground=self.fg_color)
        self.ent_mem_phone.grid(row=0, column=3, sticky="ew", padx=5, pady=5)

        tk.Label(form_frame, text="Διεύθυνση:", bg=self.card_bg, fg=self.fg_color).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.ent_mem_addr = tk.Entry(form_frame, bg=self.entry_bg, fg=self.entry_fg, insertbackground=self.fg_color)
        self.ent_mem_addr.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        tk.Label(form_frame, text="Email:", bg=self.card_bg, fg=self.fg_color).grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.ent_mem_email = tk.Entry(form_frame, bg=self.entry_bg, fg=self.entry_fg, insertbackground=self.fg_color)
        self.ent_mem_email.grid(row=1, column=3, sticky="ew", padx=5, pady=5)

        tk.Label(form_frame, text="Σημειώσεις:", bg=self.card_bg, fg=self.fg_color).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.ent_mem_notes = tk.Entry(form_frame, bg=self.entry_bg, fg=self.entry_fg, insertbackground=self.fg_color)
        self.ent_mem_notes.grid(row=2, column=1, columnspan=3, sticky="ew", padx=5, pady=5)

        save_btn = tk.Button(form_frame, text="👥 Προσθήκη Μέλους", bg="#16a085", fg="white", font=("Arial", 10, "bold"), command=self.add_member)
        save_btn.grid(row=3, column=0, columnspan=4, pady=10, sticky="ew")

        table_frame = tk.Frame(self.tab_members, bg=self.bg_color)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        cols = ("ID", "Ονοματεπώνυμο", "Τηλέφωνο", "Διεύθυνση", "Email", "Σημειώσεις")
        self.tree_mem = ttk.Treeview(table_frame, columns=cols, show="headings")
        for col in cols:
            self.tree_mem.heading(col, text=col)
            self.tree_mem.column(col, width=120)
        self.tree_mem.column("ID", width=35)

        sb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_mem.yview)
        self.tree_mem.configure(yscrollcommand=sb.set)
        self.tree_mem.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        del_btn = tk.Button(self.tab_members, text="❌ Διαγραφή Μέλους", bg="#e74c3c", fg="white", command=self.delete_member)
        del_btn.pack(pady=5)
        self.load_members()

    def add_member(self):
        name = self.ent_mem_name.get().strip()
        if not name:
            messagebox.showerror("Σφάλμα", "Το ονοματεπώνυμο είναι υποχρεωτικό!")
            return
        conn = sqlite3.connect("shelter.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO members (full_name, phone, address, email, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (name, self.ent_mem_phone.get(), self.ent_mem_addr.get(), self.ent_mem_email.get(), self.ent_mem_notes.get()))
        conn.commit()
        conn.close()
        messagebox.showinfo("Επιτυχία", "Το μέλος προστέθηκε!")
        self.ent_mem_name.delete(0, tk.END)
        self.ent_mem_phone.delete(0, tk.END)
        self.ent_mem_addr.delete(0, tk.END)
        self.ent_mem_email.delete(0, tk.END)
        self.ent_mem_notes.delete(0, tk.END)
        self.load_members()

    def load_members(self):
        for r in self.tree_mem.get_children():
            self.tree_mem.delete(r)
        conn = sqlite3.connect("shelter.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM members")
        for r in cursor.fetchall():
            self.tree_mem.insert("", "end", values=r)
        conn.close()

    def delete_member(self):
        sel = self.tree_mem.selection()
        if not sel:
            messagebox.showwarning("Προσοχή", "Επιλέξτε ένα μέλος για διαγραφή.")
            return
        if messagebox.askyesno("Επιβεβαίωση", "Διαγραφή επιλεγμένου μέλους;"):
            mid = self.tree_mem.item(sel)["values"][0]
            conn = sqlite3.connect("shelter.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM members WHERE id = ?", (mid,))
            conn.commit()
            conn.close()
            self.load_members()

    # ==========================================
    # 5. ΚΑΡΤΕΛΑ ΠΡΟΜΗΘΕΥΤΩΝ
    # ==========================================
    def setup_suppliers_tab(self):
        form_frame = tk.LabelFrame(self.tab_suppliers, text=" Διαχείριση Προμηθευτών & Συνεργατών ", padx=10, pady=10, bg=self.card_bg, fg=self.fg_color)
        form_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(form_frame, text="Όνομα Προμηθευτή:", bg=self.card_bg, fg=self.fg_color).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.ent_sup_name = tk.Entry(form_frame, bg=self.entry_bg, fg=self.entry_fg, insertbackground=self.fg_color)
        self.ent_sup_name.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        tk.Label(form_frame, text="Υπεύθυνος:", bg=self.card_bg, fg=self.fg_color).grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.ent_sup_contact = tk.Entry(form_frame, bg=self.entry_bg, fg=self.entry_fg, insertbackground=self.fg_color)
        self.ent_sup_contact.grid(row=0, column=3, sticky="ew", padx=5, pady=5)

        tk.Label(form_frame, text="Τηλέφωνο:", bg=self.card_bg, fg=self.fg_color).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.ent_sup_phone = tk.Entry(form_frame, bg=self.entry_bg, fg=self.entry_fg, insertbackground=self.fg_color)
        self.ent_sup_phone.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        tk.Label(form_frame, text="Email:", bg=self.card_bg, fg=self.fg_color).grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.ent_sup_email = tk.Entry(form_frame, bg=self.entry_bg, fg=self.entry_fg, insertbackground=self.fg_color)
        self.ent_sup_email.grid(row=1, column=3, sticky="ew", padx=5, pady=5)

        tk.Label(form_frame, text="Κατηγορία:", bg=self.card_bg, fg=self.fg_color).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.combo_sup_cat = ttk.Combobox(
            form_frame, values=["Κτηνιατρική Κλινική / Κτηνίατρος", "Προμηθευτής Τροφών", "Είδη Pet Shop", "Υπηρεσίες / Άλλο"], state="readonly"
        )
        self.combo_sup_cat.current(0)
        self.combo_sup_cat.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        tk.Label(form_frame, text="Σημειώσεις:", bg=self.card_bg, fg=self.fg_color).grid(row=2, column=2, sticky="w", padx=5, pady=5)
        self.ent_sup_notes = tk.Entry(form_frame, bg=self.entry_bg, fg=self.entry_fg, insertbackground=self.fg_color)
        self.ent_sup_notes.grid(row=2, column=3, sticky="ew", padx=5, pady=5)

        save_btn = tk.Button(form_frame, text="🚚 Προσθήκη Προμηθευτή", bg="#d35400", fg="white", font=("Arial", 10, "bold"), command=self.add_supplier)
        save_btn.grid(row=3, column=0, columnspan=4, pady=10, sticky="ew")

        table_frame = tk.Frame(self.tab_suppliers, bg=self.bg_color)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        cols = ("ID", "Όνομα Προμηθευτή", "Υπεύθυνος", "Τηλέφωνο", "Email", "Κατηγορία", "Σημειώσεις")
        self.tree_sup = ttk.Treeview(table_frame, columns=cols, show="headings")
        for col in cols:
            self.tree_sup.heading(col, text=col)
            self.tree_sup.column(col, width=110)
        self.tree_sup.column("ID", width=35)

        sb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_sup.yview)
        self.tree_sup.configure(yscrollcommand=sb.set)
        self.tree_sup.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        del_btn = tk.Button(self.tab_suppliers, text="❌ Διαγραφή Προμηθευτή", bg="#e74c3c", fg="white", command=self.delete_supplier)
        del_btn.pack(pady=5)
        self.load_suppliers()

    def add_supplier(self):
        name = self.ent_sup_name.get().strip()
        if not name:
            messagebox.showerror("Σφάλμα", "Το όνομα του προμηθευτή είναι υποχρεωτικό!")
            return
        conn = sqlite3.connect("shelter.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO suppliers (supplier_name, contact_person, phone, email, category, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            name, self.ent_sup_contact.get(), self.ent_sup_phone.get(),
            self.ent_sup_email.get(), self.combo_sup_cat.get(), self.ent_sup_notes.get()
        ))
        conn.commit()
        conn.close()
        messagebox.showinfo("Επιτυχία", "Ο προμηθευτής προστέθηκε!")
        self.ent_sup_name.delete(0, tk.END)
        self.ent_sup_contact.delete(0, tk.END)
        self.ent_sup_phone.delete(0, tk.END)
        self.ent_sup_email.delete(0, tk.END)
        self.ent_sup_notes.delete(0, tk.END)
        self.load_suppliers()

    def load_suppliers(self):
        for r in self.tree_sup.get_children():
            self.tree_sup.delete(r)
        conn = sqlite3.connect("shelter.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM suppliers")
        for r in cursor.fetchall():
            self.tree_sup.insert("", "end", values=r)
        conn.close()

    def delete_supplier(self):
        sel = self.tree_sup.selection()
        if not sel:
            messagebox.showwarning("Προσοχή", "Επιλέξτε έναν προμηθευτή για διαγραφή.")
            return
        if messagebox.askyesno("Επιβεβαίωση", "Διαγραφή επιλεγμένου προμηθευτή;"):
            sid = self.tree_sup.item(sel)["values"][0]
            conn = sqlite3.connect("shelter.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM suppliers WHERE id = ?", (sid,))
            conn.commit()
            conn.close()
            self.load_suppliers()


if __name__ == "__main__":
    root = tk.Tk()
    app = ShelterApp(root)
    root.mainloop()