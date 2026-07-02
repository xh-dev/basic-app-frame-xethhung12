from blessed import Terminal

class CustTerminal:
    def __init__(self):
        term = Terminal()
        self.term = term
        self.width=term.width
        self.height=term.height

import time
from blessed import Terminal

class SynchronousTerminal:
    def __init__(self):
        self.term = Terminal()
        self.logs = []
        
        # Section mapping:
        # Row 0: Large Banner Title
        # Row 1: Current Execution status
        # Row 2: Fixed horizontal divider
        # Row 3+: Rolling logs
        self.log_start_row = 3
        
        # Clear screen once at initialization
        print(self.term.clear, end='', flush=True)

    def draw_layout(self, title_text, execution_text):
        """Draws the single-line heavy header banner and execution status."""
        t = self.term
        
        # 1. Row 0: Heavy Title Bar (Bold + Inverted Background)
        # Center-align the text and pad it to match full screen width
        centered_title = f" {title_text} ".center(t.width)
        # t.bold_reverse applies both bold text and swaps foreground/background colors
        print(t.move_xy(0, 0) + t.bold_reverse(centered_title), end='')
        
        # 2. Row 1: Current Execution Status
        safe_exec = f"Status: {execution_text}"[:t.width]
        print(t.move_xy(0, 1) + t.clear_eol + t.cyan(safe_exec), end='')
        
        # 3. Row 2: Fixed Horizontal Divider
        print(t.move_xy(0, 2) + t.clear_eol + t.magenta("─" * t.width), end='', flush=True)

    def add_log(self, text):
        """Appends a log and slides the bottom zone down synchronously."""
        t = self.term
        available_rows = t.height - self.log_start_row
        
        self.logs.append(text)
        
        if len(self.logs) > available_rows:
            self.logs = self.logs[-available_rows:]
            
        # Redraw rolling logs
        for i, log_msg in enumerate(self.logs):
            target_row = self.log_start_row + i
            safe_log = log_msg[:t.width]
            print(t.move_xy(0, target_row) + t.clear_eol + safe_log, end='', flush=True)      
    
ui = SynchronousTerminal()
title = "LEDGER SYNCHRONIZATION ENGINE v2.0"

for i in range(1, 21):
    ui.draw_layout(title, f"Indexing block sequence ({i}/20)...")
    
    time.sleep(0.2) # Business logic simulation
    
    ui.add_log(f"[{time.strftime('%H:%M:%S')}] OK: Successfully committed segment {i}")
    
ui.add_log("[SYSTEM]: Verification step cleared. Exiting.")
time.sleep(2)

# ct=CustTerminal()
# term=ct.term()
# print(f"{term.green}hello, {term.red}world. {term.white}done~~~")