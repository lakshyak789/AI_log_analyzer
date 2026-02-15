import os
import time
import threading
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)

class LogMonitor(FileSystemEventHandler):
    def __init__(self, log_path, callback_func, buffer_delay=0.5):
        self.log_path = os.path.abspath(log_path)
        self.callback = callback_func
        self.buffer_delay = buffer_delay
        self.file_handle = None
        self.buffer = []
        self.timer = None
        self._lock = threading.Lock()

        try:
            self.file_handle = open(self.log_path, 'r')
            self.file_handle.seek(0, 2)  # Move to the end of the file
        except Exception as e:
            logger.error(f"Error opening log file: {e}")
            self.file_handle = None

    def on_modified(self, event):
        """Called when the log file is modified."""
        if event.src_path == self.log_path and self.file_handle:
            self.process_new_lines()

    def on_created(self, event):
        """Triggered when log file is deleted and recreated."""
        if event.src_path == self.log_path:
            if self.file_handle:
                self.file_handle.close()
            try:
                self.file_handle = open(self.log_path, 'r')
                self.process_new_lines()
            except Exception as e:
                logger.error(f"Error reopening log file: {e}")
                self.file_handle = None

    def process_new_lines(self):
        """Reads new lines and adds them to a buffer."""
        if not self.file_handle:
            return
        
        new_data = False
        for line in self.file_handle:
            if line.strip():
                with self._lock:
                    self.buffer.append(line)
                    new_data = True
        
        if new_data:
            self._reset_timer()

    def _reset_timer(self):
        """Resets the timer that flushes the buffer."""
        with self._lock:
            if self.timer:
                self.timer.cancel()
            self.timer = threading.Timer(self.buffer_delay, self._flush_buffer)
            self.timer.start()

    def _flush_buffer(self):
        """Joins buffered lines and sends them to the callback."""
        with self._lock:
            if not self.buffer:
                return
            full_entry = "".join(self.buffer)
            self.buffer = []
            self.timer = None
        
        self.callback(full_entry)

def start_monitoring(config, new_line_callback):
    """Starts the watchdog observer to monitor the log file."""
    monitoring_config = config.get("monitoring", {})
    log_file = monitoring_config.get("log_file", "app.log")
    buffer_delay = monitoring_config.get("poll_interval", 0.5)
    
    log_dir = os.path.dirname(os.path.abspath(log_file))
    if not os.path.exists(log_dir): 
        logger.error(f"Error log directory does not exist: {log_dir}")
        return None
    
    event_handler = LogMonitor(log_file, new_line_callback, buffer_delay=buffer_delay)
    observer = Observer()
    observer.schedule(event_handler, log_dir, recursive=False)
    observer.start()
    logger.info(f"Started monitoring log file: {log_file}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logger.info("Stopping log monitor...")
    observer.join()




        