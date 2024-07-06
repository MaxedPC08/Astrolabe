import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QSlider, QLabel, QVBoxLayout, QWidget
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt
import time
from Locater import Locater


# This file is used to create the parameters for
# the image processing algorithm. It is a GUI
# that allows the user to adjust the parameters
# in real time and see the results.
# Just run the file and adjust the sliders to see the results.
# The parameters are saved in a file called params.txt.
# Move those parameters to the raspberry pi to use them there.

class Window(QMainWindow):
    def __init__(self, array=None):
        self.green_line = np.array([[0, 255, 0] for i in range(11)])
        self.red_line = np.array([[0, 0, 255] for i in range(11)])
        super().__init__()
        self.image = cv2.imread('image.jpg')  # Load your image here
        self.original_image = self.image.copy()

        self.red_slider = self.create_slider('Red', 0, 255, 0)
        self.green_slider = self.create_slider('Green', 0, 255, 0)
        self.blue_slider = self.create_slider('Blue', 0, 255, 0)
        self.blur_slider = self.create_slider('Blur', 0, 40, 0)
        self.difference_slider = self.create_slider('Difference', 0, 40, 0)
        self.color_label = QLabel(self)
        self.color_label.setFixedSize(50, 50)  # Set the size of the color box
        self.color_label.setAutoFillBackground(True)

        # Add the color label to the layout


        self.image_label = QLabel(self)
        self.update_image()

        self.load_params()

        layout = QVBoxLayout()
        layout.addWidget(QLabel('Red:'))
        layout.addWidget(self.red_slider)
        layout.addWidget(QLabel('Green:'))
        layout.addWidget(self.green_slider)
        layout.addWidget(QLabel('Blue:'))
        layout.addWidget(self.blue_slider)
        layout.addWidget(QLabel('Current Color:'))
        layout.addWidget(self.color_label)
        layout.addWidget(QLabel('Blur:'))
        layout.addWidget(self.blur_slider)
        layout.addWidget(QLabel('Difference:'))
        layout.addWidget(self.difference_slider)
        layout.addWidget(self.image_label)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.green_vertical_line = np.array([[[0, 255, 0]] for i in range(10)])
        self.red_vertical_line = np.array([[[0, 0, 255]] for i in range(10)])
        self.red_horizontal_line = np.array([[[0, 0, 255] for i in range(10)]])


    def create_slider(self, name, min_value, max_value, default_value):
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(min_value)
        slider.setMaximum(max_value)
        slider.setValue(default_value)
        slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        slider.setTickInterval(1)
        slider.valueChanged.connect(self.update_image)
        slider.valueChanged.connect(self.save_params)
        slider.setToolTip(f"Adjust the {name}")
        return slider


    def update_image(self):
        start = time.time()
        image = self.original_image.copy()
        blur = self.blur_slider.value()
        dif = self.difference_slider.value()
        image, _, _, = locator.locate(image, blur, dif, self.blue_slider.value(), self.green_slider.value(), self.red_slider.value())

        print(f"Time: {time.time() - start:.2f} seconds")
        red = self.red_slider.value()
        green = self.green_slider.value()
        blue = self.blue_slider.value()
        self.color_label.setStyleSheet(f"background-color: rgb({red}, {green}, {blue});")

        height, width, _ = image.shape
        bytes_per_line = 3 * width
        q_image = QImage(image.data.tobytes(), width, height, bytes_per_line,
                         QImage.Format.Format_BGR888)
        self.image_label.setPixmap(QPixmap.fromImage(q_image))

    def load_params(self):
        try:
            with open('../FYRE-FRSee/params.txt', 'r') as f:
                lines = f.readlines()
                self.red_slider.setValue(int(lines[0].split(": ")[1]))
                self.green_slider.setValue(int(lines[1].split(": ")[1]))
                self.blue_slider.setValue(int(lines[2].split(": ")[1]))
                self.blur_slider.setValue(int(lines[3].split(": ")[1]))
                self.difference_slider.setValue(int(lines[4].split(": ")[1]))
        except FileNotFoundError:
            print("params.txt not found. Using default values.")

    def save_params(self):
        with open('../FYRE-FRSee/params.txt', 'w') as f:
            f.write(f"Red: {self.red_slider.value()}\n")
            f.write(f"Green: {self.green_slider.value()}\n")
            f.write(f"Blue: {self.blue_slider.value()}\n")
            f.write(f"Blur: {self.blur_slider.value()}\n")
            f.write(f"Difference: {self.difference_slider.value()}\n")

if __name__ == "__main__":
    locator = Locater()
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())