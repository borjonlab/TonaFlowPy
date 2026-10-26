from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QLineEdit, QSlider, QFrame, QColorDialog, QButtonGroup
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor, QFont




RAW_COLOR = (74, 222, 128, 255)

FILT_COLOR = (229, 231, 235, 255)

MARKER_COLOR = (245, 158, 11, 255)

FILL_COLOR = (239, 68, 68, 46)

STYLE = '''

QDialog {
    background-color: #18181b;
}
QLabel {
    color: #d4d4d8;
    font-size: 13px;
    font-weight: 400;
}
QLabel#section {
    font-weight: 600;
    letter-spacing: 1px;
    padding-top: 6px;
    color: #71717a;
    font-size: 11px;

}
QLabel#value {
    font-size: 12px;
    min-width: 44px;
    color: #a1a1aa;

}
QFrame#divider {
    background-color: #27272a;
    border: none;
    max-height: 1px;
    min-height: 1px;
}
QLineEdit#hex {
    padding: 3px 6px;
    font-size: 12px;
    background-color: #1f1f23;
    color: #e4e4e7;
    border: 1px solid #2e2e33;
    border-radius: 2px;
    selection-background-color: #3f3f46;
}
QLineEdit#hex:focus {
    border: 1px solid #52525b;
}
QSlider::groove:horizontal {
    height: 4px;
    background: #2e2e33;
    border-radius: 2px;
}
QSlider::sub-page:horizontal {
    background: #6d8fd6;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #e4e4e7;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}
QPushButton#segment {
    border-radius: 0px;
    padding: 4px 0px;
    min-width: 34px;
    font-size: 13px;
    background-color: #1f1f23;
    color: #a1a1aa;
    border: 1px solid #2e2e33;
}
QPushButton#segment:hover {
    color: #e4e4e7;
}
QPushButton#segment:checked {
    background-color: #2e2e33;
    color: #f4f4f5;
}
QPushButton#segmentLeft {
    background-color: #1f1f23;
    color: #a1a1aa;
    border: 1px solid #2e2e33;
    border-top-left-radius: 2px;
    border-bottom-left-radius: 2px;
    padding: 4px 0px;
    min-width: 34px;
    font-size: 13px;
}
QPushButton#segmentRight {
    background-color: #1f1f23;
    color: #a1a1aa;
    border: 1px solid #2e2e33;
    border-top-right-radius: 2px;
    border-bottom-right-radius: 2px;
    padding: 4px 0px;
    min-width: 34px;
    font-size: 13px;
}
QPushButton#segmentLeft:hover, QPushButton#segmentRight:hover {
    color: #e4e4e7;
}
QPushButton#segmentLeft:checked, QPushButton#segmentRight:checked {
    background-color: #2e2e33;
    color: #f4f4f5;
}
QPushButton#secondary {
    background-color: #27272a;
    color: #e4e4e7;
    border: 1px solid #3f3f46;
    border-radius: 2px;
    padding: 6px 14px;
    font-size: 13px;
}
QPushButton#secondary:hover {
    background-color: #303034;
}
QPushButton#textButton {
    background: transparent;
    color: #a1a1aa;
    border: none;
    border-radius: 2px;
    padding: 6px 10px;
    font-size: 13px;
}
QPushButton#textButton:hover {
    color: #f4f4f5;
}
QPushButton#primary {
    background-color: #6d8fd6;
    color: #0f1115;
    border: none;
    border-radius: 2px;
    padding: 6px 18px;
    font-size: 13px;
    font-weight: 600;
}
QPushButton#primary:hover {
    background-color: #7f9de0;
}
'''




class ColorRow(QWidget):
    changed = pyqtSignal()

    def __init__(self, color, alpha=False, parent=None):
        super().__init__(parent)
        self.useAlpha = alpha
        self.color = QColor(*color)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        self.swatch_btn = QPushButton()
        self.swatch_btn.setFixedSize(20, 20)
        self.swatch_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.swatch_btn.clicked.connect(self.pick_color)
        self.hexEdit = QLineEdit()
        self.hexEdit.setObjectName('hex')
        font = QFont('Menlo')
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.hexEdit.setFont(font)
        self.hexEdit.setFixedWidth(96 if alpha else 80)
        self.hexEdit.textEdited.connect(self.hex_edited)
        self.hexEdit.editingFinished.connect(self.refresh)
        layout.addWidget(self.swatch_btn)
        layout.addWidget(self.hexEdit)
        layout.addStretch()
        self.refresh()
    def hex_text(self):
        if self.useAlpha:
            return self.color.name(QColor.NameFormat.HexArgb)
        return self.color.name()
    def paint_swatch(self):
        r, g, b, a = self.color.getRgb()
        self.swatch_btn.setStyleSheet(
            f"background-color: rgba({r},{g},{b},{a}); border: 1px solid #3f3f46; border-radius: 3px;"
        )
    def refresh(self):
        self.hexEdit.setText(self.hex_text())
        self.paint_swatch()
    def pick_color(self):
        if self.useAlpha:
            c = QColorDialog.getColor(self.color, self, 'Pick a Color', QColorDialog.ColorDialogOption.ShowAlphaChannel)
        else:
            c = QColorDialog.getColor(self.color, self, 'Pick a Color')
        if not c.isValid():
            return
        self.color = c
        self.refresh()
        self.changed.emit()
    def hex_edited(self, text):
        text = text.strip()
        if not text.startswith('#'):
            text = '#' + text
        if len(text) != 7 and not (self.useAlpha and len(text) == 9):
            return
        c = QColor(text)
        if not c.isValid():
            return
        self.color = c
        self.paint_swatch()
        self.changed.emit()
    def get_color(self):
        return self.color.getRgb()
class SettingsWindow(QDialog):
    settingsApplied = pyqtSignal(dict)
    def __init__(self, settings=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Preference/Settings')
        self.resize(420, 480)
        self.setStyleSheet(STYLE)
        if not settings:
            settings = {
                'beat_color': MARKER_COLOR,
                'beat_size': 10,
                'beat_symbol': 'o',
                'region_color': FILL_COLOR,
                'raw_color': RAW_COLOR,
                'raw_width': 1,
                'filt_color': FILT_COLOR,
                'filt_width': 1,
            }
        self.cfg = dict(settings)
        self.setup_ui()
        self.update_labels()




    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)
        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(10)
        grid.setColumnMinimumWidth(0, 90)
        row = 0

        row = self.add_section(grid, row, 'Raw ECG')
        self.raw_color_row = ColorRow(self.cfg['raw_color'])
        grid.addWidget(QLabel('Color'), row, 0)
        grid.addWidget(self.raw_color_row, row, 1)
        row += 1
        self.raw_thick_slider = QSlider(Qt.Orientation.Horizontal)
        self.raw_thick_slider.setRange(5, 50)
        self.raw_thick_slider.setValue(int(self.cfg['raw_width'] * 10))
        self.rawWidthLbl = QLabel()
        self.rawWidthLbl.setObjectName('value')
        self.raw_thick_slider.valueChanged.connect(self.update_labels)
        grid.addWidget(QLabel('Thickness'), row, 0)
        grid.addLayout(self.slider_row(self.raw_thick_slider, self.rawWidthLbl), row, 1)
        row += 1
        row = self.add_section(grid, row, 'Filtered ECG')
        self.filt_color_row = ColorRow(self.cfg['filt_color'])
        grid.addWidget(QLabel('Color'), row, 0)
        grid.addWidget(self.filt_color_row, row, 1)
        row += 1
        self.filtThickSlider = QSlider(Qt.Orientation.Horizontal)
        self.filtThickSlider.setRange(5, 50)
        self.filtThickSlider.setValue(int(self.cfg['filt_width'] * 10))
        self.filt_width_lbl = QLabel()
        self.filt_width_lbl.setObjectName('value')
        self.filtThickSlider.valueChanged.connect(self.update_labels)
        grid.addWidget(QLabel('Thickness'), row, 0)
        grid.addLayout(self.slider_row(self.filtThickSlider, self.filt_width_lbl), row, 1)
        row += 1
        row = self.add_section(grid, row, 'Heartbeat Markers')
        self.markerColorRow = ColorRow(self.cfg['beat_color'])
        grid.addWidget(QLabel('Color'), row, 0)
        grid.addWidget(self.markerColorRow, row, 1)
        row += 1
        self.marker_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.marker_size_slider.setRange(4, 30)
        self.marker_size_slider.setValue(int(self.cfg['beat_size']))
        self.markerSizeLbl = QLabel()
        self.markerSizeLbl.setObjectName('value')
        self.marker_size_slider.valueChanged.connect(self.update_labels)
        grid.addWidget(QLabel('Size'), row, 0)
        grid.addLayout(self.slider_row(self.marker_size_slider, self.markerSizeLbl), row, 1)
        row += 1
        self.marker_btn_group = QButtonGroup(self)
        self.marker_btn_group.setExclusive(True)
        shapes = [('●', 'o'), ('▲', 't1'), ('■', 's'), ('✕', 'x')]
        segLayout = QHBoxLayout()
        segLayout.setSpacing(0)
        for idx in range(len(shapes)):
            btn = QPushButton(shapes[idx][0])
            btn.setCheckable(True)
            btn.setProperty('symbol', shapes[idx][1])
            if idx == 0:
                btn.setObjectName('segmentLeft')
            elif idx == len(shapes) - 1:
                btn.setObjectName('segmentRight')
            else:
                btn.setObjectName('segment')
            if shapes[idx][1] == self.cfg['beat_symbol']:
                btn.setChecked(True)
            self.marker_btn_group.addButton(btn)
            segLayout.addWidget(btn)
        if not self.marker_btn_group.checkedButton():
            self.marker_btn_group.buttons()[0].setChecked(True)
        segLayout.addStretch()
        grid.addWidget(QLabel('Shape'), row, 0)
        grid.addLayout(segLayout, row, 1)
        row += 1
        row = self.add_section(grid, row, 'Removal Regions')
        self.fill_color_row = ColorRow(self.cfg['region_color'], alpha=True)
        grid.addWidget(QLabel('Fill'), row, 0)
        grid.addWidget(self.fill_color_row, row, 1)
        row += 1
        layout.addLayout(grid)
        layout.addStretch()
        line = QFrame()
        line.setObjectName('divider')
        layout.addWidget(line)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = QPushButton('Cancel')
        cancel_btn.setObjectName('secondary')
        cancel_btn.setAutoDefault(False)
        cancel_btn.clicked.connect(self.reject)
        applyBtn = QPushButton('Apply')
        applyBtn.setObjectName('textButton')
        applyBtn.setAutoDefault(False)
        applyBtn.clicked.connect(self.apply_settings)
        save_btn = QPushButton('Save')
        save_btn.setObjectName('primary')
        save_btn.setDefault(True)
        save_btn.clicked.connect(self.save_settings)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(applyBtn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def add_section(self, grid, row, title):
        if row > 0:
            line = QFrame()
            line.setObjectName('divider')
            grid.addWidget(line, row, 0, 1, 2)
            row += 1
        header_lbl = QLabel(title.upper())
        header_lbl.setObjectName('section')
        grid.addWidget(header_lbl, row, 0, 1, 2)
        return row + 1
    def slider_row(self, slider, lbl):
        h = QHBoxLayout()
        h.setSpacing(10)
        h.addWidget(slider)
        h.addWidget(lbl)
        return h
    def update_labels(self):
        self.rawWidthLbl.setText(f"{self.raw_thick_slider.value() / 10:.1f} px")
        self.filt_width_lbl.setText(f"{self.filtThickSlider.value() / 10:.1f} px")
        self.markerSizeLbl.setText(f"{self.marker_size_slider.value()} px")

    def get_settings(self):
        self.cfg['raw_color'] = self.raw_color_row.get_color()
        self.cfg['raw_width'] = self.raw_thick_slider.value() / 10
        self.cfg['filt_color'] = self.filt_color_row.get_color()
        self.cfg['filt_width'] = self.filtThickSlider.value() / 10
        self.cfg['beat_color'] = self.markerColorRow.get_color()
        self.cfg['beat_size'] = self.marker_size_slider.value()
        self.cfg['beat_symbol'] = self.marker_btn_group.checkedButton().property('symbol')
        self.cfg['region_color'] = self.fill_color_row.get_color()
        return dict(self.cfg)
    def apply_settings(self):
        self.settingsApplied.emit(self.get_settings())
    def save_settings(self):
        self.apply_settings()
        self.accept()
