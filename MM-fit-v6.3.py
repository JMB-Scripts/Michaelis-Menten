# =============================================================================
# MM-Fit: An Enzyme Kinetics Analysis Application 
# Version: 6.3 (Unit Formatting & Discrete Hover)
# =============================================================================

import os
import sys
import tempfile
import io
import random
import re

# --- FIX: Persist Matplotlib Cache (Works with Single File Exe) ---
def set_mpl_cache_dir():
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        bundled_cache = os.path.join(sys._MEIPASS, 'pkg_mpl_cache')
        if os.path.exists(bundled_cache):
            os.environ['MPLCONFIGDIR'] = bundled_cache
            return

    app_name = "MM-Fit"
    home = os.path.expanduser("~")
    
    if sys.platform.startswith('win'):
        base_dir = os.getenv('APPDATA') or os.path.join(home, 'AppData', 'Roaming')
    elif sys.platform == 'darwin':
        base_dir = os.path.join(home, 'Library', 'Application Support')
    else:
        base_dir = os.path.join(home, '.config')

    mpl_cache_dir = os.path.join(base_dir, app_name, 'mpl_cache')
    try:
        os.makedirs(mpl_cache_dir, exist_ok=True)
        os.environ['MPLCONFIGDIR'] = mpl_cache_dir
    except Exception as e:
        print(f"Warning: Could not set custom Matplotlib cache: {e}")

set_mpl_cache_dir()

# --- Library Imports ---
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QTableWidget, QTableWidgetItem, QDialog,
                             QFileDialog, QMessageBox, QAbstractItemView, QGridLayout,
                             QCheckBox, QHeaderView, QScrollArea, QLineEdit, QSplashScreen,
                             QDoubleSpinBox, QSlider)
from PyQt5.QtCore import Qt, QRectF, QTimer
from PyQt5.QtGui import (QPainter, QPixmap, QPen, QFont, QBrush, QFontMetrics, QImage)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.ticker import FormatStrFormatter, ScalarFormatter
import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import linregress
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog

class UnitDialog(QDialog):
    """Dialog for setting X and Y axes units with ^ and _ format hint."""
    def __init__(self, current_x, current_y, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Définir les Unités")
        self.resize(360, 160)
        
        layout = QVBoxLayout(self)
        
        info = QLabel("Tips :Use '_' for subscripts and '^' for superscripts. For example, µmol.L^-1.s^-1 will render as µmol.L⁻¹.s⁻¹.")
        info.setStyleSheet("color: #666; font-size: 11px; margin-bottom: 10px;")
        layout.addWidget(info)
        
        grid = QGridLayout()
        grid.addWidget(QLabel("Unité axe X ([S]0) :"), 0, 0)
        self.x_input = QLineEdit(current_x)
        grid.addWidget(self.x_input, 0, 1)
        
        grid.addWidget(QLabel("Unité axe Y (v0) :"), 1, 0)
        self.y_input = QLineEdit(current_y)
        grid.addWidget(self.y_input, 1, 1)
        layout.addLayout(grid)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn = QPushButton("Valider")
        btn.clicked.connect(self.accept)
        btn.setStyleSheet(MainWindow.STYLE_ACTION)
        btn_layout.addWidget(btn)
        
        layout.addLayout(btn_layout)


class PedagogicalSimulation(QMainWindow):
    """How-To-Fit: Interactive window explaining the regression process."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("MM-Fit - How-To-Fit")
        self.resize(1150, 750)
        
        self.num_frames = 120 
        self.current_frame = 0
        
        self.vmax_true = 100.0
        self.km_true = 5.0
        self.s_data = np.linspace(0, 25, 15)
        
        self._generate_base_data()
        self._setup_ui()
        self.generate_trajectory()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame)
        self.timer.setInterval(60) 
        self.update_plot()

    def _generate_base_data(self):
        np.random.seed(42)
        def mm_eq(s, vmax, km): return (vmax * s) / (km + s)
            
        self.v_data = mm_eq(self.s_data, self.vmax_true, self.km_true) + np.random.normal(0, 4, len(self.s_data))
        self.v_data = np.maximum(self.v_data, 0.5)
        
        popt, _ = curve_fit(mm_eq, self.s_data, self.v_data, p0=[120, 10])
        self.vmax_opt, self.km_opt = popt
        
        self.target_idx = 7 
        self.target_s = self.s_data[self.target_idx]
        self.target_v_exp = self.v_data[self.target_idx]

    def generate_trajectory(self):
        vmax_start = self.spin_vmax.value()
        km_start = self.spin_km.value()
        
        t = np.linspace(0, 5, self.num_frames - 10)
        approche = np.exp(-t)
        vmax_base = self.vmax_opt + (vmax_start - self.vmax_opt) * approche
        km_base = self.km_opt + (km_start - self.km_opt) * approche
        
        dir_vmax = 1 if self.vmax_opt > vmax_start else -1
        dir_km = 1 if self.km_opt > km_start else -1
        
        vmax_over_target = self.vmax_opt + dir_vmax * (self.vmax_opt * 0.08)
        km_over_target = self.km_opt + dir_km * (self.km_opt * 0.15)
        
        vmax_over = np.linspace(vmax_base[-1], vmax_over_target, 5) 
        km_over = np.linspace(km_base[-1], km_over_target, 5)
        
        vmax_end = np.full(5, self.vmax_opt)
        km_end = np.full(5, self.km_opt)
        
        self.vmax_traj = np.concatenate([vmax_base, vmax_over, vmax_end])
        self.km_traj = np.concatenate([km_base, km_over, km_end])

        self.ssr_traj = np.array([
            np.sum((self.v_data - (v * self.s_data) / (k + self.s_data))**2)
            for v, k in zip(self.vmax_traj, self.km_traj)
        ])
        
        self.current_frame = 0
        if hasattr(self, 'slider'):
            self.slider.setValue(0)
        self.update_plot()

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        top_bar_layout = QHBoxLayout()
        
        top_bar_layout.addWidget(QLabel("Initial Vmax:"))
        self.spin_vmax = QDoubleSpinBox()
        self.spin_vmax.setRange(0, 300)
        self.spin_vmax.setValue(30.0) 
        top_bar_layout.addWidget(self.spin_vmax)
        
        top_bar_layout.addSpacing(20)
        
        top_bar_layout.addWidget(QLabel("Initial Km:"))
        self.spin_km = QDoubleSpinBox()
        self.spin_km.setRange(0.1, 50)
        self.spin_km.setValue(15.0) 
        top_bar_layout.addWidget(self.spin_km)
        
        top_bar_layout.addSpacing(20)
        
        btn_recalc = QPushButton("🔄 Calculate Trajectory")
        btn_recalc.setStyleSheet("font-weight: bold; background-color: #e0f7fa;")
        btn_recalc.clicked.connect(self.generate_trajectory)
        top_bar_layout.addWidget(btn_recalc)
        
        top_bar_layout.addStretch() 
        layout.addLayout(top_bar_layout)
        
        self.figure = Figure(figsize=(11, 6), dpi=100, constrained_layout=True)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        gs = self.figure.add_gridspec(3, 2, width_ratios=[1.3, 1], hspace=0.05)
        
        self.ax1 = self.figure.add_subplot(gs[:, 0])
        self.ax1.scatter(self.s_data, self.v_data, color='black', label='Experimental Data', zorder=5)
        self.s_plot = np.linspace(0, max(self.s_data) * 1.1, 100)
        self.line_mm, = self.ax1.plot([], [], 'b-', linewidth=2, label='Fitted Curve', zorder=4)
        
        self.line_residu, = self.ax1.plot([], [], 'r--', linewidth=2, label='Residual', zorder=3)
        self.ax1.plot(self.target_s, self.target_v_exp, 'ro', markersize=8, zorder=6)
        
        self.ax1.set_title("1. Global Error Minimization")
        self.ax1.set_xlim(0, max(self.s_data) * 1.1)
        self.ax1.set_ylim(0, max(self.v_data) * 1.4) 
        self.ax1.set_xlabel(MainWindow.format_units("[S]_0"))
        self.ax1.set_ylabel(MainWindow.format_units("v_0"))
        self.ax1.legend(loc='upper left')
        
        self.text_global = self.ax1.text(0.97, 0.97, "", transform=self.ax1.transAxes, 
                                      fontsize=10, verticalalignment='top', horizontalalignment='right',
                                      bbox=dict(facecolor='white', alpha=0.9))
        
        self.text_detail = self.ax1.text(0.35, 0.05, "", transform=self.ax1.transAxes, 
                                      fontsize=10, bbox=dict(facecolor='#ffcccc', edgecolor='red', alpha=0.7))

        self.ax_vmax = self.figure.add_subplot(gs[0, 1])
        self.line_traj_vmax, = self.ax_vmax.plot([], [], 'g-', label='Vmax', linewidth=2)
        self.pt_vmax, = self.ax_vmax.plot([], [], 'go', markersize=6)
        self.line_opt_vmax = self.ax_vmax.axhline(self.vmax_opt, color='green', linestyle=':', alpha=0.5)
        self.ax_vmax.set_title("2. Vmax Convergence")
        self.ax_vmax.set_ylabel("Vmax")
        self.ax_vmax.set_xlim(0, self.num_frames)
        self.ax_vmax.grid(True, linestyle=':', alpha=0.6)
        self.ax_vmax.tick_params(labelbottom=False)
        
        self.ax_km = self.figure.add_subplot(gs[1, 1], sharex=self.ax_vmax)
        self.line_traj_km, = self.ax_km.plot([], [], 'm-', label='Km', linewidth=2)
        self.pt_km, = self.ax_km.plot([], [], 'mo', markersize=6)
        self.line_opt_km = self.ax_km.axhline(self.km_opt, color='magenta', linestyle=':', alpha=0.5)
        self.ax_km.set_title("3. Km Convergence")
        self.ax_km.set_ylabel("Km")
        self.ax_km.grid(True, linestyle=':', alpha=0.6)
        self.ax_km.tick_params(labelbottom=False)

        self.ax_ssr = self.figure.add_subplot(gs[2, 1], sharex=self.ax_vmax)
        self.line_traj_ssr, = self.ax_ssr.plot([], [], '-', color='#ff7f0e', label='Σ Squared Error', linewidth=2)
        self.pt_ssr, = self.ax_ssr.plot([], [], 'o', color='#ff7f0e', markersize=6)
        
        opt_v = (self.vmax_opt * self.s_data) / (self.km_opt + self.s_data)
        self.ssr_opt = np.sum((self.v_data - opt_v)**2)
        self.line_opt_ssr = self.ax_ssr.axhline(self.ssr_opt, color='#ff7f0e', linestyle=':', alpha=0.5)
        
        self.ax_ssr.set_title("4. Σ Squared Error Convergence")
        self.ax_ssr.set_xlabel("Algorithm Step")
        self.ax_ssr.set_ylabel("Σ Squared Error")
        self.ax_ssr.grid(True, linestyle=':', alpha=0.6)
        
        control_layout = QHBoxLayout()
        self.btn_prev = QPushButton("⏪ Step")
        self.btn_prev.clicked.connect(self.step_backward)
        self.btn_play = QPushButton("▶ Play")
        self.btn_play.clicked.connect(self.toggle_play)
        self.btn_next = QPushButton("Step ⏩")
        self.btn_next.clicked.connect(self.step_forward)
        
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(self.num_frames - 1)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(10)
        self.slider.valueChanged.connect(self.on_slider_change)
        
        self.btn_save = QPushButton("💾 Save GIF")
        self.btn_save.clicked.connect(self.save_gif)
        
        control_layout.addWidget(self.btn_prev)
        control_layout.addWidget(self.btn_play)
        control_layout.addWidget(self.btn_next)
        control_layout.addWidget(self.slider)
        control_layout.addWidget(self.btn_save)
        layout.addLayout(control_layout)

    def toggle_play(self):
        if self.timer.isActive():
            self.timer.stop()
            self.btn_play.setText("▶ Play")
        else:
            if self.current_frame >= self.num_frames - 1: self.slider.setValue(0)
            self.timer.start()
            self.btn_play.setText("⏸ Pause")

    def next_frame(self):
        if self.current_frame < self.num_frames - 1:
            self.slider.setValue(self.current_frame + 1)
        else:
            self.timer.stop()
            self.btn_play.setText("▶ Play")

    def step_forward(self):
        self.timer.stop()
        self.btn_play.setText("▶ Play")
        if self.current_frame < self.num_frames - 1:
            self.slider.setValue(self.current_frame + 1)

    def step_backward(self):
        self.timer.stop()
        self.btn_play.setText("▶ Play")
        if self.current_frame > 0:
            self.slider.setValue(self.current_frame - 1)

    def on_slider_change(self, value):
        self.current_frame = value
        self.update_plot()

    def update_plot(self, frame_idx=None):
        frame = frame_idx if frame_idx is not None else self.current_frame
        if frame >= self.num_frames: frame = self.num_frames - 1 
            
        vmax = self.vmax_traj[frame]
        km = self.km_traj[frame]
        
        v_model = (vmax * self.s_plot) / (km + self.s_plot)
        self.line_mm.set_data(self.s_plot, v_model)
        
        target_v_calc = (vmax * self.target_s) / (km + self.target_s)
        self.line_residu.set_data([self.target_s, self.target_s], [self.target_v_exp, target_v_calc])
        
        v_fit_all = (vmax * self.s_data) / (km + self.s_data)
        ssr = np.sum((self.v_data - v_fit_all)**2)
        
        if frame < self.num_frames - 10:
            status = "Descent in progress..."
            box_color = 'white'
            edge_color = 'gray'
        elif frame < self.num_frames - 5:
            status = "[ WARNING ] Σ Squared Error increased! Step rejected."
            box_color = '#ffcccc'
            edge_color = 'red'
        else:
            status = "[ OK ] Convergence (Minimum reached)"
            box_color = '#d4edda'
            edge_color = 'green'
        
        global_str = (f"Step: {frame} / {self.num_frames - 1}\n"
                      f"{status}\n\n"
                      f"Tested Parameters:\n"
                      f"  • Vmax = {vmax:.2f}\n"
                      f"  • Km = {km:.2f}\n\n"
                      f"Global Error (Σ Squared Error)): {ssr:.1f}")
        self.text_global.set_text(global_str)
        self.text_global.set_bbox(dict(facecolor=box_color, edgecolor=edge_color, alpha=0.9))
        
        residu_brut = target_v_calc - self.target_v_exp
        carre_residu = residu_brut**2
        detail_str = (f"Detail for target point ([S]0 = {self.target_s:.1f}):\n"
                      f"v_calc = ({vmax:.1f} * {self.target_s:.1f}) / ({km:.1f} + {self.target_s:.1f}) = {target_v_calc:.1f}\n"
                      f"v_exp = {self.target_v_exp:.1f}\n"
                      f"Error = v_calc - v_exp = {target_v_calc:.1f} - {self.target_v_exp:.1f} = {residu_brut:.2f}\n"
                      f"Squared Error = ({residu_brut:.2f})² = {carre_residu:.2f}")
        self.text_detail.set_text(detail_str)
        
        steps = np.arange(frame + 1)
        
        self.line_traj_vmax.set_data(steps, self.vmax_traj[:frame + 1])
        self.pt_vmax.set_data([frame], [vmax])
        self.ax_vmax.set_ylim(min(self.vmax_traj) * 0.9, max(self.vmax_traj) * 1.1)
        
        self.line_traj_km.set_data(steps, self.km_traj[:frame + 1])
        self.pt_km.set_data([frame], [km])
        self.ax_km.set_ylim(min(self.km_traj) * 0.9, max(self.km_traj) * 1.1)

        self.line_traj_ssr.set_data(steps, self.ssr_traj[:frame + 1])
        self.pt_ssr.set_data([frame], [self.ssr_traj[frame]])
        self.ax_ssr.set_ylim(min(self.ssr_traj) * 0.9, max(self.ssr_traj) * 1.1)
        
        if frame_idx is None:
            QApplication.processEvents()
            self.canvas.draw()
            
        return self.line_mm, self.line_residu, self.text_global, self.text_detail, self.line_traj_vmax, self.line_traj_km, self.pt_vmax, self.pt_km, self.line_traj_ssr, self.pt_ssr

    def save_gif(self):
        was_active = self.timer.isActive()
        if was_active:
            self.timer.stop()
            self.btn_play.setText("▶ Play")
            
        self.btn_save.setText("⏳ Saving...")
        self.btn_save.setEnabled(False)
        QApplication.processEvents() 
        
        try:
            anim = animation.FuncAnimation(self.figure, self.update_plot, 
                                           frames=self.num_frames, blit=False, repeat=False)
            gif_filename = 'MM_Fit_Animation.gif'
            anim.save(gif_filename, writer='pillow', fps=15)
            QMessageBox.information(self, "Success", f"Animation saved to:\n{gif_filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save: {str(e)}")
        finally:
            self.btn_save.setText("💾 Save GIF")
            self.btn_save.setEnabled(True)
            self.update_plot() 
            if was_active:
                self.timer.start()
                self.btn_play.setText("⏸ Pause")


class MainWindow(QMainWindow):
    """The main application window for MM-Fit v6.3."""

    STYLE_ACTION = "QPushButton { background-color: #5DC8A2; color: white; border-radius: 5px; padding: 5px; font-weight: bold; border: none; min-height: 25px; } QPushButton:hover { background-color: #7ED4B4; }"
    STYLE_UTILITY = "QPushButton { background-color: #5B88A5; color: white; border-radius: 5px; padding: 5px; font-weight: bold; border: none; min-height: 25px; } QPushButton:hover { background-color: #79A2BC; }"
    STYLE_SECONDARY = "QPushButton { background-color: #708090; color: white; border-radius: 5px; padding: 5px; font-weight: bold; border: none; min-height: 25px; } QPushButton:hover { background-color: #8492A0; }"
    STYLE_WARNING = "QPushButton { background-color: #D4AC0D; color: white; border-radius: 5px; padding: 5px; font-weight: bold; border: none; min-height: 25px; } QPushButton:hover { background-color: #E7BF3A; }"
    STYLE_QUIT = "QPushButton { background-color: #C0392B; color: white; border-radius: 5px; padding: 5px; font-weight: bold; border: none; min-height: 25px; } QPushButton:hover { background-color: #D9534F; }"

    @staticmethod
    def format_units(text):
        """Converts user input with ^ and _ to Matplotlib LaTeX syntax."""
        if not text: 
            return ""
        res = re.sub(r'\^([-\d\w]+)', r'$^{\1}$', text)
        res = re.sub(r'_([-\d\w]+)', r'$_{\1}$', res)
        return res

    def __init__(self):
        super().__init__()
        
        self.excluded_data = {} 
        self.column_checkboxes = {} 
        self.processed_data_series_lb = [] 
        self.Km_best = None 
        self.series_colors = [] 
        self.series_markers = ['o', 'D', '^', 's', 'v', '*']
        self.howtofit_window = None 
        
        self.x_unit = ""
        self.y_unit = ""
        
        self.hover_data = [] 
        self._hover_cid = None
        
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("JMB-Scripts MM-fit - v6.3-")
        self.resize(1200, 700)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        main_layout = QHBoxLayout(self.central_widget)
        
        self._create_widgets()
        self._create_layouts(main_layout)
        self._connect_signals()
        self._apply_styles()

    def _create_widgets(self):
        self.column_panel = QWidget()
        self.column_layout = QVBoxLayout(self.column_panel)
        
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(1)
        self.data_table.setHorizontalHeaderLabels(["[S]0"])
        self.data_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        
        self.paste_button = QPushButton("1- Paste from Excel")
        self.fit_button = QPushButton("2- MM-Fit")
        self.lineweaver_burk_button = QPushButton("3- LB plot")
        self.exclusion_button = QPushButton("(4- Exclude data)")
        self.units_button = QPushButton("Set Units")
        self.recolor_button = QPushButton("Change Colors")
        self.save_graph_button = QPushButton("Save MM Plot")
        self.print_button = QPushButton("Print Report")
        self.reset_button = QPushButton("Reset")
        self.howtofit_button = QPushButton("How-To-Fit") 
        self.quit_button = QPushButton("Quit")
        
        self.figure = Figure(figsize=(10, 6), dpi=100, constrained_layout=True)
        self.canvas = FigureCanvas(self.figure)

    def _create_layouts(self, main_layout):
        self.column_layout.addWidget(QLabel("Series:"))
        self.column_layout.addStretch()
        
        buttons_layout = QVBoxLayout()
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        buttons_layout.addWidget(self.paste_button)
        buttons_layout.addWidget(self.fit_button)
        buttons_layout.addWidget(self.lineweaver_burk_button)
        buttons_layout.addWidget(self.exclusion_button)
        buttons_layout.addWidget(self.units_button)
        buttons_layout.addWidget(self.recolor_button)
        buttons_layout.addWidget(self.save_graph_button)
        buttons_layout.addWidget(self.print_button)
        buttons_layout.addWidget(self.reset_button)
        buttons_layout.addWidget(self.howtofit_button) 
        buttons_layout.addWidget(self.quit_button)
        
        graph_layout = QVBoxLayout()
        graph_layout.addWidget(self.canvas, 1)
        
        self.hover_label = QLabel("")
        self.hover_label.setStyleSheet("color: #666; font-size: 12px; padding: 5px;")
        self.hover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        graph_layout.addWidget(self.hover_label, 0)
        
        main_layout.addWidget(self.column_panel)
        main_layout.addWidget(self.data_table, 1) 
        main_layout.addLayout(buttons_layout)
        main_layout.addLayout(graph_layout, 3)     

    def _connect_signals(self):
        self.paste_button.clicked.connect(self.paste_from_excel)
        self.fit_button.clicked.connect(self.fit_data)
        self.lineweaver_burk_button.clicked.connect(self.show_lineweaver_burk)
        self.exclusion_button.clicked.connect(self.open_exclusion_gui)
        self.units_button.clicked.connect(self.open_units_gui)
        self.recolor_button.clicked.connect(self.change_colors)
        self.save_graph_button.clicked.connect(self.save_graph)
        self.print_button.clicked.connect(self.print_report)
        self.reset_button.clicked.connect(self.reset_data)
        self.howtofit_button.clicked.connect(self.open_howtofit) 
        self.quit_button.clicked.connect(self.close)

    def _apply_styles(self):
        self.paste_button.setStyleSheet(self.STYLE_UTILITY)
        self.fit_button.setStyleSheet(self.STYLE_ACTION)
        self.lineweaver_burk_button.setStyleSheet(self.STYLE_ACTION)
        self.exclusion_button.setStyleSheet(self.STYLE_SECONDARY)
        self.units_button.setStyleSheet(self.STYLE_SECONDARY)
        self.recolor_button.setStyleSheet(self.STYLE_SECONDARY)
        self.save_graph_button.setStyleSheet(self.STYLE_UTILITY)
        self.print_button.setStyleSheet(self.STYLE_UTILITY)
        self.reset_button.setStyleSheet(self.STYLE_WARNING)
        self.howtofit_button.setStyleSheet(self.STYLE_ACTION) 
        self.quit_button.setStyleSheet(self.STYLE_QUIT)

    def open_units_gui(self):
        dialog = UnitDialog(self.x_unit, self.y_unit, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.x_unit = dialog.x_input.text().strip()
            self.y_unit = dialog.y_input.text().strip()
            if self.data_table.rowCount() > 0 and self.processed_data_series_lb:
                self.fit_data()

    def open_howtofit(self):
        if self.howtofit_window is None or not self.howtofit_window.isVisible():
            self.howtofit_window = PedagogicalSimulation(self)
        self.howtofit_window.show()
        self.howtofit_window.raise_()
        self.howtofit_window.activateWindow()

    def paste_from_excel(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text().strip()
        if not text:
            return

        rows = text.split('\n')
        
        try:
            float(rows[0].split('\t')[0].replace(',', '.'))
            is_header = False
        except (ValueError, IndexError):
            is_header = True

        if is_header:
            rows = rows[1:]
            if not rows:
                QMessageBox.warning(self, "No Data", "Header detected, but no data rows found.")
                return

        s_values_test = []
        for row in rows:
            vals = row.split('\t')
            if vals:
                try:
                    s_values_test.append(float(vals[0].replace(',', '.')))
                except ValueError:
                    pass
        
        if 0.0 not in s_values_test:
            reply = QMessageBox.question(self, "/!\\ Warning /!\\", 
                                         "/!\\ Warning /!\\\n\nThe origin point (0,0) is missing\n\nDo you still want to proceed?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return 
                
        if s_values_test and s_values_test != sorted(s_values_test):
            reply = QMessageBox.question(self, "/!\\ Warning /!\\", 
                                         "/!\\ Warning /!\\\n\nData are not sorted from smallest to biggest\n\nDo you still want to proceed?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return 
        self.reset_data()
        
        num_cols = len(rows[0].split('\t')) + 1
        self.data_table.setColumnCount(num_cols)
        
        headers = ["Include"] + [f"v{i}" for i in range(num_cols - 2)]
        headers.insert(1, "[S]")
        self.data_table.setHorizontalHeaderLabels(headers)
        self.data_table.setRowCount(len(rows))

        high_contrast_colors = list(plt.cm.tab10.colors)
        random.shuffle(high_contrast_colors)
        self.series_colors = high_contrast_colors

        for i, row in enumerate(rows):
            checkbox_item = QTableWidgetItem()
            checkbox_item.setCheckState(Qt.CheckState.Checked)
            self.data_table.setItem(i, 0, checkbox_item)
            
            values = row.split('\t')
            for j, value in enumerate(values):
                clean_val = value.replace(',', '.')
                self.data_table.setItem(i, j + 1, QTableWidgetItem(clean_val))

        self.data_table.resizeColumnsToContents()
        self._update_column_panel(headers)

    def fit_data(self):
        if self.data_table.rowCount() == 0:
            QMessageBox.warning(self, "No Data", "Please paste data before fitting.")
            return

        processed_data_series_mm, self.processed_data_series_lb = self._get_data_from_table()

        if not processed_data_series_mm:
            QMessageBox.warning(self, "Select Data", "Please select at least one valid data series to fit.")
            return

        self.figure.clear()
        self.hover_data = [] 
        
        num_series = len(processed_data_series_mm)
        gs = self.figure.add_gridspec(num_series + 1, 1, height_ratios=[4] + [1] * num_series)
        ax_mm = self.figure.add_subplot(gs[0])
        residual_axes = []
        best_km = float('inf')
        shared_residual_ax = None 

        for i, data in enumerate(processed_data_series_mm):
            try:
                popt, pcov = curve_fit(self.michaelis_menten, 
                                       data['s_fit'], data['v_fit'], 
                                       p0=[np.max(data['v_fit']), np.mean(data['s_fit'])])
                stats = self._calculate_fit_statistics(popt, pcov, data['s_fit'], data['v_fit'])

                if stats['km'] > 0 and stats['km'] < best_km:
                    best_km = stats['km']
                    self.Km_best = (data['label'], stats['km'])
                
                self._plot_mm_series(ax_mm, data, popt, stats, i, num_series)
                ax_res = self._plot_residuals(gs[i + 1], shared_residual_ax, data, popt, i, num_series)
                
                if shared_residual_ax is None:
                    shared_residual_ax = ax_res
                
                residual_axes.append(ax_res)

            except (RuntimeError, ValueError) as e:
                QMessageBox.warning(self, "Fitting Error", f"Could not fit series {data['label']}: {e}")

        x_label = f"[S]_0 ({self.x_unit})" if self.x_unit else "[S]_0"
        y_label = f"v_0 ({self.y_unit})" if self.y_unit else "v_0"

        ax_mm.set_xlabel(self.format_units(x_label))
        ax_mm.set_ylabel(self.format_units(y_label))
        ax_mm.set_title("Michaelis-Menten Kinetics")
        ax_mm.legend(fontsize=8, markerscale=0.6, labelspacing=0.4)
        # Force l'axe Y à commencer à 0 et arrondit le plafond au chiffre entier supérieur
        ymin, ymax = ax_mm.get_ylim()
        if ymax > 0:
            order = np.floor(np.log10(ymax))
            new_ymax = np.ceil(ymax / (10**order)) * (10**order)
            ax_mm.set_ylim(0, new_ymax)
        else:
            ax_mm.set_ylim(0, ymax)
        
        scientific_formatter = ScalarFormatter(useMathText=True)
        scientific_formatter.set_scientific(True)
        scientific_formatter.set_powerlimits((-2, 2))

        ax_mm.yaxis.set_major_formatter(scientific_formatter)
        ax_mm.xaxis.set_major_formatter(scientific_formatter)

        if residual_axes:
            residual_axes[-1].set_xlabel(self.format_units(x_label))
            residual_axes[-1].xaxis.set_major_formatter(scientific_formatter)

        if self._hover_cid:
            self.canvas.mpl_disconnect(self._hover_cid)
        self._hover_cid = self.canvas.mpl_connect("motion_notify_event", self._on_hover)

        self.canvas.draw()

    def _on_hover(self, event):
        if event.inaxes is None:
            self.hover_label.setText("")
            return
            
        match_found = False
        if hasattr(self, 'hover_data') and self.hover_data:
            for scatter, x_arr, y_arr, label, color, plot_type in self.hover_data:
                # Vérifie si la souris est au-dessus du bon sous-graphique
                if event.inaxes != scatter.axes:
                    continue
                    
                contained, info = scatter.contains(event)
                if contained:
                    ind = info['ind'][0]
                    x_val = x_arr[ind]
                    y_val = y_arr[ind]
                    
                    unit_x_str = f" {self.x_unit}" if self.x_unit else ""
                    unit_y_str = f" {self.y_unit}" if self.y_unit else ""
                    
                    if plot_type == 'mm':
                        text = f"Série : {label}   |   [S]₀ = {x_val:.2e}{unit_x_str}   |   v₀ = {y_val:.2e}{unit_y_str}"
                    else:
                        text = f"Série : {label}   |   [S]₀ = {x_val:.2e}{unit_x_str}   |   Résidu = {y_val:.2e}{unit_y_str}"
                        
                    self.hover_label.setText(text)
                    match_found = True
                    break
                    
        if not match_found:
            self.hover_label.setText("")

    def change_colors(self):
        if not self.series_colors:
            return 
            
        high_contrast_colors = list(plt.cm.tab10.colors)
        random.shuffle(high_contrast_colors)
        self.series_colors = high_contrast_colors
        self.fit_data()

    def show_lineweaver_burk(self):
        if not self.processed_data_series_lb:
            QMessageBox.warning(self, "Warning", "Please load and fit data first.")
            return

        self.lb_window = LineweaverBurkWindow(self.processed_data_series_lb, self.excluded_data, self.data_table, self.Km_best, self.series_colors, self.series_markers, self.x_unit, self.y_unit, self)
        self.lb_window.show()

    def open_exclusion_gui(self):
        if self.data_table.rowCount() == 0:
            QMessageBox.warning(self, "No Data", "Please paste data first.")
            return
        
        s_values, v_values = self._get_data_for_exclusion_dialog()
        
        def on_apply(new_exclusions):
            self.excluded_data = new_exclusions
            self.fit_data() 
            
        dialog = ExclusionDialog(s_values, v_values, self.excluded_data, on_apply, self)
        dialog.exec()

    def _get_data_from_table(self):
        series_mm, series_lb = [], []
        
        for col_idx in range(2, self.data_table.columnCount()):
            if col_idx not in self.column_checkboxes or not self.column_checkboxes[col_idx].isChecked():
                continue
            
            data = {'s_fit': [], 'v_fit': [], 'excluded_s': [], 'excluded_v': [], 'original_s': [], 'original_v': []}
            excluded_indices = self.excluded_data.get(col_idx - 2, set()) 

            for row_idx in range(self.data_table.rowCount()):
                if self.data_table.item(row_idx, 0) and self.data_table.item(row_idx, 0).checkState() == Qt.CheckState.Checked:
                    try:
                        s_val = float(self.data_table.item(row_idx, 1).text())
                        v_val = float(self.data_table.item(row_idx, col_idx).text())
                        
                        if row_idx not in excluded_indices:
                            data['s_fit'].append(s_val)
                            data['v_fit'].append(v_val)
                        else:
                            data['excluded_s'].append(s_val)
                            data['excluded_v'].append(v_val)
                        
                        if s_val != 0 and v_val != 0:
                            data['original_s'].append(s_val)
                            data['original_v'].append(v_val)
                    except (ValueError, AttributeError):
                        continue 
            
            if len(data['s_fit']) >= 2:
                for key in data: data[key] = np.array(data[key])
                data['label'] = self.data_table.horizontalHeaderItem(col_idx).text()
                series_mm.append(data)
                
                series_lb.append((1/data['original_s'] if data['original_s'].size > 0 else np.array([]), 
                                  1/data['original_v'] if data['original_v'].size > 0 else np.array([]), 
                                  data['label'], data['original_s'], data['original_v']))
                
        return series_mm, series_lb
    
    def _calculate_fit_statistics(self, popt, pcov, s_fit, v_fit):
        vmax, km = popt
        perr = np.sqrt(np.diag(pcov))
        vmax_se, km_se = perr
        
        vmax_rse = (vmax_se / abs(vmax)) * 100 if vmax != 0 else np.inf
        km_rse = (km_se / abs(km)) * 100 if km != 0 else np.inf

        ss_res = np.sum((v_fit - self.michaelis_menten(s_fit, *popt))**2)
        ss_tot = np.sum((v_fit - np.mean(v_fit))**2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        return {'vmax': vmax, 'km': km, 'r_squared': r_squared, 
                'vmax_se': vmax_se, 'km_se': km_se, 
                'vmax_rse': vmax_rse, 'km_rse': km_rse}

    def _plot_mm_series(self, ax, data, popt, stats, index, total):
        color = self.series_colors[index % len(self.series_colors)]
        marker = self.series_markers[index % len(self.series_markers)] 
        
        scatter = ax.scatter(data['s_fit'], data['v_fit'], label=f"Data {data['label']}", color=color, marker=marker, s=30)
        self.hover_data.append((scatter, data['s_fit'], data['v_fit'], data['label'], color, 'mm'))
        
        if data['excluded_s'].size > 0:
            scatter_ex = ax.scatter(data['excluded_s'], data['excluded_v'], color=color, marker='x', alpha=0.5, s=30)
            self.hover_data.append((scatter_ex, data['excluded_s'], data['excluded_v'], data['label'] + " (Exclu)", color, 'mm'))
       
        s_max = np.max(np.concatenate((data['s_fit'], data['excluded_s']))) if np.concatenate((data['s_fit'], data['excluded_s'])).size > 0 else 1
        s_plot = np.linspace(0, s_max * 1.2, 100)
        
        # Add units
        unit_y_str = f" {self.format_units(self.y_unit)}" if self.y_unit else ""
        unit_x_str = f" {self.format_units(self.x_unit)}" if self.x_unit else ""
        
        fit_label = (f"Fit {data['label']} (R²={stats['r_squared']:.3f})\n"
                     f"$V_{{max}}$ = {stats['vmax']:.2e}{unit_y_str} (± {stats['vmax_se']:.1e} | {stats['vmax_rse']:.0f}%)\n"
                     f"$K_m$   = {stats['km']:.2e}{unit_x_str} (± {stats['km_se']:.1e} | {stats['km_rse']:.0f}%)")
        
        ax.plot(s_plot, self.michaelis_menten(s_plot, *popt), '-', label=fit_label, color=color)

        ax.axhline(y=stats['vmax'], color=color, linestyle='--', linewidth=1, alpha=0)
        ax.axhline(y=stats['vmax'] / 2, color=color, linestyle='--', linewidth=1, alpha=0)
        ax.axvline(x=stats['km'], color=color, linestyle='--', linewidth=1, alpha=0)

    def _plot_residuals(self, subplot_spec, share_ax, data, popt, index, total):
        ax_res = self.figure.add_subplot(subplot_spec, sharex=share_ax)
        color = self.series_colors[index % len(self.series_colors)]
        marker = self.series_markers[index % len(self.series_markers)] 
        
        residuals = data['v_fit'] - self.michaelis_menten(data['s_fit'], *popt)
        scatter_res = ax_res.scatter(data['s_fit'], residuals, color=color, marker=marker, s=30)
        self.hover_data.append((scatter_res, data['s_fit'], residuals, data['label'] + " (Résidu)", color, 'res'))
        
        if data['excluded_s'].size > 0:
            excluded_residuals = data['excluded_v'] - self.michaelis_menten(data['excluded_s'], *popt)
            scatter_res_ex = ax_res.scatter(data['excluded_s'], excluded_residuals, color=color, marker='x', alpha=0.5, s=30)
            self.hover_data.append((scatter_res_ex, data['excluded_s'], excluded_residuals, data['label'] + " (Résidu Exclu)", color, 'res'))
        
        ax_res.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        
        if data['excluded_s'].size > 0:
            all_s = np.concatenate((data['s_fit'], data['excluded_s']))
            all_res = np.concatenate((residuals, excluded_residuals))
        else:
            all_s = data['s_fit']
            all_res = residuals
            
        s_max = np.max(all_s) if all_s.size > 0 else 1
        s_plot_res = np.linspace(0, s_max * 1.2, 100)
        
        tolerance = 0.05 * self.michaelis_menten(s_plot_res, *popt)
        ax_res.fill_between(s_plot_res, -tolerance, tolerance, color=color, alpha=0.15)
        
        # Force symmetric Y-axis limits around 0 so upper/lower ticks are always rendered
        max_val = np.max(np.abs(all_res)) if all_res.size > 0 else 1.0
        if max_val == 0: max_val = 1.0
        ax_res.set_ylim(-max_val * 1.25, max_val * 1.25)
        
        ax_res.set_ylabel("Residuals")
        ax_res.yaxis.set_major_formatter(FormatStrFormatter('%.2e'))
        
        if index < total - 1:
            ax_res.tick_params(axis='x', labelbottom=False)
        return ax_res
    
    def _update_column_panel(self, headers):
        for checkbox in self.column_checkboxes.values():
            checkbox.deleteLater()
        self.column_checkboxes.clear()

        for col in range(2, self.data_table.columnCount()):
            checkbox = QCheckBox(headers[col])
            checkbox.setChecked(True)
            self.column_layout.insertWidget(self.column_layout.count() - 1, checkbox)
            self.column_checkboxes[col] = checkbox
    
    def _get_data_for_exclusion_dialog(self):
        s_values, v_values = [], {}
        for row in range(self.data_table.rowCount()):
            try:
                s_values.append(float(self.data_table.item(row, 1).text()))
            except (ValueError, AttributeError):
                s_values.append(np.nan) 
            
            for col in range(2, self.data_table.columnCount()):
                v_values.setdefault(col - 2, [])
                try:
                    v_values[col - 2].append(float(self.data_table.item(row, col).text()))
                except (ValueError, AttributeError):
                    v_values[col - 2].append(np.nan) 
        return s_values, v_values

    def _print_figure(self, figure, parent):
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, parent)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            painter = QPainter(printer)
            buffer = io.BytesIO()
            figure.savefig(buffer, format='png', dpi=600, bbox_inches='tight')
            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue())
            page_rect = printer.pageRect()
            scaled_pixmap = pixmap.scaled(page_rect.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            x_offset = (page_rect.width() - scaled_pixmap.width()) / 2
            y_offset = (page_rect.height() - scaled_pixmap.height()) / 2
            painter.drawPixmap(int(x_offset), int(y_offset), scaled_pixmap)
            painter.end()

    def print_report(self):
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
            margin = 40
            
            # Export the exact figure as rendered on screen (high DPI)
            buffer = io.BytesIO()
            self.figure.savefig(buffer, format='png', dpi=300, pad_inches=0.1)
            image = QImage.fromData(buffer.getvalue())
            
            # Maintain aspect ratio on the PDF page
            max_plot_w = page_rect.width() - 2 * margin
            max_plot_h = page_rect.height() * 0.55 
            
            img_aspect = image.width() / image.height()
            target_w = max_plot_w
            target_h = target_w / img_aspect
            
            if target_h > max_plot_h:
                target_h = max_plot_h
                target_w = target_h * img_aspect
                
            plot_x = page_rect.x() + margin + (max_plot_w - target_w) / 2
            plot_y = page_rect.y() + margin
            plot_rect = QRectF(plot_x, plot_y, target_w, target_h)
            
            table_rect = QRectF(page_rect.x() + margin, plot_rect.bottom() + 20, 
                                max_plot_w, page_rect.bottom() - plot_rect.bottom() - 20 - margin)
            
            painter.drawImage(plot_rect, image)
            self._draw_table_for_report(painter, table_rect)
            painter.end()

    def _draw_table_for_report(self, painter, target_rect):
        num_rows = self.data_table.rowCount()
        num_cols = self.data_table.columnCount() - 1 
        if num_rows == 0 or num_cols == 0:
            return

        original_font = painter.font()
        original_pen = painter.pen()
        default_pen = QPen(Qt.black)
        red_pen = QPen(Qt.red)
        
        font = QFont()
        font.setPointSize(7) 
        painter.setFont(font)
        
        fm = painter.fontMetrics() 
        padding = fm.height() // 2 
        row_height = fm.height() + padding
        header_height = fm.height() + padding + 4 
        
        # convert the unicode to latex
        def to_unicode_sub_sup(text):
            if not text: return ""
            replacements = {
                '^-1': '⁻¹', '^-2': '⁻²', '^-3': '⁻³',
                '^1': '¹', '^2': '²', '^3': '³', '^4': '⁴', '^5': '⁵', '^6': '⁶',
                '_0': '₀', '_1': '₁', '_2': '₂', '_3': '₃', '_4': '₄', '_5': '₅', '_max': 'ₘₐₓ'
            }
            for k, v in replacements.items():
                text = text.replace(k, v)
            return text

        def get_unit_text(col_index):
            raw_unit = self.x_unit if col_index == 0 else self.y_unit
            if raw_unit:
                return f"({to_unicode_sub_sup(raw_unit)})"
            return ""

        col_widths = []
        for j in range(num_cols): 
            header_text = self.data_table.horizontalHeaderItem(j + 1).text()
            if header_text == "[S]": header_text = "[S]0"
            header_text = to_unicode_sub_sup(header_text)
            
            max_width = fm.horizontalAdvance(header_text) + padding
            
            unit_text = get_unit_text(j)
            if unit_text:
                max_width = max(max_width, fm.horizontalAdvance(unit_text) + padding)

            for i in range(num_rows):
                item = self.data_table.item(i, j + 1)
                cell_text = item.text() if item else ""
                try:
                    num_val = float(cell_text)
                    formatted_text = f"{num_val:.2E}" 
                    max_width = max(max_width, fm.horizontalAdvance(formatted_text) + padding)
                except ValueError:
                    max_width = max(max_width, fm.horizontalAdvance(cell_text) + padding)
            col_widths.append(max_width)
        
        total_table_width = sum(col_widths)
        start_x = target_rect.x() 
        start_y = target_rect.y() 
        
        if total_table_width > target_rect.width():
            scale_factor = target_rect.width() / total_table_width
            col_widths = [w * scale_factor for w in col_widths]
            
        current_x = start_x
        
        # 1. Headers
        for j in range(num_cols):
            header_text = self.data_table.horizontalHeaderItem(j + 1).text()
            if header_text == "[S]": header_text = "[S]0"
            header_text = to_unicode_sub_sup(header_text)
            
            cell_rect = QRectF(current_x, start_y, col_widths[j], header_height)
            painter.setPen(default_pen)
            painter.drawRect(cell_rect)
            
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(cell_rect, Qt.AlignCenter, header_text)
            font.setBold(False)
            painter.setFont(font)
            
            current_x += col_widths[j]
            
        y_start_units = start_y + header_height
        current_x = start_x
        
        # 2. Units
        for j in range(num_cols):
            unit_text = get_unit_text(j)
            cell_rect = QRectF(current_x, y_start_units, col_widths[j], row_height)
            painter.setPen(default_pen)
            painter.drawRect(cell_rect)
            
            if unit_text:
                font.setItalic(True)
                font.setPointSize(6) # smaller font for the units
                painter.setFont(font)
                painter.drawText(cell_rect, Qt.AlignCenter, unit_text)
                font.setItalic(False)
                font.setPointSize(7)
                painter.setFont(font)
                
            current_x += col_widths[j]
        
        y_start_data = y_start_units + row_height

        # 3. Exp data
        for i in range(num_rows):
            row_y = y_start_data + i * row_height
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

                try:
                    num_val = float(cell_text)
                    cell_text = f"{num_val:.2E}"
                except ValueError:
                    pass 

                if j == 0:  
                    is_excluded = is_row_excluded
                else:  
                    is_excluded = is_row_excluded or (i in self.excluded_data.get(j - 1, set()))
                
                painter.setPen(red_pen if is_excluded else default_pen)
                painter.drawRect(cell_rect)
                painter.drawText(cell_rect, Qt.AlignCenter, cell_text)
                current_x += col_widths[j]

        painter.setFont(original_font)
        painter.setPen(original_pen)

    def save_graph(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save plot", "", "Images (*.png *.jpg *.pdf)")
        if file_path:
            self.figure.savefig(file_path, bbox_inches='tight', dpi=600, pad_inches=0.2)
            QMessageBox.information(self, "Plot Saved", f"The plot has been saved to:\n{file_path}")

    def reset_data(self):
        self.x_unit = ""
        self.y_unit = ""
        self.data_table.clearContents()
        self.data_table.setRowCount(0)
        self.data_table.setColumnCount(1)
        self.data_table.setHorizontalHeaderLabels(["[S]"])
        self._update_column_panel([])
        self.excluded_data.clear()
        self.hover_data = []
        if self._hover_cid:
            self.canvas.mpl_disconnect(self._hover_cid)
            self._hover_cid = None
        self.hover_label.setText("")
        self.figure.clear()
        self.canvas.draw()

    @staticmethod
    def michaelis_menten(s, vmax, km):
        return (vmax * s) / (km + s)


class LineweaverBurkWindow(QMainWindow):
    def __init__(self, lb_series_data, excluded_data, data_table, km_best, series_colors, series_markers, x_unit, y_unit, parent=None):
        super().__init__(parent)
        self.lb_series_data = lb_series_data
        self.excluded_data = excluded_data
        self.data_table = data_table
        self.km_best = km_best
        self.series_colors = series_colors 
        self.series_markers = series_markers 
        self.x_unit = x_unit
        self.y_unit = y_unit
        self._setup_ui()
        self._prepare_data_and_plot()

    @staticmethod
    def linear_model(x, m, c):
        return m * x + c
        
    def _setup_ui(self):
        self.setWindowTitle("Lineweaver-Burk Plot")
        self.resize(800, 700)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.figure = Figure(figsize=(8, 6), dpi=100, constrained_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        main_layout.addWidget(self.canvas)

        controls_layout = QHBoxLayout()
        self.show_fit_checkbox = QCheckBox("Display linear fit")
        self.show_fit_checkbox.stateChanged.connect(self._prepare_data_and_plot)
        controls_layout.addWidget(self.show_fit_checkbox)
        controls_layout.addStretch()

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

        apply_button = QPushButton("Apply Scale"); apply_button.clicked.connect(self._prepare_data_and_plot)
        apply_button.setStyleSheet(MainWindow.STYLE_SECONDARY)
        
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
        self.lb_plot_data = []
        
        for i, (_, _, label, _, _) in enumerate(self.lb_series_data):
            series_data = {'label': label, 'included_inv_s': [], 'included_inv_v': [], 'excluded_inv_s': [], 'excluded_inv_v': []}
            excluded_indices = self.excluded_data.get(i, set())
            
            for row in range(self.data_table.rowCount()):
                if self.data_table.item(row, 0) and self.data_table.item(row, 0).checkState() == Qt.CheckState.Checked:
                    try:
                        s_val = float(self.data_table.item(row, 1).text())
                        v_val = float(self.data_table.item(row, i + 2).text())
                        if s_val != 0 and v_val != 0:
                            inv_s, inv_v = 1/s_val, 1/v_val
                            if row not in excluded_indices:
                                series_data['included_inv_s'].append(inv_s)
                                series_data['included_inv_v'].append(inv_v)
                            else:
                                series_data['excluded_inv_s'].append(inv_s)
                                series_data['excluded_inv_v'].append(inv_v)
                    except (ValueError, AttributeError):
                        continue 
            self.lb_plot_data.append(series_data)
        
        self._update_plot()

    def _update_plot(self):
        self.ax.clear()
        show_fit = self.show_fit_checkbox.isChecked()
        all_inv_s, all_inv_v, x_intercepts = [], [], []

        for i, data in enumerate(self.lb_plot_data):
            color = self.series_colors[i % len(self.series_colors)]
            marker = self.series_markers[i % len(self.series_markers)]
            
            all_inv_s.extend(data['included_inv_s'])
            all_inv_s.extend(data['excluded_inv_s'])
            all_inv_v.extend(data['included_inv_v'])
            all_inv_v.extend(data['excluded_inv_v'])
            
            self.ax.scatter(data['included_inv_s'], data['included_inv_v'], label=f"Series {data['label']}", color=color, marker=marker, s=30)
            self.ax.scatter(data['excluded_inv_s'], data['excluded_inv_v'], color=color, alpha=0.5, marker='x', s=30)

            if show_fit and data['included_inv_s']:
                try:
                    x_data = np.array(data['included_inv_s'])
                    y_data = np.array(data['included_inv_v'])
                    
                    popt, pcov = curve_fit(self.linear_model, x_data, y_data)
                    slope, intercept = popt
                    
                    perr = np.sqrt(np.diag(pcov))
                    slope_se, intercept_se = perr
                    
                    vmax_rse = (intercept_se / abs(intercept)) * 100 if intercept != 0 else np.inf
                    km_rse = np.sqrt((slope_se / slope)**2 + (intercept_se / intercept)**2) * 100 if slope != 0 and intercept != 0 else np.inf

                    lb_vmax = 1 / intercept if intercept != 0 else np.inf
                    lb_km = slope / intercept if intercept != 0 else np.inf
                    x_intercept = -1 / lb_km if lb_km != 0 else 0
                    x_intercepts.append(x_intercept)

                    lb_vmax_se = (vmax_rse / 100) * abs(lb_vmax) if np.isfinite(vmax_rse) and np.isfinite(lb_vmax) else np.inf
                    lb_km_se = (km_rse / 100) * abs(lb_km) if np.isfinite(km_rse) and np.isfinite(lb_km) else np.inf
                    
                    ss_res = np.sum((y_data - self.linear_model(x_data, *popt))**2)
                    ss_tot = np.sum((y_data - np.mean(y_data))**2)
                    r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
                    
                    max_s = max(x_data) * 1.2 if len(x_data) > 0 else 0
                    s_plot = np.linspace(x_intercept * 1.1, max_s, 100)
                    
                    unit_y_str = f" {MainWindow.format_units(self.y_unit)}" if self.y_unit else ""
                    unit_x_str = f" {MainWindow.format_units(self.x_unit)}" if self.x_unit else ""

                    fit_label = (f"Fit {data['label']} (R²={r_squared:.3f})\n"
                                 f"$V_{{max}}$ = {lb_vmax:.2e}{unit_y_str} (± {lb_vmax_se:.1e} | {vmax_rse:.0f}%)\n"
                                 f"$K_m$   = {lb_km:.2e}{unit_x_str} (± {lb_km_se:.1e} | {km_rse:.0f}%)")
                    self.ax.plot(s_plot, self.linear_model(s_plot, *popt), '-', color=color, label=fit_label)

                except (ValueError, TypeError, RuntimeError):
                    pass 
        
        min_x_auto = -1.0
        if x_intercepts and min(x_intercepts) < 0:
            min_x_auto = min(x_intercepts) * 1.2
        elif self.km_best: 
            _, km_val = self.km_best
            if km_val > 0:
                min_x_auto = (-1 / km_val) * 1.2
        elif all_inv_s and min(all_inv_s) >= 0:
            min_x_auto = -0.1 * max(all_inv_s)
        
        max_x_auto = max(all_inv_s) * 1.2 if all_inv_s else 1.0
        min_y_auto = min(all_inv_v) * 1.2 if all_inv_v and min(all_inv_v) < 0 else -0.1 * (max(all_inv_v) if all_inv_v else 1)
        max_y_auto = max(all_inv_v) * 1.2 if all_inv_v else 1.0
        
        try:
            xmin = float(self.xmin_input.text()) if self.xmin_input.text() else min_x_auto
            xmax = float(self.xmax_input.text()) if self.xmax_input.text() else max_x_auto
            ymin = float(self.ymin_input.text()) if self.ymin_input.text() else min_y_auto
            ymax = float(self.ymax_input.text()) if self.ymax_input.text() else max_y_auto
            self.ax.set_xlim(xmin, xmax); self.ax.set_ylim(ymin, ymax)
        except ValueError:
            self.ax.set_xlim(min_x_auto, max_x_auto); self.ax.set_ylim(min_y_auto, max_y_auto)

        self.ax.axvline(x=0, color='black', linewidth=1.5); self.ax.axhline(y=0, color='black', linewidth=1.5)
        
        x_lb_label = f"1/[S]_0 (1 / {self.x_unit})" if self.x_unit else "1/[S]_0"
        y_lb_label = f"1/v_0 (1 / {self.y_unit})" if self.y_unit else "1/v_0"
        self.ax.set_xlabel(MainWindow.format_units(x_lb_label))
        self.ax.set_ylabel(MainWindow.format_units(y_lb_label))
        
        formatter = ScalarFormatter(useMathText=True)
        formatter.set_scientific(True)
        formatter.set_powerlimits((-2, 2))
        self.ax.xaxis.set_major_formatter(formatter)
        self.ax.yaxis.set_major_formatter(formatter)
        
        self.ax.set_title("Lineweaver-Burk Plot"); self.ax.legend(fontsize='small'); self.ax.grid(True)
        self.canvas.draw()


class ExclusionDialog(QDialog):
    def __init__(self, s_values, v_values, initial_exclusions, apply_callback, parent=None):
        super().__init__(parent)
        self.apply_callback = apply_callback 
        self.checkboxes = [] 
        self._setup_ui(s_values, v_values, initial_exclusions)

    def _setup_ui(self, s_values, v_values, initial_exclusions):
        self.setWindowTitle("Exclude Data Points")
        self.resize(650, 450) 
        
        main_layout = QVBoxLayout(self)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        grid_widget = QWidget()
        grid = QGridLayout(grid_widget)
        grid.setSpacing(0) 

        grid_widget.setStyleSheet("""
            QLabel { border: 1px solid #d3d3d3; padding: 4px; }
            QCheckBox { border: 1px solid #d3d3d3; padding: 4px; margin: 0px; }
        """)

        grid.addWidget(QLabel("<b>#</b>"), 0, 0, Qt.AlignmentFlag.AlignCenter) 
        grid.addWidget(QLabel("<b>[S]0</b>"), 0, 1, Qt.AlignmentFlag.AlignCenter)
        for v_idx in v_values:
            grid.addWidget(QLabel(f"<b>Series v{v_idx}</b>"), 0, 2 + v_idx * 2, 1, 2, Qt.AlignmentFlag.AlignCenter)

        for row_idx, s_val in enumerate(s_values):
            grid.addWidget(QLabel(str(row_idx + 1)), row_idx + 1, 0, Qt.AlignmentFlag.AlignCenter)
            grid.addWidget(QLabel(f"{s_val:.2E}" if not np.isnan(s_val) else "N/A"), row_idx + 1, 1, Qt.AlignmentFlag.AlignCenter)
            
            for v_idx, v_list in v_values.items():
                is_excluded = row_idx in initial_exclusions.get(v_idx, set())
                cb = QCheckBox()
                cb.setChecked(is_excluded)
                self.checkboxes.append((v_idx, row_idx, cb)) 
                
                v_val_str = ""
                if row_idx < len(v_list) and not np.isnan(v_list[row_idx]):
                    v_val_str = f"{v_list[row_idx]:.2E}"
                
                grid.addWidget(cb, row_idx + 1, 2 + v_idx * 2, Qt.AlignmentFlag.AlignCenter)
                grid.addWidget(QLabel(v_val_str), row_idx + 1, 3 + v_idx * 2, Qt.AlignmentFlag.AlignCenter)
        
        scroll_area.setWidget(grid_widget)
        main_layout.addWidget(scroll_area)
        
        button_layout = QHBoxLayout()
        apply_button = QPushButton("Apply and Re-Fit")
        apply_button.clicked.connect(self._apply_and_close)
        apply_button.setStyleSheet(MainWindow.STYLE_ACTION)
        
        button_layout.addAddition = button_layout.addStretch
        button_layout.addStretch()
        button_layout.addWidget(apply_button)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)

    def _apply_and_close(self):
        new_exclusions = {}
        for v_idx, row_idx, cb in self.checkboxes:
            if cb.isChecked():
                new_exclusions.setdefault(v_idx, set()).add(row_idx)
        self.apply_callback(new_exclusions)
        self.accept()

# --- Application Entry Point ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())