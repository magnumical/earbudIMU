import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import numpy as np
import matplotlib.image as mpimg
import customtkinter as ctk
from tkinter import messagebox
import matplotlib.pyplot as plt
plt.style.use('dark_background')

# Initialize CTk
ctk.set_appearance_mode("System")  # Options: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Options: "blue", "green", "dark-blue"

# Valid activity names
VALID_ACTIVITIES = ['brow-lowerer', 'brow-raiser', 'chewing', 'chin-raiser', 'eyes-lr', 'eyes-ud', 
                    'lip-puller', 'mouth-stretch', 'nod', 'running', 'shake', 'speaking', 
                    'still', 'swallowing', 'tilt', 'walking', 'wink-l', 'wink-r']

# Load IMU data function
def load_imu_data(user_id, activity):
    try:
        # Define file paths
        base_path = f"./dataset/P{user_id}/EARBUDS"
        left_file = f"{base_path}/{user_id}-{activity}-imu-left.csv"
        right_file = f"{base_path}/{user_id}-{activity}-imu-right.csv"

        # Check if the files exist
        if not os.path.exists(left_file) or not os.path.exists(right_file):
            raise FileNotFoundError(f"Data files for activity '{activity}' not found for user {user_id}.")

        # Load IMU data from CSV files
        imu_left = pd.read_csv(left_file)
        imu_right = pd.read_csv(right_file)
        
        return imu_left, imu_right
    
    except FileNotFoundError as e:
        ctk.CTkMessagebox.show_error("File Not Found", str(e))
        return None, None
    except Exception as e:
        ctk.CTkMessagebox.show_error("Error", f"An error occurred: {e}")
        return None, None

# Animation function embedded in the CustomTkinter window
def animate_imu(imu_left, activity, canvas, fig, ax):
    # Load the head image
    head_img = mpimg.imread('head.png')  # Ensure that 'head.png' is in the same directory

    # Standardize/Normalize the accelerometer data
    imu_left['ax'] = (imu_left['ax'] - imu_left['ax'].mean()) / imu_left['ax'].std()
    imu_left['ay'] = (imu_left['ay'] - imu_left['ay'].mean()) / imu_left['ay'].std()
    imu_left['gz'] = (imu_left['gz'] - imu_left['gz'].mean()) / imu_left['gz'].std()
    
    # Scale factor for movement amplification
    scale_factor = 5  # Increase this to amplify head movement
    
    def update(frame):
        ax.clear()
        
        # Dynamic axis limits (based on normalized and amplified data ranges)
        ax.set_xlim(-5, 5)
        ax.set_ylim(-5, 5)
        ax.grid(False)

        # Initialize tilt_x and tilt_y as 0 in case one is not defined
        tilt_x, tilt_y = 0, 0
        
        if activity == 'nod':
            tilt_y = imu_left['ay'].iloc[frame] * scale_factor  # Amplified Y-axis movement
            rotation = imu_left['gy'].iloc[frame] * 0.01  # Rotation around the Y-axis
        elif activity == 'shake':
            tilt_x = imu_left['ax'].iloc[frame] * scale_factor  # Amplified X-axis movement
            rotation = imu_left['gx'].iloc[frame] * 0.01  # Rotation around the X-axis
        else:
            tilt_x = imu_left['ax'].iloc[frame] * scale_factor
            tilt_y = imu_left['ay'].iloc[frame] * scale_factor
            rotation = imu_left['gz'].iloc[frame] * 0.01
        
        # Rotate and display the head image
        img_extent = [tilt_x - 1, tilt_x + 1, tilt_y - 1, tilt_y + 1]  # Adjust image position
        ax.imshow(head_img, extent=img_extent, aspect='auto', origin='upper')
        canvas.draw()
    
    ani = FuncAnimation(fig, update, frames=len(imu_left), interval=200)  # Animation with 200ms interval
    canvas.draw()

# GUI using CustomTkinter
def create_gui():
    def on_run():
        user_id = user_id_var.get()
        activity = activity_var.get()

        if not user_id.isdigit() or int(user_id) < 0 or int(user_id) > 29:
            ctk.CTkMessagebox.show_error("Invalid Input", "Please enter a valid User ID (0-29).")
            return
        
        if activity not in VALID_ACTIVITIES:
            ctk.CTkMessagebox.show_error("Invalid Input", f"Invalid activity. Choose from {', '.join(VALID_ACTIVITIES)}.")
            return

        imu_left, imu_right = load_imu_data(user_id, activity)
        
        if imu_left is None or imu_right is None:
            return
        
        # Clear the figure for a new plot/animation
        ax.clear()
        
        if plot_or_animate_var.get() == "Animate":
            animate_imu(imu_left, activity, canvas, fig, ax)
        else:
            plot_imu_data(imu_left, imu_right, activity, user_id)

    # Create the main window
    root = ctk.CTk()
    root.title("IMU Data Visualization")
    root.geometry("800x600")  # Set window size

    # Create a frame for options on the left side
    options_frame = ctk.CTkFrame(root)
    options_frame.pack(side=ctk.LEFT, padx=10, pady=10)

    # Dropdown for User ID
    ctk.CTkLabel(options_frame, text="Select User ID").pack()
    user_id_var = ctk.StringVar()
    user_id_dropdown = ctk.CTkComboBox(options_frame, values=[str(i) for i in range(30)], variable=user_id_var)
    user_id_dropdown.pack()

    # Dropdown for Activity
    ctk.CTkLabel(options_frame, text="Select Activity").pack()
    activity_var = ctk.StringVar()
    activity_dropdown = ctk.CTkComboBox(options_frame, values=VALID_ACTIVITIES, variable=activity_var)
    activity_dropdown.pack()

    # Radio buttons for Plot or Animate
    plot_or_animate_var = ctk.StringVar(value="Animate")
    ctk.CTkRadioButton(options_frame, text="Animate", variable=plot_or_animate_var, value="Animate").pack()
    ctk.CTkRadioButton(options_frame, text="Plot", variable=plot_or_animate_var, value="Plot").pack()

    # Run button
    ctk.CTkButton(options_frame, text="Run", command=on_run).pack()

    # Create a frame for the plot/animation on the right side
    plot_frame = ctk.CTkFrame(root)
    plot_frame.pack(side=ctk.RIGHT, padx=10, pady=10, fill="both", expand=True)

    # Create a Matplotlib figure
    fig, ax = plt.subplots()

    # Embed the figure into CustomTkinter canvas
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.get_tk_widget().pack(fill="both", expand=True)

    # Start the GUI event loop
    root.mainloop()

# Main function
if __name__ == "__main__":
    create_gui()
