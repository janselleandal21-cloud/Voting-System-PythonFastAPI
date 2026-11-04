from .Database import Database
from datetime import datetime
import uuid


class Voting(Database):
    def __init__(self):
        super().__init__()

    # CHECK STUDENT VOTING STATUS
    def checkvotingstatus(self, idnum: str, electionid: str):
        cursor = self.conn.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT
                    s.Id_Number,
                    s.Status AS Student_Status,
                    u.Status AS Account_Status
                FROM students s
                INNER JOIN users u
                    ON u.Id_Number = s.Id_Number
                WHERE s.Id_Number = %s
                """,
                (idnum,)
            )

            student = cursor.fetchone()

            if not student:
                return {
                    "success": True,
                    "can_vote": False,
                    "status": "Not Eligible",
                    "message": "Student record not found."
                }

            if (
                student["Student_Status"] != "Active"
                or student["Account_Status"] != "Active"
            ):
                return {
                    "success": True,
                    "can_vote": False,
                    "status": "Not Eligible",
                    "message": "Your student or account status is inactive."
                }

            cursor.execute(
                """
                SELECT Election_Id, Election_Name, Status,
                       Start_Date, End_Date
                FROM elections
                WHERE Election_Id = %s
                """,
                (electionid,)
            )

            election = cursor.fetchone()

            if not election:
                return {
                    "success": True,
                    "can_vote": False,
                    "status": "Election Not Found",
                    "message": "The requested election does not exist."
                }

            now = datetime.now()

            if now < election["Start_Date"]:
                return {
                    "success": True,
                    "can_vote": False,
                    "status": "Upcoming",
                    "message": "Voting has not started yet."
                }

            if now >= election["End_Date"]:
                return {
                    "success": True,
                    "can_vote": False,
                    "status": "Closed",
                    "message": "The voting period has ended."
                }

            if election["Status"] != "Ongoing":
                return {
                    "success": True,
                    "can_vote": False,
                    "status": election["Status"],
                    "message": "This election is not open for voting."
                }

            cursor.execute(
                """
                SELECT Ballot_Id
                FROM ballots
                WHERE Election_Id = %s
                  AND Id_Number = %s
                LIMIT 1
                """,
                (electionid, idnum)
            )

            if cursor.fetchone():
                return {
                    "success": True,
                    "can_vote": False,
                    "status": "Already Voted",
                    "message": "You have already submitted your ballot."
                }

            return {
                "success": True,
                "can_vote": True,
                "status": "Eligible",
                "message": "You may proceed to the ballot.",
                "election": {
                    "Election_Id": election["Election_Id"],
                    "Election_Name": election["Election_Name"],
                    "Start_Date": election["Start_Date"],
                    "End_Date": election["End_Date"]
                }
            }

        except Exception:
            return {
                "success": False,
                "message": "Unable to check voting eligibility."
            }

        finally:
            cursor.close()

    # DISPLAY BALLOT
    def displayballot(self, electionid: str):
        cursor = self.conn.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT
                    p.Position_Id,
                    p.Position_Name,
                    p.Description AS Position_Description,
                    c.Candidate_Id,
                    c.Photo,
                    c.Biography,
                    c.Platform,
                    c.Candidacy_Type,
                    pl.Partylist_Id,
                    pl.Partylist_Name,
                    pl.Logo AS Partylist_Logo
                FROM positions p
                LEFT JOIN candidates c
                    ON c.Position_Id = p.Position_Id
                    AND c.Election_Id = p.Election_Id
                    AND c.Status = 'Active'
                LEFT JOIN partylists pl
                    ON pl.Partylist_Id = c.Partylist_Id
                WHERE p.Election_Id = %s
                ORDER BY p.Id ASC, c.Id ASC
                """,
                (electionid,)
            )

            rows = cursor.fetchall()

            if not rows:
                return {
                    "success": False,
                    "message": "No positions found for this election."
                }

            ballot = {}

            for row in rows:
                positionid = row["Position_Id"]

                if positionid not in ballot:
                    ballot[positionid] = {
                        "Position_Id": positionid,
                        "Position_Name": row["Position_Name"],
                        "Description": row["Position_Description"],
                        "Candidates": []
                    }

                if row["Candidate_Id"]:
                    ballot[positionid]["Candidates"].append({
                        "Candidate_Id": row["Candidate_Id"],
                        "Photo": row["Photo"],
                        "Biography": row["Biography"],
                        "Platform": row["Platform"],
                        "Candidacy_Type": row["Candidacy_Type"],
                        "Partylist_Id": row["Partylist_Id"],
                        "Partylist_Name": row["Partylist_Name"],
                        "Partylist_Logo": row["Partylist_Logo"]
                    })

            return {
                "success": True,
                "data": list(ballot.values())
            }

        except Exception:
            return {
                "success": False,
                "message": "Unable to retrieve the ballot."
            }

        finally:
            cursor.close()

    # SUBMIT BALLOT
    def submitvote(
        self,
        electionid: str,
        idnum: str,
        selections: list
    ):
        cursor = self.conn.cursor(dictionary=True)

        try:
            # Allow an empty list to represent full abstention.
            # The ballots table records the submission either way.
            if not isinstance(selections, list):
                return {
                    "success": False,
                    "message": "Invalid ballot selections."
                }

            positionids = [
                item.get("Position_Id")
                for item in selections
                if isinstance(item, dict)
            ]

            if len(positionids) != len(selections):
                return {
                    "success": False,
                    "message": "Invalid ballot selection format."
                }

            if (
                any(not positionid for positionid in positionids)
                or len(positionids) != len(set(positionids))
            ):
                return {
                    "success": False,
                    "message": "Select at most one candidate per position."
                }

            self.conn.start_transaction()

            # Validate the student and account.
            cursor.execute(
                """
                SELECT s.Status AS Student_Status,
                       u.Status AS Account_Status
                FROM students s
                INNER JOIN users u
                    ON u.Id_Number = s.Id_Number
                WHERE s.Id_Number = %s
                FOR UPDATE
                """,
                (idnum,)
            )

            student = cursor.fetchone()

            if not student:
                self.conn.rollback()
                return {
                    "success": False,
                    "message": "Student record not found."
                }

            if (
                student["Student_Status"] != "Active"
                or student["Account_Status"] != "Active"
            ):
                self.conn.rollback()
                return {
                    "success": False,
                    "message": "You are not eligible to vote."
                }

            # Validate election status and schedule.
            cursor.execute(
                """
                SELECT Status, Start_Date, End_Date
                FROM elections
                WHERE Election_Id = %s
                FOR UPDATE
                """,
                (electionid,)
            )

            election = cursor.fetchone()

            if not election:
                self.conn.rollback()
                return {
                    "success": False,
                    "message": "Election not found."
                }

            now = datetime.now()

            if (
                election["Status"] != "Ongoing"
                or now < election["Start_Date"]
                or now >= election["End_Date"]
            ):
                self.conn.rollback()
                return {
                    "success": False,
                    "message": "Voting is not currently available."
                }

            # Create one ballot record per student per election.
            ballotid = "B" + uuid.uuid4().hex[:19].upper()

            cursor.execute(
                """
                INSERT INTO ballots (
                    Ballot_Id,
                    Election_Id,
                    Id_Number,
                    Submitted_At,
                    Status
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    ballotid,
                    electionid,
                    idnum,
                    now,
                    "Submitted"
                )
            )

            # Validate and save each selected candidate.
            for selection in selections:
                candidateid = selection.get("Candidate_Id")
                positionid = selection.get("Position_Id")

                if not candidateid:
                    self.conn.rollback()
                    return {
                        "success": False,
                        "message": "A selected candidate is missing."
                    }

                cursor.execute(
                    """
                    SELECT c.Candidate_Id
                    FROM candidates c
                    INNER JOIN positions p
                        ON p.Position_Id = c.Position_Id
                        AND p.Election_Id = c.Election_Id
                    WHERE c.Candidate_Id = %s
                      AND c.Position_Id = %s
                      AND c.Election_Id = %s
                      AND c.Status = 'Active'
                    LIMIT 1
                    """,
                    (candidateid, positionid, electionid)
                )

                if not cursor.fetchone():
                    self.conn.rollback()
                    return {
                        "success": False,
                        "message": (
                            "A selected candidate is invalid, "
                            "inactive, or belongs to another position."
                        )
                    }

                voteid = "V" + uuid.uuid4().hex[:19].upper()

                cursor.execute(
                    """
                    INSERT INTO votes (
                        Vote_Id,
                        Election_Id,
                        Id_Number,
                        Candidate_Id,
                        Position_Id,
                        Created_At
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        voteid,
                        electionid,
                        idnum,
                        candidateid,
                        positionid,
                        now
                    )
                )

            self.conn.commit()

            return {
                "success": True,
                "message": "Your ballot has been submitted successfully.",
                "Ballot_Id": ballotid,
                "Submitted_At": now
            }

        except Exception as e:
            self.conn.rollback()

            # A duplicate ballot is blocked by the database's
            # unique constraint on Election_Id and Id_Number.
            if getattr(e, "errno", None) == 1062:
                return {
                    "success": False,
                    "message": "You have already submitted a ballot."
                }

            return {
                "success": False,
                "message": "Unable to submit the ballot."
            }

        finally:
            cursor.close()
