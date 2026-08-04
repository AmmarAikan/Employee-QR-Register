"""Secure desktop employee registration with privacy-preserving signed QR IDs."""

from __future__ import annotations

import csv
import time
from datetime import datetime, timezone
from pathlib import Path
from tkinter import BOTH, END, LEFT, RIGHT, VERTICAL, WORD, StringVar, Text, Tk, Toplevel, messagebox
from tkinter import ttk

import qrcode
from tkcalendar import DateEntry

from security_utils import (
    PROJECT_ROOT,
    SecurityConfig,
    append_employee_record,
    build_signed_qr_payload,
    load_security_config,
    new_employee_id,
    validate_employee,
    verify_login,
)


DATA_FILE = PROJECT_ROOT / "data" / "employee_records.csv"
QR_DIRECTORY = PROJECT_ROOT / "qr_codes"
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_SECONDS = 30


class EmployeeRegisterApp:
    def __init__(self, root: Tk, security_config: SecurityConfig) -> None:
        self.root = root
        self.security_config = security_config
        self.failed_attempts = 0
        self.locked_until = 0.0
        self.fields: dict[str, object] = {}

        self.root.title("Secure Employee QR Register")
        self.root.geometry("760x560")
        self.root.minsize(700, 520)
        self.root.configure(bg="#101827")
        self._configure_styles()
        self.show_login()

    def _configure_styles(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("App.TFrame", background="#101827")
        style.configure("Card.TFrame", background="#172033")
        style.configure("Title.TLabel", background="#101827", foreground="#f8fafc", font=("Segoe UI", 22, "bold"))
        style.configure("Subtitle.TLabel", background="#101827", foreground="#94a3b8", font=("Segoe UI", 10))
        style.configure("Card.TLabel", background="#172033", foreground="#e2e8f0", font=("Segoe UI", 10))
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), padding=8)

    def _clear_root(self) -> None:
        for child in self.root.winfo_children():
            child.destroy()

    def show_login(self) -> None:
        self._clear_root()
        frame = ttk.Frame(self.root, style="App.TFrame", padding=50)
        frame.pack(fill=BOTH, expand=True)

        ttk.Label(frame, text="Secure Employee QR Register", style="Title.TLabel").pack(pady=(45, 5))
        ttk.Label(
            frame,
            text="Authenticated access · signed QR identifiers · local-only records",
            style="Subtitle.TLabel",
        ).pack(pady=(0, 30))

        card = ttk.Frame(frame, style="Card.TFrame", padding=28)
        card.pack()
        ttk.Label(card, text="Username", style="Card.TLabel").grid(row=0, column=0, sticky="w", pady=7)
        ttk.Label(card, text="Password", style="Card.TLabel").grid(row=1, column=0, sticky="w", pady=7)

        username_entry = ttk.Entry(card, width=34)
        password_entry = ttk.Entry(card, width=34, show="•")
        username_entry.grid(row=0, column=1, padx=(15, 0), pady=7)
        password_entry.grid(row=1, column=1, padx=(15, 0), pady=7)
        password_entry.bind("<Return>", lambda _event: self._attempt_login(username_entry, password_entry))

        ttk.Button(
            card,
            text="Sign in securely",
            style="Accent.TButton",
            command=lambda: self._attempt_login(username_entry, password_entry),
        ).grid(row=2, column=0, columnspan=2, sticky="ew", pady=(20, 0))
        username_entry.focus_set()

    def _attempt_login(self, username_entry: ttk.Entry, password_entry: ttk.Entry) -> None:
        remaining = self.locked_until - time.monotonic()
        if remaining > 0:
            messagebox.showwarning("Temporarily locked", f"Try again in {int(remaining) + 1} seconds.")
            return

        if verify_login(self.security_config, username_entry.get(), password_entry.get()):
            self.failed_attempts = 0
            password_entry.delete(0, END)
            self.show_registration()
            return

        self.failed_attempts += 1
        password_entry.delete(0, END)
        if self.failed_attempts >= MAX_LOGIN_ATTEMPTS:
            self.failed_attempts = 0
            self.locked_until = time.monotonic() + LOCKOUT_SECONDS
            messagebox.showerror("Access denied", "Too many failed attempts. Login is locked for 30 seconds.")
        else:
            messagebox.showerror("Access denied", "Invalid credentials.")

    def show_registration(self) -> None:
        self._clear_root()
        outer = ttk.Frame(self.root, style="App.TFrame", padding=24)
        outer.pack(fill=BOTH, expand=True)

        header = ttk.Frame(outer, style="App.TFrame")
        header.pack(fill="x", pady=(0, 18))
        ttk.Label(header, text="Employee Registration", style="Title.TLabel").pack(side=LEFT)
        ttk.Button(header, text="Lock", command=self.show_login).pack(side=RIGHT)

        card = ttk.Frame(outer, style="Card.TFrame", padding=22)
        card.pack(fill=BOTH, expand=True)

        specifications = [
            ("first_name", "First name"),
            ("last_name", "Last name"),
            ("birth_date", "Birth date"),
            ("gender", "Gender"),
            ("country", "Country"),
        ]
        countries = ["Saudi Arabia", "Yemen", "UAE", "Egypt", "Syria", "Other"]

        for row, (key, label) in enumerate(specifications):
            ttk.Label(card, text=label, style="Card.TLabel").grid(row=row, column=0, sticky="w", pady=7)
            if key == "birth_date":
                widget = DateEntry(card, width=32, date_pattern="yyyy-mm-dd")
            elif key == "gender":
                value = StringVar(value="")
                widget = ttk.Combobox(card, textvariable=value, values=["Male", "Female", "Other"], state="readonly", width=31)
            elif key == "country":
                widget = ttk.Combobox(card, values=countries, width=31)
            else:
                widget = ttk.Entry(card, width=34)
            widget.grid(row=row, column=1, sticky="ew", padx=(18, 0), pady=7)
            self.fields[key] = widget

        ttk.Label(card, text="Address", style="Card.TLabel").grid(row=5, column=0, sticky="nw", pady=7)
        address = Text(card, width=36, height=5, wrap=WORD)
        address.grid(row=5, column=1, sticky="ew", padx=(18, 0), pady=7)
        self.fields["address"] = address

        actions = ttk.Frame(card, style="Card.TFrame")
        actions.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(18, 0))
        ttk.Button(actions, text="Save record + signed QR", style="Accent.TButton", command=self.save_employee).pack(side=LEFT)
        ttk.Button(actions, text="Clear", command=self.clear_form).pack(side=LEFT, padx=8)
        ttk.Button(actions, text="View local records", command=self.show_records).pack(side=RIGHT)
        card.columnconfigure(1, weight=1)

        ttk.Label(
            outer,
            text="Privacy: QR codes contain only a random employee ID, timestamp, and HMAC signature — no personal data.",
            style="Subtitle.TLabel",
        ).pack(pady=(14, 0))

    def _field_values(self) -> dict[str, str]:
        values: dict[str, str] = {}
        for key, widget in self.fields.items():
            values[key] = widget.get("1.0", "end-1c") if isinstance(widget, Text) else widget.get()
        return values

    def save_employee(self) -> None:
        try:
            employee = validate_employee(self._field_values())
            employee_id = new_employee_id()
            issued_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
            record = {"employee_id": employee_id, **employee, "created_at": issued_at}
            append_employee_record(DATA_FILE, record)

            QR_DIRECTORY.mkdir(parents=True, exist_ok=True)
            payload = build_signed_qr_payload(employee_id, issued_at, self.security_config.qr_signing_key)
            qr_path = QR_DIRECTORY / f"{employee_id}.png"
            qrcode.make(payload).save(qr_path)
        except (OSError, ValueError) as exc:
            messagebox.showerror("Could not save", str(exc))
            return

        self.clear_form()
        messagebox.showinfo("Saved securely", f"Employee ID: {employee_id}\nQR: {qr_path.name}")

    def clear_form(self) -> None:
        for widget in self.fields.values():
            if isinstance(widget, Text):
                widget.delete("1.0", END)
            elif isinstance(widget, DateEntry):
                widget.set_date(datetime.now().date())
            elif isinstance(widget, ttk.Combobox):
                widget.set("")
            else:
                widget.delete(0, END)

    def show_records(self) -> None:
        if not DATA_FILE.exists():
            messagebox.showinfo("Local records", "No employee records have been created yet.")
            return

        window = Toplevel(self.root)
        window.title("Local employee records")
        window.geometry("900x420")
        text = Text(window, wrap="none")
        scrollbar = ttk.Scrollbar(window, orient=VERTICAL, command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill="y")
        text.pack(fill=BOTH, expand=True)
        with DATA_FILE.open("r", newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        for row in rows:
            text.insert(END, " | ".join(f"{key}: {value}" for key, value in row.items()) + "\n")
        text.configure(state="disabled")


def main() -> None:
    root = Tk()
    try:
        config = load_security_config()
    except RuntimeError as exc:
        root.withdraw()
        messagebox.showerror("Secure configuration required", str(exc))
        root.destroy()
        raise SystemExit(1) from exc

    EmployeeRegisterApp(root, config)
    root.mainloop()


if __name__ == "__main__":
    main()
