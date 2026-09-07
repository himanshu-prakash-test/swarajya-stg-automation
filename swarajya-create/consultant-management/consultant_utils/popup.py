import os
import sys
from datetime import datetime


def show_summary_popup(passed: int, failed: int, skipped: int, duration_sec: float):
    """Display desktop summary popup if not in headless or CI environment."""
    if os.environ.get("HEADLESS") == "1" or os.environ.get("CI") == "1" or not os.environ.get("DISPLAY", "") and sys.platform != "darwin":
        return

    try:
        import tkinter as tk
        from tkinter import ttk

        total = passed + failed + skipped
        mins, secs = divmod(int(duration_sec), 60)
        time_str = f"{mins}m {secs}s"

        root = tk.Tk()
        root.title("Consultant Management - Execution Summary")
        root.geometry("400x260")
        root.resizable(False, False)

        frame = ttk.Frame(root, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Consultant Automation Summary", font=("Helvetica", 14, "bold")).pack(pady=(0, 10))

        ttk.Label(frame, text=f"Total Tests: {total}", font=("Helvetica", 11)).pack(anchor="w", pady=2)
        ttk.Label(frame, text=f"Passed: {passed}", font=("Helvetica", 11), foreground="green").pack(anchor="w", pady=2)
        ttk.Label(frame, text=f"Failed: {failed}", font=("Helvetica", 11), foreground="red" if failed else "black").pack(anchor="w", pady=2)
        ttk.Label(frame, text=f"Skipped: {skipped}", font=("Helvetica", 11), foreground="orange" if skipped else "black").pack(anchor="w", pady=2)
        ttk.Label(frame, text=f"Duration: {time_str}", font=("Helvetica", 10, "italic")).pack(anchor="w", pady=(5, 10))

        ttk.Button(frame, text="Close", command=root.destroy).pack(pady=(5, 0))

        root.mainloop()
    except Exception:
        pass
