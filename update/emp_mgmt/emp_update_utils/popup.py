import os
import sys

try:
    from shared.utils.popup import show_summary_popup as shared_popup
except ImportError:
    shared_popup = None


def show_summary_popup(passed: int, failed: int, skipped: int, duration_sec: float, total: int = None, failed_tests: list = None):
    """Display the desktop summary popup if not in headless/CI mode."""
    if os.environ.get("PYTEST_NO_POPUP", "0") == "1" or os.environ.get("HEADLESS", "0").lower() in ("1", "true", "yes"):
        return

    dur_str = f"{duration_sec:.1f}s" if isinstance(duration_sec, (int, float)) else str(duration_sec)
    tot = total if total is not None else (passed + failed + skipped)

    if shared_popup:
        try:
            shared_popup(
                total=tot,
                passed=passed,
                failed=failed,
                skipped=skipped,
                duration_str=dur_str,
                failed_tests=failed_tests or [],
            )
            return
        except Exception:
            pass

    # Direct Tkinter fallback
    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()
        title = "Swarajya Employee Update Execution Summary"
        msg = (
            f"Execution Results:\n\n"
            f"Total Tests : {tot}\n"
            f"Passed      : {passed}\n"
            f"Failed      : {failed}\n"
            f"Skipped     : {skipped}\n"
            f"Duration    : {dur_str}\n"
        )
        messagebox.showinfo(title, msg)
        root.destroy()
    except Exception:
        pass
