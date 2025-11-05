import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

def main():
    # Create the application instance
    app = QApplication(sys.argv)

    # Optional: set a global app name and style
    app.setApplicationName("Fynix")
    app.setStyle("Fusion")

    # Create and show main window
    window = MainWindow()
    window.show()

    # Start Qt event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()