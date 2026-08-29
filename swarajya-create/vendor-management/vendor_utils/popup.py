import os
import sys
import tkinter as tk
from tkinter import ttk


def show_summary_popup(total: int, passed: int, failed: int, skipped: int, duration_str: str):
    """
    Display a styled desktop popup showing test execution results.
    Bypasses cleanly when running under CI / headless collection.
    """
    if os.environ.get("CI") or not sys.stdin.isatty():
        try:
            root = tk.Tk()
        except Exception:
            return

    try:
        root = tk.Tk()
        root.title("Swarajya Vendor Automation - Execution Summary")
        root.geometry("450x320")
        root.resizable(False, False)
        root.attributes("-topmost", True)

        # Style
        bg_color = "#1E1E2E"
        fg_color = "#CDD6F4"
        card_bg = "#313244"
        green_color = "#A6E3A1"
        red_color = "#F38BA8"
        yellow_color = "#F9E2AF"
        accent_color = "#89B4FA"

        root.configure(bg=bg_color)

        title_lbl = tk.Label(
            root,
            text="VENDOR AUTOMATION SUMMARY",
            font=("Segoe UI", 13, "bold"),
            bg=bg_color,
            fg=accent_color,
        )
        title_lbl.pack(pady=(18, 10))

        status_text = "ALL PASSED" if failed == 0 and total > 0 else "FAILURES DETECTED" if failed > 0 else "COMPLETED"
        status_fg = green_color if failed == 0 and total > 0 else red_color if failed > 0 else fg_color

        status_lbl = tk.Label(
            root,
            text=f"Status: {status_text}",
            font=("Segoe UI", 11, "bold"),
            bg=bg_color,
            fg=status_fg,
        )
        status_lbl.pack(pady=(0, 15))

        # Stats Card
        card = tk.Frame(root, bg=card_bg, padx=25, pady=15, relief="flat")
        card.pack(fill="x", padx=25)

        stats = [
            ("Total Tests", total, fg_color),
            ("Passed", passed, green_color),
            ("Failed", failed, red_color),
            ("Skipped", skipped, yellow_color),
            ("Duration", duration_str, accent_color),
        ]

        for idx, (label, val, col) in enumerate(stats):
            lbl = tk.Label(card, text=f"{label}:", font=("Segoe UI", 10), bg=card_bg, fg=fg_color, anchor="w")
            lbl.grid(row=idx, column=0, sticky="w", pady=2)
            vlbl = tk.Label(card, text=str(val), font=("Segoe UI", 10, "bold"), bg=card_bg, fg=col, anchor="e")
            vlbl.grid(row=idx, column=1, sticky="e", padx=(40, 0), pady=2)

        card.grid_columnconfigure(0, weight=1)
        card.grid_columnconfigure(1, weight=1)

        btn = tk.Button(
            root,
            text="Close",
            font=("Segoe UI", 9, "bold"),
            bg=accent_color,
            fg="#11111B",
            activebackground="#B4BEFE",
            activeforeground="#11111B",
            relief="flat",
            padx=20,
            pady=4,
            cursor="hand2",
            command=root.destroy,
        )
        btn.pack(pady=(15, 0))

        # Auto-close after 60 seconds
        root.after(60000, lambda: root.destroy())
        root.mainloop()
    except Exception:
        pass
