"""
Simplified non-blocking input for debugging
"""

import sys
import threading
import time

class SimpleNonBlockingInput:
    def __init__(self):
        self.key_pressed = None
        self.running = False
        self.thread = None
        self.lock = threading.Lock()

        # Platform detection
        self.is_windows = sys.platform.startswith('win')
        print(f"Platform detected: {'Windows' if self.is_windows else 'Unix/Linux'}")

    def start(self):
        """Start the input thread"""
        if self.running:
            return

        self.running = True
        if self.is_windows:
            self.thread = threading.Thread(target=self._windows_input, daemon=True)
        else:
            self.thread = threading.Thread(target=self._unix_input, daemon=True)

        self.thread.start()
        print("Input thread started")

    def _windows_input(self):
        """Windows input handler"""
        try:
            import msvcrt
            print("Windows input handler active")

            while self.running:
                if msvcrt.kbhit():
                    key = msvcrt.getch().decode('utf-8', errors='ignore')
                    with self.lock:
                        self.key_pressed = key
                    print(f"Windows: Key captured: {repr(key)}")
                time.sleep(0.01)

        except Exception as e:
            print(f"Windows input error: {e}")

    def _unix_input(self):
        """Unix/Linux input handler"""
        try:
            import tty
            import termios
            import select

            print("Unix input handler active")
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)

            try:
                tty.setraw(fd)

                while self.running:
                    if select.select([sys.stdin], [], [], 0.01)[0]:
                        key = sys.stdin.read(1)
                        with self.lock:
                            self.key_pressed = key
                        print(f"Unix: Key captured: {repr(key)}")
                    time.sleep(0.01)

            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        except Exception as e:
            print(f"Unix input error: {e}")

    def get_key(self):
        """Get and clear the last key pressed"""
        with self.lock:
            key = self.key_pressed
            self.key_pressed = None
            return key

    def has_key(self):
        """Check if a key is available"""
        with self.lock:
            return self.key_pressed is not None

    def stop(self):
        """Stop the input handler"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        print("Input handler stopped")


# Simple test function
def test_simple():
    print("=== Simple Test ===")
    input_handler = SimpleNonBlockingInput()
    input_handler.start()

    print("Press 'd' to test, 'q' to quit...")

    try:
        while True:
            if input_handler.has_key():
                key = input_handler.get_key()
                print(f"You pressed: {repr(key)}")

                if key == 'd':
                    print("SUCCESS: D key works!")
                elif key == 'q':
                    print("Quitting...")
                    break

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nInterrupted")
    finally:
        input_handler.stop()

if __name__ == "__main__":
    test_simple()
