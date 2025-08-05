from datetime import datetime

def print_timestamp_debug_log(text):
    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{current_timestamp}] {text}")