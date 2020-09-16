import matplotlib.pyplot as plt
from PIL import Image


class Plotter:

    def __init__(self):

        self.color_list = (
            (0, 0, 0),  # Black
            (255, 0, 0),  # Red
            (0, 255, 0),  # Green
            (255, 255, 0),  # Yellow
            (0, 0, 255),  # Blue
            (255, 0, 255),  # Violet
            (0, 255, 255),  # Cyan
            (255, 255, 255),  # White
        )

        self.states_dict = {
            1: "000",
            2: "001",
            3: "010",
            4: "011",
            5: "100",
            6: "101",
            7: "110",
            8: "111",
        }

    def data2img(self, data):
        """Converts normalized input data to a 10x10 color image representation"""
        rgb = [round(d*255) for d in data]
        return Image.new("RGB", (10, 10), tuple(rgb))

    def plot_data(self, data):
        """Plots normalized data in 3d space with the correspondant color representation"""
        fig = plt.figure(figsize=(17, 3))

        # Plot the input color in the RGB space
        ax1 = fig.add_subplot(1, 5, 2, projection='3d')
        # Plot the 3d point
        ax1.scatter(data[0], data[1], data[2], marker="o")
        # Set the axis labels
        ax1.set_xlabel('Dim_1')
        ax1.set_ylabel('Dim_2')
        ax1.set_zlabel('Dim_3')
        # Set the fixed bounds of the axis
        ax1.set_xlim([0, 1])
        ax1.set_ylim([0, 1])
        ax1.set_zlim([0, 1])

        # Plot the actual input color
        ax2 = plt.subplot(1, 5, 4)
        ax2.set_title('Data = {}\n'.format(data))
        plt.imshow(self.data2img(data))

    def plot_result(self, data, counts, shots):
        """Plots the % obtained from the simulation for each basis states"""
        plt.figure(figsize=(15, 1), dpi=150)

        # Plot the input
        axis = plt.subplot(1, 10, 1)
        axis.tick_params(axis='both',
                         which='both',
                         bottom=False,
                         top=False,
                         left=False,
                         right=False,
                         labelbottom=False,
                         labeltop=False,
                         labelleft=False,
                         labelright=False)
        axis.set_title('Input')
        axis.set_xlabel('{}'.format(data))
        plt.imshow(self.data2img(data))

        # Plot all the probabilities
        for i in range(0, 8):
            axis = plt.subplot(1, 10, i+2)
            axis.set_title("{}".format(self.states_dict[i+1]))
            axis.tick_params(axis='both',
                             which='both',
                             bottom=False,
                             top=False,
                             left=False,
                             right=False,
                             labelbottom=False,
                             labeltop=False,
                             labelleft=False,
                             labelright=False)
            axis.set_xlabel(f"{counts[self.states_dict[i+1]]/shots:%}")
            img = Image.new("RGB", (10, 10), self.color_list[i])
            plt.imshow(img)
