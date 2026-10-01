import sys
import io
import atexit
import traceback

class stderrInMemory:
    def __init__(self, log_filepath):
        self.log_filepath = log_filepath
        self.original_stderr = sys.stderr
        self.buffer = io.StringIO()
        
        sys.stderr = self.buffer
        
        atexit.register(self.save)
        
        self.original_excepthook = sys.excepthook
        sys.excepthook = self._crash_handler

    def _crash_handler(self, exc_type, exc_value, exc_tb):
        #Catch unhandled exceptions, write to RAM, trigger  save

        traceback.print_exception(exc_type, exc_value, exc_tb, file=self.buffer)

        self.save()
        


    def save(self):
        #Write the RAM buffer to disk, but only if there are actual errors
        
        atexit.unregister(self.save)
        
        content = self.buffer.getvalue()
        
        if content.strip():
            with open(self.log_filepath, 'a') as f:
                f.write(content)
        
        # Cleanup: Restore normal stderr and close the buffer
        sys.stderr = self.original_stderr
        self.buffer.close()

