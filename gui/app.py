import customtkinter as ctk
from tkinter import messagebox, filedialog
import os
from core.manager import VaultManager
from core import database
from core.generator import generate_password

ctk.set_appearance_mode("Dark")

DESIGN = {
    "bg": "#0F1117",
    "panel": "#171B22",
    "card": "#1E232D",
    "accent": "#4F8EF7",
    "accent_hover": "#6BA5FF",
    "text": "#F5F7FA",
    "text_muted": "#A6B0C3",
    "border": "#2A3140",
    "radius_main": 20,
    "radius_card": 14,
    "radius_input": 10,
    "font_family": "Segoe UI"
}

ICONS = {
    "search": "🔍",
    "eye": "👁",
    "hide": "🙈",
    "copy": "📋",
    "trash": "🗑",
    "edit": "✎",
    "lock": "🔒",
    "unlock": "🔓",
    "home": "⌂",
    "add": "➕",
    "globe": "🌐",
    "user": "👤",
    "import": "📥",
    "export": "📤"
}

class PasswordManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MyVault")
        self.root.geometry("900x650")
        self.root.configure(fg_color=DESIGN["bg"])
        
        self.vault = VaultManager()
        self.current_frame = None
        self.main_content = None
        
        self.show_auth_screen()

    def show_auth_screen(self):
        if self.current_frame:
            self.current_frame.destroy()
            
        self.current_frame = ctk.CTkFrame(self.root, fg_color=DESIGN["bg"])
        self.current_frame.pack(expand=True, fill=ctk.BOTH)

        card = ctk.CTkFrame(
            self.current_frame, 
            fg_color=DESIGN["card"], 
            corner_radius=DESIGN["radius_card"],
            border_width=1,
            border_color=DESIGN["border"]
        )
        card.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

        is_setup = not os.path.exists(database.VAULT_FILE)
        title_text = "Setup MyVault" if is_setup else "Welcome Back"
        btn_text = f"{ICONS['unlock']} Create Vault" if is_setup else f"{ICONS['unlock']} Unlock"

        ctk.CTkLabel(
            card, 
            text=title_text, 
            font=ctk.CTkFont(family=DESIGN["font_family"], size=24, weight="bold"),
            text_color=DESIGN["text"]
        ).pack(pady=(32, 8), padx=48)

        ctk.CTkLabel(
            card, 
            text="Enter your master password to continue", 
            font=ctk.CTkFont(family=DESIGN["font_family"], size=13),
            text_color=DESIGN["text_muted"]
        ).pack(pady=(0, 24), padx=48)
        
        pw_frame = ctk.CTkFrame(card, fg_color="transparent")
        pw_frame.pack(pady=(0, 24), padx=48, fill=ctk.X)
        pw_frame.grid_columnconfigure(0, weight=1)
        
        self.password_entry = ctk.CTkEntry(
            pw_frame, 
            show="*", 
            height=40,
            placeholder_text="Master Password",
            corner_radius=DESIGN["radius_input"],
            fg_color=DESIGN["panel"],
            border_color=DESIGN["border"],
            text_color=DESIGN["text"]
        )
        self.password_entry.grid(row=0, column=0, sticky="ew")
        
        self.auth_toggle_btn = ctk.CTkButton(
            pw_frame, 
            text=ICONS["eye"], 
            width=40, 
            height=40,
            fg_color=DESIGN["panel"], 
            hover_color=DESIGN["border"],
            corner_radius=DESIGN["radius_input"], 
            text_color=DESIGN["text_muted"],
            command=self.toggle_auth_password_visibility
        )
        self.auth_toggle_btn.grid(row=0, column=1, padx=(8, 0))
        
        self.password_entry.focus()
        
        submit_btn = ctk.CTkButton(
            card, 
            text=btn_text, 
            height=40,
            corner_radius=DESIGN["radius_input"],
            fg_color=DESIGN["accent"],
            hover_color=DESIGN["accent_hover"],
            font=ctk.CTkFont(family=DESIGN["font_family"], size=14, weight="bold"),
            command=lambda: self.handle_auth(is_setup)
        )
        submit_btn.pack(pady=(0, 32), padx=48, fill=ctk.X)
        
        self.password_entry.bind('<Return>', lambda event: self.handle_auth(is_setup))

    def toggle_auth_password_visibility(self):
        if self.password_entry.cget("show") == "*":
            self.password_entry.configure(show="")
            self.auth_toggle_btn.configure(text=ICONS["hide"])
        else:
            self.password_entry.configure(show="*")
            self.auth_toggle_btn.configure(text=ICONS["eye"])

    def handle_auth(self, is_setup: bool):
        password = self.password_entry.get()
        
        if not password:
            messagebox.showwarning("Error", "Password cannot be empty!")
            return
            
        if is_setup:
            try:
                self.vault.setup_new_vault(password)
                self.show_vault_screen()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create vault: {e}")
        else:
            success = self.vault.unlock_vault(password)
            if success:
                self.show_vault_screen()
            else:
                messagebox.showerror("Error", "Invalid Master Password!")
                self.password_entry.delete(0, ctk.END)

    def handle_import(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Select CSV to Import"
        )
        if filepath:
            try:
                count = self.vault.import_csv(filepath)
                messagebox.showinfo("Success", f"Successfully imported {count} accounts!")
                self.show_dashboard_tab()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import: {e}\n\nPlease ensure the CSV has 'Site', 'Username', and 'Password' headers.")

    def handle_export(self):
        confirm = messagebox.askyesno(
            "CRITICAL SECURITY WARNING",
            "Exporting will save all your passwords in a PLAIN TEXT, unencrypted file.\n\nAnyone with access to this file will be able to read your passwords. Are you sure you want to continue?"
        )
        if not confirm:
            return
            
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            title="Export Vault"
        )
        if filepath:
            try:
                self.vault.export_csv(filepath)
                messagebox.showwarning("Export Successful", "Vault exported successfully.\n\nPLEASE DELETE THIS FILE securely when you are finished migrating your data!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")

    def lock_vault(self):
        self.vault.key = None
        self.vault.salt = None
        self.vault.data = {}
        self.vault.is_unlocked = False
        self.show_auth_screen()

    def show_vault_screen(self):
        if self.current_frame:
            self.current_frame.destroy()
            
        self.current_frame = ctk.CTkFrame(self.root, fg_color=DESIGN["bg"])
        self.current_frame.pack(fill=ctk.BOTH, expand=True)
        
        sidebar = ctk.CTkFrame(self.current_frame, width=220, corner_radius=0, fg_color=DESIGN["panel"])
        sidebar.pack(side=ctk.LEFT, fill=ctk.Y)
        
        ctk.CTkLabel(
            sidebar, 
            text=f"{ICONS['lock']} MyVault", 
            font=ctk.CTkFont(family=DESIGN["font_family"], size=24, weight="bold"),
            text_color=DESIGN["text"]
        ).pack(pady=(32, 32), padx=24, anchor="w")
        
        self.btn_dashboard = ctk.CTkButton(
            sidebar,
            text=f"{ICONS['home']} All Passwords",
            fg_color=DESIGN["accent"],
            hover_color=DESIGN["accent_hover"],
            anchor="w",
            height=40,
            corner_radius=DESIGN["radius_input"],
            font=ctk.CTkFont(family=DESIGN["font_family"], size=14, weight="bold"),
            command=self.show_dashboard_tab
        )
        self.btn_dashboard.pack(pady=4, padx=16, fill=ctk.X)

        self.btn_add = ctk.CTkButton(
            sidebar,
            text=f"{ICONS['add']} Add Password",
            fg_color="transparent",
            hover_color=DESIGN["border"],
            anchor="w",
            height=40,
            corner_radius=DESIGN["radius_input"],
            text_color=DESIGN["text_muted"],
            font=ctk.CTkFont(family=DESIGN["font_family"], size=14, weight="bold"),
            command=self.show_add_tab
        )
        self.btn_add.pack(pady=4, padx=16, fill=ctk.X)

        self.btn_import = ctk.CTkButton(
            sidebar,
            text=f"{ICONS['import']} Import CSV",
            fg_color="transparent",
            hover_color=DESIGN["border"],
            anchor="w",
            height=40,
            corner_radius=DESIGN["radius_input"],
            text_color=DESIGN["text_muted"],
            font=ctk.CTkFont(family=DESIGN["font_family"], size=14, weight="bold"),
            command=self.handle_import
        )
        self.btn_import.pack(pady=4, padx=16, fill=ctk.X)

        self.btn_export = ctk.CTkButton(
            sidebar,
            text=f"{ICONS['export']} Export CSV",
            fg_color="transparent",
            hover_color=DESIGN["border"],
            anchor="w",
            height=40,
            corner_radius=DESIGN["radius_input"],
            text_color=DESIGN["text_muted"],
            font=ctk.CTkFont(family=DESIGN["font_family"], size=14, weight="bold"),
            command=self.handle_export
        )
        self.btn_export.pack(pady=4, padx=16, fill=ctk.X)
        
        ctk.CTkButton(
            sidebar,
            text=f"{ICONS['lock']} Lock Vault",
            fg_color="transparent",
            hover_color=DESIGN["border"],
            text_color=DESIGN["text_muted"],
            anchor="w",
            height=40,
            corner_radius=DESIGN["radius_input"],
            font=ctk.CTkFont(family=DESIGN["font_family"], size=14, weight="bold"),
            command=self.lock_vault
        ).pack(side=ctk.BOTTOM, pady=32, padx=16, fill=ctk.X)
        
        self.main_content = ctk.CTkFrame(self.current_frame, fg_color="transparent")
        self.main_content.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True, padx=32, pady=32)
        
        self.show_dashboard_tab()

    def update_sidebar_active_state(self, active_tab):
        self.btn_dashboard.configure(fg_color="transparent", text_color=DESIGN["text_muted"])
        self.btn_add.configure(fg_color="transparent", text_color=DESIGN["text_muted"])
        
        if active_tab == "dashboard":
            self.btn_dashboard.configure(fg_color=DESIGN["accent"], text_color=DESIGN["text"])
        elif active_tab == "add":
            self.btn_add.configure(fg_color=DESIGN["accent"], text_color=DESIGN["text"])

    def clear_main_content(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()

    def show_dashboard_tab(self):
        self.update_sidebar_active_state("dashboard")
        self.clear_main_content()

        ctk.CTkLabel(
            self.main_content, 
            text="All Passwords", 
            font=ctk.CTkFont(family=DESIGN["font_family"], size=24, weight="bold"),
            text_color=DESIGN["text"]
        ).pack(anchor="w", pady=(0, 24))

        list_card = ctk.CTkFrame(
            self.main_content, 
            fg_color=DESIGN["card"], 
            corner_radius=DESIGN["radius_card"],
            border_width=1,
            border_color=DESIGN["border"]
        )
        list_card.pack(fill=ctk.BOTH, expand=True)
        
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self.refresh_listbox)
        
        self.search_entry = ctk.CTkEntry(
            list_card, 
            textvariable=self.search_var, 
            placeholder_text=f"{ICONS['search']} Search passwords...",
            height=44,
            corner_radius=DESIGN["radius_input"],
            fg_color=DESIGN["panel"],
            border_color=DESIGN["border"]
        )
        self.search_entry.pack(pady=(24, 16), padx=24, fill=ctk.X)

        self.scrollable_frame = ctk.CTkScrollableFrame(
            list_card, 
            fg_color="transparent",
            scrollbar_button_color=DESIGN["panel"],
            scrollbar_button_hover_color=DESIGN["border"]
        )
        self.scrollable_frame.pack(pady=(0, 24), padx=24, fill=ctk.BOTH, expand=True)
        
        self.refresh_listbox()

    def show_add_tab(self):
        self.update_sidebar_active_state("add")
        self.clear_main_content()

        ctk.CTkLabel(
            self.main_content, 
            text="Add Password", 
            font=ctk.CTkFont(family=DESIGN["font_family"], size=24, weight="bold"),
            text_color=DESIGN["text"]
        ).pack(anchor="w", pady=(0, 24))

        add_card = ctk.CTkFrame(
            self.main_content, 
            fg_color=DESIGN["card"], 
            corner_radius=DESIGN["radius_card"],
            border_width=1,
            border_color=DESIGN["border"]
        )
        add_card.pack(fill=ctk.X)
        
        add_card.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(add_card, text="Site:", font=ctk.CTkFont(family=DESIGN["font_family"], weight="bold")).grid(row=0, column=0, padx=(24, 16), pady=(32, 8), sticky="e")
        self.site_entry = ctk.CTkEntry(add_card, height=40, corner_radius=DESIGN["radius_input"], fg_color=DESIGN["panel"], border_color=DESIGN["border"])
        self.site_entry.grid(row=0, column=1, columnspan=2, padx=(0, 24), pady=(32, 8), sticky="ew")
        
        ctk.CTkLabel(add_card, text="Username:", font=ctk.CTkFont(family=DESIGN["font_family"], weight="bold")).grid(row=1, column=0, padx=(24, 16), pady=8, sticky="e")
        self.username_entry = ctk.CTkEntry(add_card, height=40, corner_radius=DESIGN["radius_input"], fg_color=DESIGN["panel"], border_color=DESIGN["border"])
        self.username_entry.grid(row=1, column=1, columnspan=2, padx=(0, 24), pady=8, sticky="ew")
        
        ctk.CTkLabel(add_card, text="Password:", font=ctk.CTkFont(family=DESIGN["font_family"], weight="bold")).grid(row=2, column=0, padx=(24, 16), pady=(8, 24), sticky="e")
        
        pw_frame = ctk.CTkFrame(add_card, fg_color="transparent")
        pw_frame.grid(row=2, column=1, padx=(0, 16), pady=(8, 24), sticky="ew")
        pw_frame.grid_columnconfigure(0, weight=1)
        
        self.new_password_entry = ctk.CTkEntry(pw_frame, show="*", height=40, corner_radius=DESIGN["radius_input"], fg_color=DESIGN["panel"], border_color=DESIGN["border"])
        self.new_password_entry.grid(row=0, column=0, sticky="ew")
        
        self.toggle_btn = ctk.CTkButton(
            pw_frame, text=ICONS["eye"], width=40, height=40,
            fg_color=DESIGN["panel"], hover_color=DESIGN["border"],
            corner_radius=DESIGN["radius_input"], text_color=DESIGN["text_muted"],
            command=self.toggle_add_password_visibility
        )
        self.toggle_btn.grid(row=0, column=1, padx=(8, 0))

        ctk.CTkButton(
            add_card, text=f"{ICONS['add']} Generate", width=110, height=40,
            fg_color=DESIGN["panel"], hover_color=DESIGN["border"], text_color=DESIGN["text"],
            corner_radius=DESIGN["radius_input"], font=ctk.CTkFont(family=DESIGN["font_family"], weight="bold"),
            command=self.auto_generate
        ).grid(row=2, column=2, padx=(0, 24), pady=(8, 24), sticky="e")
        
        ctk.CTkButton(
            add_card, text="Save Entry", height=40,
            fg_color=DESIGN["accent"], hover_color=DESIGN["accent_hover"],
            corner_radius=DESIGN["radius_input"], font=ctk.CTkFont(family=DESIGN["font_family"], weight="bold", size=14),
            command=self.save_new_entry
        ).grid(row=3, column=0, columnspan=3, pady=(0, 32), padx=24, sticky="ew")

    def toggle_add_password_visibility(self):
        if self.new_password_entry.cget("show") == "*":
            self.new_password_entry.configure(show="")
            self.toggle_btn.configure(text=ICONS["hide"])
        else:
            self.new_password_entry.configure(show="*")
            self.toggle_btn.configure(text=ICONS["eye"])

    def refresh_listbox(self, *args):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        search_term = self.search_var.get().lower()
            
        for site in sorted(self.vault.data.keys()):
            if search_term in site.lower():
                card = ctk.CTkFrame(self.scrollable_frame, fg_color=DESIGN["panel"], corner_radius=DESIGN["radius_input"])
                card.pack(pady=6, padx=8, fill=ctk.X)
                
                info_frame = ctk.CTkFrame(card, fg_color="transparent")
                info_frame.pack(side=ctk.LEFT, pady=12, padx=16, fill=ctk.X, expand=True)
                
                ctk.CTkLabel(
                    info_frame, 
                    text=f"{ICONS['globe']}  {site}", 
                    font=ctk.CTkFont(family=DESIGN["font_family"], size=16, weight="bold"),
                    text_color=DESIGN["text"]
                ).pack(anchor="w")
                
                username = self.vault.data[site]["username"]
                ctk.CTkLabel(
                    info_frame, 
                    text=f"{ICONS['user']}  {username}", 
                    font=ctk.CTkFont(family=DESIGN["font_family"], size=13), 
                    text_color=DESIGN["text_muted"]
                ).pack(anchor="w", pady=(4, 0))
                
                view_btn = ctk.CTkButton(
                    card, 
                    text="View Details", 
                    width=100, 
                    height=32,
                    fg_color="transparent", 
                    border_width=1, 
                    border_color=DESIGN["border"], 
                    hover_color=DESIGN["bg"],
                    text_color=DESIGN["text"],
                    command=lambda s=site: self.on_site_selected(s)
                )
                view_btn.pack(side=ctk.RIGHT, padx=16)

    def auto_generate(self):
        new_pw = generate_password()
        self.new_password_entry.delete(0, ctk.END)
        self.new_password_entry.insert(0, new_pw)
        self.new_password_entry.configure(show="") 
        self.toggle_btn.configure(text=ICONS["hide"])

    def save_new_entry(self):
        site = self.site_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.new_password_entry.get().strip()

        if not site or not username or not password:
            messagebox.showwarning("Error", "All fields are required!")
            return

        try:
            self.vault.add_entry(site, username, password)
            self.show_dashboard_tab()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save entry: {e}")

    def on_site_selected(self, site):
        credentials = self.vault.data[site]
        self.show_credentials_popup(site, credentials['username'], credentials['password'])

    def show_credentials_popup(self, site, username, password):
        popup = ctk.CTkToplevel(self.root)
        popup.title("Account Details")
        popup.geometry("450x320")
        popup.transient(self.root)
        popup.grab_set()
        popup.configure(fg_color=DESIGN["bg"])
        
        info_frame = ctk.CTkFrame(popup, fg_color=DESIGN["card"], corner_radius=DESIGN["radius_card"])
        info_frame.pack(pady=24, padx=24, fill=ctk.BOTH, expand=True)
        
        ctk.CTkLabel(info_frame, text=f"{ICONS['globe']} {site}", font=ctk.CTkFont(family=DESIGN["font_family"], size=20, weight="bold"), text_color=DESIGN["text"]).pack(pady=(24, 16))
        ctk.CTkLabel(info_frame, text=f"{ICONS['user']} {username}", font=ctk.CTkFont(family=DESIGN["font_family"], size=14), text_color=DESIGN["text_muted"]).pack(pady=4)
        
        pw_display_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        pw_display_frame.pack(pady=4)
        
        pw_label = ctk.CTkLabel(pw_display_frame, text=f"{ICONS['lock']} •••••••••••", font=ctk.CTkFont(family=DESIGN["font_family"], size=14), text_color=DESIGN["text_muted"])
        pw_label.pack(side=ctk.LEFT, padx=(0, 12))
        
        def toggle_popup_pw():
            if "•••••••••••" in pw_label.cget("text"):
                pw_label.configure(text=f"{ICONS['unlock']} {password}")
                toggle_popup_btn.configure(text=ICONS["hide"])
            else:
                pw_label.configure(text=f"{ICONS['lock']} •••••••••••")
                toggle_popup_btn.configure(text=ICONS["eye"])

        toggle_popup_btn = ctk.CTkButton(
            pw_display_frame, text=ICONS["eye"], width=40, height=28,
            fg_color=DESIGN["panel"], hover_color=DESIGN["border"],
            corner_radius=DESIGN["radius_input"], text_color=DESIGN["text_muted"],
            command=toggle_popup_pw
        )
        toggle_popup_btn.pack(side=ctk.LEFT)
        
        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(pady=(0, 24))
        
        ctk.CTkButton(btn_frame, text=f"{ICONS['copy']} Copy", width=80, fg_color=DESIGN["accent"], hover_color=DESIGN["accent_hover"], command=lambda: self.copy_to_clipboard(password, popup)).pack(side=ctk.LEFT, padx=6)
        ctk.CTkButton(btn_frame, text=f"{ICONS['edit']} Edit", width=80, fg_color=DESIGN["panel"], hover_color=DESIGN["border"], command=lambda: self.load_for_edit(site, username, password, popup)).pack(side=ctk.LEFT, padx=6)
        ctk.CTkButton(btn_frame, text=f"{ICONS['trash']} Delete", width=80, fg_color="#F56C6C", hover_color="#DD6161", command=lambda: self.delete_saved_entry(site, popup)).pack(side=ctk.LEFT, padx=6)
        ctk.CTkButton(btn_frame, text="Close", width=80, fg_color="transparent", border_width=1, border_color=DESIGN["border"], hover_color=DESIGN["panel"], text_color=DESIGN["text"], command=popup.destroy).pack(side=ctk.LEFT, padx=6)

    def load_for_edit(self, site, username, password, window):
        self.show_add_tab()
        self.site_entry.delete(0, ctk.END)
        self.site_entry.insert(0, site)
        
        self.username_entry.delete(0, ctk.END)
        self.username_entry.insert(0, username)
        
        self.new_password_entry.delete(0, ctk.END)
        self.new_password_entry.insert(0, password)
        self.new_password_entry.configure(show="")
        self.toggle_btn.configure(text=ICONS["hide"])
        
        window.destroy()

    def delete_saved_entry(self, site, window):
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the credentials for {site}?", parent=window)
        if confirm:
            try:
                self.vault.delete_entry(site)
                self.show_dashboard_tab()
                window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete entry: {e}", parent=window)

    def copy_to_clipboard(self, text, window):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()
        messagebox.showinfo("Success", "Password copied to clipboard!", parent=window)

if __name__ == "__main__":
    root = ctk.CTk()
    app = PasswordManagerApp(root)
    root.mainloop()