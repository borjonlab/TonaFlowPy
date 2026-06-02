from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QHBoxLayout
)
from PyQt6.QtCore import Qt


class AboutWindow(QWidget):
    import darkdetect
    def __init__(self, parent=None):
        super().__init__(parent)


        self.setWindowTitle("About")
        self.resize(460, 520)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)


        if self.darkdetect.isDark():
            self.setStyleSheet("""
                QWidget {
                    background-color: #121212;
                    color: #eaeaea;
                    font-size: 14px;
                }

                #card {
                    background-color: #1e1e1e;
                    border-radius: 12px;
                }

                QLabel {
                    background: transparent;
                }

                QLabel#text {
                    color: #cfcfcf;
                }

                QLabel#credits {
                    color: #dddddd;
                }

                QLabel a {
                    color: #4da3ff;
                }

                QLabel a:hover {
                    text-decoration: underline;
                }

                QPushButton {
                    background: transparent;
                    color: #eaeaea;
                    border: none;
                    font-size: 16px;
                }

                QPushButton:hover {
                    color: #ff5c5c;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #d6d6d6;
                    color: #eaeaea;
                    font-size: 14px;
                }

                #card {
                    background-color: #b5b0ff;
                    border-radius: 12px;
                }

                QLabel {
                    background: transparent;
                }

                QLabel#text {
                    color: #cfcfcf;
                }

                QLabel#credits {
                    color: #dddddd;
                }

                QLabel a {
                    color: #4da3ff;
                }

                QLabel a:hover {
                    text-decoration: underline;
                }

                QPushButton {
                    background: transparent;
                    color: #eaeaea;
                    border: none;
                    font-size: 16px;
                }

                QPushButton:hover {
                    color: #ff5c5c;
                }
            """)


        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 20, 20, 20)
        outer.setSpacing(10)

        top_bar = QHBoxLayout()
        top_bar.addStretch()

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(28, 28)
        close_btn.clicked.connect(self.close)
        top_bar.addWidget(close_btn)

        outer.addLayout(top_bar)

        card = QWidget()
        card.setObjectName("card")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(14)

        logo = QLabel()
        logo.setPixmap(self.parent().LOGO_PIXMAP)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(logo)

        about = QLabel(
            "<h3>TonaFlow is a free and open-source application for accessible ECG processing"
            " for researchers at all technical levels. </h3>"
        )
        about.setWordWrap(True)
        about.setAlignment(Qt.AlignmentFlag.AlignCenter)
        about.setObjectName("text")
        card_layout.addWidget(about)

        credits = QLabel(
            "<h3>Built with ❤ by Manash Sahoo.</h3><br>"
            "TonaFlow would not be possible without the <i>exceptional</i> support from:<br>"
            "• Natasha Mmbajonas (Interface / GUI)<br>"
            "• Katherine D. Rhodes (Testing)<br>"
            "• Jeremy I. Borjon (Oversight)"
        )
        credits.setAlignment(Qt.AlignmentFlag.AlignCenter)
        credits.setObjectName("credits")
        credits.setWordWrap(True)
        card_layout.addWidget(credits)

        link = QLabel('<a href="http://www.borjonlab.com">www.borjonlab.com</a>')
        link.setOpenExternalLinks(True)
        link.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(link)

        link2 = QLabel('<a href="http://www.manashsahoo.com">www.manashsahoo.com</a>')
        link2.setOpenExternalLinks(True)
        link2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(link2)

        outer.addWidget(card)
        outer.addStretch()

    def center_on_parent(self):
        parent = self.parent()
        if not parent:
            return


        x = int((parent.rect().width() - self.frameSize().width()) /2)
        y = int((parent.rect().height() - self.frameSize().height()) /2)

        self.move(x,y)
