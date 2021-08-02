import matplotlib.pyplot as plt
from PIL import Image
import qiskit

class Plotter:

    def __init__(self):

        self.color_list = (
            (0,  0,    0),  # Black
            (255,  0,    0),  # Red
            (0, 255,   0),  # Green
            (255, 255,   0),  # Yellow
            (0,   0, 255),  # Blue
            (255,   0, 255),  # Violet
            (0, 255, 255),  # Cyan
            (255, 255, 255))  # White

        self.state2color = {
            "000": "black",
            "001": "red",
            "010": "green",
            "011": "yellow",
            "100": "blue",
            "101": "violet",
            "110": "cyan",
            "111": "white"}

        self.states_dict = {
            1: "000",
            2: "001",
            3: "010",
            4: "011",
            5: "100",
            6: "101",
            7: "110",
            8: "111"}

    def plot_rgb_point(self, ax, rgb):
        # Plot the rgb vector
        ax.scatter(rgb[0], rgb[1], rgb[2], marker="o")

        # Set the axis labels
        ax.set_xlabel('Red')
        ax.set_ylabel('Green')
        ax.set_zlabel('Blue')

        # Set the fixed bounds of the axis
        ax.set_xlim([0, 255])
        ax.set_ylim([0, 255])
        ax.set_zlim([0, 255])
        return ax

    def plot_input(self, input_data):
        input_rgb = input_data*255
        
        fig = plt.figure(figsize=(17, 3))

        # Plot the input color in the RGB space
        ax1 = fig.add_subplot(1, 5, 2, projection='3d')
        ax1 = self.plot_rgb_point(ax1, input_rgb)

        # Plot the actual input color
        ax2 = plt.subplot(1, 5, 4)
        ax2.set_title('Input color RGB = {}\n'.format(input_rgb))
        # Convert RGB color to 10x10 image:
        input_img = Image.new("RGB", (10, 10), tuple(input_rgb))
        # Then show it:
        plt.imshow(input_img)

    def print_color_base(self):
        plt.figure(figsize=(16, 3))

        for i in range(0, 8):
            ax = plt.subplot(1, 9, i+1)
            ax.set_title("{}".format(self.state2color[self.states_dict[i+1]]))
            ax.tick_params(axis='both', which='both', bottom=False, top=False,
                           left=False, right=False, labelbottom=False,
                           labeltop=False, labelleft=False, labelright=False)
            img = Image.new("RGB", (10, 10), self.color_list[i])
            plt.imshow(img)

    def plot_result(self, input_data, result):
        fig = plt.figure(figsize=(16, 3))

        ax1 = fig.add_subplot(1, 5, 1, projection='3d')
        ax1 = self.plot_rgb_point(ax1, input_data)

        ax2 = plt.subplot(1, 5, 3)
        ax2.set_title("Quantum probabilities")
        qiskit.visualization.plot_histogram(result, ax=ax2)

        ax3 = plt.subplot(1, 5, 5)
        # Plot the actual input color
        ax3.set_title('Input color RGB = {}\n'.format(input_data))
        # Convert RGB color to 10x10 image:
        input_img = Image.new("RGB", (10, 10), tuple(input_data))
        # Then show it:
        plt.imshow(input_img)
