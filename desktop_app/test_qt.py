import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton

app = QApplication(sys.argv)
window = QMainWindow()
window.setGeometry(100, 100, 300, 200)
window.setWindowTitle('Test App')

button = QPushButton('Click Me', window)
button.setGeometry(100, 100, 100, 30)

window.show()
sys.exit(app.exec())
