from .Database import Database
from datetime import datetime
class Partylist(Database):

    def __init__(self):
        super().__init__()

    def addpartylist(self, partylistname: str, description: str = "", platform: str = "", logo: str = "", idnum: str = ""):
        cursor = None

        try:
            cursor = self.conn.cursor(dictionary=True)

            # CHECK IF PARTYLIST NAME ALREADY EXISTS
            sql = """
                SELECT Partylist_Id
                FROM partylists
                WHERE Partylist_Name = %s
                AND Status != 'Rejected'
            """
            cursor.execute(sql, (partylistname,))
            existing = cursor.fetchone()

            if existing:
                return {
                    "success": False,
                    "message": "Partylist name already exists."
                }

            cursor.close()
            cursor = self.conn.cursor()

            # INSERT PARTYLIST
            sql = """
                INSERT INTO partylists
                (
                    Partylist_Id,
                    Partylist_Name,
                    Description,
                    Platform,
                    Logo,
                    Id_Number,
                    Status,
                    Created_At
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """

            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Temporary ID; replaced with generated ID after insertion.
            cursor.execute(
                sql,
                (
                    "",
                    partylistname,
                    description,
                    platform,
                    logo,
                    idnum,
                    "Pending",
                    created_at
                )
            )

            new_id = cursor.lastrowid
            partylist_id = f"PL{new_id:05d}"

            cursor.execute(
                """
                UPDATE partylists
                SET Partylist_Id = %s
                WHERE Id = %s
                """,
                (partylist_id, new_id)
            )

            self.conn.commit()

            return {
                "success": True,
                "message": "Partylist submitted successfully.",
                "partylistid": partylist_id
            }

        except Exception as e:
            self.conn.rollback()
            return {
                "success": False,
                "message": str(e)
            }

        finally:
            if cursor:
                cursor.close()

    # DISPLAY PARTYLlSTS
    def displaypartylists(self, search: str = "", status: str = ""):
        cursor = None

        try:
            cursor = self.conn.cursor(dictionary=True)

            sql = """
                SELECT
                    p.Partylist_Id,
                    p.Partylist_Name,
                    p.Description,
                    p.Platform,
                    p.Logo,
                    p.Id_Number,
                    p.Status,
                    p.Created_At,
                    CONCAT(
                        s.First_Name, ' ',
                        IFNULL(CONCAT(s.Middle_Name, ' '), ''),
                        s.Last_Name
                    ) AS Submitted_By
                FROM partylists p
                LEFT JOIN students s
                    ON p.Id_Number = s.Id_Number
                WHERE 1 = 1
            """

            values = []

            if search:
                sql += """
                    AND (
                        p.Partylist_Id LIKE %s
                        OR p.Partylist_Name LIKE %s
                        OR p.Id_Number LIKE %s
                    )
                """
                keyword = f"%{search}%"
                values.extend([keyword, keyword, keyword])

            if status:
                sql += " AND p.Status = %s"
                values.append(status)

            sql += " ORDER BY p.Created_At DESC"

            cursor.execute(sql, tuple(values))
            rows = cursor.fetchall()

            return {
                "success": True,
                "data": rows
            }

        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }

        finally:
            if cursor:
                cursor.close()

    # VIEW STUDENT'S PARTYLIST SUBMISSIONS
    def viewpartylistsubmissions(self, idnum: str):
        cursor = None

        try:
            cursor = self.conn.cursor(dictionary=True)

            sql = """
                SELECT
                    Partylist_Id,
                    Partylist_Name,
                    Description,
                    Platform,
                    Logo,
                    Id_Number,
                    Status,
                    Created_At
                FROM partylists
                WHERE Id_Number = %s
                ORDER BY Created_At DESC
            """

            cursor.execute(sql, (idnum,))
            rows = cursor.fetchall()

            return {
                "success": True,
                "data": rows
            }

        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }

        finally:
            if cursor:
                cursor.close()

    # UPDATE STUDENT'S PENDING PARTYLIST
    def updatepartylist(
        self,
        partylistid: str,
        idnum: str,
        partylistname: str,
        description: str = "",
        platform: str = "",
        logo: str = ""
    ):
        cursor = None

        try:
            cursor = self.conn.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT Status
                FROM partylists
                WHERE Partylist_Id = %s
                AND Id_Number = %s
                """,
                (partylistid, idnum)
            )

            partylist = cursor.fetchone()

            if not partylist:
                return {
                    "success": False,
                    "message": "Partylist not found or you do not own this submission."
                }

            if partylist["Status"] != "Pending":
                return {
                    "success": False,
                    "message": "Only pending partylist submissions can be updated."
                }

            cursor.execute(
                """
                SELECT Partylist_Id
                FROM partylists
                WHERE Partylist_Name = %s
                AND Partylist_Id != %s
                AND Status != 'Rejected'
                """,
                (partylistname, partylistid)
            )

            existing = cursor.fetchone()

            if existing:
                return {
                    "success": False,
                    "message": "Partylist name already exists."
                }

            cursor.close()
            cursor = self.conn.cursor()

            cursor.execute(
                """
                UPDATE partylists
                SET
                    Partylist_Name = %s,
                    Description = %s,
                    Platform = %s,
                    Logo = %s
                WHERE Partylist_Id = %s
                AND Id_Number = %s
                AND Status = 'Pending'
                """,
                (
                    partylistname,
                    description,
                    platform,
                    logo,
                    partylistid,
                    idnum
                )
            )

            self.conn.commit()

            if cursor.rowcount == 0:
                return {
                    "success": False,
                    "message": "No changes were made."
                }

            return {
                "success": True,
                "message": "Partylist updated successfully."
            }

        except Exception as e:
            self.conn.rollback()
            return {
                "success": False,
                "message": str(e)
            }

        finally:
            if cursor:
                cursor.close()

    # APPROVE OR REJECT A PENDING PARTYLIST
    def updatestatus(self, partylistid: str, status: str):
        cursor = None

        try:
            if status not in ["Approved", "Rejected"]:
                return {
                    "success": False,
                    "message": "Status must be Approved or Rejected."
                }

            cursor = self.conn.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT Status
                FROM partylists
                WHERE Partylist_Id = %s
                """,
                (partylistid,)
            )

            partylist = cursor.fetchone()

            if not partylist:
                return {
                    "success": False,
                    "message": "Partylist not found."
                }

            if partylist["Status"] != "Pending":
                return {
                    "success": False,
                    "message": "Only pending partylists can be approved or rejected."
                }

            cursor.close()
            cursor = self.conn.cursor()

            cursor.execute(
                """
                UPDATE partylists
                SET Status = %s
                WHERE Partylist_Id = %s
                AND Status = 'Pending'
                """,
                (status, partylistid)
            )

            self.conn.commit()

            return {
                "success": cursor.rowcount > 0,
                "message": f"Partylist {status.lower()} successfully."
                if cursor.rowcount > 0
                else "Partylist status was not changed."
            }

        except Exception as e:
            self.conn.rollback()
            return {
                "success": False,
                "message": str(e)
            }

        finally:
            if cursor:
                cursor.close()

    # VIEW PARTYLIST DETAILS (ADMIN)
    def viewpartylistdetails(self, partylistid: str):
        cursor = None

        try:
            cursor = self.conn.cursor(dictionary=True)

            sql = """
                SELECT
                    p.Partylist_Id,
                    p.Partylist_Name,
                    p.Description,
                    p.Platform,
                    p.Logo,
                    p.Id_Number,
                    p.Status,
                    p.Created_At,
                    s.First_Name,
                    s.Middle_Name,
                    s.Last_Name,
                    s.Program,
                    s.Year_Level,
                    s.Email
                FROM partylists p
                LEFT JOIN students s
                    ON p.Id_Number = s.Id_Number
                WHERE p.Partylist_Id = %s
            """

            cursor.execute(sql, (partylistid,))
            row = cursor.fetchone()

            if not row:
                return {
                    "success": False,
                    "message": "Partylist not found."
                }

            return {
                "success": True,
                "data": row
            }

        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }

        finally:
            if cursor:
                cursor.close()

    # UPDATE STATUS OF AN ALREADY REVIEWED PARTYLIST
    def updatepartyliststatus(self, partylistid: str, status: str):
        cursor = None

        try:
            if status not in ["Active", "Inactive"]:
                return {
                    "success": False,
                    "message": "Status must be Active or Inactive."
                }

            cursor = self.conn.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT Status
                FROM partylists
                WHERE Partylist_Id = %s
                """,
                (partylistid,)
            )

            partylist = cursor.fetchone()

            if not partylist:
                return {
                    "success": False,
                    "message": "Partylist not found."
                }

            if partylist["Status"] not in ["Approved", "Active", "Inactive"]:
                return {
                    "success": False,
                    "message": "Only approved partylists can be activated or deactivated."
                }

            cursor.close()
            cursor = self.conn.cursor()

            cursor.execute(
                """
                UPDATE partylists
                SET Status = %s
                WHERE Partylist_Id = %s
                """,
                (status, partylistid)
            )

            self.conn.commit()

            return {
                "success": True,
                "message": f"Partylist status changed to {status}."
            }

        except Exception as e:
            self.conn.rollback()
            return {
                "success": False,
                "message": str(e)
            }

        finally:
            if cursor:
                cursor.close()

    # VIEW PARTYLIST MEMBERS AND CANDIDATES (ADMIN)
    def viewpartylistmembers(self, partylistid: str):
        cursor = None

        try:
            cursor = self.conn.cursor(dictionary=True)

            # CHECK IF PARTYLIST EXISTS
            cursor.execute(
                """
                SELECT Partylist_Id, Partylist_Name, Status
                FROM partylists
                WHERE Partylist_Id = %s
                """,
                (partylistid,)
            )

            partylist = cursor.fetchone()

            if not partylist:
                return {
                    "success": False,
                    "message": "Partylist not found."
                }

            sql = """
                SELECT
                    c.Candidate_Id,
                    c.Id_Number,
                    CONCAT(
                        s.First_Name, ' ',
                        IFNULL(CONCAT(s.Middle_Name, ' '), ''),
                        s.Last_Name
                    ) AS Candidate_Name,
                    c.Election_Id,
                    e.Election_Name,
                    c.Position_Id,
                    pos.Position_Name,
                    c.Candidacy_Type,
                    c.Status AS Candidacy_Status,
                    c.Photo,
                    c.Biography,
                    c.Platform
                FROM candidates c
                LEFT JOIN students s
                    ON c.Id_Number = s.Id_Number
                LEFT JOIN elections e
                    ON c.Election_Id = e.Election_Id
                LEFT JOIN positions pos
                    ON c.Position_Id = pos.Position_Id
                    AND c.Election_Id = pos.Election_Id
                WHERE c.Partylist_Id = %s
                ORDER BY e.Start_Date, pos.Position_Name, Candidate_Name
            """

            cursor.execute(sql, (partylistid,))
            members = cursor.fetchall()

            return {
                "success": True,
                "partylist": partylist,
                "data": members
            }

        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }

        finally:
            if cursor:
                cursor.close()
