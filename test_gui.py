from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt

app = QApplication([])

window = QWidget()
window.setWindowTitle("Procto GUI Test")
window.resize(500, 250)

layout = QVBoxLayout(window)
label = QLabel("PROCTO GUI IS WORKING")
label.setAlignment(Qt.AlignmentFlag.AlignCenter)
layout.addWidget(label)

window.show()
window.raise_()
window.activateWindow()

app.exec()
