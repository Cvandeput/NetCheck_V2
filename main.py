import sys
import os
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from src.pages.loginPage import LoginWindow



def loadStyleSheet():
    cssFile = [
        "badges.css", "buttons.css", 
        "content.css", "dashboard.css", 
        "global.css", "login.css", 
        "results.css", "sidebar.css", 
        "table.css", "tools.css"
    ]
    full_stylesheet = ""

    for css in cssFile:
        css_path = os.path.join(os.path.dirname(__file__), "src", "style", css)

        try:
            with open(css_path, "r") as f:
                full_stylesheet += f.read() + "\n"
            
        except FileNotFoundError:
            print(f"Erreur : Le fichier {css_path} est introuvable.")
        
    return full_stylesheet
    


# --- Windows : identifiant propre a l'app pour afficher le logo dans la barre des taches (sinon icone python) ---
if sys.platform == "win32":
    import ctypes
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("NetCheck")

app = QApplication(sys.argv)
app.setStyleSheet(loadStyleSheet())

# --- Logo de l'app (applique a toutes les fenetres) ---
app.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), "src", "assets", "images", "logo.png")))


window = LoginWindow()
window.show()
sys.exit(app.exec())
