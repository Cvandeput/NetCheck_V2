import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QToolButton, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame

from .dashboardPage import DashboardWindow
from ..services.database import Database



class LoginWindow(QWidget):
	def __init__(self):
		super().__init__()

		self.dashboard_window = None

		self.setWindowTitle("NetTool - Connexion")
		self.setFixedSize(900, 500)
		self.setWindowFlags(
            Qt.Window |
            Qt.CustomizeWindowHint |
            Qt.WindowTitleHint |
            Qt.WindowMinimizeButtonHint |
            Qt.WindowCloseButtonHint
        )

		# --- Structure principale ---
		main_layout = QHBoxLayout(self)
		main_layout.setContentsMargins(0, 0, 0, 0)
		main_layout.setSpacing(0)

		# --- SECTION GAUCHE ---
		self.left_frame = QFrame()
		self.left_frame.setObjectName("leftFrame")
		left_layout = QVBoxLayout(self.left_frame)
		left_layout.setContentsMargins(0, 0, 0, 0)

		self.illustration = QLabel()
		self.illustration.setAlignment(Qt.AlignCenter)

		base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
		image_path = os.path.join(base_dir, "assets", "images", "background.jpg")
		pix = QPixmap(image_path)
		if not pix.isNull():
			self.illustration.setPixmap(pix.scaled(500, 500, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))

		left_layout.addWidget(self.illustration)
		main_layout.addWidget(self.left_frame, 1)

		# --- SECTION DROITE (Formulaire) ---
		self.right_frame = QFrame()
		self.right_frame.setObjectName("rightFrame")
		right_layout = QVBoxLayout(self.right_frame)
		right_layout.setContentsMargins(50, 40, 50, 40)
		right_layout.setSpacing(0)

		self.pending_username = None

		# --- Logo de l'app (au dessus des formulaires connexion et reset) ---
		self.logo = QLabel()
		self.logo.setAlignment(Qt.AlignCenter)
		logo_pix = QPixmap(os.path.join(base_dir, "assets", "images", "logo.png"))
		if not logo_pix.isNull():
			self.logo.setPixmap(logo_pix.scaled(72, 72, Qt.KeepAspectRatio, Qt.SmoothTransformation))

		# --- Formulaire connexion ---
		self.login_form = QFrame()
		self.login_form.setObjectName("loginForm")
		login_layout = QVBoxLayout(self.login_form)
		login_layout.setContentsMargins(0, 0, 0, 0)
		login_layout.setSpacing(0)

		title = QLabel("Connexion Utilisateur")
		title.setObjectName("mainTitle")
		title.setAlignment(Qt.AlignCenter)

		user_label = QLabel("Nom d'utilisateur")
		user_label.setObjectName("fieldLabel")
		self.username = QLineEdit()
		self.username.setPlaceholderText("Nom")
		self.username.setFixedSize(300, 40)

		pass_label = QLabel("Mot de passe")
		pass_label.setObjectName("fieldLabel")
		self.password = QLineEdit()
		self.password.setPlaceholderText("••••••••")
		self.password.setEchoMode(QLineEdit.Password)
		self.password.setFixedSize(300, 40)

		eye_open_icon = os.path.join(base_dir, "assets", "icons", "eye-open.svg")
		eye_closed_icon = os.path.join(base_dir, "assets", "icons", "eye-closed.svg")
		self.password_visible = False
		self.password_toggle_icons = {
			True: QIcon(eye_open_icon),
			False: QIcon(eye_closed_icon),
		}
		self.password_toggle_action = self.password.addAction(
			self.password_toggle_icons[False],
			QLineEdit.TrailingPosition
		)

		toggle_button = self.password.findChild(QToolButton)
		if toggle_button:
			toggle_button.setCursor(Qt.PointingHandCursor)

		self.password_toggle_action.triggered.connect(self.toggle_password_visibility)

		login_button = QPushButton("Se connecter")
		login_button.setObjectName("loginButton")
		login_button.setCursor(Qt.PointingHandCursor)
		login_button.clicked.connect(self.login)

		login_layout.addWidget(title)
		login_layout.addSpacing(30)
		login_layout.addWidget(user_label)
		login_layout.addWidget(self.username)
		login_layout.addSpacing(15)
		login_layout.addWidget(pass_label)
		login_layout.addWidget(self.password)
		login_layout.addSpacing(30)
		login_layout.addWidget(login_button)

		# --- Formulaire reset ---
		self.reset_form = QFrame()
		self.reset_form.setObjectName("resetForm")
		self.reset_form.setVisible(False)
		reset_layout = QVBoxLayout(self.reset_form)
		reset_layout.setContentsMargins(0, 0, 0, 0)
		reset_layout.setSpacing(0)

		reset_title = QLabel("Définir votre mot de passe")
		reset_title.setObjectName("mainTitle")
		reset_title.setAlignment(Qt.AlignCenter)

		new_pass_label = QLabel("Nouveau mot de passe")
		new_pass_label.setObjectName("fieldLabel")
		self.new_password = QLineEdit()
		self.new_password.setPlaceholderText("Nouveau mot de passe")
		self.new_password.setEchoMode(QLineEdit.Password)
		self.new_password.setFixedSize(300, 40)

		confirm_label = QLabel("Confirmation")
		confirm_label.setObjectName("fieldLabel")
		self.confirm_password = QLineEdit()
		self.confirm_password.setPlaceholderText("Confirmer le mot de passe")
		self.confirm_password.setEchoMode(QLineEdit.Password)
		self.confirm_password.setFixedSize(300, 40)

		reset_button = QPushButton("Enregistrer le mot de passe")
		reset_button.setObjectName("loginButton")
		reset_button.setCursor(Qt.PointingHandCursor)
		reset_button.clicked.connect(self.reset_password)

		reset_layout.addWidget(reset_title)
		reset_layout.addSpacing(30)
		reset_layout.addWidget(new_pass_label)
		reset_layout.addWidget(self.new_password)
		reset_layout.addSpacing(15)
		reset_layout.addWidget(confirm_label)
		reset_layout.addWidget(self.confirm_password)
		reset_layout.addSpacing(30)
		reset_layout.addWidget(reset_button)

		# --- Message statut ---
		self.message = QLabel("")
		self.message.setObjectName("statusMessage")
		self.message.setAlignment(Qt.AlignCenter)
		self.message.setWordWrap(True)

		right_layout.addWidget(self.logo)
		right_layout.addSpacing(10)
		right_layout.addWidget(self.login_form)
		right_layout.addWidget(self.reset_form)
		right_layout.addWidget(self.message)
		right_layout.addSpacing(70)

		main_layout.addWidget(self.right_frame, 1)


	def login(self):
		if not self.username.text().strip() or not self.password.text().strip():
			self.message.setText("Champs incomplets")
			self.message.setStyleSheet("color: #FFB74D;")
			return

		db = Database()

		if db.validateCredentials(self.username.text(), self.password.text()):
			user_info = db.getUserInfo()
			self.dashboard_window = DashboardWindow(user_info=user_info)
			self.dashboard_window.logout_requested.connect(self.on_logout)
			self.dashboard_window.show()
			self.hide()
			
		else:
			if db.password_reset_required:
				self.pending_username = self.username.text().strip()
				self.show_reset_form()
				self.message.setText("Veuillez définir un mot de passe définitif.")
				self.message.setStyleSheet("color: #FFB74D;")
				return

			if db.last_error == "COMPTE BLOQUE":
				self.message.setText("Compte bloqué temporairement. Réessayez plus tard.")
				self.message.setStyleSheet("color: #FF5252;")
				return

			self.message.setText(db.last_error if db.last_error else "Erreur de connexion")
			self.message.setStyleSheet("color: #FF5252;")


	def on_logout(self):
		self.message.setText("")
		self.password.clear()
		self.password_visible = False
		self.password.setEchoMode(QLineEdit.Password)
		self.password_toggle_action.setIcon(self.password_toggle_icons[False])
		self.show_login_form()
		self.show()


	def toggle_password_visibility(self):
		self.password_visible = not self.password_visible
		echo_mode = QLineEdit.Normal if self.password_visible else QLineEdit.Password
		self.password.setEchoMode(echo_mode)
		self.password_toggle_action.setIcon(self.password_toggle_icons[self.password_visible])

	def show_reset_form(self):
		self.login_form.setVisible(False)
		self.reset_form.setVisible(True)
		self.new_password.clear()
		self.confirm_password.clear()
		self.password.clear()

	def show_login_form(self):
		self.login_form.setVisible(True)
		self.reset_form.setVisible(False)
		self.pending_username = None
		self.new_password.clear()
		self.confirm_password.clear()

	def reset_password(self):
		new_password = self.new_password.text().strip()
		confirm_password = self.confirm_password.text().strip()

		if not self.pending_username:
			self.message.setText("Session invalide. Veuillez vous reconnecter.")
			self.message.setStyleSheet("color: #FF5252;")
			self.show_login_form()
			return

		if not new_password or not confirm_password:
			self.message.setText("Champs incomplets")
			self.message.setStyleSheet("color: #FFB74D;")
			return

		if new_password != confirm_password:
			self.message.setText("Les mots de passe ne correspondent pas")
			self.message.setStyleSheet("color: #FF5252;")
			return

		db = Database()
		if db.setPasswordAndActivate(self.pending_username, new_password):
			username = self.pending_username
			self.message.setText("Mot de passe mis à jour. Connectez-vous.")
			self.message.setStyleSheet("color: #a7f3d0;")
			self.show_login_form()
			self.username.setText(username)
			return

		if db.last_error == "PASSWORD_WEAK":
			self.message.setText(
				"Mot de passe trop simple. 13 caractères minimum avec majuscule, minuscule, chiffre et caractère spécial."
			)
			self.message.setStyleSheet("color: #FF5252;")
			return

		self.message.setText(db.last_error if db.last_error else "Erreur de mise à jour")
		self.message.setStyleSheet("color: #FF5252;")
