from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QDialog, QDialogButtonBox
from PyQt6 import QtWidgets, QtCore
import sys
import pyautogui
import numpy as np
import cv2 as cv
import pyscreenshot as ImageGrab
import os 
import shutil

DURATION_INT = 10

def secs_to_minsec(secs: int):
    mins = secs // 60
    secs = secs % 60
    return f'{mins:02}:{secs:02}'

class TimerWidget(QtWidgets.QWidget):
    timeout_signal = QtCore.pyqtSignal()  # Define custom signal

    def __init__(self):
        super().__init__()
        self.time_left_int = DURATION_INT
        self.myTimer = QtCore.QTimer(self)

        self.timerLabel = QtWidgets.QLabel(self)
        self.timerLabel.setText(secs_to_minsec(self.time_left_int))
        self.timerLabel.setStyleSheet("font: 15pt Helvetica")
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.timerLabel)
        self.setLayout(layout)

    def startTimer(self):
        self.time_left_int = DURATION_INT
        self.myTimer.timeout.connect(self.timerTimeout)
        self.myTimer.start(1000)

    def stopTimer(self):
        self.myTimer.stop()
        self.myTimer.timeout.disconnect(self.timerTimeout)

    def timerTimeout(self):
        self.time_left_int -= 1
        self.update_gui()
        if self.time_left_int <= 0:
            self.stopTimer()
            self.hide()
            self.timeout_signal.emit()

    def update_gui(self):
        self.timerLabel.setText(secs_to_minsec(self.time_left_int))

class InputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ввод данных для анализа")

        self.info_label = QLabel("Напишите значения графика", self)
        self.info_label.setStyleSheet("font: 12pt Helvetica")
        self.info_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.x_label = QLabel("X:")
        self.x_input = QLineEdit()

        self.y_label = QLabel("Y:")
        self.y_input = QLineEdit()

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.info_label)
        layout.addWidget(self.x_label)
        layout.addWidget(self.x_input)
        layout.addWidget(self.y_label)
        layout.addWidget(self.y_input)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

        self.setMinimumWidth(300)

    def get_inputs(self):
        return self.x_input.text(), self.y_input.text()

class ErrorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ошибка ввода")
        
        self.error_label = QLabel("Пожалуйста, введите корректные числовые значения для X и Y.", self)
        self.error_label.setStyleSheet("font: 12pt Helvetica")
        self.error_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)

        layout = QVBoxLayout()
        layout.addWidget(self.error_label)
        layout.addWidget(self.ok_button)
        self.setLayout(layout)

class DigitizerGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Оцифровка графика")
        self.setGeometry(300, 250, 450, 200)

        self.main_text = QLabel(self)
        self.main_text.setText("Выберите что следует сделать")
        self.main_text.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.main_text.setStyleSheet("font: 15pt Helvetica")

        self.btn_screenshot = QPushButton(self)
        self.btn_screenshot.setText("Скриншот")
        self.btn_screenshot.setFixedWidth(200)
        self.btn_screenshot.setFixedHeight(100)
        self.btn_screenshot.setStyleSheet("font: 15pt Helvetica")
        self.btn_screenshot.clicked.connect(self.make_screenshot)

        self.btn_select_file = QPushButton(self)
        self.btn_select_file.setText("Выбрать файл")
        self.btn_select_file.setFixedWidth(200)
        self.btn_select_file.setFixedHeight(100)
        self.btn_select_file.setStyleSheet("font: 15pt Helvetica")
        self.btn_select_file.clicked.connect(self.select_file)

        self.btn_view_screenshot = QPushButton(self)
        self.btn_view_screenshot.setText("Просмотреть скриншот")
        button_width = self.width()
        button_height = self.height() // 4
        self.btn_view_screenshot.setFixedSize(button_width, button_height)
        self.btn_view_screenshot.setStyleSheet("font: 15pt Helvetica")
        self.btn_view_screenshot.hide()
        self.btn_view_screenshot.clicked.connect(self.view_screenshot)

        self.btn_analyze_graph = QPushButton(self)
        self.btn_analyze_graph.setText("Анализ графика")
        self.btn_analyze_graph.setFixedSize(button_width, button_height)
        self.btn_analyze_graph.setStyleSheet("font: 15pt Helvetica;")
        self.btn_analyze_graph.hide()
        self.btn_analyze_graph.clicked.connect(self.analyze_graph)

        self.timerWidget = TimerWidget()
        self.timerWidget.hide()
        self.timerWidget.timeout_signal.connect(self.handle_timeout)

        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.layout.addWidget(self.main_text)

        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.addWidget(self.btn_screenshot)
        self.button_layout.addWidget(self.btn_select_file)
        self.layout.addLayout(self.button_layout)

        self.layout.addWidget(self.btn_view_screenshot)
        self.layout.addWidget(self.btn_analyze_graph)
        self.layout.addWidget(self.timerWidget, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

        self.stage = 0
        self.pointX1 = self.pointY1 = 0
        self.pointX2 = self.pointY2 = 0

    def make_screenshot(self):
        self.stage = 0
        self.hide_buttons()
        self.start_timer("Зафиксируйте курсор слева сверху на 10 секунд")

    def hide_buttons(self):
        self.btn_screenshot.hide()
        self.btn_select_file.hide()
        self.btn_analyze_graph.hide()

    choice = False
    filename = ""

    def show_buttons(self):
        self.btn_screenshot.hide()
        self.btn_select_file.hide()
        if self.choice == False:
            self.btn_view_screenshot.show()
            self.btn_analyze_graph.show()
        else:
            self.btn_analyze_graph.show()

    def start_timer(self, message):
        self.main_text.setText(message)
        self.timerWidget.show()
        self.timerWidget.startTimer()

    def handle_timeout(self):
        if self.stage == 0:
            self.pointX1, self.pointY1 = pyautogui.position()
            self.stage = 1
            self.start_timer("Зафиксируйте курсор справа снизу на 10 секунд")
        elif self.stage == 1:
            self.pointX2, self.pointY2 = pyautogui.position()
            self.capture_screenshot()

    def capture_screenshot(self):
        screen = np.array(ImageGrab.grab(bbox=(self.pointX1, self.pointY1, self.pointX2, self.pointY2)))
        self.filename = "screenshot.png"
        cv.imwrite(self.filename, cv.cvtColor(screen, cv.COLOR_BGR2RGB))
        
        # Проверяем, существует ли файл screenshot.png
        if os.path.exists(self.filename):
            self.main_text.setText("Скриншот сохранен!")
        else:
            self.main_text.setText("Ошибка: скриншот не сохранен")
        
        # Выводим отладочную информацию о текущем рабочем каталоге
        print("Текущий рабочий каталог:", os.getcwd())
        
        self.show_buttons()
        self.btn_view_screenshot.show()

    def select_file(self):
        options = QFileDialog.Option.ReadOnly
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите файл", "", "All Files (*);;Text Files (*.txt)", options=options)
        if file_path:
            file_name = os.path.basename(file_path)
            self.main_text.setText(f"Выбран файл: {file_name}")
            destination = os.path.join(os.path.dirname(os.path.realpath(__file__)), file_name)
            shutil.copyfile(file_path, destination)
            self.filename = destination
            self.choice = True
        self.show_buttons()

    def closeEvent(self, event):
        if hasattr(self, 'filename') and self.filename:
            file_path = self.filename
            if os.path.exists(file_path):
                os.remove(file_path)
        event.accept()

    def view_screenshot(self):
        self.filename = "screenshot.png"
        img = cv.imread(self.filename)
        cv.imshow("Screenshot", img)
        cv.waitKey(0)
        cv.destroyAllWindows()

    def analyze_graph(self):
        dialog = InputDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            xGraph, yGraph = dialog.get_inputs()
            try:
                xGraph = float(xGraph)
                yGraph = float(yGraph)
                screenshot_path = self.filename

                if os.path.exists(screenshot_path):
                    from graphAnalyzer import GraphAnalyzer
                    analyzer = GraphAnalyzer(screenshot_path, xGraph, yGraph)
                    analyzer.analyze()
                else:
                    error_dialog = ErrorDialog(self)
                    error_dialog.exec()
                    print("Файл не найден.")
            except ValueError:
                error_dialog = ErrorDialog(self)
                error_dialog.exec()
                print("Пожалуйста, введите корректные числовые значения для X и Y.")
        else:
            print("Анализ графика отменен.")

def application():
    app = QApplication(sys.argv)
    window = DigitizerGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    application()
