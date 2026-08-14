import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import json
import os
from vault import PasswordVault, generate_password
import csv

class PasswordManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure Password Manager")
        self.root.geometry("1100x700")

        self.vault = None
        self.setup_ui()

    def setup_ui(self):
        # Use a modern ttk theme if available
        style = ttk.Style()
        try:
            style.theme_use('clam')  # Try 'clam', 'alt', 'default', 'classic'
        except tk.TclError:
            pass  # Use default theme if clam not available

        # Configure styles for better appearance
        style.configure("Treeview", font=("Helvetica", 11), rowheight=25)
        style.configure("Treeview.Heading", font=("Helvetica", 12, "bold"))
        style.configure("TButton", font=("Helvetica", 11), padding=8)
        style.configure("TLabel", font=("Helvetica", 11))
        style.configure("TEntry", font=("Helvetica", 11))
        style.configure("TLabelframe.Label", font=("Helvetica", 11, "bold"))
        # Set background color
        bg_color = "#e3f2fd"
        self.root.configure(background=bg_color)
        style.configure(".", background=bg_color)

        # Create menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Import from CSV...", command=self.import_from_csv)
        file_menu.add_command(label="Export to CSV...", command=self.export_to_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Main frame
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Left panel - Sites list
        ttk.Label(main_frame, text="Saved Accounts:").grid(row=0, column=0, sticky=tk.W, pady=(0, 10))

        # Treeview for displaying accounts
        columns = ('site', 'username')
        self.tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=20)
        self.tree.heading('site', text='Website/Service')
        self.tree.heading('username', text='Username')
        self.tree.column('site', width=400)
        self.tree.column('username', width=250)
        self.tree.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))

        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=1, column=2, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))

        buttons = [
            ("Add Account", self.add_account),
            ("Edit Account", self.edit_account),
            ("Delete Account", self.delete_account),
            ("Show Password", self.show_password),
            ("Generate Password", self.generate_password_dialog),
        ]
        for i, (txt, cmd) in enumerate(buttons):
            ttk.Button(button_frame, text=txt, command=cmd).grid(row=0, column=i, padx=5, sticky="ew")
        for i in range(len(buttons)):
            button_frame.columnconfigure(i, weight=1)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Please unlock your vault")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # Bind double-click to show password
        self.tree.bind("<Double-1>", lambda e: self.show_password())

        # Initially show login dialog
        self.show_login_dialog()

    def show_login_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Unlock Vault")
        dialog.geometry("380x200")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        # Center the dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))

        ttk.Label(dialog, text="Enter your master password:").pack(pady=20)

        password_var = tk.StringVar()
        password_entry = ttk.Entry(dialog, textvariable=password_var, show="*", width=30)
        password_entry.pack(pady=10, ipadx=4, ipady=4)
        password_entry.focus()

        def on_ok():
            password = password_var.get()
            if not password:
                messagebox.showerror("Error", "Please enter a password")
                return
            try:
                self.vault = PasswordVault()
                self.vault.set_master_password(password)
                # Try to load vault to verify password
                self.vault._load_vault()
                self.status_var.set("Vault unlocked successfully")
                dialog.destroy()
                self.load_accounts()
            except Exception as e:
                messagebox.showerror("Error", f"Invalid password or corrupted vault: {str(e)}")

        def on_cancel():
            self.root.quit()

        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="OK", command=on_ok).pack(side=tk.LEFT, padx=10, ipadx=10, ipady=4)
        ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(side=tk.LEFT, padx=10, ipadx=10, ipady=4)

        # Bind Enter key
        password_entry.bind("<Return>", lambda e: on_ok())

    def load_accounts(self):
        if not self.vault:
            self.status_var.set("Vault locked")
            return
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            services = self.vault.list_services()
            for service in services:
                accounts = self.vault.get_passwords(service)
                for account in accounts:
                    self.tree.insert("", tk.END, values=(service, account["username"]))
            self.status_var.set(f"Loaded {len(services)} services with accounts")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load accounts: {str(e)}")
            self.status_var.set("Error loading accounts")

    def add_account(self):
        if not self.vault:
            messagebox.showerror("Error", "Please unlock the vault first")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Account")
        dialog.geometry("480x300")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Website/Service:").grid(row=0, column=0, padx=15, pady=15, sticky=tk.W)
        service_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=service_var, width=30).grid(row=0, column=1, padx=15, pady=15)

        ttk.Label(dialog, text="Username:").grid(row=1, column=0, padx=15, pady=15, sticky=tk.W)
        username_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=username_var, width=30).grid(row=1, column=1, padx=15, pady=15)

        ttk.Label(dialog, text="Password:").grid(row=2, column=0, padx=15, pady=15, sticky=tk.W)
        password_var = tk.StringVar()
        password_frame = ttk.Frame(dialog)
        password_frame.grid(row=2, column=1, padx=15, pady=15, sticky=tk.W)
        ttk.Entry(password_frame, textvariable=password_var, width=25, show="*").pack(side=tk.LEFT)
        ttk.Button(
            password_frame,
            text="Generate",
            command=lambda: password_var.set(generate_password()),
        ).pack(side=tk.LEFT, padx=8)

        def on_save():
            service = service_var.get().strip()
            username = username_var.get().strip()
            password = password_var.get().strip()

            if not service or not username or not password:
                messagebox.showerror("Error", "All fields are required")
                return
            try:
                self.vault.add_password(service, username, password)
                self.load_accounts()
                dialog.destroy()
                messagebox.showinfo("Success", "Account added successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add account: {str(e)}")

        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=3, column=0, columnspan=2, pady=25)
        ttk.Button(button_frame, text="Save", command=on_save).pack(side=tk.LEFT, padx=15, ipadx=15, ipady=6)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=15, ipadx=15, ipady=6)

        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))

    def edit_account(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an account to edit")
            return

        item = self.tree.item(selected[0])
        service, username = item["values"]

        # Get current password
        accounts = self.vault.get_passwords(service)
        current_pw = None
        for acc in accounts:
            if acc["username"] == username:
                current_pw = acc["password"]
                break

        if not current_pw:
            messagebox.showerror("Error", "Could not retrieve account details")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Account")
        dialog.geometry("480x300")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Website/Service:").grid(row=0, column=0, padx=15, pady=15, sticky=tk.W)
        service_var = tk.StringVar(value=service)
        ttk.Entry(dialog, textvariable=service_var, width=30).grid(row=0, column=1, padx=15, pady=15)

        ttk.Label(dialog, text="Username:").grid(row=1, column=0, padx=15, pady=15, sticky=tk.W)
        username_var = tk.StringVar(value=username)
        ttk.Entry(dialog, textvariable=username_var, width=30).grid(row=1, column=1, padx=15, pady=15)

        ttk.Label(dialog, text="Password:").grid(row=2, column=0, padx=15, pady=15, sticky=tk.W)
        password_var = tk.StringVar(value=current_pw)
        password_frame = ttk.Frame(dialog)
        password_frame.grid(row=2, column=1, padx=15, pady=15, sticky=tk.W)
        ttk.Entry(password_frame, textvariable=password_var, width=25, show="*").pack(side=tk.LEFT)
        ttk.Button(
            password_frame,
            text="Generate",
            command=lambda: password_var.set(generate_password()),
        ).pack(side=tk.LEFT, padx=8)

        def on_save():
            new_service = service_var.get().strip()
            new_username = username_var.get().strip()
            new_password = password_var.get().strip()

            if not new_service or not new_username or not new_password:
                messagebox.showerror("Error", "All fields are required")
                return
            try:
                # Delete old entry
                self.vault.delete_password(service, username)
                # Add new/updated entry
                self.vault.add_password(new_service, new_username, new_password)
                self.load_accounts()
                dialog.destroy()
                messagebox.showinfo("Success", "Account updated successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update account: {str(e)}")

        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=3, column=0, columnspan=2, pady=25)
        ttk.Button(button_frame, text="Save", command=on_save).pack(side=tk.LEFT, padx=15, ipadx=15, ipady=6)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=15, ipadx=15, ipady=6)

        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))

    def delete_account(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an account to delete")
            return

        item = self.tree.item(selected[0])
        service, username = item["values"]

        if messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete the account for {username} at {service}?",
        ):
            try:
                if self.vault.delete_password(service, username):
                    self.load_accounts()
                    messagebox.showinfo("Success", "Account deleted successfully")
                else:
                    messagebox.showwarning("Warning", "Account not found")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete account: {str(e)}")

    def show_password(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an account to view password")
            return

        item = self.tree.item(selected[0])
        service, username = item["values"]

        try:
            accounts = self.vault.get_passwords(service)
            for account in accounts:
                if account["username"] == username:
                    password = account["password"]
                    messagebox.showinfo(
                        "Password",
                        f"Password for {username}@{service}:\n\n{password}",
                    )
                    return
            messagebox.showwarning("Warning", "Account not found")
        except Exception as e:
            messagebox.showerror("Error", f"Could not retrieve password: {str(e)}")

    def generate_password_dialog(self):
        password = generate_password()
        result = messagebox.askyesno(
            "Generated Password",
            f"Your secure password:\n\n{password}\n\nWould you like to use this for a new account?",
        )
        if result:
            self.add_account()

    def import_from_csv(self):
        if not self.vault:
            messagebox.showerror("Error", "Please unlock the vault first")
            return

        filename = filedialog.askopenfilename(
            title="Import Passwords from CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )

        if not filename:
            return

        try:
            imported_count = 0
            with open(filename, "r", newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    site = (
                        row.get("name", "")
                        or row.get("website", "")
                        or row.get("site", "")
                    )
                    username = (
                        row.get("username", "")
                        or row.get("user", "")
                        or row.get("email", "")
                    )
                    password = row.get("password", "") or row.get("pass", "")

                    if not site:
                        url = row.get("url", "")
                        if url:
                            from urllib.parse import urlparse
                            try:
                                domain = urlparse(url).netloc
                                if domain.startswith("www."):
                                    domain = domain[4:]
                                site = domain
                            except Exception:
                                pass

                    if site and username and password:
                        self.vault.add_password(
                            site.strip(), username.strip(), password.strip()
                        )
                        imported_count += 1

            self.load_accounts()
            messagebox.showinfo(
                "Success",
                f"Successfully imported {imported_count} accounts from {os.path.basename(filename)}",
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import CSV: {str(e)}")

    def export_to_csv(self):
        if not self.vault:
            messagebox.showerror("Error", "Please unlock the vault first")
            return

        filename = filedialog.asksaveasfilename(
            title="Export Passwords to CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )

        if not filename:
            return

        try:
            with open(filename, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["name", "url", "username", "password"])

                services = self.vault.list_services()
                for service in services:
                    accounts = self.vault.get_passwords(service)
                    for account in accounts:
                        url = (
                            f"https://{service}"
                            if not service.startswith(("http://", "https://"))
                            else service
                        )
                        writer.writerow(
                            [
                                service,
                                url,
                                account["username"],
                                account["password"],
                            ]
                        )

            messagebox.showinfo(
                "Success",
                f"Successfully exported {len(services)} services to {os.path.basename(filename)}",
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export CSV: {str(e)}")


def main():
    root = tk.Tk()
    app = PasswordManagerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
