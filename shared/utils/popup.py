import os
import sys
import tkinter as tk
import webbrowser
from tkinter import ttk
from typing import List, Optional


def _is_remote_ci() -> bool:
    """Check if execution is happening in a headless remote CI/CD runner."""
    ci_val = os.environ.get("CI", "").strip().lower()
    if ci_val in ("true", "1", "yes"):
        return True
    if os.environ.get("GITHUB_ACTIONS", "").strip().lower() in ("true", "1"):
        return True
    if os.environ.get("TF_BUILD", "").strip().lower() == "true":
        return True
    if os.environ.get("BUILDKITE", "").strip().lower() == "true":
        return True
    return False


def show_summary_popup(
    total: Optional[int] = None,
    passed: int = 0,
    failed: int = 0,
    skipped: int = 0,
    duration_str: str = "0:00:00",
    failed_tests: Optional[List[str]] = None,
    suite_title: str = "SWARAJYA AUTOMATION",
    title: Optional[str] = None,
    duration: Optional[str] = None,
    failures: Optional[List[str]] = None,
    report_path: Optional[str] = None,
    **kwargs,
):
    """
    Display a styled desktop popup showing test execution results.
    Brings window to the foreground with sound alert and key bindings (Esc / Enter to close).
    Cleanly bypasses in headless remote CI/CD environments unless FORCE_POPUP=1.
    """
    # Normalize inputs
    if title:
        suite_title = title
    elif kwargs.get("title"):
        suite_title = kwargs["title"]
    elif kwargs.get("suite_title"):
        suite_title = kwargs["suite_title"]

    if os.environ.get("SWARAJYA_POPUP_HEADER"):
        suite_title = os.environ.get("SWARAJYA_POPUP_HEADER")
    elif os.environ.get("SWARAJYA_POPUP_TITLE"):
        suite_title = os.environ.get("SWARAJYA_POPUP_TITLE")

    if failed_tests is None:
        failed_tests = failures or kwargs.get("failures") or []

    if duration is not None:
        duration_str = str(duration)
    elif kwargs.get("duration"):
        duration_str = str(kwargs["duration"])

    if total is None:
        total = passed + failed + skipped

    # Check suppression
    force_popup = os.environ.get("FORCE_POPUP", "").strip().lower() in ("1", "true", "yes")
    no_popup = os.environ.get("PYTEST_NO_POPUP", "").strip().lower() in ("1", "true", "yes")

    if not force_popup:
        if no_popup:
            print("[POPUP] Summary popup bypassed via PYTEST_NO_POPUP=1.")
            return
        if _is_remote_ci():
            print("[POPUP] Remote CI environment detected. Desktop summary popup skipped.")
            return

    try:
        root = tk.Tk()
        root.title(f"{suite_title} - Execution Summary")
        root.resizable(False, False)

        # Force window to stay on top
        root.attributes("-topmost", True)

        # Visual theme
        bg_color = "#1E1E2E"
        fg_color = "#CDD6F4"
        card_bg = "#313244"
        green_color = "#A6E3A1"
        red_color = "#FF5555"      # Bright vivid red
        yellow_color = "#F9E2AF"
        accent_color = "#89B4FA"

        root.configure(bg=bg_color)

        title_lbl = tk.Label(
            root,
            text=f"📊  {suite_title.upper()}",
            font=("Segoe UI", 13, "bold"),
            bg=bg_color,
            fg=accent_color,
        )
        title_lbl.pack(pady=(18, 8))

        status_text = "ALL PASSED" if failed == 0 and total > 0 else f"{failed} TEST(S) FAILED" if failed > 0 else "COMPLETED"
        status_fg = green_color if failed == 0 and total > 0 else red_color if failed > 0 else fg_color

        status_lbl = tk.Label(
            root,
            text=f"Status: {status_text}",
            font=("Segoe UI", 11, "bold"),
            bg=bg_color,
            fg=status_fg,
        )
        status_lbl.pack(pady=(0, 14))

        # Stats Card
        card = tk.Frame(root, bg=card_bg, padx=25, pady=15, relief="flat")
        card.pack(fill="x", padx=25)

        stats = [
            ("Total Tests", total, fg_color),
            ("Passed", passed, green_color),
            ("Failed", failed, red_color),
            ("Skipped", skipped, yellow_color),
            ("Time Taken", duration_str, accent_color),
        ]

        for idx, (label, val, col) in enumerate(stats):
            lbl = tk.Label(card, text=f"{label}:", font=("Segoe UI", 10), bg=card_bg, fg=fg_color, anchor="w")
            lbl.grid(row=idx, column=0, sticky="w", pady=3)
            vlbl = tk.Label(card, text=str(val), font=("Segoe UI", 10, "bold"), bg=card_bg, fg=col, anchor="e")
            vlbl.grid(row=idx, column=1, sticky="e", padx=(40, 0), pady=3)

        card.grid_columnconfigure(0, weight=1)
        card.grid_columnconfigure(1, weight=1)

        # Failed Test Cases List in Vivid Red
        if failed_tests and len(failed_tests) > 0:
            fail_header = tk.Label(
                root,
                text=f"FAILED TEST CASES ({len(failed_tests)})",
                font=("Segoe UI", 10, "bold"),
                bg=bg_color,
                fg=red_color,
            )
            fail_header.pack(pady=(14, 5))

            fail_frame = tk.Frame(root, bg=card_bg, padx=12, pady=10, relief="flat")
            fail_frame.pack(fill="both", expand=True, padx=25)

            max_items = min(len(failed_tests), 6)
            canvas_h = max(max_items * 28, 56)
            canvas = tk.Canvas(fail_frame, bg=card_bg, highlightthickness=0, height=canvas_h)
            scrollbar = ttk.Scrollbar(fail_frame, orient="vertical", command=canvas.yview)
            scroll_content = tk.Frame(canvas, bg=card_bg)

            scroll_content.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            canvas.create_window((0, 0), window=scroll_content, anchor="nw", width=380)
            canvas.configure(yscrollcommand=scrollbar.set)

            for ft in failed_tests:
                display_name = ft.split("::")[-1] if "::" in ft else ft
                display_name = str(display_name).strip()

                lbl_item = tk.Label(
                    scroll_content,
                    text=f"  ✖  {display_name}",
                    font=("Segoe UI", 9, "bold"),
                    bg=card_bg,
                    fg=red_color,
                    anchor="w",
                    justify="left",
                    wraplength=360,
                )
                lbl_item.pack(fill="x", anchor="w", pady=2)

            canvas.pack(side="left", fill="both", expand=True)
            if len(failed_tests) > 4:
                scrollbar.pack(side="right", fill="y")

        # Action buttons
        btn_frame = tk.Frame(root, bg=bg_color)
        btn_frame.pack(pady=(15, 18))

        if report_path and os.path.exists(report_path):
            def _open_html():
                try:
                    webbrowser.open(f"file://{os.path.abspath(report_path)}")
                except Exception:
                    pass

            report_btn = tk.Button(
                btn_frame,
                text="🌐 View HTML Report",
                font=("Segoe UI", 9, "bold"),
                bg="#A6E3A1",
                fg="#11111B",
                activebackground="#94E2D5",
                activeforeground="#11111B",
                relief="flat",
                padx=14,
                pady=4,
                cursor="hand2",
                command=_open_html,
            )
            report_btn.pack(side="left", padx=(0, 10))

        close_btn = tk.Button(
            btn_frame,
            text="Close",
            font=("Segoe UI", 9, "bold"),
            bg=accent_color,
            fg="#11111B",
            activebackground="#B4BEFE",
            activeforeground="#11111B",
            relief="flat",
            padx=16,
            pady=4,
            cursor="hand2",
            command=root.destroy,
        )
        close_btn.pack(side="left")

        # Keyboard shortcuts to dismiss easily
        root.bind("<Escape>", lambda e: root.destroy())
        root.bind("<Return>", lambda e: root.destroy())

        # Center on screen
        root.update_idletasks()
        w = max(root.winfo_reqwidth(), 420)
        h = root.winfo_reqheight()
        x = (root.winfo_screenwidth() - w) // 2
        y = (root.winfo_screenheight() - h) // 2
        root.geometry(f"{w}x{h}+{x}+{y}")

        # Foreground activation helper
        def _activate_foreground():
            try:
                root.deiconify()
                root.lift()
                root.attributes("-topmost", True)
                root.focus_force()

                if sys.platform == "win32":
                    import ctypes
                    try:
                        hwnd = root.winfo_id()
                        ctypes.windll.user32.SetForegroundWindow(hwnd)
                        ctypes.windll.user32.BringWindowToTop(hwnd)
                    except Exception:
                        pass
                elif sys.platform == "darwin":
                    import subprocess
                    try:
                        subprocess.run(
                            ["osascript", "-e", 'tell application "System Events" to set frontmost of (first process whose name is "python" or name is "python3" or name is "Python") to true'],
                            check=False,
                            capture_output=True,
                        )
                    except Exception:
                        pass
            except Exception:
                pass

        _activate_foreground()
        root.after(100, _activate_foreground)
        root.after(250, _activate_foreground)

        # Sound alert to notify user
        try:
            root.bell()
        except Exception:
            pass

        # Optional timeout support with a safe default of 12 seconds so automated/unattended runs don't hang
        timeout_env = os.environ.get("SWARAJYA_POPUP_TIMEOUT")
        if timeout_env and timeout_env.isdigit() and int(timeout_env) > 0:
            root.after(int(timeout_env) * 1000, root.destroy)
        else:
            root.after(12000, root.destroy)

        root.mainloop()
    except Exception as exc:
        print(f"[POPUP] Could not display execution popup: {exc}")
