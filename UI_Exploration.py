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

# Preprocess function: z-score normalization (mean=0, variance=1)
def preprocess_imu_data(imu_data):
    """
    Standardizes the IMU data (mean=0, std=1) for each axis.
    Args:
        imu_data: DataFrame with IMU features like ax, ay, az, gx, gy, gz.
    Returns:
        Standardized DataFrame.
    """
    imu_columns = ['ax', 'ay', 'az', 'gx', 'gy', 'gz']
    for col in imu_columns:
        imu_data[col] = (imu_data[col] - imu_data[col].mean()) / imu_data[col].std()
    return imu_data

# Centering function to make head image start at center
def center_imu_data(imu_data):
    """
    Centers IMU data by subtracting the initial position (first row).
    Ensures that the head image starts at the center.
    """
    imu_columns = ['ax', 'ay', 'az', 'gx', 'gy', 'gz']
    for col in imu_columns:
        imu_data[col] = imu_data[col] - imu_data[col].iloc[0]  # Subtract initial position
    return imu_data

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
        
        # Preprocess and center the IMU data
        imu_left = preprocess_imu_data(imu_left)
        imu_right = preprocess_imu_data(imu_right)
        imu_left = center_imu_data(imu_left)  # Centering IMU data for starting at 0,0
        imu_right = center_imu_data(imu_right)
        
        return imu_left, imu_right
    
    except FileNotFoundError as e:
        print(e)
        return None, None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None

# Global variable to store animation object
ani = None

# Animation function
def animate_imu(imu_left, activity, canvas, fig, ax):
    global ani  # Access the global variable to control the animation

    # Stop the current animation if it's running
    if ani:
        ani.event_source.stop()

    # Load the head image
    head_img = mpimg.imread('head.png')

    # Scale factor for movement amplification
    scale_factor = 4
    image_size_factor = 2  # Increase this factor to scale the image size

    def update(frame):
        ax.clear()
        
        limits = 10
        ax.set_xlim(-limits, limits)
        ax.set_ylim(-limits, limits)
        ax.grid(False)

        tilt_x, tilt_y = 0, 0
        
        if activity == 'nod':
            tilt_y = imu_left['ay'].iloc[frame] * scale_factor
            rotation = imu_left['gy'].iloc[frame] * 0.01
        elif activity == 'shake':
            tilt_x = imu_left['ax'].iloc[frame] * scale_factor
            rotation = imu_left['gx'].iloc[frame] * 0.01
        else:
            tilt_x = imu_left['ax'].iloc[frame] * scale_factor
            tilt_y = imu_left['ay'].iloc[frame] * scale_factor
            rotation = imu_left['gz'].iloc[frame] * 0.01
        
        # Adjust the image extent to increase size
        img_extent = [
            tilt_x - image_size_factor, tilt_x + image_size_factor,
            tilt_y - image_size_factor, tilt_y + image_size_factor
        ]
        
        # Display the head image with updated size
        ax.imshow(head_img, extent=img_extent, aspect='auto', origin='upper')
        canvas.draw()
    
    # Start new animation
    ani = FuncAnimation(fig, update, frames=len(imu_left), interval=200)
    canvas.draw()


# Stop animation function
def stop_animation():
    global ani
    if ani:
        ani.event_source.stop()

# Plot function (for static plotting)
def plot_imu_data(imu_left, imu_right, activity, user_id):
    fig, axs = plt.subplots(2, 1, figsize=(10, 8))

    axs[0].plot(imu_left['timestamp'], imu_left['ax'], label='Accel X (Left)', color='r')
    axs[0].plot(imu_left['timestamp'], imu_left['ay'], label='Accel Y (Left)', color='g')
    axs[0].plot(imu_left['timestamp'], imu_left['az'], label='Accel Z (Left)', color='b')
    axs[0].set_title(f'User {user_id} - {activity} IMU (Left)')
    axs[0].legend()

    axs[1].plot(imu_right['timestamp'], imu_right['ax'], label='Accel X (Right)', color='r')
    axs[1].plot(imu_right['timestamp'], imu_right['ay'], label='Accel Y (Right)', color='g')
    axs[1].plot(imu_right['timestamp'], imu_right['az'], label='Accel Z (Right)', color='b')
    axs[1].set_title(f'User {user_id} - {activity} IMU (Right)')
    axs[1].legend()

    plt.tight_layout()
    plt.show()

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
    root.geometry("800x600")

    # Create a frame for options
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
    ctk.CTkButton(options_frame, text="Run", command=on_run).pack(pady=5)

    # Stop button to stop animation
    ctk.CTkButton(options_frame, text="Stop Animation", command=stop_animation).pack(pady=5)

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
