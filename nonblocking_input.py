"""
Non-blocking input module for cross-platform key detection
Works on Windows and Linux without external dependencies
"""

import sys
import threading
import time

class NonBlockingInput:
    def __init__(self):
        print("running non blocker")
        self.key_pressed = None
        self.running = True
        self.input_thread = None

        # Platform-specific imports
        if sys.platform == 'win32':
            try:
                import msvcrt
                self.msvcrt = msvcrt
                self.is_windows = True
            except ImportError:
                self.is_windows = False
        else:
            try:
                import tty
                import termios
                import select
                self.tty = tty
                self.termios = termios
                self.select = select
                self.is_windows = False
                self.old_settings = None
            except ImportError:
                raise ImportError("Required modules not available on this platform")

    def start_listening(self):
        """Start the key listening thread"""
        if self.input_thread and self.input_thread.is_alive():
            return  # Already running

        self.running = True
        if self.is_windows:
            self.input_thread = threading.Thread(target=self._windows_listener, daemon=True)
        else:
            self.input_thread = threading.Thread(target=self._unix_listener, daemon=True)

        self.input_thread.start()

    def _windows_listener(self):
        """Windows-specific key listener"""
        while self.running:
            if self.msvcrt.kbhit():
                key = self.msvcrt.getch()
                try:
                    # Try to decode as UTF-8
                    self.key_pressed = key.decode('utf-8')
                except UnicodeDecodeError:
                    # Handle special keys
                    self.key_pressed = f"special_{ord(key)}"
            time.sleep(0.01)

    def _unix_listener(self):
        """Unix/Linux-specific key listener"""
        import sys
        import os

        fd = sys.stdin.fileno()

        # Check if stdin is a terminal
        if not os.isatty(fd):
            print("stdin is not a tty. Listener will not run.")
            return

        try:
            self.old_settings = self.termios.tcgetattr(fd)
        except self.termios.error as e:
            print(f"Error getting terminal attributes: {e}")
            return

        try:
            self.tty.setraw(fd)

            while self.running:
                if self.select.select([sys.stdin], [], [], 0.01) == ([sys.stdin], [], []):
                    key = sys.stdin.read(1)
                    self.key_pressed = key
                time.sleep(0.01)

        finally:
            # Restore terminal settings if they were saved
            if hasattr(self, 'old_settings') and self.old_settings:
                self.termios.tcsetattr(fd, self.termios.TCSADRAIN, self.old_settings)


    def get_key(self):
        """Get the last pressed key and clear it"""
        key = self.key_pressed
        self.key_pressed = None
        return key

    def has_key(self):
        """Check if a key has been pressed"""
        return self.key_pressed is not None

    def stop(self):
        """Stop the key listener"""
        self.running = False

        # Restore terminal on Unix systems
        if not self.is_windows and self.old_settings:
            fd = sys.stdin.fileno()
            self.termios.tcsetattr(fd, self.termios.TCSADRAIN, self.old_settings)

    def __del__(self):
        """Destructor to ensure cleanup"""
        self.stop()
