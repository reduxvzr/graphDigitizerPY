import cv2 as cv
import numpy as np
import csv
from PIL import Image
import dumpNumbers

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
        self.fileCsv = open("GraphData.csv", 'w+', newline='')
        self.writer = csv.writer(self.fileCsv)
        self.nameX = nameX
        self.nameY = nameY
        self.writer.writerow([self.nameX, self.nameY])

    def image_size(self):
        image = cv.imread(self.filename)
        height, width, channels = image.shape
        return height, width, channels

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

        croppedRightBottom = graph[cY:h, 0:cX]

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

            font = cv.FONT_HERSHEY_SIMPLEX
            fontScale = 1
            color = (0, 0, 0)
            thickness = 4
            cv.putText(self.image, ".", (x, y), font, fontScale, color, thickness)
            cv.imshow('Graph', self.image)

        if event == cv.EVENT_RBUTTONDOWN:
            print((x / self.x_step), ' ', y / self.y_step)
            font = cv.FONT_HERSHEY_SIMPLEX
            fontScale = 0.4
            color = (0, 0, 0)
            thickness = 1
            b = self.image[y, x, 0]
            g = self.image[y, x, 1]
            r = self.image[y, x, 2]
            cv.putText(self.image, str(b) + ', ' + str(g) + ',' + str(r), (x, y), font, fontScale, color, thickness)
            cv.imshow('image', self.image)

    def analyze(self):
        self.image = cv.imread(self.filename, 1)
        self.find_first_black_pixel()
        cv.imshow("Graph", self.image)
        print("\nКоординаты: ")
        cv.setMouseCallback("Graph", self.click_event)
        cv.waitKey(0)
        cv.destroyAllWindows()
        self.fileCsv.close()
