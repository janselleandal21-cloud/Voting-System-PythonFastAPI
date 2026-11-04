
from .Database import Database


class Position(Database):

    def __init__(self):
        super().__init__()

    # UPDATE ELECTION STATUS BASED ON ITS DATES
    def updateelectionstatuses(self):
        cursor = self.conn.cursor()

        try:
            cursor.execute(
                """
                UPDATE elections
                SET Status = CASE
                    WHEN NOW() >= End_Date THEN 'Completed'
                    WHEN NOW() >= Start_Date THEN 'Ongoing'
                    ELSE 'Scheduled'
                END
                WHERE Status IN ('Scheduled', 'Ongoing')
                """
            )

            self.conn.commit()

        except Exception:
            self.conn.rollback()
            raise

        finally:
            cursor.close()

    # ADD POSITION
    def addposition(self, positionid, electionid, positionname, description=""):
        cursor = None

        try:
            self.updateelectionstatuses()

            cursor = self.conn.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT Election_Id, Status
                FROM elections
                WHERE Election_Id = %s
                """,
                (electionid,)
            )

            election = cursor.fetchone()

            if not election:
                return {
                    "success": False,
                    "message": "Election does not exist."
                }

            if election["Status"] != "Scheduled":
                return {
                    "success": False,
                    "message": "Positions can only be added to scheduled elections."
                }

            cursor.execute(
                """
                SELECT Position_Id
                FROM positions
                WHERE Position_Id = %s
                """,
                (positionid,)
            )

            if cursor.fetchone():
                return {
                    "success": False,
                    "message": "Position ID already exists."
                }

            cursor.execute(
                """
                SELECT Position_Id
                FROM positions
                WHERE Election_Id = %s
                AND Position_Name = %s
                """,
                (electionid, positionname)
            )

            if cursor.fetchone():
                return {
                    "success": False,
                    "message": "This position name already exists in the selected election."
                }

            cursor.execute(
                """
                INSERT INTO positions
                (
                    Position_Id,
                    Election_Id,
                    Position_Name,
                    Description,
                    Created_At
                )
                VALUES (%s, %s, %s, %s, NOW())
                """,
                (
                    positionid,
                    electionid,
                    positionname,
                    description
                )
            )

            self.conn.commit()

            return {
                "success": True,
                "message": "Position added successfully."
            }

        except Exception as error:
            self.conn.rollback()

            return {
                "success": False,
                "message": "Unable to add position.",
                "error": str(error)
            }

        finally:
            if cursor:
                cursor.close()

    # DISPLAY AND SEARCH POSITIONS
    def displaypositions(self, search="", electionid=""):
        cursor = None

        try:
            self.updateelectionstatuses()

            cursor = self.conn.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT
                    p.Id,
                    p.Position_Id,
                    p.Election_Id,
                    p.Position_Name,
                    p.Description,
                    p.Created_At,
                    e.Election_Name,
                    e.Status AS Election_Status
                FROM positions p
                LEFT JOIN elections e
                    ON p.Election_Id = e.Election_Id
                WHERE (
                    p.Position_Id LIKE %s
                    OR p.Position_Name LIKE %s
                    OR p.Description LIKE %s
                )
                AND (%s = '' OR p.Election_Id = %s)
                ORDER BY p.Election_Id ASC, p.Id ASC
                """,
                (
                    "%" + search + "%",
                    "%" + search + "%",
                    "%" + search + "%",
                    electionid,
                    electionid
                )
            )

            positions = cursor.fetchall()

            return {
                "success": True,
                "data": positions
            }

        except Exception as error:
            return {
                "success": False,
                "message": "Unable to display positions.",
                "error": str(error)
            }

        finally:
            if cursor:
                cursor.close()

    # UPDATE POSITION
    def updateposition(self, positionid, positionname, description=""):
        cursor = None

        try:
            self.updateelectionstatuses()

            cursor = self.conn.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT
                    p.Position_Id,
                    p.Election_Id,
                    e.Status
                FROM positions p
                LEFT JOIN elections e
                    ON p.Election_Id = e.Election_Id
                WHERE p.Position_Id = %s
                """,
                (positionid,)
            )

            position = cursor.fetchone()

            if not position:
                return {
                    "success": False,
                    "message": "Position does not exist."
                }

            if position["Status"] != "Scheduled":
                return {
                    "success": False,
                    "message": "Positions can only be updated in scheduled elections."
                }

            electionid = position["Election_Id"]

            cursor.execute(
                """
                SELECT Position_Id
                FROM positions
                WHERE Election_Id = %s
                AND Position_Name = %s
                AND Position_Id != %s
                """,
                (electionid, positionname, positionid)
            )

            if cursor.fetchone():
                return {
                    "success": False,
                    "message": "This position name already exists in the selected election."
                }

            cursor.execute(
                """
                UPDATE positions
                SET Position_Name = %s,
                    Description = %s
                WHERE Position_Id = %s
                """,
                (positionname, description, positionid)
            )

            self.conn.commit()

            return {
                "success": True,
                "message": "Position updated successfully."
            }

        except Exception as error:
            self.conn.rollback()

            return {
                "success": False,
                "message": "Unable to update position.",
                "error": str(error)
            }

        finally:
            if cursor:
                cursor.close()

    # DELETE POSITION
    def deleteposition(self, positionid):
        cursor = None

        try:
            self.updateelectionstatuses()

            cursor = self.conn.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT
                    p.Position_Id,
                    p.Election_Id,
                    e.Status
                FROM positions p
                LEFT JOIN elections e
                    ON p.Election_Id = e.Election_Id
                WHERE p.Position_Id = %s
                """,
                (positionid,)
            )

            position = cursor.fetchone()

            if not position:
                return {
                    "success": False,
                    "message": "Position does not exist."
                }

            if position["Status"] != "Scheduled":
                return {
                    "success": False,
                    "message": "Positions can only be deleted from scheduled elections."
                }

            cursor.execute(
                """
                DELETE FROM positions
                WHERE Position_Id = %s
                """,
                (positionid,)
            )

            self.conn.commit()

            return {
                "success": True,
                "message": "Position deleted successfully."
            }

        except Exception as error:
            self.conn.rollback()

            return {
                "success": False,
                "message": "Unable to delete position.",
                "error": str(error)
            }

        finally:
            if cursor:
                cursor.close()
