import sys
import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk


def show_summary_popup(passed=10, failed=2, skipped=0, total=12, duration="0:02:15", failures=None):
    if failures is None:
        failures = []

    root = tk.Tk()
    root.title("Swarajya Automation — Execution Summary")
    root.geometry("620x600")
    root.minsize(560, 480)
    root.configure(bg="#0f172a")

    # Center dialog on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() - 620) // 2
    y = (root.winfo_screenheight() - 600) // 2
    root.geometry(f"+{x}+{y}")

    root.lift()
    root.attributes("-topmost", True)
    root.focus_force()

    # Header
    hdr = tk.Frame(root, bg="#1e293b", pady=16, padx=20)
    hdr.pack(fill="x")
    tk.Label(
        hdr,
        text="SWARAJYA CREATE AUTOMATION",
        font=tkfont.Font(family="Segoe UI", size=15, weight="bold"),
        fg="#f8fafc",
        bg="#1e293b",
    ).pack()
    tk.Label(
        hdr,
        text="Employee Management Automated Test Suite",
        font=tkfont.Font(family="Segoe UI", size=10),
        fg="#94a3b8",
        bg="#1e293b",
    ).pack(pady=(3, 0))

    # Status Banner
    if failed == 0:
        bg_color = "#16a34a"
        status_text = "ALL AUTOMATION TESTS PASSED"
    else:
        bg_color = "#dc2626"
        status_text = f"{failed} TEST(S) FAILED (APPLICATION DEFECTS IDENTIFIED)"

    bf = tk.Frame(root, bg=bg_color, pady=10)
    bf.pack(fill="x")
    tk.Label(
        bf,
        text=status_text,
        font=tkfont.Font(family="Segoe UI", size=11, weight="bold"),
        fg="white",
        bg=bg_color,
    ).pack()

    # Metrics Grid
    sf = tk.Frame(root, bg="#0f172a", pady=14, padx=28)
    sf.pack(fill="x")
    mono = tkfont.Font(family="Consolas", size=11, weight="bold")
    lbl = tkfont.Font(family="Segoe UI", size=11)
    
    rows = [
        ("Total Scenarios", str(total), "#94a3b8"),
        ("Passed", str(passed), "#22c55e"),
        ("Failed (Defects)", str(failed), "#ef4444" if failed else "#94a3b8"),
        ("Skipped (API)", str(skipped), "#f59e0b" if skipped else "#94a3b8"),
        ("Execution Time", str(duration), "#38bdf8"),
    ]
    for i, (l, v, c) in enumerate(rows):
        tk.Label(sf, text=l, font=lbl, fg="#cbd5e1", bg="#0f172a", anchor="w", width=18).grid(
            row=i, column=0, sticky="w", pady=2
        )
        tk.Label(sf, text=":", font=lbl, fg="#475569", bg="#0f172a").grid(row=i, column=1, padx=6)
        tk.Label(sf, text=v, font=mono, fg=c, bg="#0f172a", anchor="w").grid(
            row=i, column=2, sticky="w", pady=2
        )

    # Failures list section
    if failures:
        ff = tk.Frame(root, bg="#0f172a", padx=28)
        ff.pack(fill="both", expand=True)
        tk.Label(
            ff,
            text="Failed Scenarios & Defect Details:",
            font=tkfont.Font(family="Segoe UI", size=10, weight="bold"),
            fg="#f87171",
            bg="#0f172a",
        ).pack(anchor="w", pady=(6, 4))

        # Text box with scrollbar for failure remarks
        txt_frame = tk.Frame(ff, bg="#1e293b", bd=1, relief="solid")
        txt_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(txt_frame)
        scrollbar.pack(side="right", fill="y")

        txt = tk.Text(
            txt_frame,
            wrap="word",
            bg="#1e293b",
            fg="#fca5a5",
            font=tkfont.Font(family="Consolas", size=9),
            bd=0,
            padx=10,
            pady=8,
            yscrollcommand=scrollbar.set,
        )
        txt.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=txt.yview)

        for item in failures:
            txt.insert("end", f"• {item}\n\n")
        txt.config(state="disabled")

    # Bottom Actions
    bk = tk.Frame(root, bg="#0f172a", pady=14)
    bk.pack(fill="x", side="bottom")
    tk.Button(
        bk,
        text="Close Summary",
        font=tkfont.Font(family="Segoe UI", size=10, weight="bold"),
        fg="white",
        bg="#334155",
        activebackground="#475569",
        cursor="hand2",
        relief="flat",
        padx=28,
        pady=6,
        command=root.destroy,
    ).pack()

    # Automatically release topmost flag after 1.5s so other windows aren't permanently blocked
    root.after(1500, lambda: root.attributes("-topmost", False))
    root.after(60000, root.destroy)  # Auto-close after 60s
    root.mainloop()


if __name__ == "__main__":
    show_summary_popup(
        passed=19,
        failed=9,
        skipped=2,
        total=30,
        duration="0:04:12",
        failures=[
            "TC_NEG_EMP_002: Application accepted numeric characters in name without error",
            "TC_NEG_EMP_003: Application accepted invalid mobile number (<10 digits)",
        ],
    )
