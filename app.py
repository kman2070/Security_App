import sys
import ctypes
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QFrame
)
from PySide6.QtGui import QFont, QTextCursor, QTextCharFormat
from PySide6.QtCore import Qt

# -------------------------------------------------------------
# DIRECT C WINDOWS API HOOKS (Kernel32)
# -------------------------------------------------------------
kernel32 = ctypes.windll.kernel32

PROCESS_TERMINATE = 0x0001
FALSE = 0
SW_HIDE = 0
STARTF_USESHOWWINDOW = 1

class STARTUPINFO(ctypes.Structure):
    _fields_ = [
        ("cb", ctypes.c_ulong), ("lpReserved", ctypes.c_wchar_p),
        ("lpDesktop", ctypes.c_wchar_p), ("lpTitle", ctypes.c_wchar_p),
        ("dwX", ctypes.c_ulong), ("dwY", ctypes.c_ulong),
        ("dwXCountChars", ctypes.c_ulong), ("dwYCountChars", ctypes.c_ulong),
        ("dwFillAttribute", ctypes.c_ulong), ("dwFlags", ctypes.c_ulong),
        ("wShowWindow", ctypes.c_ushort), ("cbReserved2", ctypes.c_ushort),
        ("lpReserved2", ctypes.c_char_p), ("hStdInput", ctypes.c_void_p),
        ("hStdOutput", ctypes.c_void_p), ("hStdError", ctypes.c_void_p),
    ]

class PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("hProcess", ctypes.c_void_p), ("hThread", ctypes.c_void_p),
        ("dwProcessId", ctypes.c_ulong), ("dwThreadId", ctypes.c_ulong),
    ]

def launch_target_process(command: str) -> int:
    si = STARTUPINFO()
    si.cb = ctypes.sizeof(STARTUPINFO)
    si.dwFlags = STARTF_USESHOWWINDOW
    si.wShowWindow = SW_HIDE
    pi = PROCESS_INFORMATION()

    success = kernel32.CreateProcessW(
        None, command, None, None, FALSE, 0, None, None, ctypes.byref(si), ctypes.byref(pi)
    )
    if success:
        pid = pi.dwProcessId
        kernel32.CloseHandle(pi.hProcess)
        kernel32.CloseHandle(pi.hThread)
        return pid
    return 0

def kill_target_process(pid: int) -> bool:
    h_process = kernel32.OpenProcess(PROCESS_TERMINATE, FALSE, pid)
    if not h_process:
        return False
    success = kernel32.TerminateProcess(h_process, 1)
    kernel32.CloseHandle(h_process)
    return bool(success)

# -------------------------------------------------------------
# BALANCED MODERN DARK THEME STYLESHEET
# -------------------------------------------------------------
THEME_STYLESHEET = """
QWidget {
    background-color: #12151e;
    color: #e2e8f0;
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
}

QLabel {
    background-color: transparent;
}

QFrame#HeaderCard {
    background-color: #1e2330;
    border: 1px solid #2d3548;
    border-radius: 12px;
}

QLabel#MainTitle {
    font-size: 18px;
    font-weight: 700;
    color: #f8fafc;
    background-color: transparent;
}

QLabel#Subtitle {
    font-size: 13px;
    color: #94a3b8;
    background-color: transparent;
}

QLabel#StatusBadgeSecure {
    font-size: 14px;
    font-weight: 600;
    color: #10b981;
    padding: 6px 14px;
    border-radius: 16px;
    background-color: rgba(16, 185, 129, 0.15);
    border: 1px solid rgba(16, 185, 129, 0.35);
}

QLabel#StatusBadgeThreat {
    font-size: 14px;
    font-weight: 600;
    color: #ef4444;
    padding: 6px 14px;
    border-radius: 16px;
    background-color: rgba(239, 68, 68, 0.15);
    border: 1px solid rgba(239, 68, 68, 0.35);
}

QPushButton#ActionButton {
    background-color: #4f46e5;
    color: #ffffff;
    border: none;
    border-radius: 10px;
    font-size: 15px;
    font-weight: 600;
    padding: 12px 20px;
}

QPushButton#ActionButton:hover {
    background-color: #6366f1;
}

QPushButton#ActionButton:pressed {
    background-color: #3730a3;
}

QPushButton#ZoomButton {
    background-color: #2a3142;
    color: #cbd5e1;
    border: 1px solid #3b455a;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 600;
    padding: 5px 12px;
}

QPushButton#ZoomButton:hover {
    background-color: #3b455a;
    color: #ffffff;
}

QTextEdit#ConsoleLog {
    background-color: #0b0d13;
    color: #38bdf8;
    border: 1px solid #232936;
    border-radius: 10px;
    font-family: 'Consolas', 'Cascadia Code', monospace;
    padding: 14px;
}

QScrollBar:vertical {
    background: transparent;
    width: 8px;
    margin: 4px;
}

QScrollBar::handle:vertical {
    background: #334155;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #475569;
}
"""

# -------------------------------------------------------------
# MAIN APPLICATION GUI
# -------------------------------------------------------------
class SecurityDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sentinel Safeguard // Enterprise Defense Node")
        self.resize(720, 520)
        self.setStyleSheet(THEME_STYLESHEET)

        self.current_font_size = 15  # Base font size (pt)
        self.base_font_size = 15     # Baseline for 100%

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # Header Card
        header = QFrame()
        header.setObjectName("HeaderCard")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(18, 16, 18, 16)

        # Title & Subtitle
        title_box = QVBoxLayout()
        title_box.setSpacing(3)
        title = QLabel("System Defense Node")
        title.setObjectName("MainTitle")
        subtitle = QLabel("Local Air-Gapped Threat Watcher & Remediator")
        subtitle.setObjectName("Subtitle")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)

        header_layout.addLayout(title_box)
        header_layout.addStretch()

        # Status Badge
        self.status = QLabel("● SECURE")
        self.status.setObjectName("StatusBadgeSecure")
        header_layout.addWidget(self.status)

        main_layout.addWidget(header)

        # Controls Toolbar (Simulation button + Zoom Controls)
        controls_layout = QHBoxLayout()

        self.btn = QPushButton("⚡ Run Live Defense Simulation", self)
        self.btn.setObjectName("ActionButton")
        self.btn.clicked.connect(self.run_simulation)
        controls_layout.addWidget(self.btn)

        controls_layout.addStretch()

        # Zoom Controls
        zoom_label = QLabel("Font Size:")
        zoom_label.setStyleSheet("font-size: 13px; color: #94a3b8;")
        controls_layout.addWidget(zoom_label)

        btn_zoom_out = QPushButton("A -", self)
        btn_zoom_out.setObjectName("ZoomButton")
        btn_zoom_out.setToolTip("Decrease Font Size")
        btn_zoom_out.clicked.connect(self.zoom_out)
        controls_layout.addWidget(btn_zoom_out)

        self.lbl_zoom_level = QLabel("100%")
        self.lbl_zoom_level.setStyleSheet("font-size: 13px; font-weight: bold; color: #818cf8; min-width: 45px;")
        self.lbl_zoom_level.setAlignment(Qt.AlignCenter)
        controls_layout.addWidget(self.lbl_zoom_level)

        btn_zoom_in = QPushButton("A +", self)
        btn_zoom_in.setObjectName("ZoomButton")
        btn_zoom_in.setToolTip("Increase Font Size")
        btn_zoom_in.clicked.connect(self.zoom_in)
        controls_layout.addWidget(btn_zoom_in)

        main_layout.addLayout(controls_layout)

        # Console Activity View
        self.logs = QTextEdit(self)
        self.logs.setObjectName("ConsoleLog")
        self.logs.setReadOnly(True)
        
        # Set initial font programmatically
        init_font = QFont("Consolas", self.current_font_size)
        self.logs.setFont(init_font)
        self.logs.document().setDefaultFont(init_font)

        self.append_log("<span style='color:#a78bfa;'>[SYSTEM]</span> Kernel telemetry stream initialized.")
        self.append_log("<span style='color:#a78bfa;'>[SYSTEM]</span> Standby status active. Awaiting threat emulation trigger...\n")

        main_layout.addWidget(self.logs)

        self.setLayout(main_layout)

    def append_log(self, html_text: str):
        """Appends HTML formatted text to log while auto-scrolling to bottom."""
        self.logs.append(html_text)
        self.logs.moveCursor(QTextCursor.End)

    def zoom_in(self):
        if self.current_font_size < 28:
            self.current_font_size += 2
            self.apply_font_size()

    def zoom_out(self):
        if self.current_font_size > 9:
            self.current_font_size -= 2
            self.apply_font_size()

    def apply_font_size(self):
        # Update default font for document & widget
        font = QFont("Consolas", self.current_font_size)
        self.logs.setFont(font)
        self.logs.document().setDefaultFont(font)

        # Update font size on existing document content without overriding colors
        cursor = self.logs.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        fmt = QTextCharFormat()
        fmt.setFontPointSize(self.current_font_size)
        cursor.mergeCharFormat(fmt)

        # Return cursor to bottom
        self.logs.moveCursor(QTextCursor.End)

        # Update percentage label
        percentage = int((self.current_font_size / self.base_font_size) * 100)
        self.lbl_zoom_level.setText(f"{percentage}%")

    def run_simulation(self):
        self.append_log("<span style='color:#f43f5e; font-weight:bold;'>• [RED TEAM]</span> Dispatching atomic test vector (notepad.exe)...")
        pid = launch_target_process("notepad.exe")

        if pid > 0:
            self.status.setText("● THREAT DETECTED")
            self.status.setObjectName("StatusBadgeThreat")
            self.status.setStyle(self.status.style())

            self.append_log(f"  <span style='color:#fb7185;'>└─ Process running under PID:</span> <b style='color:#fbbf24;'>{pid}</b>")

            # Blue Team Auto-Remediation
            self.append_log("<span style='color:#38bdf8; font-weight:bold;'>• [BLUE TEAM]</span> Intercepting threat process via Win32 C APIs...")
            success = kill_target_process(pid)

            if success:
                self.append_log(f"  <span style='color:#34d399;'>└─ Process {pid} isolated &amp; terminated cleanly.</span>")
                self.append_log("<span style='color:#10b981; font-weight:bold;'>• [SYSTEM]</span> System state verified. Host fully restored.\n")

                self.status.setText("● SECURE")
                self.status.setObjectName("StatusBadgeSecure")
                self.status.setStyle(self.status.style())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SecurityDashboard()
    window.show()
    sys.exit(app.exec())
    