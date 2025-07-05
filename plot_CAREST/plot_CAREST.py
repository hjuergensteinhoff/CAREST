'''
plot_CAREST 
by Heinz-Juergen Steinhoff, University Osnabrueck, Germany.
Version 7, April 2025

Copyright (c) 2025 Heinz-Juergen Steinhoff

Permission is hereby granted, free of charge, to any person obtaining a copy of this 
software and associated documentation files (the "Software"), to deal in the Software 
without restriction, including without limitation the rights to use, copy, modify, merge, 
publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons
to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR 
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE 
FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, 
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''

import pandas as pd
import matplotlib.pyplot as plt
import sys
from matplotlib.gridspec import GridSpec
import numpy as np
import tkinter as tk
import pandas as pd
from scipy.interpolate import splrep, splev

import numpy as np
from scipy.interpolate import splrep, splev



def get_user_inputs_gui(default_values):
    """
    Opens a single Tkinter window with four editable fields.
    Users can modify values or press 'Continue' to proceed.
    Returns:
    tuple: User-entered or default values for baseline range, pain threshold temperature, and factor.
    """
    labels = ["Baseline Start Temperature (C)", 
              "Baseline End Temperature(C)", 
              "Threshold Offset (x SD above baseline)"]
    
    # Tkinter setup
    root = tk.Tk()
    root.title("Enter Calculation Parameters")

    # Create input fields
    entries = []
    for i, label in enumerate(labels):
        tk.Label(root, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="w")
        entry = tk.Entry(root)
        entry.insert(0, str(default_values[i]))  # Pre-fill with default
        entry.grid(row=i, column=1, padx=10, pady=5)
        entries.append(entry)

    # Store user values in a mutable list
    user_values = []

    # Function to retrieve input values and close window
    def submit():
        user_values.extend([float(entry.get()) if entry.get() else default_values[i] for i, entry in enumerate(entries)])
        root.destroy()  # Close the window

    # Continue button
    tk.Button(root, text="Continue", command=submit).grid(row=len(labels), columnspan=2, pady=10)

    root.mainloop()  # Run the window

    return tuple(user_values)  # Return user input values

	
def l_curve_corner(x_data, y_data, experiment_type, smooth_factor=0):
    """
    Finds the L-curve corner by maximum curvature on (x_data, y_data)
    """

    t = np.arange(len(x_data))

    # B-spline representations
    tck_y = splrep(t, y_data, s=smooth_factor)

    # Second derivatives
    ddy = splev(t, tck_y, der=2)

    # Mask for y_data < 50
    mask = y_data < 50

    # Use the mask to find the index of the max curvature in the masked region
    if np.any(mask):
        # Get the indices of the masked region
        valid_indices = np.where(mask)[0]
   
        # Find the index of the max curvature within the masked values
        local_max_index = np.argmax(ddy[mask])
        idx_corner = valid_indices[local_max_index]
    else:
        idx_corner = None  # or handle the case where no values are < 50

    return {
      'corner_index': idx_corner,
      'corner_x':     x_data[idx_corner],
      'corner_y':     y_data[idx_corner],
      'curvature':    ddy[idx_corner],
	  '2nd_derivative': ddy
    }

def plot_csv_columns(file_path):
    """
    Plots data from the specified columns of a CSV file using column headers.
    
    Parameters:
    file_path (str): Path to the CSV file.
    """
    try:

        # Read the CSV file
        data = pd.read_csv(file_path)

        # Initialize variables with default values
        x_col_index = y_col_index = y2_col_index = 0
        columns = []

        # Try to locate each required column
        try:
            x_col_index = data.columns.get_loc("temperature_PT")
        except KeyError:
            print("Column 'temperature_PT' not found.")
        
        try:
            y_col_index = data.columns.get_loc("sliderRating.markerPos")
        except KeyError:
            print("Column 'sliderRating.markerPos' not found.")

        try:
            y2_col_index = data.columns.get_loc("contact_force")
        except KeyError:
            print("Column 'contact_force' not found.")
            y2_col_index = None  # Allow None if not found

        # Optional VAS response columns
        for col_name in ["sliderRating_VASex1.response", "sliderRating_VASex2.response", "sliderRating_VASex3.response"]:
            try:
                columns.append(data.columns.get_loc(col_name))
            except KeyError:
                print(f"Optional column '{col_name}' not found.")
        
        # Extract the columns
        x_data = data.iloc[:, x_col_index] if x_col_index is not None else None
        y_data = data.iloc[:, y_col_index] if y_col_index is not None else None
        y2_data = pd.to_numeric(data.iloc[:, y2_col_index], errors='coerce') if y2_col_index is not None else pd.Series([0]*len(data))

        x_values = [1, 2, 3]
        y_values = []
        for col in columns:
            try:
                y_values.append(data.iloc[:, col].dropna().values[0])
            except IndexError:
                y_values.append(0)

        if not y_values or len(y_values) != len(x_values):
           y_values = [0] * len(x_values)  # Default to zeros if missing or mismatched

        # Extract the required data
        temperature = x_data
        pain_intensity = y_data
        hand_contact_force = y2_data

        first_valid_idx = temperature.first_valid_index()
        last_valid_idx = temperature.last_valid_index()

        # Detect experiment type
        if temperature[last_valid_idx] > temperature[first_valid_idx]:
            experiment_type = "heat"
            print("Detected heat pain experiment.")
            default_values = [36.5, 37.5, 2.0]
        else:
            experiment_type = "cold"
            print("Detected cold pain experiment.")
            default_values = [24.0, 22.0, 2.0]

        # Ask the user to confirm/edit the values via GUI
        baseline_start_temp, baseline_end_temp, threshold_sd_multiplier = get_user_inputs_gui(default_values)

        # Determine baseline
        if experiment_type == "heat":
           baseline_mask = (temperature >= baseline_start_temp) & (temperature <= baseline_end_temp)
        else:
           baseline_mask = (temperature <= baseline_start_temp) & (temperature >= baseline_end_temp)

        baseline_pain = pain_intensity[baseline_mask]
        pain_baseline_mean = baseline_pain.mean()
        pain_baseline_std = baseline_pain.std()

        # ----- 1. Pain Intensity Metrics -----
        # Pain intensity max before hand is removed (force < 2)
        valid_indices = hand_contact_force >= 2
        if not valid_indices.sum() >= 2:
            if experiment_type == "heat":
               valid_indices = ((temperature > 35.5) & (pain_intensity > 0))
            else:
               valid_indices = ((temperature < 24.5) & (pain_intensity > 0))
        # Extract last two pain intensity values before removal
        last_two_pain_values = pain_intensity[valid_indices].iloc[-2:]
        pain_at_temp_before_removal = last_two_pain_values.mean()
        if experiment_type == "heat":
           temp_at_pain_max = temperature[valid_indices].max()
        else:
           temp_at_pain_max = temperature[valid_indices].min()        
		   
        # ----- 2. Temperature at Pain Threshold and Hand Contact Force Metrics -----

        if experiment_type == "heat":
           threshold_condition = (temperature > baseline_end_temp) & (pain_intensity > (pain_baseline_mean + 10 + threshold_sd_multiplier * pain_baseline_std))
           hand_contact_mask = (temperature > baseline_start_temp)  & (hand_contact_force > 2)
           derivative_mask = (temperature >= baseline_start_temp) & (temperature <= temp_at_pain_max)
           temp_at_pain_threshold = temperature[threshold_condition].min()

        else:  
           threshold_condition = (temperature < baseline_end_temp) & (pain_intensity > (pain_baseline_mean + 10 + threshold_sd_multiplier * pain_baseline_std))
           hand_contact_mask = (temperature < baseline_start_temp)  & (hand_contact_force > 2)
           derivative_mask = (temperature <= baseline_start_temp) & (temperature >= temp_at_pain_max)
           temp_at_pain_threshold = temperature[threshold_condition].max()

        # Hand Contact Force Dynamics (Slope Calculation)
        if hand_contact_mask.sum() > 1:
           hand_contact_avg = hand_contact_force[hand_contact_mask].mean()
           hand_contact_std = hand_contact_force[hand_contact_mask].std()
           force_slope = np.polyfit(temperature[hand_contact_mask], hand_contact_force[hand_contact_mask], 1)[0]
        else:
           hand_contact_avg = np.nan
           hand_contact_std = np.nan
           force_slope = np.nan
           print("Insufficient data for contact force dynamics calculation.")    

        # Apply the mask to temperature and pain intensity for curvature calculation
        temperature_filtered = np.array(temperature[derivative_mask])
        pain_filtered = np.array(pain_intensity[derivative_mask])

        # Compute the corner point from splined L-curve 
        res = l_curve_corner(temperature_filtered, pain_filtered, experiment_type, smooth_factor=50)

        # Plot the data
        fig = plt.figure(figsize=(12, 6))
        gs = GridSpec(1, 3, width_ratios=[1, 3, 0])  # 1:4 ratio for the two graphs
        # First graph (1/4 width)
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.bar(x_values, y_values, color=['blue', 'blue', 'blue'], tick_label=['1', '2', '3'])
        ax1.set_title('VAS use')
        ax1.set_xlabel('VAS exercise')
        ax1.set_ylabel(f'Pain intensity, hand contact force')
        ax1.set_ylim(-1, 100)
        ax1.grid(True)

        # Second graph (3/4 width)
        ax2 = fig.add_subplot(gs[0, 1])
        ax2.plot(x_data, y_data, marker='o', linestyle='-', color='b', label="Pain Intensity")
        ax2.plot(x_data, y2_data, marker='.', linestyle='-', color='black', label="Hand Contact Force")
        ax2.set_title('Pain intensity (blue) and hand contact force (black) \n'+file_path)
        ax2.set_xlabel('Temperature/Celsius')
        ax2.set_ylim(-1, 100)
        if experiment_type == "heat":
           ax2.set_xlim(left=35.0, right=49.0)
        else:
           ax2.set_xlim(left=30.0, right=5.0)
        ax2.grid(True)

        # Plot the second derivative in light grey
        ax2.plot(temperature_filtered, 10*res['2nd_derivative'], linestyle='-', color='orange', 
                 alpha=0.8, label="Pain Intensity 2nd Derivative")     

				 # Check if temp_at_pain_threshold is a valid number
        if not np.isnan(temp_at_pain_threshold):
               # Find the closest data point before threshold is reached
               closest_idx = (temperature - temp_at_pain_threshold).abs().idxmin()
               threshold_x = temperature.iloc[closest_idx - 1]
               threshold_y = pain_intensity.iloc[closest_idx - 1]

               # Scatter plot with different color for the threshold point
               ax2.scatter(threshold_x, threshold_y, color='red', s=100, zorder=3, label="Pain Threshold PT")

               # Integrate and shade area between threshold_x and temp_at_pain_max
               if not np.isnan(threshold_x) and not np.isnan(temp_at_pain_max):
                  # Ensure threshold_x < temp_at_pain_max for correct range
                  start_temp = min(threshold_x, temp_at_pain_max)
                  end_temp = max(threshold_x, temp_at_pain_max)

               # Mask for values in the integration range
               integration_mask = (temperature >= start_temp) & (temperature <= end_temp)
               temp_range = temperature[integration_mask]
               pain_range = pain_intensity[integration_mask]
               pain_integral = np.trapz(pain_range, temp_range)
               # Fill area under the curve
               ax2.fill_between(temp_range, pain_range, color='lightgrey', alpha=0.5, label='Integrated Pain Area')

               # Annotation
               ax2.annotate(
                   f"Threshold: {threshold_x:.1f}C", 
                   xy=(threshold_x, threshold_y), xytext=(threshold_x + 0.3, threshold_y + 3),
                       fontsize=10, color='red'
                )

        ax2.legend(loc="upper right")

        # ----- Text Box for Statistics -----
        stats_text = (
            f"Pain Intensity Avg at Baseline {baseline_start_temp:.1f}-{baseline_end_temp:.1f}C: {pain_baseline_mean:.1f} +/- {pain_baseline_std:.1f}\n"
            f"Pain Intensity at Temp Before Removal: {pain_at_temp_before_removal:.1f} at {temp_at_pain_max:.1f}C\n"
            f"Temperature at Individual Pain Threshold: {threshold_x:.1f}C\n"
            f"Integrated Pain Intensity from {start_temp:.1f}C to {end_temp:.1f}C: {pain_integral:.1f}C\n"			
            f"Hand Contact Force Avg: {hand_contact_avg:.1f}N +/- {hand_contact_std:.1f}N\n"
            f"Hand Contact Force Dynamics (Slope): {force_slope:.3f}N/C"
        )

        # Position the text box
        ax2.text(0.02, 0.98, stats_text, transform=ax2.transAxes, fontsize=10, 
                 verticalalignment='top', bbox=dict(facecolor='white', alpha=0.7))
        # Adjust layout
        plt.tight_layout()
        plt.show()

    except FileNotFoundError:
        print("The specified file was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    # Check if a file was dragged onto the script
    if len(sys.argv) < 2:
        print("Usage: Drag and drop a CSV file onto the script to run.")
        # Ask the user for the file path
        file_path = input("Enter the path to the CSV file: ").strip()
    else:
		# Get the file path from the command-line argument
        file_path = sys.argv[1]	

    plot_csv_columns(file_path)
