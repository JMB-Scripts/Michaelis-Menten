####
#
# Python script to fit data with Michaelis Menten equation
# The data need to be in the system international unit and comming from excel 
#
# You need to have a scintific format 12E-03
# for decimal it can be dots or commas  
#
# Becarefull each series are fitted independently
#
# 
#
#
#  Usage:
# 1. python Michaelis-Menten-fit-vXX.py
# 2. Use the "Paste from Excel" button to input data.
# 3. Click the "Save Data and Fit" button to perform the fit and visualize the results.
#
# Dependencies: numpy, tkinter, scipy, matplotlib
#
# View the source code and contribute at https://github.com/JMB-Scripts/Michaelis-Menten
#
#
# 2023 Jean-Marie Bourhis with the help of chat-gpt because I'm a "tanche" in python programming 
#
# For educational purpose only 
#
####

import numpy as np
import tkinter as tk
from tkinter import ttk
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

#Check the configuration 
missing_packages = []

try:
    import numpy as np
except ImportError:
    missing_packages.append("numpy")

try:
    import tkinter as tk
except ImportError:
    missing_packages.append("tkinter")

try:
    from scipy.optimize import curve_fit
except ImportError:
    missing_packages.append("scipy")

# If something is missing 
if missing_packages:
    required = ", ".join(missing_packages)
    print(f"Error: The following packages are missing: {required}")
    print("Please install them and run the script again.")
    exit(1)

################
#
# Let's start
#
###############


# Define the Michaelis-Menten equation
def michaelis_menten(S, Vmax, Km):
    return Vmax * S / (Km + S)

#######
# What happens under the button save data and fit 
########

def save_data_and_fit():
    #This will retrieves the text content from the tkinter.Entry widget
    # Convert only valid, non-empty entries to floats and remove space 
    S_values_float = [float(S_entry.get()) for S_entry in S_entries if S_entry.get().strip() != '']
    
    v0_values_float = [
        [float(entry.get()) for entry in v0_list if entry.get().strip() != ''] 
        for v0_list in v0_entries
    ]
# Filter out any v0 series without valid data
    v0_values_float = [v_values for v_values in v0_values_float if v_values]

     # Check if the lengths are consistent
    if not all(len(S_values_float) == len(v_values) for v_values in v0_values_float):
        print("Error: Mismatch between S values and v0 values.")
        return
    
    #########
    # Define properties of the graph 
    #########
    
    # Serie 1 red, 2 blue , 3 green 
    colors = ['red', 'blue', 'green']
    # For Black and white impression added circle, diamond, square
    markers = ['o', 'D', 's']  

    for idx, v_values in enumerate(v0_values_float):
        # Fit the Michaelis-Menten equation to the data
        params, _ = curve_fit(michaelis_menten, S_values_float, v_values)
        Vmax_estimated, Km_estimated = params

        # Print the estimated parameters in scientific notation
        print(f"For v0 set {idx+1}:")
        print(f"  Estimated Vmax = {Vmax_estimated:.2E}")
        print(f"  Estimated Km = {Km_estimated:.2E}")

         # Plot the data and the fit using specified markers
        plt.scatter(S_values_float, v_values, color=colors[idx], label=f'Observed data {idx+1}', marker=markers[idx])
        S_fit = np.linspace(0, max(S_values_float), 1000)
        v_fit = michaelis_menten(S_fit, Vmax_estimated, Km_estimated)

        # Update the legend with the formatted values
        plt.plot(S_fit, v_fit, color=colors[idx], label=f'Michaelis-Menten Fit {idx+1} (Vmax={Vmax_estimated:.2E}, Km={Km_estimated:.2E})')

    plt.xlabel('[S] (substrate concentration)')
    plt.ylabel('v (reaction rate)')
    plt.legend()
    plt.show()

##########
# Define what happen under the paste from excel button   
######
# Each row from the spreadsheet corresponds to a separate line in the string.
# Each cell in a row is separated by a tab character (\t).
# A   B   C
# 1   2   3
# 4   5   6
# so we need 
#A\t B\t C\n
#1\t 2\t 3\n
#4\t 5\t 6\n

def paste_from_excel():
    clipboard_data = root.clipboard_get()
    rows = clipboard_data.split('\n')
    
    # Check that there are 10 rows or less
    for idx, row in enumerate(rows):
        if idx >= 10:  # Limit to 10 rows
            break
        
        columns = row.split('\t')
        if len(columns) > 0:  
            S_value = float(columns[0].replace(',', '.').strip())
            S_entries[idx].delete(0, tk.END)
            S_entries[idx].insert(0, f"{S_value:.2E}")
            
            # Now for each v0 column
            for v_idx, v0_value in enumerate(columns[1:]):  # This allows for varying numbers of v0 columns
                if v_idx < 3:  # We only handle up to three v0 columns
                    v0_val = float(v0_value.replace(',', '.').strip())
                    v0_entries[v_idx][idx].delete(0, tk.END)
                    v0_entries[v_idx][idx].insert(0, f"{v0_val:.2E}")
##########
# Define what happen under reset_data button  
######
def reset_data():
    for entry in S_entries:
        entry.delete(0, tk.END)
        
    for v0_list in v0_entries:
        for entry in v0_list:
            entry.delete(0, tk.END)


#####
# Define the widget 
#####
root = tk.Tk()
root.title("Michaelis-Menten Data Entry")
frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

#This is for the widget TK 
# Create labels for columns
ttk.Label(frame, text="S (substrate concentration)").grid(column=0, row=0, sticky=tk.W, pady=5)
for idx in range(3):
    ttk.Label(frame, text=f"v0-{idx+1} (observed reaction rate)").grid(column=idx+1, row=0, sticky=tk.W, pady=5)
# Three lists for the three v0 columns
S_entries = []
v0_entries = [[], [], []]  

# Create entries for each row
for i in range(10):
    S_entry = ttk.Entry(frame, width=20)
    S_entry.grid(column=0, row=i+1, pady=5)
    S_entries.append(S_entry)

    for idx in range(3):  # Loop for the three v0 columns
        v0_entry = ttk.Entry(frame, width=20)
        v0_entry.grid(column=idx+1, row=i+1, pady=5)
        v0_entries[idx].append(v0_entry)

####
# Add button
####

# Paste from Excel button
paste_button = ttk.Button(frame, text="1- Paste from Excel", command=paste_from_excel)
paste_button.grid(column=0, row=11, pady=20)

# Save button
save_button = ttk.Button(frame, text="2- Fit Data", command=save_data_and_fit)
save_button.grid(column=1, row=11, pady=20)

# Reset button
reset_button = ttk.Button(frame, text="3- Reset Data", command=reset_data)
reset_button.grid(column=2, row=11, pady=20)

# Made by JMB 2023 Label
made_by_label = ttk.Label(frame, text="UGA, IBS, JMB-Scripts, 2023")
made_by_label.grid(column=3, columnspan=2, row=12, pady=10)  # Spanning 2 columns for centering

root.mainloop()
