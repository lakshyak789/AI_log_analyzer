import os
import time
import threading
from core import monitor

def test_monitoring(tmp_path):
    log_file = tmp_path / "test.log"
    log_file.write_text("Initial log line\n")
    
    test_config = {
        'monitoring': {'log_file': str(log_file)}
    }

    detected_lines = []
    def callback(line):
        detected_lines.append(line.strip())

    # Run monitor in a separate thread so we can write to the file
    monitor_thread = threading.Thread(target=monitor.start_monitoring, args=(test_config, callback))
    monitor_thread.daemon = True # Ensure it kills when main thread exits
    monitor_thread.start()

    # Give it a moment to start
    time.sleep(1)

    # Append to the file
    with open(log_file, "a") as f:
        f.write("New Error Line\n")

    # Wait for detection (Increased to account for buffer delay)
    time.sleep(2)

    # We can't easily stop the infinite loop in monitor.start_monitoring without refactoring it to be stoppable.
    # However, for this simple test extraction, we verify if logic works.
    # Note: In a real test suite, you'd refactor monitor to have a stop event.

    # Actually, a better test for the *class* LogMonitor is:
    # Set a very short buffer delay for testing
    event_handler = monitor.LogMonitor(str(log_file), callback, buffer_delay=0.1)

    # Simulate a file modification event manually to test logic without waiting on FS events
    class MockEvent:
        src_path = str(log_file)

    # Write new line
    with open(log_file, "a") as f:
        f.write("Manual Trigger Line\n")

    event_handler.on_modified(MockEvent())
    
    # Wait for buffer to flush
    time.sleep(0.5)

    assert "Manual Trigger Line" in detected_lines
