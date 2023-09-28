####
#
# Python script to fit data with Michaelis Menten equation
# The data need to be in the system international unit and comming from excel 
#
# 2023 Jean-Marie Bourhis with the help of chat-gpt because I'm a "tanche" in python programming 
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

# ... continue for other packages
if missing_packages:
    required = ", ".join(missing_packages)
    print(f"Error: The following packages are missing: {required}")
    print("Please install them and run the script again.")
    exit(1)

# Define the Michaelis-Menten equation
def michaelis_menten(S, Vmax, Km):
    return Vmax * S / (Km + S)

def save_data_and_fit():
    # Convert only valid, non-empty entries to floats
    S_values_float = [float(S_entry.get()) for S_entry in S_entries if S_entry.get().strip() != '']
    v0_values_float = [float(v0_entry.get()) for v0_entry in v0_entries if v0_entry.get().strip() != '']

    # Check if the lengths are consistent
    if len(S_values_float) != len(v0_values_float):
        print("Error: Mismatch between S values and v0 values.")
        return

    # Fit the Michaelis-Menten equation to the data
    params, covariance = curve_fit(michaelis_menten, S_values_float, v0_values_float)
    Vmax_estimated, Km_estimated = params

    # Print the estimated parameters in scientific notation
    print(f"Estimated Vmax = {Vmax_estimated:.2E}")
    print(f"Estimated Km = {Km_estimated:.2E}")

    # Plot the data and the fit
    plt.scatter(S_values_float, v0_values_float, color='red', label='Observed data')
    S_fit = np.linspace(0, max(S_values_float), 1000)
    v_fit = michaelis_menten(S_fit, Vmax_estimated, Km_estimated)

    # Update the legend with the formatted values
    plt.plot(S_fit, v_fit, label=f'Michaelis-Menten Fit (Vmax={Vmax_estimated:.2E}, Km={Km_estimated:.2E})')

    plt.xlabel('[S] (substrate concentration)')
    plt.ylabel('v (reaction rate)')
    plt.legend()
    plt.show()
# Paste value directly from excel for more convinience 

def paste_from_excel():
    clipboard_data = root.clipboard_get()
    rows = clipboard_data.split('\n')
    
    for idx, row in enumerate(rows):
        if idx >= 10:  # Limit to 10 rows
            break
        columns = row.split('\t')
        if len(columns) >= 2:
            # Replace commas with periods and then convert to float
            S_value = float(columns[0].replace(',', '.').strip())
            v0_value = float(columns[1].replace(',', '.').strip())

            # Update the entries
            S_entries[idx].delete(0, tk.END)
            S_entries[idx].insert(0, f"{S_value:.2E}")  # Format in scientific notation

            v0_entries[idx].delete(0, tk.END)
            v0_entries[idx].insert(0, f"{v0_value:.2E}") 

root = tk.Tk()
root.title("Michaelis-Menten Data Entry")

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Create labels for columns
ttk.Label(frame, text="S (substrate concentration)").grid(column=0, row=0, sticky=tk.W, pady=5)
ttk.Label(frame, text="v0 (observed reaction rate)").grid(column=1, row=0, sticky=tk.W, pady=5)

S_entries = []
v0_entries = []

# Create entries for each row
for i in range(10):
    S_entry = ttk.Entry(frame, width=20)
    v0_entry = ttk.Entry(frame, width=20)
    
    S_entry.grid(column=0, row=i+1, pady=5)
    v0_entry.grid(column=1, row=i+1, pady=5)
    
    S_entries.append(S_entry)
    v0_entries.append(v0_entry)

# Save button
save_button = ttk.Button(frame, text="Save Data and Fit", command=save_data_and_fit)
save_button.grid(column=0, row=11, pady=20)

# Paste from Excel button
paste_button = ttk.Button(frame, text="Paste from Excel", command=paste_from_excel)
paste_button.grid(column=1, row=11, pady=20)

# Made by JMB 2023 Label
made_by_label = ttk.Label(frame, text="UGA, IBS, JMB-Scripts 2023")
made_by_label.grid(column=0, columnspan=2, row=12, pady=10)  # Spanning 2 columns for centering

root.mainloop()
