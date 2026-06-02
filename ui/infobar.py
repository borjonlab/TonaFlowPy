from PyQt6.QtWidgets import (
    QGroupBox,
    QToolButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize

import pyqtgraph as pg
import numpy as np
import darkdetect


class InfoBarButton(QToolButton):
    def __init__(self,iconName,text="",istoggle=False):
        super().__init__()
        self.setCheckable(istoggle)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.change_style_mode(iconName)
        self.setIconSize(QSize(50,50))
        self.setText(text)
        self.setStyleSheet("""
                             QToolButton:checked {background:#8a8a8a;}  
                          """)

    def change_style_mode(self,iconName):
        # detect dark or not
        if darkdetect.isDark():
            self.setIcon(QIcon("imgs/icons/Infobar/dark/" + iconName))
        else:
            self.setIcon(QIcon("imgs/icons/Infobar/light/" + iconName))

class InfoBarGroupBox(QGroupBox):
    def __init__(self, title):
        super().__init__(title)

        if darkdetect.isDark():
            self.setStyleSheet("""
                            QGroupBox {
                                border: 1px solid #d6d6d6;
                                border-radius: 6px;
                                margin-top: 18px; /* space for title */
                                background-color: #242423;
                            }

                            /* Title styling */
                                 QGroupBox::title {
                                subcontrol-origin: margin;
                                subcontrol-position: top left;
                                padding: 2px 10px;
                                margin-left: 8px;

                                font-size: 11px;
                                font-weight: 600;
                                color: #ffffff;

                                background-color: #242423;
                            }
                            """)
        else:
            self.setStyleSheet("""
                            QGroupBox {
                                border: 1px solid #d6d6d6;
                                border-radius: 6px;
                                margin-top: 18px; /* space for title */
                                background-color: #242423;
                            }

                            /* Title styling */
                                 QGroupBox::title {
                                subcontrol-origin: margin;
                                subcontrol-position: top left;
                                padding: 2px 10px;
                                margin-left: 8px;

                                font-size: 11px;
                                font-weight: 600;
                                color: #ffffff;

                                background-color: #242423;
                            }
                            """)
            
