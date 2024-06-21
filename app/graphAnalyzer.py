import cv2 as cv
import csv
import tempfile
import numpy as np

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
        gray = cv.cvtColor(graph, cv.COLOR_BGR2GRAY)
        _, binary = cv.threshold(gray, 220, 255, cv.THRESH_BINARY)

        # Left margin
        for x in range(binary.shape[1]):
            if np.any(binary[:, x] == 0):
                self.trashedWhiteLeft = x
                break

        # Bottom margin
        for y in range(binary.shape[0]-1, -1, -1):
            if np.any(binary[y, :] == 0):
                self.trashedWhiteBottom = binary.shape[0] - y
                break

        self.height -= self.trashedWhiteBottom
        self.width -= self.trashedWhiteLeft

    def click_event(self, event, x, y, flags, params):
        if event == cv.EVENT_LBUTTONDOWN or event == cv.EVENT_RBUTTONDOWN:
            corrected_x = x - self.trashedWhiteLeft
            corrected_y = y - self.trashedWhiteBottom

            if corrected_x < 0 or corrected_y < 0:
                print("Click outside the graph area.")
                return

            otherX = round(corrected_x / self.width * (self.x_step - 1),3)
            otherY = round(((self.height - corrected_y) / self.height * (self.y_step - 1) + 1), 3)
            data = round(otherX, 3), round(otherY, 3)
            self.writer.writerow(data)
            print(f"Clicked at: ({x}, {y}), corrected: ({corrected_x}, {corrected_y}), result: {otherX}, {otherY}")

            self.data_window.add_data(otherX, otherY)

            if event == cv.EVENT_LBUTTONDOWN:
                color = (0, 0, 0)
                cv.circle(self.image, (x, y), 3, color, -1)
            elif event == cv.EVENT_RBUTTONDOWN:
                font = cv.FONT_HERSHEY_SIMPLEX
                fontScale = 0.5
                color = (0, 165, 255)
                thickness = 2
                cv.putText(self.image, f"({otherX:.3f}, {otherY:.3f})", (x, y), font, fontScale, color, thickness)
            
            cv.imshow('Graph', self.image)

    def save_image_with_points(self):
        temp_file_path = tempfile.mktemp(suffix='.png')
        image_with_points = self.image.copy()
        for point in self.points:
            cv.circle(image_with_points, point, 5, (0, 255, 0), -1)
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
