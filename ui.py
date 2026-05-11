import sys
import logging
import threading
import time
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem, QTextEdit,
    QHeaderView, QFrame, QSplitter, QStatusBar
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QFont, QColor, QPalette, QTextCursor

from scheduler import SchedulerManager
from audio_manager import AudioManager
from timetable_manager import TimetableManager
from config import Config


class LogHandler(logging.Handler, QObject):
    log_signal = pyqtSignal(str)

    def __init__(self):
        logging.Handler.__init__(self)
        QObject.__init__(self)
        self.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))

    def emit(self, record):
        msg = self.format(record)
        self.log_signal.emit(msg)


class SchedulerThread(threading.Thread):
    def __init__(self, scheduler, timetable_manager, config):
        super().__init__(daemon=True)
        self.scheduler = scheduler
        self.timetable_manager = timetable_manager
        self.config = config
        self.running = False

    def run(self):
        self.running = True
        last_timetable_check = time.time()
        check_interval = self.config.get('timetable_check_interval', 300)
        while self.running:
            try:
                self.scheduler.check_schedule()
                now = time.time()
                if now - last_timetable_check > check_interval:
                    if self.timetable_manager.has_timetable_changed():
                        self.timetable_manager.load_timetable()
                        self.scheduler.load_schedule(self.timetable_manager.get_events())
                    last_timetable_check = now
                time.sleep(1)
            except Exception as e:
                logging.getLogger(__name__).error(f"Scheduler error: {e}")
                time.sleep(5)

    def stop(self):
        self.running = False


class SwiftBellUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.audio_manager = AudioManager(self.config)
        self.timetable_manager = TimetableManager(self.config)
        self.scheduler = SchedulerManager(self.config, self.audio_manager, self.timetable_manager)
        self.scheduler_thread = None
        self.running = False
        self.emergency_active = False

        self._setup_logging()
        self._setup_ui()
        self._setup_timers()
        self._update_status()

    def _setup_logging(self):
        self.log_handler = LogHandler()
        logging.getLogger().addHandler(self.log_handler)
        logging.getLogger().setLevel(logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _setup_ui(self):
        self.setWindowTitle("SwiftBell")
        self.setMinimumSize(800, 600)
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e2e; }
            QLabel { color: #cdd6f4; font-size: 13px; }
            QPushButton {
                background-color: #313244; color: #cdd6f4;
                border: 1px solid #45475a; border-radius: 6px;
                padding: 8px 20px; font-size: 13px; font-weight: bold;
            }
            QPushButton:hover { background-color: #45475a; }
            QPushButton:pressed { background-color: #585b70; }
            QPushButton:disabled { background-color: #181825; color: #585b70; }
            QTableWidget {
                background-color: #1e1e2e; color: #cdd6f4;
                border: 1px solid #313244; border-radius: 4px;
                gridline-color: #313244; font-size: 12px;
            }
            QTableWidget::item { padding: 6px; }
            QHeaderView::section {
                background-color: #181825; color: #a6adc8;
                border: none; padding: 6px; font-weight: bold;
            }
            QTextEdit {
                background-color: #11111b; color: #a6adc8;
                border: 1px solid #313244; border-radius: 4px;
                font-family: 'JetBrains Mono', 'Consolas', monospace;
                font-size: 11px;
            }
            QFrame { border: none; }
        """)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        header = QLabel("SwiftBell — School Bell & Announcement System")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #cba6f7; padding: 4px 0;")
        layout.addWidget(header)

        status_frame = QFrame()
        status_frame.setStyleSheet("QFrame { background-color: #181825; border-radius: 8px; padding: 12px; }")
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(16, 12, 16, 12)

        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet("font-size: 24px; color: #f38ba8;")
        self.status_label = QLabel("STOPPED")
        self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #f38ba8;")
        self.time_label = QLabel()
        self.time_label.setStyleSheet("font-size: 16px; color: #bac2de;")
        self.time_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        status_layout.addWidget(self.status_indicator)
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.time_label)
        layout.addWidget(status_frame)

        btn_frame = QFrame()
        btn_layout = QHBoxLayout(btn_frame)
        btn_layout.setSpacing(10)

        self.start_btn = QPushButton("▶ Start")
        self.start_btn.setStyleSheet(self.start_btn.styleSheet() + "QPushButton { background-color: #a6e3a1; color: #11111b; } QPushButton:hover { background-color: #94e2d5; }")
        self.start_btn.clicked.connect(self._start_system)

        self.stop_btn = QPushButton("■ Stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._stop_system)

        self.test_btn = QPushButton("♫ Test Audio")
        self.test_btn.clicked.connect(self._test_audio)

        self.emergency_btn = QPushButton("🚨 EMERGENCY")
        self.emergency_btn.setStyleSheet(self.emergency_btn.styleSheet() + "QPushButton { background-color: #f38ba8; color: #11111b; font-size: 15px; } QPushButton:hover { background-color: #eba0ac; }")
        self.emergency_btn.clicked.connect(self._emergency)

        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addWidget(self.test_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.emergency_btn)
        layout.addWidget(btn_frame)

        splitter = QSplitter(Qt.Vertical)
        splitter.setHandleWidth(2)

        events_widget = QWidget()
        events_layout = QVBoxLayout(events_widget)
        events_layout.setContentsMargins(0, 0, 0, 0)
        events_label = QLabel("Upcoming Events")
        events_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #89b4fa; padding: 4px 0;")
        events_layout.addWidget(events_label)

        self.events_table = QTableWidget(0, 4)
        self.events_table.setHorizontalHeaderLabels(["Time", "Event", "Day", "Type"])
        self.events_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.events_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.events_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.events_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.events_table.setSelectionMode(QTableWidget.NoSelection)
        self.events_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.events_table.verticalHeader().setVisible(False)
        self.events_table.setAlternatingRowColors(True)
        self.events_table.setStyleSheet(self.events_table.styleSheet() + """
            QTableWidget { alternate-background-color: #181825; }
        """)
        events_layout.addWidget(self.events_table)
        splitter.addWidget(events_widget)

        log_widget = QWidget()
        log_layout = QVBoxLayout(log_widget)
        log_layout.setContentsMargins(0, 0, 0, 0)
        log_label = QLabel("Activity Log")
        log_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #89b4fa; padding: 4px 0;")
        log_layout.addWidget(log_label)

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        log_layout.addWidget(self.log_view)
        splitter.addWidget(log_widget)

        splitter.setSizes([250, 200])
        layout.addWidget(splitter, stretch=1)

        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("QStatusBar { background-color: #11111b; color: #585b70; font-size: 11px; }")
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def _setup_timers(self):
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._update_status)
        self.status_timer.start(2000)

        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self._update_clock)
        self.clock_timer.start(1000)

        self.log_handler.log_signal.connect(self._append_log)

    def _update_clock(self):
        self.time_label.setText(datetime.now().strftime("%H:%M:%S"))

    def _update_status(self):
        if self.running:
            self.status_indicator.setStyleSheet("font-size: 24px; color: #a6e3a1;")
            self.status_label.setText("RUNNING")
            self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #a6e3a1;")
        elif self.emergency_active:
            self.status_indicator.setStyleSheet("font-size: 24px; color: #f38ba8;")
            self.status_label.setText("EMERGENCY")
            self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #f38ba8;")
        else:
            self.status_indicator.setStyleSheet("font-size: 24px; color: #f38ba8;")
            self.status_label.setText("STOPPED")
            self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #f38ba8;")

        self._refresh_events()

    def _refresh_events(self):
        now = datetime.now()
        today = now.strftime("%A").lower()
        all_events = self.timetable_manager.get_events()
        future = []
        for e in all_events:
            day = e.get("day", "everyday").lower()
            if day not in ("everyday", today):
                continue
            try:
                h, m = map(int, e["time"].split(":"))
                et = time.struct_time((2000, 1, 1, h, m, 0, 0, 0, -1))
                future.append(e)
            except:
                pass
        future.sort(key=lambda x: x["time"])

        self.events_table.setRowCount(0)
        for e in future:
            row = self.events_table.rowCount()
            self.events_table.insertRow(row)
            self.events_table.setItem(row, 0, QTableWidgetItem(e["time"]))
            self.events_table.setItem(row, 1, QTableWidgetItem(e["event"]))
            self.events_table.setItem(row, 2, QTableWidgetItem(e.get("day", "Everyday")))
            self.events_table.setItem(row, 3, QTableWidgetItem(e.get("type", "announcement")))

    def _append_log(self, msg):
        self.log_view.append(msg)
        cursor = self.log_view.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_view.setTextCursor(cursor)

    def _start_system(self):
        try:
            self.timetable_manager.load_timetable()
            self.scheduler.load_schedule(self.timetable_manager.get_events())
            self.scheduler_thread = SchedulerThread(
                self.scheduler, self.timetable_manager, self.config
            )
            self.scheduler_thread.start()
            self.running = True
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.logger.info("SwiftBell started")
            self.status_bar.showMessage("System running")
        except Exception as e:
            self.logger.error(f"Failed to start: {e}")

    def _stop_system(self):
        if self.scheduler_thread:
            self.scheduler_thread.stop()
            self.scheduler_thread = None
        self.audio_manager.stop_all()
        self.running = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.logger.info("SwiftBell stopped")
        self.status_bar.showMessage("System stopped")

    def _test_audio(self):
        self.logger.info("Testing audio...")
        self.audio_manager.speak("Audio test. This is a test of the announcement system.")
        self.status_bar.showMessage("Audio test sent")

    def _emergency(self):
        self.logger.warning("EMERGENCY EVACUATION TRIGGERED!")
        self.emergency_active = True
        self._update_status()
        siren = self.config.get('evacuation_siren', 'sounds/evacuation.wav')
        msg = self.config.get('emergency_message',
            "EMERGENCY! Please evacuate the building immediately.")
        self.audio_manager.play_siren_then_speak(siren, msg, repeat_count=3)
        QTimer.singleShot(30000, self._reset_emergency)
        self.status_bar.showMessage("🚨 EMERGENCY EVACUATION ACTIVE")

    def _reset_emergency(self):
        try:
            self.emergency_active = False
            self.logger.info("Emergency evacuation procedure completed")
            self._update_status()
        except RuntimeError:
            pass

    def closeEvent(self, event):
        self._stop_system()
        logging.getLogger().removeHandler(self.log_handler)
        self.log_handler.deleteLater()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = SwiftBellUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
