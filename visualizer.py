import cv2

from image_processor import Image

DELAY_TIME: int = 1

class Visualizer:
    def __init__(self, win_name: str) -> None:
        self.win_name: str = win_name
        cv2.namedWindow(self.win_name)

    def refresh_image(self, image: Image, center_point: bool = False) -> None:
        if center_point and len(image) > 0:

            y_half: int = int(len(image) / 2)
            x_half: int = int(len(image[0]) / 2)

            # make small square in the middle
            for y_offset in range(-1, 2):
                for x_offset in range(-1, 2):
                    image[y_half + y_offset][x_half + x_offset] = [0, 0, 255]

        cv2.imshow(self.win_name, image)
        cv2.waitKey(DELAY_TIME)