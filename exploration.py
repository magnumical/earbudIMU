import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import matplotlib.image as mpimg
import seaborn as sns
sns.set_theme()
sns.set(style="whitegrid")  # Default setting with grid
sns.set(style="white")      # Remove the grid


# Valid activity names
VALID_ACTIVITIES = ['brow-lowerer', 'brow-raiser', 'chewing', 'chin-raiser', 'eyes-lr', 'eyes-ud', 
                    'lip-puller', 'mouth-stretch', 'nod', 'running', 'shake', 'speaking', 
                    'still', 'swallowing', 'tilt', 'walking', 'wink-l', 'wink-r']

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
        print(e)
        return None, None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None

def animate_imu(imu_left, activity):
    fig, ax = plt.subplots()
    
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
        return ax,

    ani = FuncAnimation(fig, update, frames=len(imu_left), interval=250)  # Slower animation
    
    plt.show()
    


def main():
    # User input: user ID and activity
    user_id = input("Enter user ID (0-29): ")
    activity = input("Enter activity (e.g., chewing, running, etc.): ").lower()

    # Validate activity name
    if activity not in VALID_ACTIVITIES:
        print(f"Invalid activity name. Valid activities are: {', '.join(VALID_ACTIVITIES)}")
        return
    
    # Load data
    imu_left, imu_right = load_imu_data(user_id, activity)
    
    if imu_left is None or imu_right is None:
        print("Failed to load data.")
        return
    
    # Ask if user wants to plot or animate
    action = input("Do you want to (P)lot or (A)nimate the data? (P/A): ").lower()
    
    if action == 'a':
        animate_imu(imu_left, activity)
    elif action == 'p':
        plot_imu_data(imu_left, imu_right, activity, user_id)
    else:
        print("Invalid input! Please choose 'P' for plot or 'A' for animate.")

if __name__ == "__main__":
    main()

# IMU Columns: timestamp, ax (Accel X), ay (Accel Y), az (Accel Z), gx (Gyro X), gy (Gyro Y), gz (Gyro Z)
