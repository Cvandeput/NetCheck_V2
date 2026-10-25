from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QHeaderView, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from ...services.database import Database

from ...services.logic import ClassMask, getIPClass, getIPClassMask, getNetworkAddress, getSubnet, isClassFull, isIp, isSubnetMask, parseMask
from ...services.utils import remove_spaces



class GetSubnetPage(QWidget):
    def __init__(self, user_info):
        super().__init__()
        self.db = Database()
        self.user_info = user_info
        self.idSelection = None

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

        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("IPv4")
        self.ip_input.setObjectName("primaryInput")
        self.ip_input.setFixedHeight(46)

        self.mask_input = QLineEdit()
        self.mask_input.setPlaceholderText("Masque classful")
        self.mask_input.setObjectName("primaryInput")
        self.mask_input.setFixedHeight(46)
        self.mask_input.returnPressed.connect(self.run_check)

        run_button = QPushButton("Calculer")
        run_button.setObjectName("actionButton")
        run_button.setFixedSize(122, 46)
        run_button.setCursor(Qt.PointingHandCursor)
        run_button.clicked.connect(self.run_check)

        row.addWidget(self.ip_input, 1)
        row.addWidget(self.mask_input, 1)
        row.addWidget(run_button)

        # --- Etat vide ---
        self.empty_state = QFrame()
        self.empty_state.setObjectName("emptyState")
        empty_layout = QHBoxLayout(self.empty_state)
        empty_layout.setContentsMargins(18, 14, 18, 14)

        empty_text = QLabel("Ajoutez IP + masque pour calculer le sous-réseau")
        empty_text.setObjectName("emptyStateText")
        empty_layout.addWidget(empty_text)

        # --- Carte resultat ---
        self.result_card = QFrame()
        self.result_card.setObjectName("resultCard")
        self.result_card.setVisible(False)
        result_layout = QVBoxLayout(self.result_card)
        result_layout.setContentsMargins(16, 12, 16, 12)
        result_layout.setSpacing(8)

        self.status_badge = QLabel("SOUS-RÉSEAU")
        self.status_badge.setObjectName("badgeNeutral")
        self.status_badge.setAlignment(Qt.AlignCenter)
        self.status_badge.setFixedWidth(140)

        self.result = QLabel("")
        self.result.setObjectName("statusMessage")

        result_layout.addWidget(self.status_badge, 0, Qt.AlignLeft)
        result_layout.addWidget(self.result)
        
        # --- Historique des calculs ---
        self.data_history = QTableWidget(0, 3)
        self.data_history.setHorizontalHeaderLabels(["IP", "Masque", "Utilisateur"])
        self.data_history.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.data_history.verticalHeader().setVisible(False)
        self.data_history.setAlternatingRowColors(True)
        self.data_history.setObjectName("cidrTable") # --- reutilise le style du tableau CIDR ---
        self.data_history.setSelectionBehavior(QTableWidget.SelectRows)
        self.data_history.setSelectionMode(QTableWidget.SingleSelection)
        self.data_history.setEditTriggers(QTableWidget.NoEditTriggers)
        self.data_history.cellClicked.connect(self.selectionner_ip)

        card_layout.addLayout(row)
        card_layout.addWidget(self.empty_state)
        card_layout.addWidget(self.result_card)
        card_layout.addStretch(1)
        card_layout.addWidget(self.data_history)

        layout.addWidget(card)
        self.charger_liste()

    def charger_liste(self):
        rows = self.db.getIps(4)
        self.data_history.setRowCount(len(rows))

        for row_idx, (id_ip, ip, masque, username) in enumerate(rows):
            for col_idx, cell_value in enumerate((ip, masque, username)):
                self.data_history.setItem(row_idx, col_idx, QTableWidgetItem(cell_value))
            # --- donnees de la ligne stockees sur la 1ere cellule ---
            self.data_history.item(row_idx, 0).setData(Qt.UserRole, (id_ip, ip, masque))

    def selectionner_ip(self, row, column):
        id_ip, ip, masque = self.data_history.item(row, 0).data(Qt.UserRole)
        self.idSelection = id_ip
        self.ip_input.setText(ip)
        self.mask_input.setText(masque) 


    def run_check(self):
        # --- Execution du calcul de sous-reseau ---
        ip = remove_spaces(self.ip_input.text())
        mask = remove_spaces(self.mask_input.text())
        normalized_mask = parseMask(mask)

        self.empty_state.setVisible(False)
        self.result_card.setVisible(True)

        if not isIp(ip):
            self.result.setText("Adresse IP invalide")
            self.result.setStyleSheet("color: #ef4444;")
            self.status_badge.setText("ERREUR")
            self.status_badge.setObjectName("badgeInvalid")
            self.status_badge.style().unpolish(self.status_badge)
            self.status_badge.style().polish(self.status_badge)
            return

        if not normalized_mask or not isSubnetMask(normalized_mask):
            self.result.setText("Masque invalide")
            self.result.setStyleSheet("color: #ef4444;")
            self.status_badge.setText("ERREUR")
            self.status_badge.setObjectName("badgeInvalid")
            self.status_badge.style().unpolish(self.status_badge)
            self.status_badge.style().polish(self.status_badge)
            return

        if not isClassFull(normalized_mask):
            self.result.setText("Ce calcul n'accepte que des masques classful")
            self.result.setStyleSheet("color: #f59e0b;")
            self.status_badge.setText("NON CLASSFUL")
            self.status_badge.setObjectName("badgeWarn")
            self.status_badge.style().unpolish(self.status_badge)
            self.status_badge.style().polish(self.status_badge)
            return

        ip_class = getIPClass(ip)
        expected_mask = getIPClassMask(ip)

        if ip_class in (ClassMask.CLASS_D, ClassMask.CLASS_E):
            self.result.setText("Classe IP non supportee")
            self.result.setStyleSheet("color: #f59e0b;")
            self.status_badge.setText("NON SUPPORTEE")
            self.status_badge.setObjectName("badgeWarn")
            self.status_badge.style().unpolish(self.status_badge)
            self.status_badge.style().polish(self.status_badge)
            return

        if expected_mask == ClassMask.ERROR.value:
            self.result.setText("Adresse IP invalide")
            self.result.setStyleSheet("color: #ef4444;")
            self.status_badge.setText("ERREUR")
            self.status_badge.setObjectName("badgeInvalid")
            self.status_badge.style().unpolish(self.status_badge)
            self.status_badge.style().polish(self.status_badge)
            return

        subnet = getSubnet(ip, normalized_mask)
        if subnet == ClassMask.ERROR.value:
            self.result.setText("Adresse IP invalide")
            self.result.setStyleSheet("color: #ef4444;")
            self.status_badge.setText("ERREUR")
            self.status_badge.setObjectName("badgeInvalid")
            self.status_badge.style().unpolish(self.status_badge)
            self.status_badge.style().polish(self.status_badge)
            return

        class_network = getNetworkAddress(ip, expected_mask)
        if class_network == ClassMask.ERROR.value:
            self.result.setText("Adresse IP invalide")
            self.result.setStyleSheet("color: #ef4444;")
            self.status_badge.setText("ERREUR")
            self.status_badge.setObjectName("badgeInvalid")
            self.status_badge.style().unpolish(self.status_badge)
            self.status_badge.style().polish(self.status_badge)
            return

        self.result.setText(
            "Réseau de classe (Majeur) : "
            f"{class_network}\n"
            "Sous-réseau personnalisé : "
            f"{subnet}"
        )
        self.result.setStyleSheet("color: #22c55e;")
        self.status_badge.setText("RÉSEAU")
        self.status_badge.setObjectName("badgeValid")
        self.status_badge.style().unpolish(self.status_badge)
        self.status_badge.style().polish(self.status_badge)

        if self.idSelection is not None:
            self.db.updateIp(self.idSelection, ip, self.user_info["id"], self.user_info["username"], 4, masque=mask)
        else:
            self.db.addIp(self.user_info["id"], self.user_info["username"], ip, 4, masque=mask)

        self.ip_input.clear()
        self.mask_input.clear()
        self.charger_liste()
        self.idSelection = None
