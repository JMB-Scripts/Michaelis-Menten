####
#
# The goal is to find a simple way to fit Michaelis Menten equation during biochemistry practicals.
#
# Python script to fit data with Michaelis Menten equation
# The data need to be in the system international unit and coming from excel 
#
# You need to have a scientific format 1,2E-03 or 1.2E-03
# 
# Be careful each series are fitted independently
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
# Thanks to Sylvie, Olivier, Jérome the "MEB biochemistry Team" for their help  
#
# For educational purpose only 
#
####
import webbrowser
import numpy as np
import tkinter as tk
from tkinter import ttk
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

# Define the Michaelis-Menten equation
def michaelis_menten(S, Vmax, Km):
    return Vmax * S / (Km + S)

# Action for the "Save Data and Fit" button
def save_data_and_fit():
    # Convert only valid, non-empty entries to floats
    S_values_float = [float(S_entry.get()) for S_entry in S_entries if S_entry.get().strip() != '']
    
    v0_values_float = [
        [float(entry.get()) for entry in v0_list if entry.get().strip() != ''] 
        for v0_list in v0_entries
    ]
    v0_values_float = [v_values for v_values in v0_values_float if v_values]
    
    if not all(len(S_values_float) == len(v_values) for v_values in v0_values_float):
        print("Error: Mismatch between S values and v0 values.")
        return
    
    # Plotting
    # color and marker for each series
    colors = ['red', 'blue', 'green']
    markers = ['o', 'D', 's'] 

    # Loop through each set of v0 values. The variable `idx` is the index (0, 1, 2 for the three v0 columns)
    # and `v_values` is the list of v0 values for the current set.
    # `curve_fit` is a function from the scipy library that fits a curve to the provided data.
    # Here, we're fitting the Michaelis-Menten equation to our data. 
    # The function returns optimized parameters (Vmax and Km) for the fit and a covariance matrix.
    # We are only interested in the optimized parameters, hence the use of `params, _` 
    # (where `_` is a common convention in Python to ignore unwanted values).

    for idx, v_values in enumerate(v0_values_float):
        params, _ = curve_fit(michaelis_menten, S_values_float, v_values)
        Vmax_estimated, Km_estimated = params

        print(f"For v0 set {idx+1}:")
        print(f"  Estimated Vmax = {Vmax_estimated:.2E}")
        print(f"  Estimated Km = {Km_estimated:.2E}")

        plt.scatter(S_values_float, v_values, color=colors[idx], label=f'Observed data {idx+1}', marker=markers[idx])
        S_fit = np.linspace(0, max(S_values_float), 1000)
        v_fit = michaelis_menten(S_fit, Vmax_estimated, Km_estimated)
        plt.plot(S_fit, v_fit, color=colors[idx], label=f'Michaelis-Menten Fit {idx+1} (Vmax={Vmax_estimated:.2E}, Km={Km_estimated:.2E})')

    plt.xlabel('[S]0 (substrate concentration)')
    plt.ylabel('v0 (reaction rate)')

    # Format x-axis to be in 10^xx
    ax = plt.gca()
    ax.xaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax.ticklabel_format(axis="x", style="sci", scilimits=(0,0), useMathText=True)
    # Format y-axis to b e in 10^yy
    ay = plt.gca()
    ay.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax.ticklabel_format(axis="y", style="sci", scilimits=(0,0), useMathText=True)
    
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
    
    for idx, row in enumerate(rows):
        if idx >= 10:
            break
        
        columns = row.split('\t')
        if len(columns) > 0:
            S_value = float(columns[0].replace(',', '.').strip())
            S_entries[idx].delete(0, tk.END)
            S_entries[idx].insert(0, f"{S_value:.2E}")
            
            for v_idx, v0_value in enumerate(columns[1:]):
                if v_idx < 3:
                    v0_val = float(v0_value.replace(',', '.').strip())
                    v0_entries[v_idx][idx].delete(0, tk.END)
                    v0_entries[v_idx][idx].insert(0, f"{v0_val:.2E}")

# Action for the "Reset Data" button

# Reset values in the widget    
def reset_data():
    for entry in S_entries:
        entry.delete(0, tk.END)
        
    for v0_list in v0_entries:
        for entry in v0_list:
            entry.delete(0, tk.END)

# GUI setup
root = tk.Tk()
root.title("Michaelis-Menten Data Entry")
frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

ttk.Label(frame, text="[S]0 (substrate concentration)").grid(column=0, row=0, sticky=tk.W, pady=5)
for idx in range(3):
    ttk.Label(frame, text=f"v0-{idx+1} (observed reaction rate)").grid(column=idx+1, row=0, sticky=tk.W, pady=5)

S_entries = [ttk.Entry(frame, width=20) for _ in range(10)]
v0_entries = [[ttk.Entry(frame, width=20) for _ in range(10)] for _ in range(3)]

for idx in range(10):
    S_entries[idx].grid(column=0, row=idx+1, padx=5, pady=5)
    for v_idx in range(3):
        v0_entries[v_idx][idx].grid(column=v_idx+1, row=idx+1, padx=5, pady=5)

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
made_by_label = ttk.Label(frame, text="JMB-Scripts - 2023 -")
made_by_label.grid(column=3, columnspan=2, row=11, pady=10)  # Spanning 2 columns for centering

# add links
def open_url(url):
    webbrowser.open(url)
url1 = "https://github.com/JMB-Scripts/Michaelis-Menten"
link1 = ttk.Label(frame, text="GitHub", cursor="hand2", foreground="black", underline=False)
link1.grid(row=12, column=0)
link1.bind("<Button-1>", lambda e: open_url(url1))

url2 = "https://www.univ-grenoble-alpes.fr/"
link2 = ttk.Label(frame, text="UGA", cursor="hand2", foreground="orange", underline=False)
link2.grid(row=12, column=1)
link2.bind("<Button-1>", lambda e: open_url(url2))

url3 = "https://www.ibs.fr/"
link3 = ttk.Label(frame, text="IBS", cursor="hand2", foreground="red", underline=False)
link3.grid(row=12, column=2)
link3.bind("<Button-1>", lambda e: open_url(url3))

root.mainloop()
