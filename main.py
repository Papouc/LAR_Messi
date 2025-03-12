from robolab_turtlebot import Turtlebot, Rate

from scene_info import SceneInfo
from visualizer import Visualizer
from hsv_filter import HSVFilter
from image_processor import ImageProcessor, Image

LOOP_RATE: int = 10


def main() -> None:
    turtle: Turtlebot = Turtlebot(rgb=True)
    main_loop_rate: Rate = Rate(LOOP_RATE)

    visual: Visualizer = Visualizer("WINDOW")

    while not turtle.is_shutting_down():
        new_img: Image = turtle.get_rgb_image()

        img_processor: ImageProcessor = ImageProcessor(new_img)

        # "yellow" filter
        ball_filter: HSVFilter = HSVFilter(30, 130, 60, 48)
        img_processor.add_color_filter(ball_filter)

        # "blue" filter
        goal_filter: HSVFilter = HSVFilter(105, 160, 98, 196)
        img_processor.add_color_filter(goal_filter)

        img_processor.filter_color()

        result: SceneInfo = img_processor.segment_scene(draw=True)
        print(result.has_ball, result.ball_position)

        visual.refresh_image(img_processor.retrieve_image(), center_point=True)

        main_loop_rate.sleep()


if __name__ == "__main__":
    main()
