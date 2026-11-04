from datetime import datetime, timedelta, timezone
import jwt

from .Database import Database
from .Auth import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_MINUTES


class Authentication(Database):
    def __init__(self):
        super().__init__()

    # USER LOGIN
    def login(self, idnum: str, password: str):
        cursor = self.conn.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT Id_Number, Password, Role, Status
                FROM users
                WHERE Id_Number = %s
                LIMIT 1
                """,
                (idnum,)
            )

            user = cursor.fetchone()

            # CHECK CREDENTIALS
            if not user or user["Password"] != password:
                return {
                    "success": False,
                    "message": "Invalid ID number or password."
                }

            # CHECK ACCOUNT STATUS
            if user["Status"] != "Active":
                return {
                    "success": False,
                    "message": "Your account is inactive. Please contact the administrator."
                }

            # GENERATE ACCESS TOKEN
            now = datetime.now(timezone.utc)

            payload = {
                "Id_Number": user["Id_Number"],
                "Role": user["Role"],
                "iat": now,
                "exp": now + timedelta(
                    minutes=ACCESS_TOKEN_MINUTES
                )
            }

            access_token = jwt.encode(
                payload,
                SECRET_KEY,
                algorithm=ALGORITHM
            )

            # LOGIN SUCCESSFUL
            return {
                "success": True,
                "message": "Login successful.",
                "data": {
                    "Id_Number": user["Id_Number"],
                    "Role": user["Role"],
                    "Access_Token": access_token,
                    "Token_Type": "bearer",
                    "Expires_In": ACCESS_TOKEN_MINUTES * 60
                }
            }

        except Exception:
            return {
                "success": False,
                "message": "Unable to process login. Please try again."
            }

        finally:
            cursor.close()
