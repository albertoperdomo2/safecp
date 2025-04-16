import sys
import os
import time
import threading
import argparse
import re
import uuid
import shutil
import json

from pathlib import Path


def init_patterns_file():
    """
    Check if ~/.safecp.patterns.json exists and if not,
    copy the default patterns file from script_dir/patterns/basic.json
    """

    home_dir = str(Path.home())
    patterns_file = os.path.join(home_dir, ".safecp.patterns.json")

    if not os.path.exists(patterns_file):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        default_patterns_file = os.path.join(script_dir, "patterns", "basic.json")

        if os.path.exists(default_patterns_file):
            os.makedirs(os.path.dirname(patterns_file), exist_ok=True)
            shutil.copy2(default_patterns_file, patterns_file)
        else:
            raise FileNotFoundError(
                f"Default patterns file not found at {default_patterns_file}"
            )

    return patterns_file


def sanitize_sensitive_data(text):
    """
    Replace potentially sensitive data in text with dummy values.

    Args:
        text (str): The input text to sanitize

    Returns:
        str: Sanitized text with sensitive data replaced by placeholders
    """
    replacements = {}

    patterns_file = init_patterns_file()
    with open(patterns_file, "r") as f:
        patterns = json.load(f)

    for pattern_name, pattern_info in patterns.items():
        pattern = pattern_info["pattern"]
        replacement_template = pattern_info["replacement_template"]

        matches = re.finditer(pattern, text)
        for match in matches:
            sensitive_value = match.group(0)

            if sensitive_value not in replacements:
                if "{counter}" in replacement_template:
                    replacement = replacement_template.replace(
                        "{counter}", str(len(replacements) + 1)
                    )
                else:
                    replacement = replacement_template

                replacements[sensitive_value] = replacement

    sanitized_text = text
    for sensitive_value, replacement in replacements.items():
        sanitized_text = sanitized_text.replace(sensitive_value, replacement)

    return sanitized_text


def process_text(text):
    """
    Process the copied text and update the clipboard with the processed content.

    Args:
        text (str): The text copied to the clipboard
    """
    if not text:
        return

    processed = sanitize_sensitive_data(text)

    if sys.platform == "darwin":
        # macOS clipboard update
        from AppKit import NSPasteboard, NSString

        pb = NSPasteboard.generalPasteboard()
        pb.clearContents()
        pb.setString_forType_(
            processed, NSString.stringWithString_("public.utf8-plain-text")
        )
    elif sys.platform == "linux":
        # Linux clipboard update
        import gi

        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk, Gdk

        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(processed, -1)
        clipboard.store()


def setup_macos_monitor():
    from AppKit import NSPasteboard, NSStringPboardType
    import objc
    from Foundation import NSObject, NSString

    class ClipboardWatcher(NSObject):
        def init(self):
            self = objc.super(ClipboardWatcher, self).init()
            self.last_change = ""
            self.clipboard = NSPasteboard.generalPasteboard()
            self.change_count = self.clipboard.changeCount()
            return self

        def poll_clipboard(self):
            change_count = self.clipboard.changeCount()
            if change_count != self.change_count:
                self.change_count = change_count
                if self.clipboard.stringForType_(NSStringPboardType):
                    text = self.clipboard.stringForType_(NSStringPboardType)
                    if text != self.last_change:
                        self.last_change = text
                        process_text(text)

    watcher = ClipboardWatcher.alloc().init()

    print("Starting safecp...")
    # start the monitoring loop
    while True:
        watcher.poll_clipboard()
        time.sleep(0.1)


def setup_linux_monitor():
    import gi

    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk, Gdk, GLib

    clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
    previous_text = ""

    def check_clipboard():
        nonlocal previous_text
        text = clipboard.wait_for_text()
        if text and text != previous_text:
            previous_text = text
            process_text(text)
        return True

    print("Starting safecp...")
    # set up clipboard monitoring interval
    GLib.timeout_add(100, check_clipboard)
    Gtk.main()


def main():
    if sys.platform == "darwin":
        platform = "macos"
    elif sys.platform == "linux":
        platform = "linux"
    else:
        print(f"Unsupported platform: {sys.platform}")
        sys.exit(1)

    if platform == "macos":
        setup_macos_monitor()
    elif platform == "linux":
        setup_linux_monitor()


if __name__ == "__main__":
    main()
