import os
import sys
import tkinter as tk
from tkinter import ttk
from typing import List, Optional


def show_summary_popup(
    total: int,
    passed: int,
    failed: int,
    skipped: int,
    duration_str: str = "0:00:00",
    failed_tests: Optional[List[str]] = None,
    suite_title: str = "SWARAJYA AUTOMATION",
    duration: Optional[str] = None,
):
    """
    Display a styled desktop popup showing test execution results.
    Lists failed test case names if any.
    Bypasses cleanly when running under CI or with PYTEST_NO_POPUP=1.
    """
    duration_str = duration if duration is not None else duration_str
    if os.environ.get("CI") or os.environ.get("PYTEST_NO_POPUP") == "1":
        return

    try:
        root = tk.Tk()
        root.title(f"{suite_title} - Execution Summary")
        root.resizable(False, False)
        root.attributes("-topmost", True)

        # Visual theme
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
            text=f"{suite_title} SUMMARY",
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

        # Failed Test Cases List
        if failed_tests:
            fail_header = tk.Label(
                root,
                text="FAILED TEST CASES",
                font=("Segoe UI", 10, "bold"),
                bg=bg_color,
                fg=red_color,
            )
            fail_header.pack(pady=(12, 4))

            fail_frame = tk.Frame(root, bg=card_bg, padx=10, pady=8, relief="flat")
            fail_frame.pack(fill="x", padx=25)

            canvas = tk.Canvas(fail_frame, bg=card_bg, highlightthickness=0, height=min(len(failed_tests) * 22, 132))
            scrollbar = ttk.Scrollbar(fail_frame, orient="vertical", command=canvas.yview)
            scroll_content = tk.Frame(canvas, bg=card_bg)

            scroll_content.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            canvas.create_window((0, 0), window=scroll_content, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            for ft in failed_tests:
                display_name = ft.split("::")[-1] if "::" in ft else ft
                lbl_item = tk.Label(
                    scroll_content,
                    text=f"  {display_name}",
                    font=("Segoe UI", 9),
                    bg=card_bg,
                    fg=red_color,
                    anchor="w",
                )
                lbl_item.pack(fill="x", anchor="w")

            canvas.pack(side="left", fill="both", expand=True)
            if len(failed_tests) > 6:
                scrollbar.pack(side="right", fill="y")

        # Close button
        btn = tk.Button(
            root,
            text="Close",
            font=("Segoe UI", 10, "bold"),
            bg=accent_color,
            fg="#11111B",
            activebackground="#B4BEFE",
            activeforeground="#11111B",
            relief="flat",
            padx=20,
            pady=4,
            command=root.destroy,
        )
        btn.pack(pady=(15, 18))

        root.update_idletasks()
        w = max(root.winfo_reqwidth(), 380)
        h = root.winfo_reqheight()
        x = (root.winfo_screenwidth() - w) // 2
        y = (root.winfo_screenheight() - h) // 2
        root.geometry(f"{w}x{h}+{x}+{y}")

        root.mainloop()
    except Exception as exc:
        print(f"[POPUP] Could not display execution popup: {exc}")
