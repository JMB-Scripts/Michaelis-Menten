####
#
# The goal is to find a simple way to fit Michaelis Menten equation during biochemistry practicals.
#
# Python script to fit data with Michaelis Menten equation
# The data need to be in the system international unit and preferably coming from excel 
#
# You need to have a scientific format 1,2E-03 or 1.2E-03
# 
# Each series are fitted independently
#
#  Usage:
# 1. python MM-fit-vXX.py
# 2. Use the "Paste from Excel" button to input data.
# 3. Click the "Save Data and Fit" button to perform the fit and visualize the results:
#   a- First MM plot with at lower vmax KM and Rsquare and at the bottom the simple residual to have a better view of adnormal points.
#   b- then LB plot for student to fill.
# 4. You can exclude some data if you want by using exclude data button
# 5. a reset button for the next uses (reset values and chkedboxes)
# 6. push quit to quit 
#
# Dependencies: numpy, tkinter, scipy, matplotlib
#
# View the source code and contribute at https://github.com/JMB-Scripts/Michaelis-Menten
#
# 2024 v16 add:
# 1- Rsquare for all fit
# 2- LB representation 
# 3- Residuals of the MM fits
# 4- Exclud data for improving the fit with bad data
# 5- The rest data unchecked previously check excluded data (was harsh to do)
# 6- a better view of the graph with smooth major and minor lines
#
# 2024 Jean-Marie Bourhis with the help of chat-gpt and Claude because I'm a "tanche" in python programming but getting better
# 
# Thanks to Sylvie, Olivier, Jérome, Alex, the "MEB biochemistry Team" for their help  
#
# For educational purpose only 
#
####

import webbrowser
import numpy as np
import tkinter as tk
from tkinter import ttk
from scipy.optimize import curve_fit
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

###################################################
# Check the configuration 
###################################################
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

try:
    import webbrowser
except ImportError:
    missing_packages.append("webbrowser")

# If something is missing 
if missing_packages:
    required = ", ".join(missing_packages)
    print(f"Error: The following packages are missing: {required}")
    print("Please install them and run the script again.")
    exit(1)


###################################################
# Define the Michaelis-Menten equation
###################################################

def michaelis_menten(S, Vmax, Km):
    return Vmax * S / (Km + S)

# Global variable to store Km of the first series in order to scale properly the L&B plot
km_serie1 = None
excluded_data = {0: set(), 1: set(), 2: set()}  # Dictionary to store excluded indices for each series

# Modified save_data_and_fit function
def save_data_and_fit():
    global km_serie1
    
    # Create separate datasets for each series
    datasets = []
    for series in range(3):
        S_values = []
        v0_values = []
        for idx, S_entry in enumerate(S_entries):
            if S_entry.get().strip() != '' and idx not in excluded_data[series] and v0_entries[series][idx].get().strip() != '':
                S_values.append(float(S_entry.get()))
                v0_values.append(float(v0_entries[series][idx].get()))
        datasets.append((S_values, v0_values))
    
    # Michaelis-Menten Plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10), gridspec_kw={'height_ratios': [2, 1]})
    
    colors = ['crimson', 'darkseagreen', 'cornflowerblue']
    markers = ['o', 'v', 'X']
    
    for idx, (S_values, v0_values) in enumerate(datasets):
        if len(S_values) > 0 and len(v0_values) > 0:
            try:
                params, _ = curve_fit(michaelis_menten, S_values, v0_values)
                Vmax_estimated, Km_estimated = params
                
                if idx == 0:
                    km_serie1 = Km_estimated

                print(f"For v0 set {idx+1}:")
                print(f"  Estimated Vmax = {Vmax_estimated:.2E}")
                print(f"  Estimated Km = {Km_estimated:.2E}")
                
                ###################################################
                # Calculate fitted values and R-squared
                ###################################################
                
                v_fit = michaelis_menten(np.array(S_values), Vmax_estimated, Km_estimated)
                ss_total = np.sum((np.array(v0_values) - np.mean(v0_values)) ** 2)
                ss_residual = np.sum((np.array(v0_values) - v_fit) ** 2)
                r_squared = 1 - (ss_residual / ss_total)
                print(f"  R-squared = {r_squared:.2E}")
                
                # Plot the Michaelis-Menten fit on the first subplot
                ax1.scatter(S_values, v0_values, color=colors[idx], label=f'Observed data {idx+1}', marker=markers[idx])
                S_fit = np.linspace(0, max(S_values), 1000)
                v_fit_smooth = michaelis_menten(S_fit, Vmax_estimated, Km_estimated)
                ax1.plot(S_fit, v_fit_smooth, color=colors[idx], 
                         label=f'MM Fit {idx+1} (Vmax={Vmax_estimated:.2E}, Km={Km_estimated:.2E})\nR²={r_squared:.2E}')
                         
                 #plot vmax for enure that we have enough space
                ax1.axhline(y=Vmax_estimated, color=colors[idx], linestyle='--', alpha=0.0)
                
                # Residuals
                v_fit = michaelis_menten(np.array(S_values), Vmax_estimated, Km_estimated)
                residuals = np.array(v0_values) - v_fit
                
                # Scatter plot for residuals on the second subplot
                ax2.scatter(S_values, residuals, color=colors[idx], label=f'Residuals {idx+1}', marker=markers[idx])
            
            except RuntimeError:
                print(f"Error: Could not fit data for series {idx+1}. Skipping this series.")
    
    
    # Format the top plot (Michaelis-Menten plot)
    ax1.set_xlabel('[S]0 (substrate concentration)')
    ax1.set_ylabel('v0 (reaction rate)')
    ax1.xaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax1.ticklabel_format(axis="x", style="sci", scilimits=(0,0), useMathText=True)
    ax1.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax1.ticklabel_format(axis="y", style="sci", scilimits=(0,0), useMathText=True)
    # Show the major grid and style it slightly.
    ax1.grid(which='major', color='#DDDDDD', linewidth=0.8)
    # Show the minor grid as well. Style it in very light gray as a thin,
    # dotted line.
    ax1.grid(which='minor', color='#EEEEEE', linestyle=':', linewidth=0.5)
    # Make the minor ticks and gridlines show.
    ax1.minorticks_on()  
    ax1.grid(True, which='both')
    ax1.legend(loc='lower right')

    # Customize the second plot (Residuals)
    ax2.axhline(0, color='black', linewidth=1.0, linestyle='--')
    ax2.set_xlabel('[S]0 (substrate concentration)')
    ax2.set_ylabel('Residuals (Observed - Fitted)')
    ax2.xaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax2.ticklabel_format(axis="x", style="sci", scilimits=(0,0), useMathText=True)
    ax2.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax2.ticklabel_format(axis="y", style="sci", scilimits=(0,0), useMathText=True)
    ax2.grid(which='major', color='#DDDDDD', linewidth=0.8)
    ax2.grid(which='minor', color='#EEEEEE', linestyle=':', linewidth=0.5)
    ax2.minorticks_on()
    ax2.legend(loc='upper right')
    
    # Adjust layout for better spacing between plots
    plt.tight_layout()
       

    plt.tight_layout()
    plt.show()

###################################################
# Lineweaver-Burk Plot
###################################################

    plt.figure(figsize=(10, 6))
    
    for idx, (S_values, v0_values) in enumerate(datasets):
        if len(S_values) > 0 and len(v0_values) > 0:
            # Mask to exclude zero values
            non_zero_mask = (np.array(S_values) != 0) & (np.array(v0_values) != 0)
            S_values_filtered = np.array(S_values)[non_zero_mask]
            v0_values_filtered = np.array(v0_values)[non_zero_mask]

            # Plot the double inverse of the filtered values
            plt.scatter(1/S_values_filtered, 1/v0_values_filtered, color=colors[idx], 
                        label=f'Observed data {idx+1}', marker=markers[idx], s=20)

    # Customize the axis limits
    if km_serie1:
        x_min = round(-1.5 / km_serie1)
        x_max = min(S_values_filtered)
        x_max = round(1.5/(x_max))  # Add 15% margin
        plt.xlim(x_min,x_max)
        y_min = 0
        plt.ylim(y_min)
    else:
        print("Warning: Unable to set custom axis limits for Lineweaver-Burk plot.")

    # Make the vertical axis at x=0 bold
    plt.axvline(x=0, color='black', linewidth=2)

    # Format axes
    ax = plt.gca()
    ax.xaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax.ticklabel_format(axis="x", style="sci", scilimits=(0,0), useMathText=True)
    ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax.ticklabel_format(axis="y", style="sci", scilimits=(0,0), useMathText=True)
    ax.grid(which='major', color='#DDDDDD', linewidth=0.8)
    ax.grid(which='minor', color='#EEEEEE', linestyle=':', linewidth=0.5)
    ax.minorticks_on()
    plt.xlabel('1/[S]0 (substrate concentration)')
    plt.ylabel('1/v0 (reaction rate)')
    plt.legend(loc='lower right')
    plt.grid(True)
    plt.show()

###################################################
# Data exclusion GUI
###################################################

def open_exclusion_gui():
    global checkboxes 

    exclusion_window = tk.Toplevel(root)
    exclusion_window.title("Exclude Data Points")
    
    frame = ttk.Frame(exclusion_window, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    ttk.Label(frame, text="Select v0 values to exclude:").grid(column=0, row=0, columnspan=7, sticky=tk.W, pady=5)
    
    ttk.Label(frame, text="S0").grid(column=1, row=1, padx=5, pady=2)
    for v_idx in range(3):
        ttk.Label(frame, text=f"v0-{v_idx+1}").grid(column=2+v_idx*2, row=1, padx=5, pady=2, columnspan=2)
    
    checkboxes = []

    for idx in range(10):  # Assuming max 10 data points
        if S_entries[idx].get().strip() != '':
            S_value = float(S_entries[idx].get())
            ttk.Label(frame, text=f"{S_value:.2E}").grid(column=1, row=idx+2, padx=5, pady=2)
            
            for v_idx in range(3):
                if v0_entries[v_idx][idx].get().strip() != '':
                    v0_value = float(v0_entries[v_idx][idx].get())
                    cb_var = tk.BooleanVar(value=idx in excluded_data[v_idx])
                    cb = ttk.Checkbutton(frame, variable=cb_var)
                    cb.grid(column=2+v_idx*2, row=idx+2, padx=5, pady=2)
                    checkboxes.append((v_idx, idx, cb_var))
                    ttk.Label(frame, text=f"{v0_value:.2E}").grid(column=3+v_idx*2, row=idx+2, padx=5, pady=2)
    
    def apply_exclusion():
        global excluded_data
        excluded_data = {0: set(), 1: set(), 2: set()}  # Reset exclusions
        for v_idx, idx, var in checkboxes:
            if var.get():
                excluded_data[v_idx].add(idx)
        exclusion_window.destroy()
        save_data_and_fit()  # Refit the data with excluded points
    
    apply_button = ttk.Button(frame, text="Apply and Refit", command=apply_exclusion)
    apply_button.grid(column=0, row=12, columnspan=7, pady=10)

###################################################
# Define what happens under the paste from excel button   
###################################################

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

###################################################
# Action for the "Reset Data" button
###################################################

def reset_data():
    global checkboxes 
    # Uncheck all checkboxes in the exclusion GUI
    for _, _, cb_var in checkboxes:
        cb_var.set(False)  # Uncheck all checkboxes

    # Reset the global variable that stores the excluded data
    global excluded_data
    excluded_data = {0: set(), 1: set(), 2: set()}

    # remove entry
    for entry in S_entries:
        entry.delete(0, tk.END)
    for v0_list in v0_entries:
        for entry in v0_list:
            entry.delete(0, tk.END)
    
###################################################
# GUI setup
###################################################

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

###################################################
# Paste from Excel button
###################################################

paste_button = ttk.Button(frame, text="1- Paste from Excel", command=paste_from_excel)
paste_button.grid(column=0, row=11, pady=20)

###################################################
# Save button
###################################################

save_button = ttk.Button(frame, text="2- Fit Data", command=save_data_and_fit)
save_button.grid(column=1, row=11, pady=20)

###################################################
# Reset button
###################################################

reset_button = ttk.Button(frame, text="3- Reset Data", command=reset_data)
reset_button.grid(column=2, row=11, pady=20)

###################################################
# Exclude Data button
###################################################

exclude_button = ttk.Button(frame, text="(4- Exclude Data)", command=open_exclusion_gui)
exclude_button.grid(column=3, row=11, pady=20)

###################################################
# Add buttons
###################################################

# Paste from Excel button
paste_button = ttk.Button(frame, text="1- Paste from Excel", command=paste_from_excel)
paste_button.grid(column=0, row=11, pady=20)

# Save button
save_button = ttk.Button(frame, text="2- Fit Data", command=save_data_and_fit)
save_button.grid(column=1, row=11, pady=20)

# Reset button
reset_button = ttk.Button(frame, text="3- Reset Data", command=reset_data)
reset_button.grid(column=2, row=11, pady=20)
###################################################
# Add Quit button function
###################################################

def quit_program():
    root.quit()

###################################################
# Quit button
###################################################

quit_button = ttk.Button(frame, text="Quit", command=quit_program)
quit_button.grid(column=4, row=11, pady=20)

###################################################
# add links
###################################################

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
# Made by JMB 2023 Label
made_by_label = ttk.Label(frame, text="JMB-Scripts - 2024 -")
made_by_label.grid(column=3, columnspan=2, row=12, pady=10)  # Spanning 2 columns for centering

root.mainloop()
