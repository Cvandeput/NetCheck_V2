from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

class DivideSubnetworkPage(QWidget):
    def __init__(self):
            super().__init__()
            
            # --- Structure principale ---
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
    
            # --- Carte outil ---
            card = QFrame()
            card.setObjectName("toolCard")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(24, 22, 24, 22)
            card_layout.setSpacing(14)
    
            # --- Ligne de saisie ---
            row = QHBoxLayout()
            row.setSpacing(10)
            
            # --- input IP ---
            self.ip_input = QLineEdit()
            self.ip_input.setPlaceholderText("IPv4")
            self.ip_input.setObjectName("primaryInput")
            self.ip_input.setFixedHeight(46)
    
            # --- input masque reseau ---
            self.mask_input = QLineEdit()
            self.mask_input.setPlaceholderText("Masque du réseau")
            self.mask_input.setObjectName("primaryInput")
            self.mask_input.setFixedHeight(46)
            self.mask_input.returnPressed.connect(self.run_check)
            
            # --- input number IP ---
            self.number_ip_input = QLineEdit()
            self.number_ip_input.setPlaceholderText("Nombre IP")
            self.number_ip_input.setObjectName("primaryInput")
            self.number_ip_input.setFixedHeight(46)
    
            # --- input number subnet ---            
            self.number_subnet_input = QLineEdit()
            self.number_subnet_input.setPlaceholderText("Nombre sous réseau")
            self.number_subnet_input.setObjectName("primaryInput")
            self.number_subnet_input.setFixedHeight(46)
            self.number_subnet_input.returnPressed.connect(self.run_check)
            
            # --- bouton calculer ---
            run_button = QPushButton("Calculer")
            run_button.setObjectName("actionButton")
            run_button.setFixedSize(122, 46)
            run_button.setCursor(Qt.PointingHandCursor)
            run_button.clicked.connect(self.run_check)
            
            row.addWidget(self.ip_input, 1)
            row.addWidget(self.mask_input, 1)
            row.addWidget(self.number_ip_input, 1)
            row.addWidget(self.number_subnet_input, 1)
            row.addWidget(run_button)
            
            # --- Etat vide ---
            self.empty_state = QFrame()
            self.empty_state.setObjectName("emptyState")
            empty_layout = QHBoxLayout(self.empty_state)
            empty_layout.setContentsMargins(18, 14, 18, 14)
    
            empty_text = QLabel("Ajoutez une IP, un Masque, le nombre de sous réseau souhaité et le nombre d'ip par sous réseau")
            empty_text.setObjectName("emptyStateText")
            empty_layout.addWidget(empty_text)
            
            # --- Carte resultat ---
            self.result_card = QFrame()
            self.result_card.setObjectName("resultCard")
            self.result_card.setVisible(False)
            result_layout = QVBoxLayout(self.result_card)
            result_layout.setContentsMargins(16, 12, 16, 12)
            result_layout.setSpacing(8)

            self.status_badge = QLabel("SOUS-RÉSEAU") # --- a modifier ---
            self.status_badge.setObjectName("badgeNeutral")
            self.status_badge.setAlignment(Qt.AlignCenter)
            self.status_badge.setFixedWidth(140)

            self.result = QLabel("")
            self.result.setObjectName("statusMessage")

            result_layout.addWidget(self.status_badge, 0, Qt.AlignLeft)
            result_layout.addWidget(self.result)

            card_layout.addLayout(row)
            card_layout.addWidget(self.empty_state)
            card_layout.addWidget(self.result_card)
            card_layout.addStretch(1)

            layout.addWidget(card)
            
    def run_check(self):
        # --- inserer la logique pour les calculs ici ---
        pass