#!/usr/bin/env python3
"""
AURA Premium UI - MVP Version
Modern glassmorphism design with voice waveform visualization
"""

import sys
import math
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QLineEdit, QSystemTrayIcon,
    QMenu, QAction, QFrame, QGraphicsOpacityEffect, QSlider,
    QComboBox, QDialog, QDialogButtonBox
)
from PyQt5.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, 
    QPoint, QSize, pyqtSignal, QThread
)
from PyQt5.QtGui import (
    QIcon, QPalette, QColor, QLinearGradient, QPainter,
    QFont, QPen, QBrush, QPainterPath
)
import os
import logging
from typing import Optional

# Import AURA components
from aura_core import AuraCore
from credit_manager import CreditManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VoiceWaveformWidget(QWidget):
    """Animated voice waveform visualization"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 80)
        self.setMaximumSize(400, 80)
        
        self.amplitude = 0.0
        self.phase = 0.0
        self.is_listening = False
        
        # Animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_wave)
        self.timer.start(50)  # 20 FPS
        
    def start_listening(self):
        """Start waveform animation"""
        self.is_listening = True
        
    def stop_listening(self):
        """Stop waveform animation"""
        self.is_listening = False
        self.amplitude = 0.0
        
    def update_wave(self):
        """Update wave phase"""
        if self.is_listening:
            self.phase += 0.2
            self.amplitude = min(1.0, self.amplitude + 0.1)
        else:
            self.amplitude = max(0.0, self.amplitude - 0.05)
        self.update()
        
    def paintEvent(self, event):
        """Draw animated waveform"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        center_y = height / 2
        
        # Draw multiple sine waves
        for i in range(3):
            pen = QPen(QColor(0, 200, 255, 100 - i * 30))
            pen.setWidth(2)
            painter.setPen(pen)
            
            path = QPainterPath()
            phase_offset = self.phase + i * 0.5
            
            for x in range(width):
                wave_height = math.sin((x / 20.0) + phase_offset) * 20 * self.amplitude
                wave_height += math.sin((x / 10.0) + phase_offset * 2) * 10 * self.amplitude
                y = center_y + wave_height * (1 + i * 0.3)
                
                if x == 0:
                    path.moveTo(x, y)
                else:
                    path.lineTo(x, y)
                    
            painter.drawPath(path)


class CreditBalanceWidget(QWidget):
    """Credit balance display with progress bar"""
    
    def __init__(self, credit_manager, parent=None):
        super().__init__(parent)
        self.credit_manager = credit_manager
        self.setup_ui()
        
    def setup_ui(self):
        """Setup credit display UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Balance label
        self.balance_label = QLabel()
        self.balance_label.setStyleSheet("""
            QLabel {
                color: #00D9FF;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        
        # Status label
        self.status_label = QLabel()
        self.status_label.setStyleSheet("""
            QLabel {
                color: #88CCFF;
                font-size: 11px;
            }
        """)
        
        layout.addWidget(self.balance_label)
        layout.addWidget(self.status_label)
        
        self.update_display()
        
    def update_display(self):
        """Update credit balance display"""
        balance = self.credit_manager.get_balance()
        has_unlimited = self.credit_manager.has_unlimited_subscription()
        
        if has_unlimited:
            self.balance_label.setText("∞ Unlimited")
            self.status_label.setText("Pro Subscription Active")
        elif balance > 0:
            self.balance_label.setText(f"💎 {balance:,} credits")
            if balance < 100:
                self.status_label.setText("⚠️ Low balance")
                self.status_label.setStyleSheet("QLabel { color: #FFB000; font-size: 11px; }")
            else:
                self.status_label.setText("Balance healthy")
                self.status_label.setStyleSheet("QLabel { color: #88CCFF; font-size: 11px; }")
        else:
            self.balance_label.setText("💎 0 credits")
            self.status_label.setText("⚠️ Buy credits to use AI features")
            self.status_label.setStyleSheet("QLabel { color: #FF6B6B; font-size: 11px; }")


class BuyCreditDialog(QDialog):
    """Dialog for purchasing credits"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Buy Credits")
        self.setModal(True)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup purchase dialog UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Choose Your Credit Package")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #00D9FF;")
        layout.addWidget(title)
        
        # Packages
        packages = [
            ("Starter Pack", "1,000 credits", "$4.99", "starter"),
            ("Popular Pack", "2,500 credits", "$9.99", "popular"),
            ("Power Pack", "6,000 credits", "$19.99", "power"),
        ]
        
        self.selected_package = None
        
        for name, credits, price, package_id in packages:
            btn = QPushButton(f"{name}\n{credits}\n{price}")
            btn.setMinimumHeight(80)
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(0, 217, 255, 0.1);
                    border: 2px solid #00D9FF;
                    border-radius: 10px;
                    color: white;
                    font-size: 14px;
                    padding: 10px;
                }
                QPushButton:hover {
                    background: rgba(0, 217, 255, 0.2);
                    border: 2px solid #00FFCC;
                }
            """)
            btn.clicked.connect(lambda checked, pid=package_id: self.select_package(pid))
            layout.addWidget(btn)
        
        # Unlimited option
        unlimited_btn = QPushButton("⚡ Unlimited Plan\nUnlimited AI calls\n$9.99/month")
        unlimited_btn.setMinimumHeight(80)
        unlimited_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255, 100, 100, 0.3),
                    stop:1 rgba(0, 217, 255, 0.3));
                border: 2px solid #FFD700;
                border-radius: 10px;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255, 100, 100, 0.5),
                    stop:1 rgba(0, 217, 255, 0.5));
            }
        """)
        unlimited_btn.clicked.connect(lambda: self.select_package("unlimited"))
        layout.addWidget(unlimited_btn)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Cancel)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def select_package(self, package_id):
        """Select a package and proceed to checkout"""
        self.selected_package = package_id
        logger.info(f"Selected package: {package_id}")
        # TODO: Integrate with payment provider
        self.accept()


class AuraPremiumUI(QMainWindow):
    """Main premium UI window for AURA"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize core components
        self.aura_core = AuraCore(user_name="Sir")
        self.credit_manager = CreditManager()
        
        self.is_compact = False
        self.is_listening = False
        
        self.setup_window()
        self.setup_ui()
        self.setup_system_tray()
        self.setup_animations()
        
        # Auto-greet on startup
        QTimer.singleShot(1000, self.aura_core.greet)
        
    def setup_window(self):
        """Setup main window properties"""
        self.setWindowTitle("AURA - Advanced AI Assistant")
        self.setGeometry(100, 100, 800, 600)
        
        # Frameless window with rounded corners
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
    def setup_ui(self):
        """Setup main UI components"""
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Main layout
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Container with glassmorphism effect
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(20, 30, 48, 0.95),
                    stop:1 rgba(36, 59, 85, 0.95));
                border: 2px solid rgba(0, 217, 255, 0.3);
                border-radius: 20px;
            }
        """)
        
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setSpacing(15)
        
        # Header
        header = self.create_header()
        container_layout.addWidget(header)
        
        # Voice waveform
        self.waveform = VoiceWaveformWidget()
        container_layout.addWidget(self.waveform, alignment=Qt.AlignCenter)
        
        # Chat area
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setStyleSheet("""
            QTextEdit {
                background: rgba(10, 20, 35, 0.8);
                border: 1px solid rgba(0, 217, 255, 0.2);
                border-radius: 10px;
                color: #E0E0E0;
                font-size: 13px;
                padding: 10px;
            }
        """)
        container_layout.addWidget(self.chat_area, stretch=1)
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type a command or press Voice button...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background: rgba(10, 20, 35, 0.8);
                border: 2px solid rgba(0, 217, 255, 0.3);
                border-radius: 10px;
                color: white;
                font-size: 14px;
                padding: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #00D9FF;
            }
        """)
        self.input_field.returnPressed.connect(self.send_command)
        
        self.voice_btn = QPushButton("🎤 Voice")
        self.voice_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00D9FF,
                    stop:1 #00FFCC);
                border: none;
                border-radius: 10px;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 24px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00FFCC,
                    stop:1 #00D9FF);
            }
            QPushButton:pressed {
                background: #0088AA;
            }
        """)
        self.voice_btn.clicked.connect(self.toggle_voice)
        
        self.send_btn = QPushButton("Send")
        self.send_btn.setStyleSheet("""
            QPushButton {
                background: rgba(0, 217, 255, 0.2);
                border: 2px solid #00D9FF;
                border-radius: 10px;
                color: white;
                font-size: 14px;
                padding: 12px 20px;
            }
            QPushButton:hover {
                background: rgba(0, 217, 255, 0.3);
            }
        """)
        self.send_btn.clicked.connect(self.send_command)
        
        input_layout.addWidget(self.input_field, stretch=1)
        input_layout.addWidget(self.voice_btn)
        input_layout.addWidget(self.send_btn)
        
        container_layout.addLayout(input_layout)
        
        # Status bar
        status_layout = QHBoxLayout()
        
        # Credit balance
        self.credit_widget = CreditBalanceWidget(self.credit_manager)
        status_layout.addWidget(self.credit_widget)
        
        status_layout.addStretch()
        
        # Buy credits button
        buy_btn = QPushButton("💎 Buy Credits")
        buy_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 215, 0, 0.2);
                border: 1px solid #FFD700;
                border-radius: 8px;
                color: #FFD700;
                font-size: 12px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background: rgba(255, 215, 0, 0.3);
            }
        """)
        buy_btn.clicked.connect(self.show_buy_credits_dialog)
        status_layout.addWidget(buy_btn)
        
        container_layout.addLayout(status_layout)
        
        main_layout.addWidget(container)
        
    def create_header(self):
        """Create header with logo and controls"""
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Logo and title
        title = QLabel("⚡ AURA")
        title.setStyleSheet("""
            QLabel {
                color: #00D9FF;
                font-size: 28px;
                font-weight: bold;
            }
        """)
        layout.addWidget(title)
        
        subtitle = QLabel("Advanced AI Assistant")
        subtitle.setStyleSheet("""
            QLabel {
                color: #88CCFF;
                font-size: 12px;
            }
        """)
        layout.addWidget(subtitle)
        
        layout.addStretch()
        
        # Window controls
        minimize_btn = QPushButton("─")
        minimize_btn.setFixedSize(30, 30)
        minimize_btn.clicked.connect(self.showMinimized)
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.clicked.connect(self.close)
        
        for btn in [minimize_btn, close_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255, 255, 255, 0.1);
                    border: none;
                    border-radius: 15px;
                    color: white;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background: rgba(255, 255, 255, 0.2);
                }
            """)
        
        layout.addWidget(minimize_btn)
        layout.addWidget(close_btn)
        
        return header
        
    def setup_system_tray(self):
        """Setup system tray icon"""
        self.tray_icon = QSystemTrayIcon(self)
        
        # Use existing icon or create simple one
        icon_path = "jarvis_icon.ico"
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            # Create a simple icon placeholder
            self.tray_icon.setIcon(self.style().standardIcon(self.style().SP_ComputerIcon))
        
        # Tray menu
        tray_menu = QMenu()
        show_action = QAction("Show AURA", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # Tray icon click
        self.tray_icon.activated.connect(self.tray_icon_clicked)
        
    def tray_icon_clicked(self, reason):
        """Handle tray icon clicks"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()
            self.activateWindow()
            
    def setup_animations(self):
        """Setup UI animations"""
        # Fade-in animation
        self.fade_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.fade_effect)
        
        self.fade_animation = QPropertyAnimation(self.fade_effect, b"opacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.fade_animation.start()
        
    def toggle_voice(self):
        """Toggle voice input"""
        if self.is_listening:
            self.stop_voice_input()
        else:
            self.start_voice_input()
            
    def start_voice_input(self):
        """Start listening for voice commands"""
        self.is_listening = True
        self.voice_btn.setText("🔴 Listening...")
        self.voice_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FF6B6B,
                    stop:1 #FF8E53);
                border: none;
                border-radius: 10px;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 24px;
            }
        """)
        self.waveform.start_listening()
        self.add_message("SYSTEM", "Listening... Speak now.", "#00D9FF")
        
        # TODO: Integrate with voice_input.py
        # For now, simulate after 3 seconds
        QTimer.singleShot(3000, self.stop_voice_input)
        
    def stop_voice_input(self):
        """Stop listening"""
        self.is_listening = False
        self.voice_btn.setText("🎤 Voice")
        self.voice_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00D9FF,
                    stop:1 #00FFCC);
                border: none;
                border-radius: 10px;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 24px;
            }
        """)
        self.waveform.stop_listening()
        
    def send_command(self):
        """Send text command"""
        command = self.input_field.text().strip()
        if not command:
            return
            
        self.input_field.clear()
        self.add_message("YOU", command, "#00FFCC")
        
        # Process command
        self.process_command(command)
        
    def process_command(self, command: str):
        """Process user command through AURA core"""
        try:
            # Check if command needs credits
            route_result = self.aura_core.router.route(command)
            
            if route_result.route_type == "local":
                # Free local command
                response = self.aura_core.process_command(command)
            else:
                # Needs credits
                if not self.credit_manager.check_credits():
                    self.add_message("AURA", "⚠️ You need credits for AI-powered features. Click 'Buy Credits' to continue.", "#FFB000")
                    return
                    
                # Deduct credits and process
                self.credit_manager.deduct_credits(1)
                response = self.aura_core.process_command(command)
                self.credit_widget.update_display()
                
            self.add_message("AURA", response, "#00D9FF")
            
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            self.add_message("AURA", f"❌ Error: {str(e)}", "#FF6B6B")
            
    def add_message(self, sender: str, message: str, color: str):
        """Add message to chat area"""
        formatted = f'<p><b style="color: {color};">{sender}:</b> {message}</p>'
        self.chat_area.append(formatted)
        
    def show_buy_credits_dialog(self):
        """Show credit purchase dialog"""
        dialog = BuyCreditDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            # TODO: Process payment
            logger.info(f"Purchasing: {dialog.selected_package}")
            self.add_message("SYSTEM", f"Opening payment for {dialog.selected_package} package...", "#FFD700")
            
    def mousePressEvent(self, event):
        """Enable window dragging"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event):
        """Handle window dragging"""
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()


def main():
    """Launch AURA Premium UI"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Dark palette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(20, 30, 48))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(10, 20, 35))
    palette.setColor(QPalette.AlternateBase, QColor(20, 30, 48))
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(36, 59, 85))
    palette.setColor(QPalette.ButtonText, Qt.white)
    app.setPalette(palette)
    
    window = AuraPremiumUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
