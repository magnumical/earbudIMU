import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

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

def animate_imu(imu_left):
    fig, ax = plt.subplots()
    head_circle = plt.Circle((0, 0), 1, fill=False, edgecolor='b')
    ax.add_patch(head_circle)
    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)

    def update(frame):
        ax.clear()
        ax.set_xlim(-2, 2)
        ax.set_ylim(-2, 2)
        
        # Tilt effect based on accelerometer
        tilt_x = imu_left['ax'].iloc[frame] / 1000  # Adjust scaling for better visualization
        tilt_y = imu_left['ay'].iloc[frame] / 1000
        
        # Rotate effect based on gyroscope (integrate angular velocity over time)
        rotation = imu_left['gz'].iloc[frame] * 0.01  # Gyroscope Z-axis for rotation
        
        # Create rotated circle (simulating head tilt + rotation)
        t = np.linspace(0, 2 * np.pi, 100)
        x = np.cos(t + rotation)
        y = np.sin(t + rotation)
        
        ax.plot(x + tilt_x, y + tilt_y, 'b')
        return head_circle,

    ani = FuncAnimation(fig, update, frames=len(imu_left), interval=500)  # Slower animation (500ms interval)
    plt.show()

def plot_imu_data(imu_left, imu_right, activity, user_id):
    # Plot the accelerometer and gyroscope data (X, Y, Z) for both left and right IMU
    plt.figure(figsize=(12, 10))
    
    # Left IMU
    plt.subplot(2, 1, 1)
    plt.plot(imu_left['timestamp'], imu_left['ax'], label='Accel X (Left)', color='r')
    plt.plot(imu_left['timestamp'], imu_left['ay'], label='Accel Y (Left)', color='g')
    plt.plot(imu_left['timestamp'], imu_left['az'], label='Accel Z (Left)', color='b')
    plt.plot(imu_left['timestamp'], imu_left['gx'], label='Gyro X (Left)', linestyle='--', color='r')
    plt.plot(imu_left['timestamp'], imu_left['gy'], label='Gyro Y (Left)', linestyle='--', color='g')
    plt.plot(imu_left['timestamp'], imu_left['gz'], label='Gyro Z (Left)', linestyle='--', color='b')
    plt.title(f'User {user_id} - {activity} IMU (Left)')
    plt.xlabel('Time')
    plt.ylabel('Acceleration (g) / Gyroscope (dps)')
    plt.legend()

    # Right IMU
    plt.subplot(2, 1, 2)
    plt.plot(imu_right['timestamp'], imu_right['ax'], label='Accel X (Right)', color='r')
    plt.plot(imu_right['timestamp'], imu_right['ay'], label='Accel Y (Right)', color='g')
    plt.plot(imu_right['timestamp'], imu_right['az'], label='Accel Z (Right)', color='b')
    plt.plot(imu_right['timestamp'], imu_right['gx'], label='Gyro X (Right)', linestyle='--', color='r')
    plt.plot(imu_right['timestamp'], imu_right['gy'], label='Gyro Y (Right)', linestyle='--', color='g')
    plt.plot(imu_right['timestamp'], imu_right['gz'], label='Gyro Z (Right)', linestyle='--', color='b')
    plt.title(f'User {user_id} - {activity} IMU (Right)')
    plt.xlabel('Time')
    plt.ylabel('Acceleration (g) / Gyroscope (dps)')
    plt.legend()

    # Show the plot
    plt.tight_layout()
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
        animate_imu(imu_left)
    elif action == 'p':
        plot_imu_data(imu_left, imu_right, activity, user_id)
    else:
        print("Invalid input! Please choose 'P' for plot or 'A' for animate.")

if __name__ == "__main__":
    main()

# IMU Columns: timestamp, ax (Accel X), ay (Accel Y), az (Accel Z), gx (Gyro X), gy (Gyro Y), gz (Gyro Z)
