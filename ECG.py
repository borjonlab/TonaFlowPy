import tkinter as tk

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import ttk, filedialog
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from scipy.signal.windows import gaussian as gausswin
from scipy.signal import butter, lfilter
from scipy.fft import fft,fftfreq
from matplotlib.animation import FuncAnimation


import ECG_Mod
from ECG_Mod import ECGProcessor





class ecg_applicaion:
    def __init__(self, mast, csvPath=None):
        # Set up the main window and frames.
        self.m = mast
        self.m.title("ECG Analysis")
        self.m.geometry("1200x600")
        self.topF = tk.Frame(self.m, bg="white", height=20)
        self.topF.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.m.grid_rowconfigure(0, weight=1)
        self.lsideF = tk.Frame(self.m, bg="white")
        self.lsideF.grid(row=1, column=0, sticky="nsew")
        self.rsideF = tk.Frame(self.m, bg="lightgray")
        self.rsideF.grid(row=1, column=1, sticky="ns")
        self.m.grid_rowconfigure(1, weight=1)
        self.m.grid_columnconfigure(0, weight=1)
        self.m.grid_columnconfigure(1, weight=0)

        self.beat_markers = []
        self.th_lines      = []

        self.X_Data = None
        self.Y_Data = None
        self.SamplingRate = None
        self.data = None

        if csvPath:
            x, y = self.read_csv(csvPath)
            self.X_Data, self.Y_Data = x, y
            self.SamplingRate = self.estimate_sampling_rate()

        self.SpliceLocations = []
        self.HeartBeats = None
        self.HeartBeats_Spliced = None
        self.Thresholds = None

        self.HeartRate_X = None
        self.HeartRate_Y = None

        self.Active_Version = 'raw'

        # Variables for point select.
        self.selected_index = 0
        self.data = None
        self.time_values = None
        self.ecg_values = None
        self.ecg_col = None
        self.selected_marker = None
        self.tooltip = None
        self.heart_line = None  # Var for rand linear line on the heart  graph.
        self.rect = None
        self.rect_start = None
        self.rect_end = None

        self.rects = []
        self._drawing = None
        self._dragging = None



        # Intializing functions for graphs
        self.makecontrols()
        self.dographs()

        self.m.bind("<Left>", self.on_left)
        self.m.bind("<Right>", self.on_right)
        self.create_menu()

        self.window_duration = 5
        self.view_start_index = 0

    def create_menu(self):
        menubar = tk.Menu(self.m)
        self.m.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load ECG...", command=self.load_ecg)

    def load_ecg(self):
        filepath = filedialog.askopenfilename(
            title="Select ECG CSV file", filetypes=[("CSV Files", "*.csv")]
        )
        if filepath:
            self.read_csv(filepath)
            self.load_signal_data(filepath)
            self.dographs(self.data)


    def read_csv(self,filepath):
        file = pd.read_csv(filepath)

        x = file.iloc[:,0].to_numpy()
        y = file.iloc[:,1].to_numpy()

        self.X_Data, self.Y_Data = x, y
        self.SamplingRate = self.estimate_sampling_rate()

        return x,y


    def estimate_sampling_rate(self):
        print(1/np.mean(np.diff(self.X_Data)))
        self.fs = 1/np.mean(np.diff(self.X_Data))
        return 1/np.mean(np.diff(self.X_Data))

    def dographs(self, data=None):
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

        fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 6))
        fig.subplots_adjust(hspace=0.7)
        self.ax1 = a1
        self.ax2 = a2

        if data is not None:
            time_col = data.columns[0]
            self.time_values = data[time_col].values

            non_time_cols = data.columns[1:]

            for col in non_time_cols:
                ecg_values = data[col].values
                a1.plot(self.time_values, ecg_values, label=col)

            x_min, x_max = self.time_values.min(), self.time_values.max()
            x_range = x_max - x_min
            windowFraction = 0.4
            a1.set_xlim(x_min, x_min + x_range * windowFraction)

            a1.set_title("ECG")
            a1.legend()

            self.data = data
            non_time_cols = [col for col in data.columns if col != 'Time']
            if non_time_cols:
                self.ecg_col = non_time_cols[0]
                self.ecg_values = data[self.ecg_col].values
            else:
                self.ecg_col = None
                self.ecg_values = None

            if self.selected_index >= len(self.time_values):
                self.selected_index = len(self.time_values) - 1

            xVal = self.time_values[self.selected_index]
            y_val = self.ecg_values[self.selected_index] if self.ecg_values is not None else 0
            self.selected_marker, = a1.plot([xVal], [y_val], 'ro', markersize=8)
            self.tooltip = a1.text(
                xVal, y_val,
                f'Time: {xVal:.2f}\nAmp: {y_val:.2f}',
                fontsize=9, color='black',
                bbox=dict(facecolor='white', alpha=0.7)
            )
        else:
            a1.set_title("ECG")

        if hasattr(self, 'c'):
            self.c.get_tk_widget().destroy()
            self.toolbar.destroy()

        a2.set_title("Heart Rate")

        self.c = FigureCanvasTkAgg(fig, master=self.lsideF)
        self.toolbar = NavigationToolbar2Tk(self.c, self.lsideF)
        self.toolbar.update()
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        self.c.draw()
        self.c.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.c.mpl_connect("pick_event", self.on_pick)

        if data is not None:
            self.c.mpl_connect("button_press_event", self.press)
            self.c.mpl_connect("motion_notify_event", self.on_motion)
            self.c.mpl_connect("button_press_event", self.on_click)
            self.c.mpl_connect("motion_notify_event", self.on_drag)
            self.c.mpl_connect("button_release_event", self.on_release)

    def on_pick(self, event):
        artist = event.artist
        for r in list(self.rects):
            if r['close'] is artist:
                r['patch'].remove()
                r['close'].remove()
                self.rects.remove(r)
                self.c.draw()
                return

    def press(self, event):
        if event.inaxes is not self.ax1:
            return
        if event.button == 3:
            self._drawing = (event.xdata, event.ydata)
            return
        if event.button == 1:
            for r in list(self.rects):
                tx, ty = r['close'].get_position()
                xhRange = np.ptp(self.ax1.get_xlim())*0.02
                yhRange = np.ptp(self.ax1.get_ylim())*0.05
                if abs(event.xdata-tx)<xhRange and abs(event.ydata-ty)<yhRange:
                    r['patch'].remove()
                    r['close'].remove()
                    self.rects.remove(r)
                    self.c.draw()
                    return
            for r in self.rects:
                x0,y0 = r['patch'].get_xy()
                width,height  = r['patch'].get_width(), r['patch'].get_height()
                if x0<=event.xdata<=x0+width and y0<=event.ydata<=y0+height:
                    self._dragging = (r, event.xdata, event.ydata, x0, y0)
                    return

    def on_motion(self, event):
        if event.inaxes is not self.ax1:
            return
        if self._drawing:
            x0,y0 = self._drawing
            dx, dy = event.xdata-x0, event.ydata-y0
            if hasattr(self, '_temp'):
                self._temp.remove()
            self._temp = plt.Rectangle((x0,y0), dx, dy,
                                       edgecolor='black', facecolor='none')
            self.ax1.add_patch(self._temp)
            self.c.draw()
        # dragging
        elif self._dragging:
            r, px, py, x0, y0 = self._dragging
            dx, dy = event.xdata - px, event.ydata - py

            newX, new_y = x0 + dx, y0 + dy
            r['patch'].set_xy((newX, new_y))

            w, h = r['patch'].get_width(), r['patch'].get_height()
            cx, cy = newX + w, new_y + h
            r['close'].set_position((cx, cy))

            idxs = np.where((self.time_values >= newX) and
                            (self.time_values <= newX + w))[0]
            r['start'] = idxs.min() if idxs.size else None
            r['end'] = idxs.max() if idxs.size else None
            print(f" indices are  {r['start']} to {r['end']}")
            self.c.draw()

    def on_release(self, event):
        if event.inaxes is not self.ax1:
            return
        if event.button == 3 and self._drawing:
            x0, y0 = self._drawing
            x1, y1 = event.xdata, event.ydata
            xmin, xmax = sorted([x0, x1])
            ymin, ymax = sorted([y0, y1])
            idxs = np.where((self.time_values >= xmin) & (self.time_values <= xmax))[0]
            start = idxs.min() if idxs.size else None
            end = idxs.max() if idxs.size else None

            patch = plt.Rectangle((xmin, ymin), xmax - xmin, ymax - ymin,
                                  edgecolor='black', facecolor='blue',alpha=0.3)
            self.ax1.add_patch(patch)

            close_x = xmin + (xmax - xmin)
            close_y = ymin + (ymax - ymin) + 1

            close = self.ax1.text(
                close_x, close_y, "×",
                color='black', fontsize=5, weight='bold',
                ha='right', va='top',
                bbox=dict(
                    boxstyle="circle,pad=0.2",
                    facecolor="white",
                    edgecolor="gray",
                    linewidth=1
                ),
            picker = True
            )

            self.rects.append({'patch': patch, 'close': close, 'start': start, 'end': end})

            if hasattr(self, '_temp'):
                self._temp.remove()
                del self._temp

            self._drawing = None
            print(f"Rectangle covers indices {start} to {end}")
            self.c.draw()

        if event.button == 1 and self._dragging:
            self._dragging = None

    def on_click(self, event):
        if event.inaxes is not None:
            if self.rect is None:
                self.rect_start = (event.xdata, event.ydata)
                self.rect = self.ax1.add_patch(
                    plt.Rectangle(self.rect_start, 0, 0, linewidth=1, edgecolor='r', facecolor='none'))
            else:
                self.rect_end = (event.xdata, event.ydata)
                self.update_rectangle()
                self.c.draw()

    def on_drag(self, event):
        if self.rect is not None and event.inaxes is not None:
            self.rect_end = (event.xdata, event.ydata)
            self.update_rectangle()
            self.c.draw()

    def update_rectangle(self):
        if self.rect_start is not None and self.rect_end is not None:
            x1, y1 = self.rect_start
            x2, y2 = self.rect_end
            width = x2 - x1
            height = y2 - y1
            self.rect.set_width(width)
            self.rect.set_height(height)
            self.rect.set_xy((min(x1, x2), min(y1, y2)))

    def makecontrols(self):
        # making UI for the controls
        r = 0
        control_sects = [
            ("Heartbeats", ["Add Heartbeat", "Remove Heartbeat"]),
            ("Data Removal", ["Toggle Removal Mode", "Draw Removal Interval"]),
            ("Rectangle Controls", ["Delete Rectangle"]),
            ("Windows", ["Open Beat Detector"])

        ]
        for sect_title, button_list in control_sects:
            sectFrame = ttk.LabelFrame(self.rsideF, text=sect_title)
            sectFrame.grid(row=r, column=0, sticky="ew", padx=5, pady=5)
            r += 1
            for button in button_list:
                ttk.Button(sectFrame, text=button,
                           command=self.delete_rectangle if button == "Delete Rectangle" else None).pack(fill=tk.X,padx=5, pady=2)

        # Add more UI elements if needed...

    def delete_rectangle(self):
        """Delete the current rectangle."""
        if self.rect is not None:
            self.rect.remove()
            self.rect = None
            self.rect_start = None
            self.rect_end = None
            self.c.draw()

    def on_left(self, event):
        if self.time_values is not None and self.selected_index > 0:
            self.selected_index -= 1
            self.update_selected_point()

    def on_right(self, event):
        if self.time_values is not None and self.selected_index < len(self.time_values) - 1:
            self.selected_index += 1
            self.update_selected_point()

    def update_selected_point(self):
        if self.time_values is not None and self.ecg_values is not None:
            x_val = self.time_values[self.selected_index]
            y_val = self.ecg_values[self.selected_index]
            self.selected_marker.set_data([x_val], [y_val])
            self.tooltip.set_position((x_val, y_val))
            self.tooltip.set_text(f'Time: {x_val:.2f}\nAmp: {y_val:.2f}')
            self.c.draw()

    def on_click(self, event):
        if event.inaxes is not None and self.time_values is not None:
            x_click = event.xdata
            idx = (np.abs(self.time_values - x_click)).argmin()
            self.selected_index = idx
            self.update_selected_point()
            self.add_random_heart_line()

    def on_drag(self, event):
        if event.inaxes is not None and event.xdata is not None and event.button is not None:
            x_drag = event.xdata
            idx = (np.abs(self.time_values - x_drag)).argmin()
            self.selected_index = idx
            self.update_selected_point()

    def on_left(self, event):
        if self.time_values is not None and self.selected_index > 0:
            self.selected_index -= 1
            self.update_selected_point()

    def on_right(self, event):
        if self.time_values is not None and self.selected_index < len(self.time_values) - 1:
            self.selected_index += 1
            self.update_selected_point()

    def add_random_heart_line(self):
        randslope = np.random.uniform(-0.5, 0.5)
        random_intercept = np.random.uniform(50, 150)
        if self.heart_line is not None:
            self.heart_line.remove()
        x_vals = np.linspace(*self.ax2.get_xlim(), num=100)
        y_vals = randslope * x_vals + random_intercept
        self.heart_line, = self.ax2.plot(x_vals, y_vals, color='green', linestyle='-', label='Random Linear')
        self.ax2.legend()
        self.c.draw()



    def makecontrols(self):
        # making UI for the controls
        r = 0
        control_sects = [
            ("Heartbeats", ["Add Heartbeat", "Remove Heartbeat"]),
            ("Data Removal", ["Toggle Removal Mode", "Draw Removal Interval"])
        ]
        for sect_title, button_list in control_sects:
            sectFrame = ttk.LabelFrame(self.rsideF, text=sect_title)
            sectFrame.grid(row=r, column=0, sticky="ew", padx=5, pady=5)
            r += 1
            for button in button_list:
                ttk.Button(sectFrame, text=button).pack(fill=tk.X, padx=5, pady=2)

        viewF = ttk.LabelFrame(self.rsideF, text="View")
        viewF.grid(row=r, column=0, sticky="ew", padx=5, pady=5)
        r += 1
        ttk.Label(viewF, text="View Window (s)").pack()
        ttk.Entry(viewF).pack(fill=tk.X, padx=5)
        ttk.Label(viewF, text="ECG Y Limits").pack()
        ttk.Entry(viewF).pack(fill=tk.X, padx=5)
        ttk.Label(viewF, text="HR Y Limits").pack()
        ttk.Entry(viewF).pack(fill=tk.X, padx=5)
        ttk.Checkbutton(viewF, text="Show Raw Signal").pack(anchor="w", padx=5)
        ttk.Checkbutton(viewF, text="Show Partial Calculation Area").pack(anchor="w", padx=5)

        upload_btn = ttk.Button(self.rsideF, text="Upload ECG Data", command=self.upload_file)
        upload_btn.grid(row=r, column=0, sticky="ew", padx=5, pady=5)
        r += 1

        info = ttk.LabelFrame(self.rsideF, text="Session Info")
        info.grid(row=r, column=0, sticky="ew", padx=5, pady=5)
        r += 1
        ttk.Label(info, text="Session Length (s): 44.05").pack(pady=2)
        ttk.Label(info, text="Sampling Rate (Hz): 1000").pack(pady=2)
        ttk.Label(info, text="Filename:").pack()
        ttk.Label(info, text="Filepath: /Users/devlab...").pack()

        tab = ttk.LabelFrame(self.rsideF, text="Chart Data")
        tab.grid(row=0, column=1, rowspan=len(self.rsideF.winfo_children()), sticky="new", padx=10, pady=5)
        cols = ("Start", "Stop")
        self.tab = ttk.Treeview(tab, columns=cols, show="headings", height=20)
        self.tab.heading("Start", text="Start", anchor="w")
        self.tab.heading("Stop", text="Stop", anchor="w")
        self.tab.column("Start", width=100, anchor="w")
        self.tab.column("Stop", width=100, anchor="w")
        self.tab.pack(side="top", fill=tk.X)

        # just before the final return of makecontrols():
        ttk.Button(self.rsideF,
                   text="Beat Detection",
                   command=self.open_beat_window)\
            .grid(row=r, column=0, sticky="ew", padx=5, pady=5)
        r += 1

    def open_beat_window(self):
        if self.data is None:
            tk.messagebox.showwarning("No Data", "Please upload ECG data first.")
            return

        win = tk.Toplevel(self.m)
        win.title("Beat Detection Settings")

        frm = ttk.Frame(win, padding=10)
        frm.pack(side="left", fill="y")

        ttk.Label(frm, text="Threshold Window (sec):").grid(row=0, column=0, sticky="w")
        self.tw_var = tk.DoubleVar()
        ttk.Entry(frm, textvariable=self.tw_var, width=8).grid(row=0, column=1)

        ttk.Label(frm, text="Threshold Percentile:").grid(row=1, column=0, sticky="w")
        self.tp_var = tk.DoubleVar()
        ttk.Entry(frm, textvariable=self.tp_var, width=8).grid(row=1, column=1)

        self.abs_var = tk.BooleanVar()
        ttk.Checkbutton(frm, text="Use Absolute Value", variable=self.abs_var) \
            .grid(row=2, column=0, columnspan=2, pady=5)

        self.conv_var = tk.IntVar()
        hrFrm = ttk.LabelFrame(frm, text="Heart Rate Calculation Settings…")
        hrFrm.grid(row=3, column=0, columnspan=2, sticky="ew", pady=5)
        ttk.Label(hrFrm, text="Convolution Window Size").grid(row=0, column=0, sticky="w")
        ttk.Entry(hrFrm, textvariable=self.conv_var, width=8).grid(row=0, column=1)

        self.psize_var = tk.DoubleVar(value=1.0)
        prevFrm = ttk.LabelFrame(frm, text="Preview Settings…")
        prevFrm.grid(row=4, column=0, columnspan=2, sticky="ew", pady=5)
        ttk.Label(prevFrm, text="Preview Size (Seconds)").grid(row=0, column=0, sticky="w")
        ttk.Entry(prevFrm, textvariable=self.psize_var, width=8).grid(row=0, column=1)

        btns = ttk.Frame(frm)
        btns.grid(row=5, column=0, columnspan=2, pady=(10, 0))
        ttk.Button(btns, text="Run", command=self.detect_beats).pack(side="left", padx=5)
        ttk.Button(btns, text="Cancel", command=win.destroy).pack(side="left")

        plot_frame = tk.Frame(win, bg="white")
        plot_frame.pack(side="left", fill="both", expand=True)

        figp, axp = plt.subplots(figsize=(6, 3))
        axp.set_facecolor("white")

        # Create a second axis for heart rate
        fig_hr, ax_hr = plt.subplots(figsize=(6, 3))
        ax_hr.set_facecolor("white")

        t_col = self.data.columns[0]
        t = self.data[t_col].values
        for lead in self.data.columns[1:]:
            axp.plot(t, self.data[lead].values, label=lead)

        axp.set_title("ECG Preview")
        axp.set_xlabel("Time (s)")
        axp.set_ylabel("Amplitude")
        axp.legend(loc="upper right")

        canvasp = FigureCanvasTkAgg(figp, master=plot_frame)
        canvasp.draw()
        canvasp.get_tk_widget().pack(fill="both", expand=True)

        self.beat_win = win
        self.beat_preview_ax = axp
        self.heart_rate_ax = ax_hr  # Store the heart rate axis

        self.beat_preview_fig = figp
        self.beat_preview_cv = canvasp



    def detect_beats(self):
        tw = self.tw_var.get()  # Threshold Window (sec)
        tp = self.tp_var.get()  # Threshold Percentile

        self.processData = ECGProcessor(self.X_Data, self.Y_Data, self.fs)

        ECGProcessor.plot_full_analysis_gui(
            self.beat_preview_ax,
            self.heart_rate_ax,
            self.processData,
            threshold_percentile=tp,
            threshold_window=tw
        )

        # Redraw canvas
        self.beat_preview_cv.draw()

        xlims = self.ax1.get_xlim()
        ylims = self.ax1.get_ylim()

        # Clear main ECG axis
        self.ax1.clear()

        # Plot full ECG signal on main axis
        self.ax1.plot(self.X_Data, self.Y_Data, label='ECG Signal', color='blue')

        # take out detected beats times and values from the processor
        detected_beats_times =self.processData.X_Data[np.where(self.processData.HeartBeats == 1)]
        detected_beats_values = self.processData.Y_Data[np.where(self.processData.HeartBeats == 1)]

        # Plot detected beats as red dots
        self.ax1.plot(detected_beats_times, detected_beats_values, 'ro', label='Detected Beats')

        self.ax1.set_title("ECG")
        self.ax1.grid(True)

        self.ax1.set_xlim(xlims)
        self.ax1.set_ylim(ylims)

        # Redraw main canva
        self.c.draw()

    def upload_file(self):
        filepath = filedialog.askopenfilename(
            title="Select ECG CSV file", filetypes=[("CSV Files", "*.csv")]
        )
        if filepath:
            self.read_csv(filepath)
            self.load_signal_data(filepath)
        else:
            print("No file selected")

    def load_signal_data(self, what):
        try:
            df = pd.read_csv(what)
            column_names = df.columns
            print("Columns in the file:", df.columns)

            self.without_time = []

            # Assume the first column is the time column.
            self.signal_time = df[column_names[0]].values

            self.signal_data = {}

            for col in column_names:
                self.signal_data[col] = df[col].values

            for col in column_names:
                if col != "Time":
                    self.without_time.append(self.signal_data[col])

            self.signal_data["rest"] = np.transpose(np.array(self.without_time))
            print("Signal time:", self.signal_time)
            print("Rest data :", self.signal_data["rest"])

            print("Calling method")
            self.nothing()
        except Exception as e:
            print("Error loading signal data:", e)

    def nothing(self):
        """Update the ECG graph with the loaded signal data."""
        data_dict = {"Time": self.signal_time}
        for key in self.signal_data:
            if key not in ["rest"]:
                if key != "Time":
                    data_dict[key] = self.signal_data[key]
        df = pd.DataFrame(data_dict)
        self.dographs(df)

if __name__ == "__main__":
    root = tk.Tk()
    application = ecg_applicaion(root)
    root.mainloop()

