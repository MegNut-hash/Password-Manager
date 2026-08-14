import os
import csv
import pytest
from unittest.mock import MagicMock, patch
import tkinter as tk
from tkinter import ttk

# Import the GUI class from your main script file
# Replace 'main' with the filename of your Tkinter script if it's named differently (e.g. gui.py)
from gui import Password_Manager


@pytest.fixture
def root():
    """Provides a Tkinter root window instance and destroys it after test execution."""
    root_window = tk.Tk()
    root_window.withdraw()  # Hide root window during testing
    yield root_window
    try:
        root_window.destroy()
    except tk.TclError:
        pass


@pytest.fixture
def mock_vault():
    """Provides a mocked PasswordVault instance with default behaviors."""
    vault = MagicMock()
    vault.list_services.return_value = ["github.com", "google.com"]
    vault.get_passwords.side_effect = lambda service: {
        "github.com": [{"username": "dev_user", "password": "SecretPassword123!"}],
        "google.com": [{"username": "user@gmail.com", "password": "GooglePass456!"}],
    }.get(service, [])
    vault.delete_password.return_value = True
    return vault


@pytest.fixture
def app(root, mock_vault):
    """Initializes PasswordManagerGUI with a pre-unlocked mock vault."""
    with patch("main.PasswordVault", return_value=mock_vault):
        app_instance = PasswordManagerGUI(root)
        app_instance.vault = mock_vault
        return app_instance


# --- TEST SUITE ---

def test_initialization(root):
    """Test that GUI initial state sets up treeview and status correctly."""
    with patch("main.PasswordVault"):
        app_instance = PasswordManagerGUI(root)
        assert app_instance.vault is None
        assert "Ready" in app_instance.status_var.get()
        assert isinstance(app_instance.tree, ttk.Treeview)


def test_load_accounts(app, mock_vault):
    """Test that saved accounts are populated into the Treeview widget."""
    app.load_accounts()
    
    # Check tree items
    children = app.tree.get_children()
    assert len(children) == 2
    
    item1 = app.tree.item(children[0])["values"]
    item2 = app.tree.item(children[1])["values"]
    
    assert item1 == ["github.com", "dev_user"]
    assert item2 == ["google.com", "user@gmail.com"]
    assert "Loaded 2 services" in app.status_var.get()


@patch("tkinter.messagebox.showinfo")
def test_show_password(mock_showinfo, app):
    """Test viewing password for a selected Treeview item."""
    app.load_accounts()
    item_id = app.tree.get_children()[0]
    app.tree.selection_set(item_id)
    
    app.show_password()
    
    mock_showinfo.assert_called_once()
    assert "SecretPassword123!" in mock_showinfo.call_args[0][1]


@patch("tkinter.messagebox.askyesno", return_value=True)
@patch("tkinter.messagebox.showinfo")
def test_delete_account_success(mock_showinfo, mock_askyesno, app, mock_vault):
    """Test deleting an account updates the vault and reloads UI list."""
    app.load_accounts()
    item_id = app.tree.get_children()[0]
    app.tree.selection_set(item_id)
    
    app.delete_account()
    
    mock_vault.delete_password.assert_called_once_with("github.com", "dev_user")
    mock_showinfo.assert_called_once_with("Success", "Account deleted successfully")


@patch("tkinter.filedialog.asksaveasfilename")
@patch("tkinter.messagebox.showinfo")
def test_export_to_csv(mock_showinfo, mock_dialog, app, tmp_path):
    """Test exporting vault credentials to a valid CSV file format."""
    target_csv = tmp_path / "exported_passwords.csv"
    mock_dialog.return_value = str(target_csv)
    
    app.export_to_csv()
    
    assert target_csv.exists()
    
    with open(target_csv, "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
        assert reader[0] == ["name", "url", "username", "password"]
        assert len(reader) == 3  # Header + 2 entries
        assert reader[1][0] == "github.com"
        assert reader[1][3] == "SecretPassword123!"


@patch("tkinter.filedialog.askopenfilename")
@patch("tkinter.messagebox.showinfo")
def test_import_from_csv(mock_showinfo, mock_dialog, app, mock_vault, tmp_path):
    """Test parsing CSV rows and adding entries into the vault."""
    import_csv = tmp_path / "import_me.csv"
    with open(import_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["site", "username", "password"])
        writer.writerow(["discord.com", "gamer_tag", "SuperSecret99"])
    
    mock_dialog.return_value = str(import_csv)
    
    app.import_from_csv()
    
    mock_vault.add_password.assert_called_once_with("discord.com", "gamer_tag", "SuperSecret99")
    mock_showinfo.assert_called_once()