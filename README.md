# Michaelis-Menten Equation Fitting Tool

This tool allows users to input data for substrate concentration (`S`) and observed reaction rates (`v0`) to fit the Michaelis-Menten equation. The application provides a graphical user interface to easily input the data and visualize the curve fitting results.

## Features:

- Graphical table to manually input data.
- Paste functionality compatible with data copied from Excel.
- Real-time curve fitting to the Michaelis-Menten equation.
- Visual representation of observed data and fitted curve.
- Output of estimated \( V_{max} \) and \( K_m \) parameters in scientific notation.

## Dependencies:

- `numpy`
- `tkinter`
- `scipy`
- `matplotlib`

## Installation:

Ensure you have Python installed on your system.

Install the required packages using `pip`:

```bash
pip install numpy scipy matplotlib
```
or conda 
```bash
conda install numpy scipy matplotlib
```

## Usage:

1. Run the script:

```bash
python Practicals-Michaelis-Menten-Fit-vXX.py
```

2. Use the graphical interface to input data manually or paste it directly from Excel.
3. Click on "Save Data and Fit" to fit the Michaelis-Menten equation and visualize the results.

## Notes:

Ensure all values are valid and in the correct format like 12E3  (for 12000 e.g., scientific notation) before fitting. If copying from Excel, ensure the data is in two columns with the substrate concentration in the first column and the observed reaction rate in the second.
