from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QPushButton, QLabel, QWidget,
    QVBoxLayout, QHBoxLayout, QLineEdit, QDialog, QDialogButtonBox, QTableWidget, QTableWidgetItem, QSpacerItem, QSizePolicy
)
from PyQt6 import QtWidgets, QtCore
import sys
import pyautogui
import numpy as np
import cv2 as cv
import pyscreenshot as ImageGrab
import os
import csv
from openpyxl import Workbook
import shutil
import tempfile

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
        self.info2_label =  QLabel("ПКМ для точек", self)
        self.info3_label =  QLabel("ЛКМ для текста", self)
        self.info_label.setStyleSheet("font: 14pt Helvetica")
        self.info_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.x_label = QLabel("X:")
        self.x_input = QLineEdit()

        self.y_label = QLabel("Y:")
        self.y_input = QLineEdit()

        self.x_axis_label = QLabel("Наименование оси X:")
        self.x_axis_input = QLineEdit()

        self.y_axis_label = QLabel("Наименование оси Y:")
        self.y_axis_input = QLineEdit()

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.info_label)
        layout.addWidget(self.x_label)
        layout.addWidget(self.x_input)
        layout.addWidget(self.y_label)
        layout.addWidget(self.y_input)
        layout.addWidget(self.x_axis_label)
        layout.addWidget(self.x_axis_input)
        layout.addWidget(self.y_axis_label)
        layout.addWidget(self.y_axis_input)
        layout.addWidget(self.info2_label)
        layout.addWidget(self.info3_label)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

        self.setMinimumWidth(300)

    def get_inputs(self):
        return self.x_input.text(), self.y_input.text(), self.x_axis_input.text(), self.y_axis_input.text()

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

class DataTableWindow(QDialog):
    def __init__(self, x_axis_name, y_axis_name):
        super().__init__()
        self.graph_analyzer = None
        
        self.setWindowTitle("Ваши данные:")
        self.setGeometry(400, 300, 400, 300)
        self.x_axis_name = x_axis_name
        self.y_axis_name = y_axis_name
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels([self.x_axis_name, self.y_axis_name])

        self.save_image_button = QPushButton("Сохранить изображение как")
        self.export_label = QLabel("Экспортировать таблицу:")
        self.export_xlsx_button = QPushButton("Как xlsx")
        self.export_csv_button = QPushButton("Как csv")
        self.feedback_button = QPushButton("Оставить отзыв")

        self.save_image_button.clicked.connect(self.save_image_dialog)
        self.export_xlsx_button.clicked.connect(self.export_to_xlsx)
        self.export_csv_button.clicked.connect(self.export_to_csv)
        self.feedback_button.clicked.connect(self.leave_feedback)

        layout = QVBoxLayout()
        layout.addWidget(self.table_widget)  
        layout.addWidget(self.export_label)
        layout.addWidget(self.export_xlsx_button)
        layout.addWidget(self.export_csv_button)
       

        # Добавляем отступ перед кнопкой "save_image_button"
        spacer = QSpacerItem(20, 80, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addItem(spacer)

        layout.addWidget(self.save_image_button)
        layout.addWidget(self.feedback_button)
        self.setLayout(layout)

    def save_image_dialog(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить изображение", "", "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg)")
        if file_path and self.graph_analyzer:  # Убедимся, что self.graph_analyzer не None
            temp_file_path = self.graph_analyzer.save_image_with_points()  # Используйте метод GraphAnalyzer
            try:
                shutil.copy(temp_file_path, file_path)  # Копируйте временный файл в выбранное место
                os.remove(temp_file_path)  # Удалите временный файл после копирования
            except Exception as e:
                error_dialog = ErrorDialog(self)
                error_dialog.error_label.setText("Закройте изображение графика перед сохранением")
                error_dialog.exec()
        else:
            error_dialog = ErrorDialog(self)
            error_dialog.error_label.setText("Закройте изображение графика перед сохранением")
            error_dialog.exec()


    def add_data(self, x, y):
        row_position = self.table_widget.rowCount()
        self.table_widget.insertRow(row_position)
        self.table_widget.setItem(row_position, 0, QTableWidgetItem(str(x)))
        self.table_widget.setItem(row_position, 1, QTableWidgetItem(str(y)))

    def export_to_xlsx(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить как xlsx", "", "Excel Files (*.xlsx)")
        if file_path:
            workbook = Workbook()
            worksheet = workbook.active
            worksheet.append([self.x_axis_name, self.y_axis_name])  # записываем имена столбцов
            for row in range(self.table_widget.rowCount()):
                row_data = []
                for col in range(self.table_widget.columnCount()):
                    item = self.table_widget.item(row, col)
                    if item is not None:
                        row_data.append(item.text())
                worksheet.append(row_data)
            workbook.save(file_path)

    def export_to_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить как csv", "", "CSV Files (*.csv)")
        if file_path:
            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([self.x_axis_name, self.y_axis_name])  # записываем имена столбцов
                for row in range(self.table_widget.rowCount()):
                    row_data = []
                    for col in range(self.table_widget.columnCount()):
                        item = self.table_widget.item(row, col)
                        if item is not None:
                            row_data.append(item.text())
                    writer.writerow(row_data)
    
    def leave_feedback(self):
        dialog = FeedbackDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name, rating, comments = dialog.get_feedback()
            print(f"ФИО: {name}, Оценка: {rating}, Пожелания: {comments}")
            # Здесь вы можете сохранить данные в файл или обработать их другим образом

from PyQt6.QtWidgets import (
    QDialog, QLabel, QLineEdit, QDialogButtonBox, QVBoxLayout,
    QTextEdit, QComboBox
)

class FeedbackDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Оставить отзыв")

        self.name_label = QLabel("ФИО:")
        self.name_input = QLineEdit()

        self.rating_label = QLabel("Оценка (1-5):")
        self.rating_input = QComboBox()
        self.rating_input.addItems(["1", "2", "3", "4", "5"])

        self.comments_label = QLabel("Ваши пожелания:")
        self.comments_input = QTextEdit()

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)
        layout.addWidget(self.rating_label)
        layout.addWidget(self.rating_input)
        layout.addWidget(self.comments_label)
        layout.addWidget(self.comments_input)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

    def get_feedback(self):
        return self.name_input.text(), self.rating_input.currentText(), self.comments_input.toPlainText()


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
        self.start_timer("Зафиксируйте курсор СЛЕВА СВЕРХУ на 10 секунд")

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
        if "СЛЕВА СВЕРХУ" in message:
            message = message.replace("СЛЕВА СВЕРХУ", "<b>СЛЕВА СВЕРХУ</b>")
        elif "СПРАВА СНИЗУ" in message:
            message = message.replace("СПРАВА СНИЗУ", "<b>СПРАВА СНИЗУ</b>")

        self.main_text.setText(message)
        self.timerWidget.show()
        self.timerWidget.startTimer()

    def handle_timeout(self):
        if self.stage == 0:
            self.pointX1, self.pointY1 = pyautogui.position()
            self.stage = 1
            self.start_timer("Зафиксируйте курсор СПРАВА СНИЗУ на 10 секунд")
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
            self.main_text.setText("Ошибка: скриншот не был сохранен.")

        self.show_buttons()

    def select_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Выберите файл", "", "Images (*.png *.xpm *.jpg)")
        if filename:
            self.choice = True
            # Получаем полный путь к файлу
            self.filename = os.path.abspath(filename)
            # Отображаем только название файла
            self.main_text.setText(f"Файл выбран: {os.path.basename(self.filename)}")
            self.show_buttons()

    def view_screenshot(self):
        if self.filename:
            img = cv.imread(self.filename)
            cv.imshow('Скриншот', img)
            cv.waitKey(0)
            cv.destroyAllWindows()

    def analyze_graph(self):
        if self.filename:
            dialog = InputDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                x_step, y_step, x_axis_name, y_axis_name = dialog.get_inputs()
                try:
                    x_step = float(x_step)
                    y_step = float(y_step)
                    self.data_window = DataTableWindow(x_axis_name, y_axis_name)
                    self.graph_analyzer = GraphAnalyzer(self.filename, x_step, y_step, self.data_window, x_axis_name, y_axis_name)
                    self.graph_analyzer.analyze()
                    self.data_window.graph_analyzer = self.graph_analyzer
                    self.data_window.exec()
                except ValueError:
                    error_dialog = ErrorDialog(self)
                    error_dialog.exec()

class GraphAnalyzer:
    def __init__(self, filename, x_step, y_step, data_window, nameX, nameY):
        self.filename = filename
        self.x_step = x_step
        self.y_step = y_step
        self.data_window = data_window
        self.trashedWhiteLeft = 0
        self.trashedWhiteBottom = 0
        self.height, self.width = self.image_size()[:2]
        self.image = None
        self.points = []  # Хранение координат точек
        self.nameX = nameX
        self.nameY = nameY
        self.fileCsv = open("GraphData.csv", 'w+', newline='')
        self.writer = csv.writer(self.fileCsv)
        self.writer.writerow([self.nameX, self.nameY])

    def image_size(self):
        image = cv.imread(self.filename)
        if image is not None:
            height, width, channels = image.shape
            return height, width, channels
        else:
            return 0, 0, 0

    def find_first_black_pixel(self):
        graph = cv.imread(self.filename)
        cv.cvtColor(graph, cv.COLOR_BGR2RGB)

        (h, w) = graph.shape[:2]
        (cX, cY) = (w // 2, h // 2)

        y, x = 0, 0
        newHeight, newWidth = cY, cX
        croppedLeftTop = graph[y:newHeight, x:newWidth]

        for i in range(0, newHeight):
            for j in range(0, newWidth):
                r, g, b = graph[i][j]
                if r < 220 or g < 220 or b < 220:
                    self.trashedWhiteLeft = j
                    break

        counter = 0
        for i in range(newHeight, 0, -1):
            for j in range(newHeight, 0, -1):
                r, g, b = graph[i][j]
                if r < 220 or g < 220 or b < 220:
                    self.trashedWhiteBottom = counter
                    counter += 1

        self.height -= self.trashedWhiteLeft
        self.width -= self.trashedWhiteBottom

    def click_event(self, event, x, y, flags, params):
        if event == cv.EVENT_LBUTTONDOWN:
            otherX = round(x / self.x_step, 2)
            otherY = round((self.height - y) / self.y_step, 2)
            data = otherX, otherY
            self.writer.writerow(data)
            print(otherX, ' ', otherY)

            self.data_window.add_data(otherX, otherY)

            # Сохраняем координаты точек для последующего использования
            self.points.append((x, y))

            font = cv.FONT_HERSHEY_SIMPLEX
            fontScale = 1
            color = (0, 0, 0)
            thickness = 4
            cv.putText(self.image, ".", (x, y), font, fontScale, color, thickness)
            cv.imshow('Graph', self.image)

        if event == cv.EVENT_RBUTTONDOWN:
            otherX = round(x / self.x_step, 2)
            otherY = round((self.height - y) / self.y_step, 2)
            data = otherX, otherY
            self.writer.writerow(data)
            print(otherX, ' ', otherY)

            self.data_window.add_data(otherX, otherY)

            font = cv.FONT_HERSHEY_SIMPLEX
            fontScale = 0.5  # Уменьшаем размер текста
            color = (0, 165, 255)  # оранжевый цвет
            thickness = 2
            cv.putText(self.image, f"({otherX}, {otherY})", (x, y), font, fontScale, color, thickness)
            cv.circle(self.image, (x, y), 3, color, -1)  # Рисуем черную точку вместо текста
            cv.imshow('Graph', self.image)

    def save_image_with_points(self):
        # Создание временного файла для сохранения изображения с точками
        try:
            temp_file_path = tempfile.mktemp(suffix='.png')
            image_with_points = self.image.copy()
            for point in self.points:
                cv.circle(image_with_points, point, 5, (0, 255, 0), -1)
            cv.imwrite(temp_file_path, image_with_points)
            
            # Проверка существования временного файла
            if not os.path.exists(temp_file_path):
                raise FileNotFoundError(f"Временный файл не создан: {temp_file_path}")

            return temp_file_path
        except Exception as e:
            print(f"Ошибка при создании временного файла: {str(e)}")
            return None
    def analyze(self):
        self.image = cv.imread(self.filename, 1)
        self.find_first_black_pixel()
        cv.imshow("Graph", self.image)
        self.data_window.show()
        print("\nКоординаты: ")
        cv.setMouseCallback("Graph", self.click_event)
        cv.waitKey(0)
        cv.destroyAllWindows()
        print("\nДанные сохранены!")
        self.fileCsv.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = DigitizerGUI()
    mainWin.show()
    sys.exit(app.exec())