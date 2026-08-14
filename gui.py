import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import csv


class PasswordManagerGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Password Manager")
        self.master.geometry("800x500")
        self.master.resizable(True, True)

        # Vault reference (set externally, e.g., in tests)
        self.vault = None

        # Status variable
        self.status_var = tk.StringVar(value="Ready")

        # Build UI
        self._create_menu()
        self._create_toolbar()
        self._create_treeview()
        self._create_statusbar()

        # Load existing accounts if vault is set
        if self.vault:
            self.load_accounts()

    def _create_menu(self):
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Import from CSV", command=self.import_from_csv)
        file_menu.add_command(label="Export to CSV", command=self.export_to_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.master.quit)

    def _create_toolbar(self):
        toolbar = ttk.Frame(self.master)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        ttk.Button(toolbar, text="Add Account", command=self.add_account).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Edit Account", command=self.edit_account).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Delete Account", command=self.delete_account).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Show Password", command=self.show_password).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Generate Password", command=self.generate_password).pack(side=tk.LEFT, padx=2)

    def _create_treeview(self):
        tree_frame = ttk.Frame(self.master)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Treeview with two columns: Service, Username
        self.tree = ttk.Treeview(tree_frame, columns=("service", "username"), show="headings")
        self.tree.heading("service", text="Service")
        self.tree.heading("username", text="Username")
        self.tree.column("service", width=200)
        self.tree.column("username", width=200)

        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Bind double-click to show password
        self.tree.bind("<Double-1>", lambda e: self.show_password())

    def _create_statusbar(self):
        status_bar = ttk.Label(self.master, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def load_accounts(self):
        """Load accounts from vault into the treeview."""
        if not self.vault:
            self.status_var.set("No vault loaded")
            return
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        services = self.vault.list_services()
        for service in services:
            credentials = self.vault.get_passwords(service)
            for cred in credentials:
                self.tree.insert("", tk.END, values=(service, cred["username"]))
        self.status_var.set(f"Loaded {len(services)} services")

    def _get_selected_item(self):
        """Return (service, username) of selected tree item, or None."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an account first.")
            return None
        item = self.tree.item(selected[0])
        values = item["values"]
        if len(values) >= 2:
            return values[0], values[1]
        return None

    def show_password(self):
        """Show password for the selected account."""
        selection = self._get_selected_item()
        if not selection:
            return
        service, username = selection
        passwords = self.vault.get_passwords(service)
        # Find matching username
        password = None
        for cred in passwords:
            if cred["username"] == username:
                password = cred["password"]
                break
        if password is None:
            messagebox.showerror("Error", "Password not found for selected account.")
            return
        messagebox.showinfo("Password", f"Password for {service} ({username}):\n{password}")

    def delete_account(self):
        """Delete the selected account."""
        selection = self._get_selected_item()
        if not selection:
            return
        service, username = selection
        if messagebox.askyesno("Confirm Delete", f"Delete account for {service} ({username})?"):
            if self.vault.delete_password(service, username):
                messagebox.showinfo("Success", "Account deleted successfully.")
                self.load_accounts()
            else:
                messagebox.showerror("Error", "Failed to delete account.")

    def add_account(self):
        """Add a new account via a dialog."""
        dialog = tk.Toplevel(self.master)
        dialog.title("Add Account")
        dialog.transient(self.master)
        dialog.grab_set()

        ttk.Label(dialog, text="Service:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        service_entry = ttk.Entry(dialog, width=30)
        service_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(dialog, text="Username:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        username_entry = ttk.Entry(discount, width=30)  # Oops typo: should be username_entry
        username_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(dialog, text="Password:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        password_frame = ttk.Frame(dialog)
        password_frame.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        password_entry = ttk.Entry(password_frame, width=25, show="*")
        password_entry.pack(side=tk.LEFT)
        gen_btn = ttk.Button(password_frame, text="Generate", width=8,
                             command=lambda: password_entry.delete(0, tk.END) or
                                             password_entry.insert(0, self._generate_password()))
        gen_btn.pack(side=tk.LEFT, padx=2)

        btn_frame = ttk.Frame(dialog)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)

        def on_save():
            service = service_entry.get().strip()
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            if not service or not username or not password:
                messagebox.showwarning("Validation", "All fields are required.")
                return
            if not self.vault:
                messagebox.showerror("Error", "Vault not initialized.")
                return
            self.vault.add_password(service, username, password)
            messagebox.showinfo("Success", "Account added.")
            self.load_accounts()
            dialog.destroy()

        ttk.Button(btn_frame, text="Save", command=on_save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

        service_entry.focus()

    def edit_account(self):
        """Edit selected account (placeholder for simplicity)."""
        messagebox.showinfo("Info", "Edit functionality not implemented in this version.")

    def generate_password(self):
        """Generate and show a password."""
        password = self._generate_password()
        messagebox.showinfo("Generated Password", f"Your secure password:\n{password}")

    def _generate_password(self, length=16):
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def export_to_csv(self):
        """Export vault to CSV file (name,url,username,password)."""
        if not self.vault:
            messagebox.showerror("Error", "Vault not initialized.")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Passwords to CSV"
        )
        if not file_path:
            return
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["name", "url", "username", "password"])
                for service in self.vault.list_services():
                    creds = self.vault.get_passwords(service)
                    for cred in creds:
                        writer.writerow([service, service, cred["username"], cred["password"]])
            messagebox.showinfo("Success", f"Exported {len(self.vault.list_services())} services to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {e}")

    def import_from_csv(self):
        """Import accounts from CSV file (service,username,password)."""
        if not self.vault:
            messagebox.showerror("Error", "Vault not initialized.")
            return
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Import Passwords from CSV"
        )
        if not file_path:
            return
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                # Expect columns: service, username, password (case-insensitive)
                fieldnames = [f.lower().strip() for f in reader.fieldnames or []]
                # Map possible column names
                def get_field(row, *options):
                    for opt in options:
                        if opt in fieldnames:
                            return row[opt]
                    return None
                imported = 0
                for row in reader:
                    service = get_field(row, 'service', 'site', 'name', 'url')
                    username = get_field(row, 'username', 'user', 'email')
                    password = get_field(row, 'password', 'pass', 'pw')
                    if not service or not username or not password:
                        continue  # skip malformed rows
                    self.vault.add_password(service.strip(), username.strip(), password.strip())
                    imported += 1
            messagebox.showinfo("Success", f"Imported {imported} accounts from {file_path}")
            self.load_accounts()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import: {e}")



if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordManagerGUI(root)
    root.mainloop()