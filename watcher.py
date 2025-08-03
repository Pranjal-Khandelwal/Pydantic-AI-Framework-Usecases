from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import os

class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return
        print(f"🔄 Modified: {event.src_path}")

    def on_created(self, event):
        print(f"📄 Created: {event.src_path}")

if __name__ == "__main__":
    path = "."  # Watch current directory
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path=path, recursive=True)
    observer.start()
    print(f"👀 Watching directory: {os.path.abspath(path)}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
