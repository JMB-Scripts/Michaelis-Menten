# =============================================================================
# MM-Fit: An Enzyme Kinetics Analysis Application
# Version: 5.0
# =============================================================================
#
# This script creates a desktop application for analyzing enzyme kinetics data
# by fitting it to the Michaelis-Menten model.
#
# Main Libraries Used:
# - PyQt5: For the graphical user interface (GUI).
# - Matplotlib: For plotting and embedding graphs in the GUI.
# - NumPy & SciPy: For numerical operations and the curve-fitting algorithm.
#
# =============================================================================

import os
import sys
import tempfile
import io  # Used for creating an in-memory buffer for high-res printing

# --- PyInstaller/Matplotlib Font Cache Optimization ---
# This is a fix to prevent font-related issues when the app is bundled
# into an .exe or .app file using PyInstaller.
if getattr(sys, 'frozen', False):
    os.environ['MPLCONFIGDIR'] = tempfile.mkdtemp()

# --- Library Imports ---

# PyQt5: For all GUI elements (windows, buttons, tables, etc.)
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QTableWidget, QTableWidgetItem, QDialog,
                             QFileDialog, QMessageBox, QAbstractItemView, QGridLayout,
                             QCheckBox, QHeaderView, QScrollArea, QLineEdit, QSplashScreen)
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import (QPainter, QPixmap, QPen, QFont, QBrush, QFontMetrics)

# Matplotlib: For plotting
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter, ScalarFormatter

# NumPy & SciPy: For numerical analysis and fitting
import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import linregress

# PyQt5 Printer Support
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog


class MainWindow(QMainWindow):
    """The main application window for MM-Fit."""

    # --- Stylesheets defined as class constants for cleanliness ---
    STYLE_ACTION = "QPushButton { background-color: #5DC8A2; color: white; border-radius: 5px; padding: 5px; font-weight: bold; border: none; min-height: 25px; } QPushButton:hover { background-color: #7ED4B4; }"
    STYLE_UTILITY = "QPushButton { background-color: #5B88A5; color: white; border-radius: 5px; padding: 5px; font-weight: bold; border: none; min-height: 25px; } QPushButton:hover { background-color: #79A2BC; }"
    STYLE_SECONDARY = "QPushButton { background-color: #708090; color: white; border-radius: 5px; padding: 5px; font-weight: bold; border: none; min-height: 25px; } QPushButton:hover { background-color: #8492A0; }"
    STYLE_WARNING = "QPushButton { background-color: #D4AC0D; color: white; border-radius: 5px; padding: 5px; font-weight: bold; border: none; min-height: 25px; } QPushButton:hover { background-color: #E7BF3A; }"
    STYLE_QUIT = "QPushButton { background-color: #C0392B; color: white; border-radius: 5px; padding: 5px; font-weight: bold; border: none; min-height: 25px; } QPushButton:hover { background-color: #D9534F; }"

    def __init__(self):
        """Initializes the main window and all its components."""
        super().__init__()
        
        # --- Data Storage ---
        self.excluded_data = {} # Stores {col_index: {row_index1, row_index2}}
        self.column_checkboxes = {} # Stores {col_index: QCheckBox_widget}
        self.processed_data_series_lb = [] # Stores data for the LB plot
        self.Km_best = None # Stores the best-fit Km to help scale the LB plot
        
        # --- Build UI ---
        self._setup_ui()

    def _setup_ui(self):
        """Sets up the main UI layout and widgets."""
        self.setWindowTitle("JMB-Scripts MM-fit - v5.0 -")
        self.resize(1200, 700)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # The main layout is horizontal
        main_layout = QHBoxLayout(self.central_widget)
        
        # Create all the individual widgets
        self._create_widgets()
        # Organize widgets into layouts
        self._create_layouts(main_layout)
        # Connect button clicks to functions
        self._connect_signals()
        # Apply CSS-like styles
        self._apply_styles()

    def _create_widgets(self):
        """Creates all the widgets used in the main window."""
        # Left Panel (for series checkboxes)
        self.column_panel = QWidget()
        self.column_layout = QVBoxLayout(self.column_panel)
        
        # Data Table
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(1)
        self.data_table.setHorizontalHeaderLabels(["[S]0"])
        self.data_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        
        # Buttons
        self.paste_button = QPushButton("1- Paste from Excel")
        self.fit_button = QPushButton("2- MM-Fit")
        self.lineweaver_burk_button = QPushButton("3- LB plot")
        self.exclusion_button = QPushButton("(4- Exclude data)")
        self.save_graph_button = QPushButton("5- Save MM Plot")
        self.print_button = QPushButton("6- Print Report")
        self.reset_button = QPushButton("7- Reset")
        self.quit_button = QPushButton("8- Quit")
        
        # Matplotlib Graph Canvas
        self.figure = Figure(figsize=(10, 6), dpi=100, constrained_layout=True)
        self.canvas = FigureCanvas(self.figure)

    def _create_layouts(self, main_layout):
        """Creates and arranges the layouts for the UI."""
        # Left Panel Layout
        self.column_layout.addWidget(QLabel("Series:"))
        self.column_layout.addStretch()
        
        # Button Panel Layout
        buttons_layout = QVBoxLayout()
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        buttons_layout.addWidget(self.paste_button)
        buttons_layout.addWidget(self.fit_button)
        buttons_layout.addWidget(self.lineweaver_burk_button)
        buttons_layout.addWidget(self.exclusion_button)
        buttons_layout.addWidget(self.save_graph_button)
        buttons_layout.addWidget(self.print_button)
        buttons_layout.addWidget(self.reset_button)
        buttons_layout.addWidget(self.quit_button)
        
        # Add widgets to main layout
        main_layout.addWidget(self.column_panel)
        main_layout.addWidget(self.data_table, 1) # Stretch factor 1
        main_layout.addLayout(buttons_layout)
        main_layout.addWidget(self.canvas, 3)     # Stretch factor 3

    def _connect_signals(self):
        """Connects widget signals to their corresponding slots (methods)."""
        self.paste_button.clicked.connect(self.paste_from_excel)
        self.fit_button.clicked.connect(self.fit_data)
        self.lineweaver_burk_button.clicked.connect(self.show_lineweaver_burk)
        self.exclusion_button.clicked.connect(self.open_exclusion_gui)
        self.save_graph_button.clicked.connect(self.save_graph)
        self.print_button.clicked.connect(self.print_report)
        self.reset_button.clicked.connect(self.reset_data)
        self.quit_button.clicked.connect(self.close)

    def _apply_styles(self):
        """Applies stylesheets to widgets."""
        self.paste_button.setStyleSheet(self.STYLE_UTILITY)
        self.fit_button.setStyleSheet(self.STYLE_ACTION)
        self.lineweaver_burk_button.setStyleSheet(self.STYLE_ACTION)
        self.exclusion_button.setStyleSheet(self.STYLE_SECONDARY)
        self.save_graph_button.setStyleSheet(self.STYLE_UTILITY)
        self.print_button.setStyleSheet(self.STYLE_UTILITY)
        self.reset_button.setStyleSheet(self.STYLE_WARNING)
        self.quit_button.setStyleSheet(self.STYLE_QUIT)

    # --- Core Application Methods ---

    def paste_from_excel(self):
        """Handles pasting data from the clipboard, skipping headers automatically."""
        clipboard = QApplication.clipboard()
        text = clipboard.text().strip()
        if not text:
            return

        rows = text.split('\n')
        
        # Try to convert the first cell to a float. If it fails, it's a header.
        try:
            float(rows[0].split('\t')[0].replace(',', '.'))
            is_header = False
        except (ValueError, IndexError):
            is_header = True

        if is_header:
            rows = rows[1:] # Skip the header row
            if not rows:
                QMessageBox.warning(self, "No Data", "Header detected, but no data rows found.")
                return

        # Clear all old data
        self.reset_data()
        
        # Set table dimensions
        num_cols = len(rows[0].split('\t')) + 1 # +1 for the "Include" column
        self.data_table.setColumnCount(num_cols)
        
        headers = ["Include"] + [f"v{i}" for i in range(num_cols - 2)]
        headers.insert(1, "[S]")
        self.data_table.setHorizontalHeaderLabels(headers)
        self.data_table.setRowCount(len(rows))

        # Populate the table
        for i, row in enumerate(rows):
            # Add the "Include" checkbox to column 0
            checkbox_item = QTableWidgetItem()
            checkbox_item.setCheckState(Qt.CheckState.Checked)
            self.data_table.setItem(i, 0, checkbox_item)
            
            # Add the data values (S, v0, v1, ...)
            values = row.split('\t')
            for j, value in enumerate(values):
                # Replace commas with dots for float conversion
                self.data_table.setItem(i, j + 1, QTableWidgetItem(value.replace(',', '.')))

        self.data_table.resizeColumnsToContents()
        self._update_column_panel(headers) # Create checkboxes for v0, v1...

    def fit_data(self):
        """Performs the main Michaelis-Menten curve fitting and plotting."""
        if self.data_table.rowCount() == 0:
            QMessageBox.warning(self, "No Data", "Please paste data before fitting.")
            return

        # Get all valid data from the table
        processed_data_series_mm, self.processed_data_series_lb = self._get_data_from_table()

        if not processed_data_series_mm:
            QMessageBox.warning(self, "Select Data", "Please select at least one valid data series to fit.")
            return

        self.figure.clear()
        num_series = len(processed_data_series_mm)
        
        # Create a grid for plots: 1 large plot + 1 small plot for each residual
        gs = self.figure.add_gridspec(num_series + 1, 1, height_ratios=[4] + [1] * num_series)
        ax_mm = self.figure.add_subplot(gs[0])
        residual_axes = []
        best_km = float('inf')
        shared_residual_ax = None # To share the X-axis for all residual plots

        # Loop through each data series (v0, v1, etc.)
        for i, data in enumerate(processed_data_series_mm):
            try:
                # --- The Core Fit ---
                # Fit the data to the M-M function
                popt, pcov = curve_fit(self.michaelis_menten, 
                                       data['s_fit'], data['v_fit'], 
                                       p0=[np.max(data['v_fit']), np.mean(data['s_fit'])])
                # Calculate stats (Vmax, Km, R2, errors)
                stats = self._calculate_fit_statistics(popt, pcov, data['s_fit'], data['v_fit'])

                # Store the best Km for the LB plot scaling
                if stats['km'] > 0 and stats['km'] < best_km:
                    best_km = stats['km']
                    self.Km_best = (data['label'], stats['km'])
                
                # --- Plotting ---
                self._plot_mm_series(ax_mm, data, popt, stats, i, num_series)
                
                ax_res = self._plot_residuals(gs[i + 1], shared_residual_ax, data, popt, i, num_series)
                
                # Set the first residual plot as the one to share the X-axis with
                if shared_residual_ax is None:
                    shared_residual_ax = ax_res
                
                residual_axes.append(ax_res)

            except (RuntimeError, ValueError) as e:
                QMessageBox.warning(self, "Fitting Error", f"Could not fit series {data['label']}: {e}")

        # --- Final Plot Formatting ---
        ax_mm.set_xlabel("$[S]_0$")
        ax_mm.set_ylabel("$v_0$")
        ax_mm.set_title("Michaelis-Menten Kinetics")
        ax_mm.legend(fontsize='small')
        
        # Use scientific notation for axes
        scientific_formatter = ScalarFormatter(useMathText=True)
        scientific_formatter.set_scientific(True)
        scientific_formatter.set_powerlimits((-2, 2))

        ax_mm.yaxis.set_major_formatter(scientific_formatter)
        ax_mm.xaxis.set_major_formatter(scientific_formatter)

        # Add the X-axis label only to the *last* residual plot
        if residual_axes:
            residual_axes[-1].set_xlabel("$[S]_0$")
            residual_axes[-1].xaxis.set_major_formatter(scientific_formatter)
        
        self.canvas.draw()

    def show_lineweaver_burk(self):
        """Creates and displays a new window for the Lineweaver-Burk plot."""
        if not self.processed_data_series_lb:
            QMessageBox.warning(self, "Warning", "Please load and fit data first.")
            return

        # Create and show the new window
        self.lb_window = LineweaverBurkWindow(self.processed_data_series_lb, self.excluded_data, self.data_table, self.Km_best, self)
        self.lb_window.show()

    def open_exclusion_gui(self):
        """Opens the dialog for excluding individual data points."""
        if self.data_table.rowCount() == 0:
            QMessageBox.warning(self, "No Data", "Please paste data first.")
            return
        
        # Get all data to show in the dialog
        s_values, v_values = self._get_data_for_exclusion_dialog()
        
        # This is a "callback" function. It will be passed to the dialog
        # and called when the "Apply" button is clicked.
        def on_apply(new_exclusions):
            self.excluded_data = new_exclusions
            self.fit_data() # Re-fit and re-plot the data
            
        dialog = ExclusionDialog(s_values, v_values, self.excluded_data, on_apply, self)
        dialog.exec()

    # --- Helper & Utility Methods ---

    def _get_data_from_table(self):
        """Extracts and organizes data from the QTableWidget for fitting."""
        series_mm, series_lb = [], []
        
        # Loop over columns (v0, v1, ...), starting from index 2
        for col_idx in range(2, self.data_table.columnCount()):
            # Check if the series checkbox is checked
            if col_idx not in self.column_checkboxes or not self.column_checkboxes[col_idx].isChecked():
                continue
            
            # This dict holds the data for *one* series
            data = {'s_fit': [], 'v_fit': [], 'excluded_s': [], 'excluded_v': [], 'original_s': [], 'original_v': []}
            excluded_indices = self.excluded_data.get(col_idx - 2, set()) # Get specific excluded points

            # Loop over all rows
            for row_idx in range(self.data_table.rowCount()):
                # Check if the "Include" checkbox for this *row* is checked
                if self.data_table.item(row_idx, 0) and self.data_table.item(row_idx, 0).checkState() == Qt.CheckState.Checked:
                    try:
                        s_val = float(self.data_table.item(row_idx, 1).text())
                        v_val = float(self.data_table.item(row_idx, col_idx).text())
                        
                        # Check if this specific point was excluded in the dialog
                        if row_idx not in excluded_indices:
                            data['s_fit'].append(s_val)
                            data['v_fit'].append(v_val)
                        else:
                            data['excluded_s'].append(s_val)
                            data['excluded_v'].append(v_val)
                        
                        # Store data for LB plot (which needs 1/x, 1/y)
                        if s_val != 0 and v_val != 0:
                            data['original_s'].append(s_val)
                            data['original_v'].append(v_val)
                    except (ValueError, AttributeError):
                        continue # Skip empty or invalid cells
            
            # Only add the series if it has enough data to fit
            if len(data['s_fit']) >= 2:
                for key in data: data[key] = np.array(data[key])
                data['label'] = self.data_table.horizontalHeaderItem(col_idx).text()
                series_mm.append(data)
                
                # Add the 1/x, 1/y data for the LB plot
                series_lb.append((1/data['original_s'] if data['original_s'].size > 0 else np.array([]), 
                                  1/data['original_v'] if data['original_v'].size > 0 else np.array([]), 
                                  data['label'], data['original_s'], data['original_v']))
                
        return series_mm, series_lb
    
    def _calculate_fit_statistics(self, popt, pcov, s_fit, v_fit):
        """Calculates Vmax, Km, R², and uncertainties from fit results."""
        vmax, km = popt
        # Get standard errors from the covariance matrix
        perr = np.sqrt(np.diag(pcov))
        vmax_se, km_se = perr
        
        # Calculate relative standard error (as percentage)
        vmax_rse = (vmax_se / abs(vmax)) * 100 if vmax != 0 else np.inf
        km_rse = (km_se / abs(km)) * 100 if km != 0 else np.inf

        # Calculate R-squared
        ss_res = np.sum((v_fit - self.michaelis_menten(s_fit, *popt))**2)
        ss_tot = np.sum((v_fit - np.mean(v_fit))**2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        return {'vmax': vmax, 'km': km, 'r_squared': r_squared, 
                'vmax_se': vmax_se, 'km_se': km_se, 
                'vmax_rse': vmax_rse, 'km_rse': km_rse}

    def _plot_mm_series(self, ax, data, popt, stats, index, total):
            """Plots a single data series on the Michaelis-Menten graph."""
            # Use the pastel 'Set2' colormap
            color = plt.cm.Set2(index % 8) # % 8 to loop colors if > 8 series
            
            # Plot included data as circles
            ax.scatter(data['s_fit'], data['v_fit'], label=f"Data {data['label']}", color=color, s=20)
            # Plot excluded data as 'x'
            if data['excluded_s'].size > 0:
                ax.scatter(data['excluded_s'], data['excluded_v'], color=color, marker='x', alpha=0.5, s=20)

            # Generate S values for plotting the fit line
            s_max = np.max(np.concatenate((data['s_fit'], data['excluded_s']))) if np.concatenate((data['s_fit'], data['excluded_s'])).size > 0 else 1
            s_plot = np.linspace(0, s_max * 1.2, 100)
            
            # Create the label text for the legend
            fit_label = (f"Fit {data['label']} (R²={stats['r_squared']:.3f})\n"
                         f"$V_{{max}}$ = {stats['vmax']:.2e} (± {stats['vmax_se']:.1e} | {stats['vmax_rse']:.0f}%)\n"
                         f"$K_m$   = {stats['km']:.2e} (± {stats['km_se']:.1e} | {stats['km_rse']:.0f}%)")
            
            # Plot the fit line
            ax.plot(s_plot, self.michaelis_menten(s_plot, *popt), '-', label=fit_label, color=color)

            # Add invisible guide lines (useful for toggling visibility later)
            ax.axhline(y=stats['vmax'], color=color, linestyle='--', linewidth=1, alpha=0)
            ax.axhline(y=stats['vmax'] / 2, color=color, linestyle='--', linewidth=1, alpha=0)
            ax.axvline(x=stats['km'], color=color, linestyle='--', linewidth=1, alpha=0)


    def _plot_residuals(self, subplot_spec, share_ax, data, popt, index, total):
        """Plots the residuals for a single data series."""
        ax_res = self.figure.add_subplot(subplot_spec, sharex=share_ax)
        color = plt.cm.Set2(index % 8)
        
        # Residuals = (actual Y) - (predicted Y)
        residuals = data['v_fit'] - self.michaelis_menten(data['s_fit'], *popt)
        ax_res.scatter(data['s_fit'], residuals, color=color, s=20)
        
        # Plot excluded residuals
        if data['excluded_s'].size > 0:
            excluded_residuals = data['excluded_v'] - self.michaelis_menten(data['excluded_s'], *popt)
            ax_res.scatter(data['excluded_s'], excluded_residuals, color=color, marker='x', alpha=0.5, s=20)
        
        # Draw the y=0 line and a 5% tolerance band
        ax_res.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        tolerance = 0.05 * self.michaelis_menten(data['s_fit'], *popt)
        ax_res.fill_between(data['s_fit'], -tolerance, tolerance, color=color, alpha=0.15)
        
        ax_res.set_ylabel("Residuals")
        ax_res.yaxis.set_major_formatter(FormatStrFormatter('%.2e'))
        
        # Hide X-axis labels for all but the last residual plot
        if index < total - 1:
            ax_res.tick_params(axis='x', labelbottom=False)
        return ax_res

    def _update_column_panel(self, headers):
        """Dynamically creates the series checkboxes on the left panel."""
        # Clear old checkboxes
        for checkbox in self.column_checkboxes.values():
            checkbox.deleteLater()
        self.column_checkboxes.clear()

        # Create new checkboxes for each data column (v0, v1, ...)
        for col in range(2, self.data_table.columnCount()):
            checkbox = QCheckBox(headers[col])
            checkbox.setChecked(True)
            self.column_layout.insertWidget(self.column_layout.count() - 1, checkbox)
            self.column_checkboxes[col] = checkbox
    
    def _get_data_for_exclusion_dialog(self):
        """Gathers all data from the table to populate the exclusion dialog."""
        s_values, v_values = [], {}
        for row in range(self.data_table.rowCount()):
            try:
                s_values.append(float(self.data_table.item(row, 1).text()))
            except (ValueError, AttributeError):
                s_values.append(np.nan) # Handle empty S cells
            
            for col in range(2, self.data_table.columnCount()):
                v_values.setdefault(col - 2, [])
                try:
                    v_values[col - 2].append(float(self.data_table.item(row, col).text()))
                except (ValueError, AttributeError):
                    v_values[col - 2].append(np.nan) # Handle empty V cells
        return s_values, v_values

    # --- Print & Save Functions ---

    def _print_figure(self, figure, parent):
        """Opens a print dialog for a given Matplotlib figure (e.g., the LB plot)."""
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, parent)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            painter = QPainter(printer)
            
            # Save the figure to an in-memory buffer at 600 DPI
            buffer = io.BytesIO()
            figure.savefig(buffer, format='png', dpi=600, bbox_inches='tight')
            
            # Load that image data into a QPixmap
            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue())
            
            # Scale the pixmap to fit the printer page
            page_rect = printer.pageRect()
            scaled_pixmap = pixmap.scaled(page_rect.size(), 
                                          Qt.KeepAspectRatio, 
                                          Qt.SmoothTransformation)
            
            # Center and draw the pixmap
            x_offset = (page_rect.width() - scaled_pixmap.width()) / 2
            y_offset = (page_rect.height() - scaled_pixmap.height()) / 2
            
            painter.drawPixmap(int(x_offset), int(y_offset), scaled_pixmap)
            painter.end()

    def print_report(self):
        """Prints a single-page report containing the plot and data table."""
        if self.data_table.rowCount() == 0:
            QMessageBox.warning(self, "No Data", "Please paste data before printing a report.")
            return

        printer = QPrinter(QPrinter.HighResolution)
        printer.setPageSize(QPrinter.A4)
        printer.setOrientation(QPrinter.Portrait)
        
        dialog = QPrintDialog(printer, self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            painter = QPainter(printer)
            page_rect = printer.pageRect()
            
            # --- 1. Define Layout Rectangles ---
            margin = 40
            plot_rect = QRectF(page_rect.x() + margin, 
                               page_rect.y() + margin, 
                               page_rect.width() - 2*margin, 
                               page_rect.height() * 0.70 - margin)
            
            table_rect = QRectF(page_rect.x() + margin, 
                                plot_rect.bottom() + 20, 
                                page_rect.width() - 2*margin, 
                                page_rect.height() * 0.25 - margin - 20)

            # --- 2. Draw Plot (High-Res) ---
            # Save the main figure to a buffer at 600 DPI
            buffer = io.BytesIO()
            self.figure.savefig(buffer, format='png', dpi=600, bbox_inches='tight')
            
            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue())
            
            # Scale and draw the plot pixmap
            scaled_pixmap = pixmap.scaled(plot_rect.size().toSize(), 
                                          Qt.KeepAspectRatio, 
                                          Qt.SmoothTransformation)
            x_offset = (plot_rect.width() - scaled_pixmap.width()) / 2
            y_offset = (plot_rect.height() - scaled_pixmap.height()) / 2
            
            painter.drawPixmap(int(plot_rect.x() + x_offset), 
                               int(plot_rect.y() + y_offset), 
                               scaled_pixmap)

            # --- 3. Draw Table ---
            self._draw_table_for_report(painter, table_rect)

            painter.end()
    
    def _draw_table_for_report(self, painter, target_rect):
        """Draws the data table into the target_rect with red highlighting."""
        num_rows = self.data_table.rowCount()
        num_cols = self.data_table.columnCount() - 1 # Skip "Include" column
        if num_rows == 0 or num_cols == 0:
            return

        original_font = painter.font()
        original_pen = painter.pen()

        default_pen = QPen(Qt.black)
        red_pen = QPen(Qt.red)
        
        # --- Set Font and Get Metrics ---
        font = QFont()
        font.setPointSize(10) # Use a small, fixed 8-point font
        painter.setFont(font)
        
        # Get font metrics *from the painter* to get correct high-DPI sizes
        fm = painter.fontMetrics() 
        
        padding = fm.height() // 2 # Padding based on font size
        row_height = fm.height() + padding
        header_height = fm.height() + padding + 4 # Slightly taller header
        
        # --- Calculate Column Widths ---
        col_widths = []
        for j in range(num_cols): # j=0 is [S]0, j=1 is v0...
            # Get header text
            header_text = self.data_table.horizontalHeaderItem(j + 1).text()
            if header_text == "[S]": header_text = "[S]0"
            max_width = fm.horizontalAdvance(header_text) + padding

            # Find the widest data text in this column
            for i in range(num_rows):
                item = self.data_table.item(i, j + 1)
                cell_text = item.text() if item else ""
                try:
                    num_val = float(cell_text)
                    formatted_text = f"{num_val:.2E}" # Format as Sci. Notation
                    max_width = max(max_width, fm.horizontalAdvance(formatted_text) + padding)
                except ValueError:
                    max_width = max(max_width, fm.horizontalAdvance(cell_text) + padding)
            col_widths.append(max_width)
        
        # --- Calculate Table Position ---
        total_table_width = sum(col_widths)
        
        # Align table to the left of the target rectangle
        start_x = target_rect.x() 
        start_y = target_rect.y() 
        
        # Scale columns down if the total width is wider than the page
        if total_table_width > target_rect.width():
            scale_factor = target_rect.width() / total_table_width
            col_widths = [w * scale_factor for w in col_widths]
            
        # --- Draw Headers ---
        current_x = start_x
        for j in range(num_cols):
            header_text = self.data_table.horizontalHeaderItem(j + 1).text()
            if header_text == "[S]": header_text = "[S]0"
            
            cell_rect = QRectF(current_x, start_y, col_widths[j], header_height)
            painter.setPen(default_pen)
            painter.drawRect(cell_rect)
            painter.drawText(cell_rect, Qt.AlignCenter | Qt.TextWordWrap, header_text)
            current_x += col_widths[j]
        
        y_start_data = start_y + header_height

        # --- Draw Data Rows ---
        for i in range(num_rows):
            row_y = y_start_data + i * row_height
            # Stop drawing if we run out of vertical space
            if row_y + row_height > target_rect.bottom():
                break 

            item_0 = self.data_table.item(i, 0)
            is_row_excluded = (item_0 and item_0.checkState() != Qt.CheckState.Checked)

            current_x = start_x
            for j in range(num_cols):
                cell_rect = QRectF(current_x, row_y, col_widths[j], row_height)
                
                item = self.data_table.item(i, j + 1)
                cell_text = item.text() if item else ""
                is_excluded = False

                # Format as scientific notation
                try:
                    num_val = float(cell_text)
                    cell_text = f"{num_val:.2E}"
                except ValueError:
                    pass # Keep as text

                # Determine exclusion status for coloring
                if j == 0:  # [S]0 column
                    is_excluded = is_row_excluded
                else:  # Data columns (v0, v1, ...)
                    is_excluded = is_row_excluded or (i in self.excluded_data.get(j - 1, set()))
                
                # Set pen to red if excluded, black otherwise
                painter.setPen(red_pen if is_excluded else default_pen)
                
                painter.drawRect(cell_rect)
                painter.drawText(cell_rect, Qt.AlignCenter | Qt.TextWordWrap, cell_text)
                current_x += col_widths[j]

        # Restore painter's original font and pen
        painter.setFont(original_font)
        painter.setPen(original_pen)


    def save_graph(self):
        """Opens a file dialog to save the current MM plot as an image."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Save plot", "", "Images (*.png *.jpg *.pdf)")
        if file_path:
            # Save the figure at 600 DPI for high quality
            self.figure.savefig(file_path, bbox_inches='tight', dpi=600)
            QMessageBox.information(self, "Plot Saved", f"The plot has been saved to:\n{file_path}")

    def reset_data(self):
        """Clears all data from the application to start a fresh analysis."""
        self.data_table.clearContents()
        self.data_table.setRowCount(0)
        self.data_table.setColumnCount(1)
        self.data_table.setHorizontalHeaderLabels(["[S]"])
        self._update_column_panel([])
        self.excluded_data.clear()
        self.figure.clear()
        self.canvas.draw()

    @staticmethod
    def michaelis_menten(s, vmax, km):
        """The Michaelis-Menten equation."""
        return (vmax * s) / (km + s)


class LineweaverBurkWindow(QMainWindow):
    """A separate window for displaying the Lineweaver-Burk plot."""
    def __init__(self, lb_series_data, excluded_data, data_table, km_best, parent=None):
        super().__init__(parent)
        self.lb_series_data = lb_series_data
        self.excluded_data = excluded_data
        self.data_table = data_table
        self.km_best = km_best
        self._setup_ui()
        self._prepare_data_and_plot()
        
    @staticmethod
    def linear_model(x, m, c):
        """A simple linear model: y = mx + c"""
        return m * x + c
        
    def _setup_ui(self):
        """Sets up the UI for the Lineweaver-Burk window."""
        self.setWindowTitle("Lineweaver-Burk Plot")
        self.resize(800, 700)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Matplotlib canvas and figure
        self.figure = Figure(figsize=(8, 6), dpi=100, constrained_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        main_layout.addWidget(self.canvas)

        # --- Controls Layout ---
        controls_layout = QHBoxLayout()
        self.show_fit_checkbox = QCheckBox("Display linear fit")
        self.show_fit_checkbox.stateChanged.connect(self._prepare_data_and_plot)
        controls_layout.addWidget(self.show_fit_checkbox)
        controls_layout.addStretch()

        # Axis scale inputs
        scale_layout = QGridLayout()
        self.xmin_input, self.xmax_input = QLineEdit(), QLineEdit()
        self.ymin_input, self.ymax_input = QLineEdit(), QLineEdit()
        self.xmin_input.setPlaceholderText("X min")
        self.xmax_input.setPlaceholderText("X max")
        self.ymin_input.setPlaceholderText("Y min")
        self.ymax_input.setPlaceholderText("Y max")
        scale_layout.addWidget(QLabel("X:"), 0, 0); scale_layout.addWidget(self.xmin_input, 0, 1); scale_layout.addWidget(self.xmax_input, 0, 2)
        scale_layout.addWidget(QLabel("Y:"), 1, 0); scale_layout.addWidget(self.ymin_input, 1, 1); scale_layout.addWidget(self.ymax_input, 1, 2)
        controls_layout.addLayout(scale_layout)

        # Control buttons
        apply_button = QPushButton("Apply Scale"); apply_button.clicked.connect(self._prepare_data_and_plot)
        apply_button.setStyleSheet(MainWindow.STYLE_SECONDARY)
        
        # This button calls the main window's generic figure printer
        print_button = QPushButton("Print"); print_button.clicked.connect(lambda: self.parent()._print_figure(self.figure, self))
        print_button.setStyleSheet(MainWindow.STYLE_UTILITY) 
        
        close_button = QPushButton("Close")
        close_button.setStyleSheet(MainWindow.STYLE_QUIT)
        close_button.clicked.connect(self.close)
        
        controls_layout.addWidget(apply_button)
        controls_layout.addWidget(print_button)
        controls_layout.addWidget(close_button)
        main_layout.addLayout(controls_layout)

    def _prepare_data_and_plot(self):
        """Prepares the data by separating included/excluded points and calls the plot function."""
        self.lb_plot_data = []
        
        # Loop over all series
        for i, (_, _, label, _, _) in enumerate(self.lb_series_data):
            series_data = {'label': label, 'included_inv_s': [], 'included_inv_v': [], 'excluded_inv_s': [], 'excluded_inv_v': []}
            excluded_indices = self.excluded_data.get(i, set())
            
            # Loop over all rows
            for row in range(self.data_table.rowCount()):
                # Check if the row is included
                if self.data_table.item(row, 0) and self.data_table.item(row, 0).checkState() == Qt.CheckState.Checked:
                    try:
                        s_val = float(self.data_table.item(row, 1).text())
                        v_val = float(self.data_table.item(row, i + 2).text())
                        if s_val != 0 and v_val != 0:
                            inv_s, inv_v = 1/s_val, 1/v_val
                            # Check if the specific point is excluded
                            if row not in excluded_indices:
                                series_data['included_inv_s'].append(inv_s)
                                series_data['included_inv_v'].append(inv_v)
                            else:
                                series_data['excluded_inv_s'].append(inv_s)
                                series_data['excluded_inv_v'].append(inv_v)
                    except (ValueError, AttributeError):
                        continue # Skip empty/invalid cells
            self.lb_plot_data.append(series_data)
        
        # Redraw the plot with the newly processed data
        self._update_plot()

    def _update_plot(self):
            """Clears and redraws the Lineweaver-Burk plot with intelligent auto-scaling and fit uncertainties."""
            self.ax.clear()
            show_fit = self.show_fit_checkbox.isChecked()
            all_inv_s, all_inv_v, x_intercepts = [], [], []

            for i, data in enumerate(self.lb_plot_data):
                color = plt.cm.Set2(i % 8) # Use pastel colormap
                
                all_inv_s.extend(data['included_inv_s']); all_inv_s.extend(data['excluded_inv_s'])
                all_inv_v.extend(data['included_inv_v']); all_inv_v.extend(data['excluded_inv_v'])
                
                # Plot included points as circles, excluded as 'x'
                self.ax.scatter(data['included_inv_s'], data['included_inv_v'], label=f"Series {data['label']}", color=color)
                self.ax.scatter(data['excluded_inv_s'], data['excluded_inv_v'], color=color, alpha=0.5, marker='x')

                # If "Display fit" is checked, perform linear regression
                if show_fit and data['included_inv_s']:
                    try:
                        x_data = np.array(data['included_inv_s'])
                        y_data = np.array(data['included_inv_v'])
                        
                        # Fit y = mx + c
                        popt, pcov = curve_fit(self.linear_model, x_data, y_data)
                        slope, intercept = popt
                        
                        # --- Calculate Errors ---
                        perr = np.sqrt(np.diag(pcov))
                        slope_se, intercept_se = perr
                        
                        # Vmax = 1 / intercept
                        vmax_rse = (intercept_se / abs(intercept)) * 100 if intercept != 0 else np.inf
                        # Km = slope / intercept
                        km_rse = np.sqrt((slope_se / slope)**2 + (intercept_se / intercept)**2) * 100 if slope != 0 and intercept != 0 else np.inf

                        # Calculate Vmax and Km from the fit
                        lb_vmax = 1 / intercept if intercept != 0 else np.inf
                        lb_km = slope / intercept if intercept != 0 else np.inf
                        x_intercept = -1 / lb_km if lb_km != 0 else 0
                        x_intercepts.append(x_intercept)

                        # Propagate absolute errors
                        lb_vmax_se = (vmax_rse / 100) * abs(lb_vmax) if np.isfinite(vmax_rse) and np.isfinite(lb_vmax) else np.inf
                        lb_km_se = (km_rse / 100) * abs(lb_km) if np.isfinite(km_rse) and np.isfinite(lb_km) else np.inf
                        
                        # Calculate R-squared
                        ss_res = np.sum((y_data - self.linear_model(x_data, *popt))**2)
                        ss_tot = np.sum((y_data - np.mean(y_data))**2)
                        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
                        
                        # Plot the fit line
                        max_s = max(x_data) * 1.2 if len(x_data) > 0 else 0
                        s_plot = np.linspace(x_intercept * 1.1, max_s, 100)
                        
                        fit_label = (f"Fit {data['label']} (R²={r_squared:.3f})\n"
                                     f"$V_{{max}}$ = {lb_vmax:.2e} (± {lb_vmax_se:.1e} | {vmax_rse:.0f}%)\n"
                                     f"$K_m$   = {lb_km:.2e} (± {lb_km_se:.1e} | {km_rse:.0f}%)")
                        self.ax.plot(s_plot, self.linear_model(s_plot, *popt), '-', color=color, label=fit_label)

                    except (ValueError, TypeError, RuntimeError):
                        pass # Fail silently if regression is not possible
            
            # --- Auto-scaling Logic ---
            # Try to show the x-intercept
            min_x_auto = -1.0
            if x_intercepts and min(x_intercepts) < 0:
                min_x_auto = min(x_intercepts) * 1.2
            elif self.km_best: # Fallback to the MM plot's best Km
                _, km_val = self.km_best
                if km_val > 0:
                    min_x_auto = (-1 / km_val) * 1.2
            elif all_inv_s and min(all_inv_s) >= 0:
                min_x_auto = -0.1 * max(all_inv_s)
            
            max_x_auto = max(all_inv_s) * 1.2 if all_inv_s else 1.0
            min_y_auto = min(all_inv_v) * 1.2 if all_inv_v and min(all_inv_v) < 0 else -0.1 * (max(all_inv_v) if all_inv_v else 1)
            max_y_auto = max(all_inv_v) * 1.2 if all_inv_v else 1.0
            
            # Apply user-defined scales if present, otherwise use auto-scale
            try:
                xmin = float(self.xmin_input.text()) if self.xmin_input.text() else min_x_auto
                xmax = float(self.xmax_input.text()) if self.xmax_input.text() else max_x_auto
                ymin = float(self.ymin_input.text()) if self.ymin_input.text() else min_y_auto
                ymax = float(self.ymax_input.text()) if self.ymax_input.text() else max_y_auto
                self.ax.set_xlim(xmin, xmax); self.ax.set_ylim(ymin, ymax)
            except ValueError:
                self.ax.set_xlim(min_x_auto, max_x_auto); self.ax.set_ylim(min_y_auto, max_y_auto)

            # --- Final Plot Formatting ---
            self.ax.axvline(x=0, color='black', linewidth=1.5); self.ax.axhline(y=0, color='black', linewidth=1.5)
            self.ax.set_xlabel("1/$[S]_0$"); self.ax.set_ylabel("1/$v_0$")
            
            formatter = ScalarFormatter(useMathText=True)
            formatter.set_scientific(True)
            formatter.set_powerlimits((-2, 2))
            self.ax.xaxis.set_major_formatter(formatter)
            self.ax.yaxis.set_major_formatter(formatter)
            
            self.ax.set_title("Lineweaver-Burk Plot"); self.ax.legend(fontsize='small'); self.ax.grid(True)
            self.canvas.draw()


class ExclusionDialog(QDialog):
    """A dialog for selecting individual data points to exclude from fits."""
    def __init__(self, s_values, v_values, initial_exclusions, apply_callback, parent=None):
        super().__init__(parent)
        self.apply_callback = apply_callback # Function to call on "Apply"
        self.checkboxes = [] # To store all created checkboxes
        self._setup_ui(s_values, v_values, initial_exclusions)

    def _setup_ui(self, s_values, v_values, initial_exclusions):
        """Builds the dynamic grid of checkboxes for the dialog."""
        self.setWindowTitle("Exclude Data Points")
        self.resize(600, 400)
        
        main_layout = QVBoxLayout(self)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        grid_widget = QWidget()
        grid = QGridLayout(grid_widget)

        # Create column headers
        grid.addWidget(QLabel("<b>[S]0</b>"), 0, 0)
        for v_idx in v_values:
            grid.addWidget(QLabel(f"<b>Series v{v_idx}</b>"), 0, 1 + v_idx * 2, 1, 2, Qt.AlignmentFlag.AlignCenter)

        # Create rows
        for row_idx, s_val in enumerate(s_values):
            # Add [S]0 value
            grid.addWidget(QLabel(f"{s_val:.2E}" if not np.isnan(s_val) else "N/A"), row_idx + 1, 0)
            
            # Add a checkbox and a v-value label for each series
            for v_idx, v_list in v_values.items():
                is_excluded = row_idx in initial_exclusions.get(v_idx, set())
                cb = QCheckBox()
                cb.setChecked(is_excluded)
                self.checkboxes.append((v_idx, row_idx, cb)) # Store checkbox with its ID
                
                v_val_str = ""
                if row_idx < len(v_list) and not np.isnan(v_list[row_idx]):
                    v_val_str = f"{v_list[row_idx]:.2E}"
                
                grid.addWidget(cb, row_idx + 1, 1 + v_idx * 2, Qt.AlignmentFlag.AlignCenter)
                grid.addWidget(QLabel(v_val_str), row_idx + 1, 2 + v_idx * 2)
        
        scroll_area.setWidget(grid_widget)
        main_layout.addWidget(scroll_area)
        
        # Add "Apply" button
        button_layout = QHBoxLayout()
        apply_button = QPushButton("Apply and Re-Fit")
        apply_button.clicked.connect(self._apply_and_close)
        button_layout.addStretch()
        button_layout.addWidget(apply_button)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)

    def _apply_and_close(self):
        """Gathers checkbox states and sends them back to the main window."""
        new_exclusions = {}
        # Loop through all stored checkboxes
        for v_idx, row_idx, cb in self.checkboxes:
            if cb.isChecked():
                # Build the exclusion dictionary
                new_exclusions.setdefault(v_idx, set()).add(row_idx)
        
        # Send the dictionary back to the main window
        self.apply_callback(new_exclusions)
        self.accept()


# --- Application Entry Point ---
if __name__ == '__main__':
    # This block only runs when the script is executed directly
    app = QApplication(sys.argv)
    
    main_window = MainWindow()
    main_window.show()
        
    sys.exit(app.exec())