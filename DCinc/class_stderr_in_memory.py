import sys
import io
import atexit
import traceback

class stderrInMemory:
    def __init__(self, log_filepath):
        self.log_filepath = log_filepath
        self.original_stderr = sys.stderr
        self.buffer = io.StringIO()
        
        # 1. Redirect standard error to our RAM buffer
        sys.stderr = self.buffer

        # 2. Register the save function to run on normal program exit
        atexit.register(self.save)

        # 3. Override the default exception hook to catch program crashes
        self.original_excepthook = sys.excepthook
        sys.excepthook = self._crash_handler

    def _crash_handler(self, exc_type, exc_value, exc_tb):
        """Catches unhandled exceptions, writes them to RAM, and triggers the save."""
        # Write the traceback into our memory buffer
        traceback.print_exception(exc_type, exc_value, exc_tb, file=self.buffer)
        
        # Save to disk immediately since the program is breaking
        self.save()
        
        # Optional: If you still want the crash to print to the console, uncomment the next line
        # self.original_excepthook(exc_type, exc_value, exc_tb)

    def save(self):
        """Writes the RAM buffer to disk, but only if there are actual errors."""
        # Unregister from atexit so we don't accidentally save twice if called manually
        atexit.unregister(self.save)
        
        content = self.buffer.getvalue()
        
        # Only create/write to the file if there is actually an error recorded
        if content.strip():
            with open(self.log_filepath, 'a') as f:
                f.write(content)
        
        # Cleanup: Restore normal stderr and close the buffer
        sys.stderr = self.original_stderr
        self.buffer.close()

# ==========================================
# Example Usage
# ==========================================

"""
if __name__ == "__main__":
    # Initialize the class at the very start of your program
    error_catcher = memStderr("error_log.txt")

    print("Program is running normally...")
    
    # Simulating a minor error being explicitly sent to stderr
    print("Warning: Something minor happened.", file=sys.stderr)

    # Simulating a fatal crash (unhandled exception)
    # The program will break here, but our class will catch it, save it, and exit safely.
    x = 1 / 0  

    print("This line will never be reached.")
"""