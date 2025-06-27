from PyQt5.QtWidgets import (QApplication, QWidget, QMainWindow, QLabel, 
                           QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
                           QStackedWidget, QMessageBox, QInputDialog)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
import sys
from datetime import datetime

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Тест Руф'є")
        self.setMinimumSize(800, 600)
        
        # Initialize stacked widget for multiple screens
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Initialize screens
        self.init_welcome_screen()
        self.init_test_screen()
        self.init_result_screen()
        
        # Timer setup
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.time_remaining = 0
        self.current_stage = 0
        
        # Test data
        self.pulse_data = []
        self.name = ""
        self.age = 0

    def init_welcome_screen(self):
        welcome_widget = QWidget()
        layout = QVBoxLayout()
        
        # Welcome title
        title = QLabel("Ласкаво просимо до тесту Руф'є!")
        title.setFont(QFont('Arial', 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Test description
        description = QLabel(
            "Тест Руф'є використовується для оцінки працездатності серця під час фізичного навантаження.\n\n"
            "Процедура тесту:\n"
            "1. Вимірювання пульсу в стані спокою (15 секунд)\n"
            "2. Виконання 30 присідань за 45 секунд\n"
            "3. Вимірювання пульсу відразу після навантаження (15 секунд)\n"
            "4. Вимірювання пульсу після 1 хвилини відпочинку (15 секунд)\n\n"
            "Цей тест допоможе оцінити стан вашої серцево-судинної системи та рівень фізичної підготовки."
        )
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignCenter)
        layout.addWidget(description)
        
        # Start button
        start_button = QPushButton("Почати тест")
        start_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        layout.addWidget(start_button)
        
        welcome_widget.setLayout(layout)
        self.stacked_widget.addWidget(welcome_widget)

    def init_test_screen(self):
        test_widget = QWidget()
        layout = QVBoxLayout()
        
        # Form layout
        form_layout = QVBoxLayout()
        
        # Name input
        name_label = QLabel("ПІБ:")
        self.name_input = QLineEdit()
        form_layout.addWidget(name_label)
        form_layout.addWidget(self.name_input)
        
        # Age input
        age_label = QLabel("Вік:")
        self.age_input = QLineEdit()
        form_layout.addWidget(age_label)
        form_layout.addWidget(self.age_input)
        
        layout.addLayout(form_layout)
        
        # Timer display
        self.timer_label = QLabel("00:00:00")
        self.timer_label.setFont(QFont('Arial', 32, QFont.Bold))
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet("color: black;")
        layout.addWidget(self.timer_label)
        
        # Instruction label
        self.instruction_label = QLabel("Підготуйтеся до вимірювання пульсу")
        self.instruction_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.instruction_label)
        
        # Start test button
        self.start_test_button = QPushButton("Почати вимірювання")
        self.start_test_button.clicked.connect(self.start_test)
        layout.addWidget(self.start_test_button)
        
        test_widget.setLayout(layout)
        self.stacked_widget.addWidget(test_widget)

    def init_result_screen(self):
        result_widget = QWidget()
        layout = QVBoxLayout()
        
        self.result_index_label = QLabel()
        self.result_index_label.setFont(QFont('Arial', 14))
        self.result_index_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.result_index_label)
        
        self.result_interpretation_label = QLabel()
        self.result_interpretation_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.result_interpretation_label)
        
        restart_button = QPushButton("Почати новий тест")
        restart_button.clicked.connect(self.restart_test)
        layout.addWidget(restart_button)
        
        result_widget.setLayout(layout)
        self.stacked_widget.addWidget(result_widget)

    def start_test(self):
        if not self.validate_inputs():
            return
            
        self.name = self.name_input.text()
        self.age = int(self.age_input.text())
        self.pulse_data = []
        self.current_stage = 0
        self.start_next_stage()

    def validate_inputs(self):
        if not self.name_input.text():
            QMessageBox.warning(self, "Помилка", "Будь ласка, введіть ПІБ")
            return False
            
        try:
            age = int(self.age_input.text())
            if age < 7 or age > 100:
                QMessageBox.warning(self, "Помилка", "Будь ласка, введіть коректний вік (7-100)")
                return False
        except ValueError:
            QMessageBox.warning(self, "Помилка", "Будь ласка, введіть коректний вік")
            return False
            
        return True

    def start_next_stage(self):
        stages = [
            ("Виміряйте пульс протягом 15 секунд", 15),
            ("Виконайте 30 присідань", 45),
            ("Виміряйте пульс протягом 15 секунд", 15),
            ("Зачекайте", 60),
            ("Виміряйте пульс протягом 15 секунд", 15)
        ]
        
        if self.current_stage < len(stages):
            instruction, duration = stages[self.current_stage]
            self.instruction_label.setText(instruction)
            self.time_remaining = duration
            self.timer.start(1000)  # Update every second
        else:
            self.show_results()

    def update_timer(self):
        if self.time_remaining > 0:
            self.time_remaining -= 1
            minutes = self.time_remaining // 60
            seconds = self.time_remaining % 60
            self.timer_label.setText(f"{minutes:02d}:{seconds:02d}:00")
        else:
            self.timer.stop()
            if self.current_stage in [0, 2, 4]:  # Pulse measurement stages
                pulse, ok = QInputDialog.getInt(self, "Введіть пульс", 
                                              "Введіть кількість ударів за 15 секунд:",
                                              min=0, max=50)
                if ok:
                    self.pulse_data.append(pulse)
            
            self.current_stage += 1
            self.start_next_stage()

    def calculate_ruffier_index(self):
        if len(self.pulse_data) != 3:
            return None
            
        P1, P2, P3 = [p * 4 for p in self.pulse_data]  # Convert to beats per minute
        return (P1 + P2 + P3 - 200) / 10

    def get_result_interpretation(self, index):
        if self.age < 15:
            ranges = [
                (0, 3, "Відмінно"),
                (4, 6, "Добре"),
                (7, 9, "Задовільно"),
                (10, 14, "Слабко"),
                (15, float('inf'), "Незадовільно")
            ]
        else:
            ranges = [
                (0, 5, "Відмінно"),
                (6, 10, "Добре"),
                (11, 15, "Задовільно"),
                (16, 20, "Слабко"),
                (21, float('inf'), "Незадовільно")
            ]
            
        for min_val, max_val, interpretation in ranges:
            if min_val <= index <= max_val:
                return interpretation
        return "Незадовільно"

    def show_results(self):
        index = self.calculate_ruffier_index()
        if index is not None:
            interpretation = self.get_result_interpretation(index)
            self.result_index_label.setText(f"Індекс Руф'є: {index:.1f}")
            self.result_interpretation_label.setText(f"Оцінка: {interpretation}")
            self.stacked_widget.setCurrentIndex(2)

    def restart_test(self):
        self.name_input.clear()
        self.age_input.clear()
        self.timer_label.setText("00:00:00")
        self.instruction_label.setText("Підготуйтеся до вимірювання пульсу")
        self.pulse_data = []
        self.stacked_widget.setCurrentIndex(0)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())