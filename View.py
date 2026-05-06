import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QCheckBox, QFrame, QFileDialog, QMessageBox, QLineEdit, QGroupBox,
    QHBoxLayout, QGridLayout, QToolBar, QMenuBar, QToolButton
)
from PyQt6.QtCore import Qt, QSize

from PyQt6.QtGui import QPalette, QColor, QAction, QKeySequence, QPixmap, QIcon, QShortcut

import pyqtgraph as pg
from ECG_controller import ECG_controller

from widgets import EcgPlot, HeartRatePlot, InfoBarButton, InfoBarGroupBox
import darkdetect




class TonaFlow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.controller = ECG_controller(self)
        # Set up the events from the controller
        # self.setup_events()

        self.setWindowTitle("TonaFlow")
        self.setGeometry(100, 100, 1800, 720)
        self.setup_ui()
        # Setup the button events/functions
        self.setup_events()
        # Setup keyboard shortcuts
        self.setup_keyboard_shortcuts()
        # Detect the system theme so we can apply the right logo and stylesheet.
        self.detect_os_theme()

        # Set resize to false
        self.setFixedSize(1800,720)
        
    def detect_os_theme(self):
        if darkdetect.isDark():
            self.setStyleSheet("""
                           background-color:#0d0d0d;
                            QPushButton {
                                        background-color: #252626;
                                        }
                            """)
            # Change the logo accordingly
            pixmap = QPixmap("imgs/logos/TonaFlow_DarkMode.png")
            self.LOGO_PIXMAP = pixmap.scaled(300,80,Qt.AspectRatioMode.KeepAspectRatio)
            self.logolabel.setPixmap(self.LOGO_PIXMAP)
            
            # Change the ECG / HR axes as well
            self.HR_Axis.setup_styling(style="dark")
            self.ECG_Axis.setup_styling(style="dark")
        else:
            self.setStyleSheet("""
                           background-color:#ffffff;
                            QPushButton {
                                        background-color: #dedede;
                                        }
                            """)
            # Change the logo accordingly
            pixmap = QPixmap("imgs/logos/TonaFlow_LightMode.png")
            self.LOGO_PIXMAP = pixmap.scaled(300,80,Qt.AspectRatioMode.KeepAspectRatio)
            self.logolabel.setPixmap(self.LOGO_PIXMAP)
            # Change the ECG / HR axes as well
            self.HR_Axis.setup_styling(style="light")
            self.ECG_Axis.setup_styling(style="light")
    
    def setup_ui(self):
        #### Set up the main interface of the app
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)


        #### Setup the rest of the UI, 
        self.setup_infobar(self.main_layout)
        # set up the Heart Rate and ECG Plots:
        self.setup_plots(self.main_layout)
        # Set up the menubar
        self.setup_menubar(self.main_layout)

    def setup_infobar(self,mainlayout):
        container_frame = QFrame()
        container_layout = QHBoxLayout(container_frame)
        container_layout.setContentsMargins(0,0,0,0)
        # Add the logo
        logo = QPixmap("imgs/logos/TonaFlow_DarkMode.png")
        logo = logo.scaled(300,80,Qt.AspectRatioMode.KeepAspectRatio)
        self.logolabel = QLabel("")
        self.logolabel.setPixmap(logo)
        container_layout.addWidget(self.logolabel)
        
        ### Control Groups for checkboxes and options
        ## View Controls
        view_controls_groupbox = InfoBarGroupBox("ECG View")
        view_controls_layout = QHBoxLayout()

        # View filtered signal toggle button
        self.show_filtered_signal_toggle = InfoBarButton("showfiltered.svg", text="Show Filtered \n ECG Signal", istoggle = True)
        view_controls_layout.addWidget(self.show_filtered_signal_toggle)

        # Show Partial Calculation
        self.show_partial_calc_toggle = InfoBarButton("showpartialcalc.svg", text="Show Partial \n Calculation", istoggle = True)
        self.show_partial_calc_toggle.setChecked(True)
        view_controls_layout.addWidget(self.show_partial_calc_toggle)


        # Show removed heartbeats checkbox 
        self.show_removed_heartbeats_toggle = InfoBarButton("removedbeats.svg",text="Show Removed \n Heartbeats", istoggle = True)
        view_controls_layout.addWidget(self.show_removed_heartbeats_toggle)


        view_controls_groupbox.setLayout(view_controls_layout)
        container_layout.addSpacing(100)
        # Add to the container layout for the infobar
        container_layout.addWidget(view_controls_groupbox)

        


        ## ECG Controls
        ECG_controls_groupbox = InfoBarGroupBox("ECG Controls")
        ECG_controls_layout = QHBoxLayout()

        ECG_controls_groupbox.setLayout(ECG_controls_layout)
        self.add_heartbeat_button = InfoBarButton("addheartbeat.svg",text="Add Heartbeat", istoggle = False)
        ECG_controls_layout.addWidget(self.add_heartbeat_button)

        self.remove_heartbeat_button = InfoBarButton("removeheartbeat.svg",text = "Remove Heartbeat", istoggle = False)
        ECG_controls_layout.addWidget(self.remove_heartbeat_button)

        self.insert_removal_region_button = InfoBarButton("insertremovalregion.svg",text = "Insert Removal \n Region", istoggle = False)
        ECG_controls_layout.addWidget(self.insert_removal_region_button)
        
        
        container_layout.addWidget(ECG_controls_groupbox)


        container_layout.addStretch()
        ### Finally, add to the main layout
        mainlayout.addWidget(container_frame) 
        

    def setup_plots(self,mainlayout):
        # Create a base frame and layout to put the plots in
        container_frame = QFrame()
        container_layout = QVBoxLayout(container_frame)

        # #### First create and add a toolbar
        # toolbar_layout = QHBoxLayout()

        # # Create all the buttons.
        # self.addHeartBeat_btn = QPushButton(icon=QIcon("imgs/icons/plus-2.svg"))
        # self.addHeartBeat_btn.setToolTip("Add Heart Beat")
        # self.remHeartBeat_btn = QPushButton(icon=QIcon("imgs/icons/minus.svg"))
        # self.remHeartBeat_btn.setToolTip("Remove Heart Beat")
        # self.addRemovalRegion_btn = QPushButton(icon=QIcon("imgs/icons/row-remove.svg"))
        # self.addRemovalRegion_btn.setToolTip("Add Removal Region")
        # # Add buttons to layout
        # toolbar_layout.addWidget(self.addHeartBeat_btn)
        # toolbar_layout.addWidget(self.remHeartBeat_btn)
        # toolbar_layout.addWidget(self.addRemovalRegion_btn)

    

        # # Set params
        # toolbar_layout.addStretch()
        # toolbar_layout.setContentsMargins(45,0,0,0)
        # container_layout.addLayout(toolbar_layout)
        
        #### Plots
        # Add the ECG Axis to the plot layout
        self.ECG_Axis = EcgPlot()
        container_layout.addWidget(self.ECG_Axis)
        
        # Adding the heart rate axis
        self.HR_Axis = HeartRatePlot()
        container_layout.addWidget(self.HR_Axis)

        # Changing background to transparent so its the same color as the app background.
        # Just looks nicer (imo)    
        self.HR_Axis.setBackground(background=None)
        self.ECG_Axis.setBackground(background=None)

        # Finally we add the frame to the layout.
        mainlayout.addWidget(container_frame)

        # Last thing actually - need to connect the plots together so they are linked on the X axis
        self.HR_Axis.setXLink(self.ECG_Axis)

    def setup_menubar(self,mainlayout):
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        filemenu = menubar.addMenu("File...")
        ecgmenu = menubar.addMenu("ECG...")
        helpmenu = menubar.addMenu("Help...")

        ## Add actions for file... menu
        # Loading ECG files
        load_ecg_action = filemenu.addAction("New Project / Load New ECG (.csv)")
        load_ecg_action.triggered.connect(self.load_ecg_action_clicked)
        # Exporting Heart Rate and Beats
        export_data_action = filemenu.addAction("Export Heart Rate and Heart Beats (.csv)")
        export_data_action.triggered.connect(self.export_data_action_clicked)
        # Saving Project Files
        save_project_file_action = filemenu.addAction("Save Project File (.Flow)")
        save_project_file_action.triggered.connect(self.save_project_file_action_clicked)
        # Open Project File
        open_project_file_action = filemenu.addAction("Open Project File (.Flow)")
        open_project_file_action.triggered.connect(self.open_project_file_action_clicked)

        ## Add actions for ecgmenu...
        beat_detection_action = ecgmenu.addAction("Beat Detection")
        beat_detection_action.triggered.connect(self.beat_detection_action_clicked)
        cwt_bandpass_action = ecgmenu.addAction("CWT Bandpass")
        cwt_bandpass_action.triggered.connect(self.cwt_bandpass_action_clicked)

        ## Add actions for help...
        open_docs_action = helpmenu.addAction("Open Documentation")
        open_docs_action.triggered.connect(self.open_docs_action_clicked)
        about_action = helpmenu.addAction("About")
        about_action.triggered.connect(self.about_action_clicked)

        
    ### MenuBar Actions/Events ###
    ## File...
    def open_project_file_action_clicked(self):
        pass
    def save_project_file_action_clicked(self):
        pass
    def load_ecg_action_clicked(self):
        self.controller.load_data()
    def export_data_action_clicked(self):
        self.controller.export_csv()
    ## ECG...
    def beat_detection_action_clicked(self):
        self.controller.open_beat_detection()
    def cwt_bandpass_action_clicked(self):
        self.controller.open_filter_ecg()
    ## Help...
    def open_docs_action_clicked(self):
        pass
    def about_action_clicked(self):
        self.controller.open_about_window()
    
    


    ### Setup the events for buttons and such 
    def setup_events(self):
        ## ECG Controls
        self.add_heartbeat_button.clicked.connect(
            self.controller.add_heartbeat
        )
        self.remove_heartbeat_button.clicked.connect(
            self.controller.remove_heartbeat
        )
        self.insert_removal_region_button.clicked.connect(
            self.controller.insert_removal_region
        )

        ## ECG View
        self.show_filtered_signal_toggle.clicked.connect(
            self.controller.show_filtered_signal_toggled
        )
        self.show_partial_calc_toggle.clicked.connect(
            self.controller.show_partial_calc_toggled
        )

    def setup_keyboard_shortcuts(self):
        self.shortcut_add_heartbeat = QShortcut(QKeySequence('Ctrl+A'),self)
        self.shortcut_add_heartbeat.activated.connect(self.controller.add_heartbeat)

        self.shortcut_remove_heartbeat = QShortcut(QKeySequence('Ctrl+R'),self)
        self.shortcut_remove_heartbeat.activated.connect(self.controller.remove_heartbeat)

        self.shortcut_insert_removal_region = QShortcut(QKeySequence('Ctrl+I'),self)
        self.shortcut_insert_removal_region.activated.connect(self.controller.insert_removal_region)

        self.shortcut_load_ecg = QShortcut(QKeySequence('Ctrl+N'),self)
        self.shortcut_load_ecg.activated.connect(self.controller.load_data)

        self.shortcut_export_ecg = QShortcut(QKeySequence('Ctrl+E'),self)
        self.shortcut_load_ecg.activated.connect(self.controller.export_csv)


def main():

    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    window = TonaFlow()
    window.show()

    exit_code = app.exec()  # this blocks until window is closed



    sys.exit(exit_code)

