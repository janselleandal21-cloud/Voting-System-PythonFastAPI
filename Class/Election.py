
from .Database import Database
from datetime import datetime


class Election(Database):

    def __init__(self):
        super().__init__()

    # AUTOMATICALLY UPDATE ELECTION STATUSES
    def updateelectionstatuses(self):
        cursor = None

        try:
            cursor = self.conn.cursor()

            # Automatically open elections when their start time arrives.
            # An election cannot open if its end time has already passed.
            cursor.execute("""
                UPDATE elections
                SET Status = 'Ongoing'
                WHERE Status = 'Scheduled'
                AND Start_Date <= NOW()
                AND End_Date > NOW()
            """)

            # Automatically complete elections when their end time arrives.
            # This also handles scheduled elections whose entire schedule passed.
            cursor.execute("""
                UPDATE elections
                SET Status = 'Completed'
                WHERE Status IN ('Scheduled', 'Ongoing')
                AND End_Date <= NOW()
            """)

            self.conn.commit()

        except Exception:
            self.conn.rollback()
            raise

        finally:
            if cursor:
                cursor.close()

    # ADD ELECTION
    def addelection(
        self,
        electionid: str,
        electionname: str,
        description: str,
        schoolyear: str,
        startdate: str,
        enddate: str,
        createdby: str
    ):
        cursor = None

        try:
            start = datetime.strptime(startdate, "%Y-%m-%d %H:%M:%S")
            end = datetime.strptime(enddate, "%Y-%m-%d %H:%M:%S")

            if start >= end:
                return {
                    "success": False,
                    "message": "End date must be later than start date."
                }

            cursor = self.conn.cursor(dictionary=True)

            cursor.execute(
                "SELECT Id FROM elections WHERE Election_Id = %s",
                (electionid,)
            )

            if cursor.fetchone():
                return {
                    "success": False,
                    "message": "Election ID already exists."
                }

            cursor.close()
            cursor = self.conn.cursor()

            cursor.execute("""
                INSERT INTO elections (
                    Election_Id,
                    Election_Name,
                    Description,
                    School_Year,
                    Start_Date,
                    End_Date,
                    Status,
                    Created_By,
                    Created_At
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """, (
                electionid,
                electionname,
                description,
                schoolyear,
                startdate,
                enddate,
                "Scheduled",
                createdby
            ))

            self.conn.commit()

            # Update immediately if the schedule is already active or expired.
            self.updateelectionstatuses()

            return {
                "success": True,
                "message": "Election created successfully."
            }

        except ValueError:
            return {
                "success": False,
                "message": "Invalid date format. Use YYYY-MM-DD HH:MM:SS."
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

    # DISPLAY ALL ELECTIONS
    def displayelections(self, search: str = "", status: str = ""):
        cursor = None

        try:
            # Update statuses before applying the search and status filters.
            self.updateelectionstatuses()

            cursor = self.conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT *
                FROM elections
                WHERE (
                    Election_Name LIKE %s
                    OR Election_Id LIKE %s
                )
                AND Status LIKE %s
                ORDER BY Start_Date DESC
            """, (
                "%" + search + "%",
                "%" + search + "%",
                "%" + status + "%"
            ))

            return {
                "success": True,
                "data": cursor.fetchall()
            }

        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }

        finally:
            if cursor:
                cursor.close()

    # UPDATE ELECTION
    def updateelection(
        self,
        electionid: str,
        electionname: str,
        description: str,
        schoolyear: str,
        startdate: str,
        enddate: str
    ):
        cursor = None

        try:
            start = datetime.strptime(startdate, "%Y-%m-%d %H:%M:%S")
            end = datetime.strptime(enddate, "%Y-%m-%d %H:%M:%S")

            if start >= end:
                return {
                    "success": False,
                    "message": "End date must be later than start date."
                }

            cursor = self.conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT Status
                FROM elections
                WHERE Election_Id = %s
            """, (electionid,))

            election = cursor.fetchone()

            if not election:
                return {
                    "success": False,
                    "message": "Election not found."
                }

            if election["Status"] != "Scheduled":
                return {
                    "success": False,
                    "message": "Only scheduled elections can be edited."
                }

            cursor.execute("""
                UPDATE elections
                SET Election_Name = %s,
                    Description = %s,
                    School_Year = %s,
                    Start_Date = %s,
                    End_Date = %s
                WHERE Election_Id = %s
            """, (
                electionname,
                description,
                schoolyear,
                startdate,
                enddate,
                electionid
            ))

            self.conn.commit()

            # Recheck the schedule after updating it.
            self.updateelectionstatuses()

            return {
                "success": True,
                "message": "Election updated successfully."
            }

        except ValueError:
            return {
                "success": False,
                "message": "Invalid date format. Use YYYY-MM-DD HH:MM:SS."
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

    # OPEN ELECTION MANUALLY
    def openelection(self, electionid: str):
        cursor = None

        try:
            # Apply any automatic status changes first.
            self.updateelectionstatuses()

            cursor = self.conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT Status, Start_Date, End_Date
                FROM elections
                WHERE Election_Id = %s
            """, (electionid,))

            election = cursor.fetchone()

            if not election:
                return {
                    "success": False,
                    "message": "Election not found."
                }

            if election["Status"] != "Scheduled":
                return {
                    "success": False,
                    "message": "Only scheduled elections can be opened."
                }

            now = datetime.now()
            start = election["Start_Date"]
            end = election["End_Date"]

            if now < start:
                return {
                    "success": False,
                    "message": "Election cannot be opened before its start date."
                }

            if now >= end:
                return {
                    "success": False,
                    "message": "Election schedule has already ended."
                }

            cursor.execute("""
                UPDATE elections
                SET Status = 'Ongoing'
                WHERE Election_Id = %s
                AND Status = 'Scheduled'
            """, (electionid,))

            self.conn.commit()

            return {
                "success": True,
                "message": "Election opened successfully."
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

    # CLOSE ELECTION MANUALLY
    def closeelection(self, electionid: str):
        cursor = None

        try:
            self.updateelectionstatuses()

            cursor = self.conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT Status
                FROM elections
                WHERE Election_Id = %s
            """, (electionid,))

            election = cursor.fetchone()

            if not election:
                return {
                    "success": False,
                    "message": "Election not found."
                }

            if election["Status"] != "Ongoing":
                return {
                    "success": False,
                    "message": "Only ongoing elections can be closed."
                }

            cursor.execute("""
                UPDATE elections
                SET Status = 'Completed'
                WHERE Election_Id = %s
                AND Status = 'Ongoing'
            """, (electionid,))

            self.conn.commit()

            return {
                "success": True,
                "message": "Election closed successfully."
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

    # LOCK COMPLETED ELECTION
    def lockelection(self, electionid: str):
        cursor = None

        try:
            self.updateelectionstatuses()

            cursor = self.conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT Status
                FROM elections
                WHERE Election_Id = %s
            """, (electionid,))

            election = cursor.fetchone()

            if not election:
                return {
                    "success": False,
                    "message": "Election not found."
                }

            if election["Status"] != "Completed":
                return {
                    "success": False,
                    "message": "Only completed elections can be locked."
                }

            cursor.execute("""
                UPDATE elections
                SET Status = 'Locked'
                WHERE Election_Id = %s
                AND Status = 'Completed'
            """, (electionid,))

            self.conn.commit()

            return {
                "success": True,
                "message": "Election locked successfully."
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

    # DISPLAY ACTIVE ELECTIONS FOR STUDENTS
    def displayactiveelections(self):
        cursor = None

        try:
            self.updateelectionstatuses()

            cursor = self.conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT *
                FROM elections
                WHERE Status = 'Ongoing'
                ORDER BY Start_Date ASC
            """)

            return {
                "success": True,
                "data": cursor.fetchall()
            }

        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }

        finally:
            if cursor:
                cursor.close()

    # VIEW ELECTION DETAILS
    def viewelectiondetails(self, electionid: str):
        cursor = None

        try:
            self.updateelectionstatuses()

            cursor = self.conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT *
                FROM elections
                WHERE Election_Id = %s
                AND Status IN (%s, %s)
            """, (electionid, "Scheduled", "Ongoing"))

            election = cursor.fetchone()

            if not election:
                return {
                    "success": False,
                    "message": "Election not found or unavailable for viewing."
                }

            return {
                "success": True,
                "data": election
            }

        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }

        finally:
            if cursor:
                cursor.close()
