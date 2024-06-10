import cv2 as cv 
import csv 
import tempfile

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

    # def save_image_with_points(self):
    #     # Создание временного файла для сохранения изображения с точками
    #     temp_file_path = tempfile.mktemp(suffix='.png')

    #     # Сохранение изображения с точками во временном файле
    #     image_with_points = self.image.copy()
    #     for point in self.points:
    #         cv.circle(image_with_points, point, 5, (0, 255, 0), -1)  # Убрана обводка
    #     cv.imwrite(temp_file_path, image_with_points)

    #     return temp_file_path
    def save_image_with_points(self):
        # Создание временного файла для сохранения изображения с точками
        temp_file_path = tempfile.mktemp(suffix='.png')

        # Сохранение изображения с точками во временном файле
        image_with_points = self.image.copy()
        for point in self.points:
            cv.circle(image_with_points, point, 5, (0, 255, 0), -1)  # Убрана обводка
        cv.imwrite(temp_file_path, image_with_points)

        return temp_file_path

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