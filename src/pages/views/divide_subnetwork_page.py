from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QPushButton, QSizePolicy, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from ...services.database import Database

from ...services.logic import isIp, parseMask, isSubnetMask, maskToCidr, getSubnetBits, getSubnetStep, divideSubnetwork
from ...services.utils import remove_spaces

class DivideSubnetworkPage(QWidget):
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
            self.status_badge.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

            self.result = QLabel("")
            self.result.setObjectName("statusMessage")

            result_layout.addWidget(self.status_badge, 0, Qt.AlignLeft)
            result_layout.addWidget(self.result)

            # --- Tableau des sous-reseaux ---
            self.table = QTableWidget(0, 8)
            self.table.setHorizontalHeaderLabels(["N°", "IP réseau", "IP broadcast", "1ère IP", "Dernière IP", "Masque", "IP utilisables", "Pas"])
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            # --- colonnes courtes : largeur ajustee au contenu, les colonnes IP prennent le reste ---
            for col in (0, 5, 6, 7):
                self.table.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeToContents)
            self.table.verticalHeader().setVisible(False)
            self.table.setAlternatingRowColors(True)
            self.table.setObjectName("cidrTable") # --- reutilise le style du tableau CIDR ---
            self.table.setSelectionBehavior(QTableWidget.SelectRows)
            self.table.setEditTriggers(QTableWidget.NoEditTriggers)
            self.table.setVisible(False)

            # --- Historique des calculs ---
            self.data_history = QTableWidget(0, 5)
            self.data_history.setHorizontalHeaderLabels(["IP", "Masque", "Sous-réseaux", "IP / sous-réseau", "Utilisateur"])
            self.data_history.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.data_history.verticalHeader().setVisible(False)
            self.data_history.setAlternatingRowColors(True)
            self.data_history.setObjectName("cidrTable") # --- reutilise le style du tableau CIDR ---
            self.data_history.setSelectionBehavior(QTableWidget.SelectRows)
            self.data_history.setSelectionMode(QTableWidget.SingleSelection)
            self.data_history.setEditTriggers(QTableWidget.NoEditTriggers)
            self.data_history.setMaximumHeight(180) # --- laisse la place au tableau ---
            self.data_history.cellClicked.connect(self.selectionner_ip)

            card_layout.addLayout(row)
            card_layout.addWidget(self.empty_state)
            card_layout.addWidget(self.result_card)
            card_layout.addWidget(self.table, 1)
            card_layout.addStretch(0) # --- 0 : le tableau prend toute la place libre quand il est affiche ---
            card_layout.addWidget(self.data_history)

            layout.addWidget(card)
            self.charger_liste()

    def charger_liste(self):
        rows = self.db.getIps(6)
        self.data_history.setRowCount(len(rows))

        for row_idx, (id_ip, ip, masque, number_ip, number_subnet, username) in enumerate(rows):
            for col_idx, cell_value in enumerate((ip, masque, str(number_subnet), str(number_ip), username)):
                self.data_history.setItem(row_idx, col_idx, QTableWidgetItem(cell_value))
            # --- donnees de la ligne stockees sur la 1ere cellule ---
            self.data_history.item(row_idx, 0).setData(Qt.UserRole, (id_ip, ip, masque, number_ip, number_subnet))

    def selectionner_ip(self, row, column):
        id_ip, ip, masque, number_ip, number_subnet = self.data_history.item(row, 0).data(Qt.UserRole)
        self.idSelection = id_ip
        self.ip_input.setText(ip)
        self.mask_input.setText(masque)
        self.number_ip_input.setText(str(number_ip))
        self.number_subnet_input.setText(str(number_subnet))

    def run_check(self):
        
        # --- Execution du calcul de sous-reseau ---
        ip = remove_spaces(self.ip_input.text())
        mask = remove_spaces(self.mask_input.text())
        normalized_mask = parseMask(mask)
        
        number_ip = remove_spaces(self.number_ip_input.text())
        number_subnet = remove_spaces(self.number_subnet_input.text())
        
        self.empty_state.setVisible(False)
        self.result_card.setVisible(True)
        self.result.setVisible(True) # --- message d'erreur visible, cache seulement si le calcul est valide ---

        # --- on cache le tableau tant que le calcul n'est pas valide ---
        self.table.setVisible(False)

        # --- affichage des erreurs ---
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
        
        # --- etape 1 : verification du nombre d'IP et du nombre de sous-reseaux (entier > 0) ---
        if not number_ip.isdigit() or int(number_ip) == 0:
            self.result.setText("Nombre d'IP invalide")
            self.result.setStyleSheet("color: #ef4444;")
            self.status_badge.setText("ERREUR")
            self.status_badge.setObjectName("badgeInvalid")
            self.status_badge.style().unpolish(self.status_badge)
            self.status_badge.style().polish(self.status_badge)
            return

        if not number_subnet.isdigit() or int(number_subnet) == 0:
            self.result.setText("Nombre de sous-réseaux invalide")
            self.result.setStyleSheet("color: #ef4444;")
            self.status_badge.setText("ERREUR")
            self.status_badge.setObjectName("badgeInvalid")
            self.status_badge.style().unpolish(self.status_badge)
            self.status_badge.style().polish(self.status_badge)
            return

        number_ip = int(number_ip)
        number_subnet = int(number_subnet)

        # --- etape 2 : nouveau masque classless (CIDR + n avec 2^n >= nombre de sous-reseaux) ---
        subnet_bits = getSubnetBits(number_subnet)
        new_cidr = maskToCidr(normalized_mask) + subnet_bits

        # --- plus de bits disponibles -> trop de sous-reseaux demandes pour ce masque ---
        if new_cidr > 32:
            self.result.setText("Trop de sous-réseaux demandés pour ce masque")
            self.result.setStyleSheet("color: #ef4444;")
            self.status_badge.setText("ERREUR")
            self.status_badge.setObjectName("badgeInvalid")
            self.status_badge.style().unpolish(self.status_badge)
            self.status_badge.style().polish(self.status_badge)
            return

        # --- etape 3 : IP utilisables = pas - 2 (adresse reseau + broadcast), 0 pour /31 et /32 ---
        step = getSubnetStep(new_cidr)
        hosts = max(step - 2, 0)
        if hosts < number_ip:
            self.result.setText(
                f"Pas assez d'IP par sous-réseau avec un /{new_cidr} "
                f"({hosts} disponibles pour {number_ip} demandées)"
            )
            self.result.setStyleSheet("color: #ef4444;")
            self.status_badge.setText("ERREUR")
            self.status_badge.setObjectName("badgeInvalid")
            self.status_badge.style().unpolish(self.status_badge)
            self.status_badge.style().polish(self.status_badge)
            return

        # --- etape 4 : generation des sous-reseaux avec le pas ---
        rows = divideSubnetwork(ip, normalized_mask, number_subnet, new_cidr)

        # --- calcul valide : on garde seulement le badge, le resume passe dans le tableau ---
        self.result.setVisible(False)
        self.status_badge.setText("VALIDE")
        self.status_badge.setObjectName("badgeValid")
        self.status_badge.style().unpolish(self.status_badge)
        self.status_badge.style().polish(self.status_badge)

        # --- affichage du tableau : N° | IP reseau | IP broadcast | 1ere IP | derniere IP | masque | IP utilisables | pas ---
        new_mask = f"/{new_cidr} ({parseMask(str(new_cidr))})"
        self.table.setRowCount(len(rows))

        for row_idx, row_values in enumerate(rows):
            row_values[0] = f"{row_values[0]} / {2 ** subnet_bits}" # --- N° / sous-reseaux possibles ---
            row_values += [new_mask, str(hosts), str(step)]
            for col_idx, cell_value in enumerate(row_values):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(cell_value))

        self.table.setVisible(True)

        # --- sauvegarde dans l'historique ---
        if self.idSelection is not None:
            self.db.updateIp(self.idSelection, ip, self.user_info["id"], self.user_info["username"], 6, masque=mask, number_ip=number_ip, number_subnet=number_subnet)
        else:
            self.db.addIp(self.user_info["id"], self.user_info["username"], ip, 6, masque=mask, number_ip=number_ip, number_subnet=number_subnet)


        self.ip_input.clear()
        self.mask_input.clear()
        self.number_ip_input.clear()
        self.number_subnet_input.clear()
        self.charger_liste()
        self.idSelection = None