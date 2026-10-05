import os
import re
from datetime import datetime, timedelta

import bcrypt
import psycopg2
from psycopg2 import Error
from dotenv import load_dotenv


load_dotenv()

class Database:
    def __init__(self):
        self.host = os.getenv("DB_HOST")
        self.database = os.getenv("DB_NAME")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASS")
        self.port = os.getenv("DB_PORT")

        self.conn = None
        self.userId = None
        self.userName = None
        self.userRole = None
        self.previous_last_login = None
        self.last_error = ""
        self.password_reset_required = False

        self.max_failed_attempts = 3
        self.lockout_minutes = 5 #temps de blocage par defaut en minute

        self.password_min_length = 13

    def _connection(self):
        if self.conn is not None:
            return self.conn

        try:
            self.conn = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port
            )
            self.last_error = ""
            return self.conn
        
        except Exception:
            self.last_error = "Erreur de connexion a la base de donnees"
            self.conn = None
            return None

    def _cursor(self):
        conn = self._connection()
        if conn is None:
            return None
        return conn.cursor()


    def _close(self):
        if self.conn is not None:
            self.conn.close()
    



    def listUsers(self):
        cursor = self._cursor()
        if cursor is None:
            return []

        cursor.execute(
            """
            SELECT id, username, role, is_temporary, is_active, failed_attempts, locked_until, last_login
            FROM users
            ORDER BY id
            """
        )
        records = cursor.fetchall()
        cursor.close()
        self.last_error = ""

        return records


    def addUser(self, username, password, role, is_temporary=True):
        cursor = self._cursor()
        if cursor is None:
            return False

        try:
            if not is_temporary and not self._isPasswordStrong(password):
                self.last_error = "PASSWORD_WEAK"
                return False

            salt = bcrypt.gensalt(rounds=13)
            hashPassword = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

            cursor.execute(
                """
                INSERT INTO users (username, hashpassword, role, is_temporary, is_active, failed_attempts, locked_until, last_login)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (username, hashPassword, role, is_temporary, True, 0, None, None)
            )
            self._connection().commit()
            return True
        
        except Error:
            self.last_error = "Operation SQL impossible"
            self._connection().rollback()
            return False
        finally:
            cursor.close()


    def updateRole(self, username, newRole):
        cursor = self._cursor()
        if cursor is None:
            return False

        try:
            cursor.execute("UPDATE users SET role = %s WHERE username = %s", (newRole, username))
            affected = cursor.rowcount
            self._connection().commit()
            return affected > 0
        
        except Error:
            self.last_error = "Operation SQL impossible"
            self._connection().rollback()
            return False
        finally:
            cursor.close()


    def updateUsername(self, username, newUsername):
        cursor = self._cursor()
        if cursor is None:
            return False

        try:
            cursor.execute(
                "UPDATE users SET username = %s WHERE username = %s",
                (newUsername, username)
            )
            affected = cursor.rowcount
            self._connection().commit()
            return affected > 0

        except Error:
            self.last_error = "USERNAME_TAKEN"
            self._connection().rollback()
            return False
        finally:
            cursor.close()


    def setPassword(self, username, newPassword):
        cursor = self._cursor()
        if cursor is None:
            return False

        try:
            if not self._isPasswordStrong(newPassword):
                self.last_error = "PASSWORD_WEAK"
                return False

            salt = bcrypt.gensalt(rounds=13)
            hashPassword = bcrypt.hashpw(newPassword.encode("utf-8"), salt).decode("utf-8")

            cursor.execute(
                """
                UPDATE users
                SET hashpassword = %s,
                    is_temporary = %s,
                    failed_attempts = %s,
                    locked_until = %s
                WHERE username = %s
                """,
                (hashPassword, False, 0, None, username)
            )
            affected = cursor.rowcount
            self._connection().commit()
            return affected > 0
        
        except Error:
            self.last_error = "Operation SQL impossible"
            self._connection().rollback()
            return False
        finally:
            cursor.close()


    def setPasswordAndActivate(self, username, newPassword):
        return self.setPassword(username, newPassword)


    def setTemporaryPassword(self, username, newPassword):
        cursor = self._cursor()
        if cursor is None:
            return False

        try:
            salt = bcrypt.gensalt(rounds=13)
            hashPassword = bcrypt.hashpw(newPassword.encode("utf-8"), salt).decode("utf-8")

            cursor.execute(
                """
                UPDATE users
                SET hashpassword = %s,
                    is_temporary = %s,
                    failed_attempts = %s,
                    locked_until = %s
                WHERE username = %s
                """,
                (hashPassword, True, 0, None, username)
            )
            affected = cursor.rowcount
            self._connection().commit()
            return affected > 0
        
        except Error:
            self.last_error = "Operation SQL impossible"
            self._connection().rollback()
            return False
        finally:
            cursor.close()

    #modifie le blocage
    def updateLockout(self, username, locked_until):
        cursor = self._cursor()
        if cursor is None:
            return False

        try:
            if locked_until is None:
                # déblocage manuel par l'admin : on remet les tentatives ET le nombre de blocages à zéro
                cursor.execute(
                    "UPDATE users SET locked_until = %s, failed_attempts = 0, lockout_count = 0 WHERE username = %s",
                    (locked_until, username)
                )
            else:
                cursor.execute(
                    "UPDATE users SET locked_until = %s WHERE username = %s",
                    (locked_until, username)
                )
            affected = cursor.rowcount
            self._connection().commit()
            return affected > 0
        
        except Error:
            self.last_error = "Operation SQL impossible"
            self._connection().rollback()
            return False
        finally:
            cursor.close()


    def deleteUser(self, username):
        cursor = self._cursor()
        if cursor is None:
            return False

        try:
            cursor.execute("UPDATE users SET is_active = %s WHERE username = %s", (False, username))
            affected = cursor.rowcount
            self._connection().commit()
            return affected > 0
        except Error:
            self.last_error = "Operation SQL impossible"
            self._connection().rollback()
            return False
        finally:
            cursor.close()
    


    def validateCredentials(self, username, password):
        cursor = self._cursor()
        if cursor is None:
            return False

        self.password_reset_required = False

        cursor.execute(
            """
            SELECT id, username, hashpassword, role, is_temporary, is_active, failed_attempts, locked_until, last_login, lockout_count
            FROM users
            WHERE username = %s
            """,
            (username,)
        )
        record = cursor.fetchone()
        cursor.close()

        if record:
            hash_stocke = record[2]
            is_temporary = bool(record[4])
            is_active = bool(record[5])
            failed_attempts = record[6] if record[6] is not None else 0
            locked_until = record[7]
            # nombre de blocages déjà subis par CET utilisateur (stocké en base, colonne 10 du SELECT)
            lockout_count = record[9] if record[9] is not None else 0

            if not is_active:
                self.last_error = "COMPTE INACTIVE"
                return False

            now = datetime.now()
            if locked_until and locked_until > now:
                self.last_error = "COMPTE BLOQUE"
                return False

            # Blocage expiré : on redonne un nouveau cycle de tentatives
            if locked_until and locked_until <= now:
                failed_attempts = 0

            if bcrypt.checkpw(password.encode('utf-8'), hash_stocke.encode('utf-8')):
                if is_temporary:
                    self.last_error = "PASSWORD_RESET_REQUIRED"
                    self.password_reset_required = True
                    return False

                self.previous_last_login = record[8]
                self._resetFailedAttempts(username)
                self._setLastLogin(username)
                self.userId = record[0]
                self.userName = record[1]
                self.userRole = record[3]
                self.last_error = ""
                return True

            # on transmet aussi lockout_count pour calculer la durée du prochain blocage
            self._registerFailedAttempt(username, failed_attempts, lockout_count)
            self.last_error = "Identifiants incorrects"
        else:
            self.last_error = "Identifiants incorrects"

        return False

        


    def _isPasswordStrong(self, password):
        if not password or len(password) < self.password_min_length:
            return False

        if not re.search(r"[A-Z]", password):
            return False

        if not re.search(r"[a-z]", password):
            return False

        if not re.search(r"\d", password):
            return False

        if not re.search(r"[^A-Za-z0-9]", password):
            return False

        return True


    def _registerFailedAttempt(self, username, failed_attempts, lockout_count):
        cursor = self._cursor()
        if cursor is None:
            return

        try:
            next_attempts = failed_attempts + 1
            locked_until = None

            if next_attempts >= self.max_failed_attempts:
                # nouveau blocage : +1 au compteur, la durée augmente à chaque blocage (5, 10, 15 min...)
                lockout_count += 1
                locked_until = datetime.now() + timedelta(minutes=self.lockout_minutes * lockout_count)

            # on sauvegarde aussi lockout_count en base pour le retrouver à la prochaine connexion
            cursor.execute(
                """
                UPDATE users
                SET failed_attempts = %s,
                    locked_until = %s,
                    lockout_count = %s
                WHERE username = %s
                """,
                (next_attempts, locked_until, lockout_count, username)
            )
            self._connection().commit()

        except Error:
            self._connection().rollback()
        finally:
            cursor.close()


    def _resetFailedAttempts(self, username):
        cursor = self._cursor()
        if cursor is None:
            return

        try:
            cursor.execute(
                # connexion réussie : on remet tout à zéro, y compris le nombre de blocages
                "UPDATE users SET failed_attempts = %s, locked_until = %s, lockout_count = %s WHERE username = %s",
                (0, None, 0, username)
            )
            self._connection().commit()
        except Error:
            self._connection().rollback()
        finally:
            cursor.close()


    def _setLastLogin(self, username):
        cursor = self._cursor()
        if cursor is None:
            return

        try:
            cursor.execute(
                "UPDATE users SET last_login = %s WHERE username = %s",
                (datetime.now(), username)
            )
            self._connection().commit()
        except Error:
            self._connection().rollback()
        finally:
            cursor.close()


    def getLastLogin(self, username):
        if self.userName == username and self.previous_last_login is not None:
            return self.previous_last_login

        cursor = self._cursor()
        if cursor is None:
            return None

        cursor.execute("SELECT last_login FROM users WHERE username = %s", (username,))
        record = cursor.fetchone()
        cursor.close()

        return record[0] if record else None
    

    def getUserInfo(self):
        if self.userId is None or self.userName is None or self.userRole is None:
            return None

        return {
            "id": self.userId,
            "username": self.userName,
            "role": self.userRole,
            "last_login": self.previous_last_login
        }