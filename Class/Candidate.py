
from .Database import Database
from datetime import datetime


class Candidate(Database):

    def __init__(self):
        super().__init__()

    # ADD CANDIDACY REQUEST (STUDENT)
    def addcandidate(
        self,
        idnum: str,
        electionid: str,
        positionid: str,
        candidacytype: str,
        partylistid: str = "",
        photo: str = "",
        biography: str = "",
        platform: str = ""
    ):
        cursor = None

        try:
            if candidacytype not in ["Partylist", "Independent"]:
                return {
                    "success": False,
                    "message": "Candidacy type must be Partylist or Independent."
                }

            if candidacytype == "Partylist" and not partylistid:
                return {
                    "success": False,
                    "message": "Please select an approved partylist."
                }

            if candidacytype == "Independent":
                partylistid = ""

            cursor = self.conn.cursor(dictionary=True)

            # CHECK ELECTION
            cursor.execute(
                """
                SELECT Election_Id, Status, Start_Date
                FROM elections
                WHERE Election_Id = %s
                """,
                (electionid,)
            )

            election = cursor.fetchone()

            if not election:
                return {
                    "success": False,
                    "message": "Election not found."
                }

            if election["Status"] != "Scheduled":
                return {
                    "success": False,
                    "message": "Candidacy requests are only allowed for scheduled elections."
                }

            if election["Start_Date"] and datetime.now() >= election["Start_Date"]:
                return {
                    "success": False,
                    "message": "Candidacy submission is already closed."
                }

            # CHECK POSITION BELONGS TO THE ELECTION
            cursor.execute(
                """
                SELECT Position_Id
                FROM positions
                WHERE Position_Id = %s
                AND Election_Id = %s
                """,
                (positionid, electionid)
            )

            position = cursor.fetchone()

            if not position:
                return {
                    "success": False,
                    "message": "Position does not belong to the selected election."
                }

            # CHECK PARTYLIST STATUS
            if candidacytype == "Partylist":
                cursor.execute(
                    """
                    SELECT Partylist_Id
                    FROM partylists
                    WHERE Partylist_Id = %s
                    AND Status IN ('Approved', 'Active')
                    """,
                    (partylistid,)
                )

                partylist = cursor.fetchone()

                if not partylist:
                    return {
                        "success": False,
                        "message": "Selected partylist is not approved or active."
                    }

            # PREVENT DUPLICATE ACTIVE SUBMISSIONS
            cursor.execute(
                """
                SELECT Candidate_Id
                FROM candidates
                WHERE Id_Number = %s
                AND Election_Id = %s
                AND Position_Id = %s
                AND Status IN ('Pending', 'Approved')
                """,
                (idnum, electionid, positionid)
            )

            existing = cursor.fetchone()

            if existing:
                return {
                    "success": False,
                    "message": "You already have a pending or approved candidacy for this position."
                }

            cursor.close()
            cursor = self.conn.cursor()

            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # INSERT CANDIDACY
            cursor.execute(
                """
                INSERT INTO candidates
                (
                    Candidate_Id,
                    Id_Number,
                    Election_Id,
                    Position_Id,
                    Partylist_Id,
                    Candidacy_Type,
                    Photo,
                    Biography,
                    Platform,
                    Status,
                    Created_At
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    "",
                    idnum,
                    electionid,
                    positionid,
                    partylistid if partylistid else None,
                    candidacytype,
                    photo,
                    biography,
                    platform,
                    "Pending",
                    created_at
                )
            )

            new_id = cursor.lastrowid
            candidate_id = f"CAN{new_id:05d}"

            cursor.execute(
                """
                UPDATE candidates
                SET Candidate_Id = %s
                WHERE Id = %s
                """,
                (candidate_id, new_id)
            )

            self.conn.commit()

            return {
                "success": True,
                "message": "Candidacy submitted successfully.",
                "candidateid": candidate_id
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

    # DISPLAY CANDIDATES (ADMIN)
    def displaycandidates(
        self,
        search: str = "",
        status: str = "",
        electionid: str = ""
    ):
        cursor = None

        try:
            cursor = self.conn.cursor(dictionary=True)

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
                    p.Position_Name,
                    c.Partylist_Id,
                    pl.Partylist_Name,
                    c.Candidacy_Type,
                    c.Photo,
                    c.Biography,
                    c.Platform,
                    c.Status,
                    c.Created_At
                FROM candidates c
                LEFT JOIN students s
                    ON c.Id_Number = s.Id_Number
                LEFT JOIN elections e
                    ON c.Election_Id = e.Election_Id
                LEFT JOIN positions p
                    ON c.Position_Id = p.Position_Id
                    AND c.Election_Id = p.Election_Id
                LEFT JOIN partylists pl
                    ON c.Partylist_Id = pl.Partylist_Id
                WHERE 1 = 1
            """

            values = []

            if search:
                sql += """
                    AND (
                        c.Candidate_Id LIKE %s
                        OR c.Id_Number LIKE %s
                        OR s.First_Name LIKE %s
                        OR s.Last_Name LIKE %s
                        OR e.Election_Name LIKE %s
                        OR p.Position_Name LIKE %s
                        OR pl.Partylist_Name LIKE %s
                    )
                """
                keyword = f"%{search}%"
                values.extend([keyword] * 7)

            if status:
                sql += " AND c.Status = %s"
                values.append(status)

            if electionid:
                sql += " AND c.Election_Id = %s"
                values.append(electionid)

            sql += " ORDER BY c.Created_At DESC"

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

    # STUDENT: VIEW OWN CANDIDACY STATUS
    def viewcandidacystatus(self, idnum: str):
        cursor = None

        try:
            cursor = self.conn.cursor(dictionary=True)

            sql = """
                SELECT
                    c.Candidate_Id,
                    c.Id_Number,
                    c.Election_Id,
                    e.Election_Name,
                    e.Status AS Election_Status,
                    e.Start_Date,
                    e.End_Date,
                    c.Position_Id,
                    p.Position_Name,
                    c.Partylist_Id,
                    pl.Partylist_Name,
                    c.Candidacy_Type,
                    c.Photo,
                    c.Biography,
                    c.Platform,
                    c.Status,
                    c.Created_At
                FROM candidates c
                LEFT JOIN elections e
                    ON c.Election_Id = e.Election_Id
                LEFT JOIN positions p
                    ON c.Position_Id = p.Position_Id
                    AND c.Election_Id = p.Election_Id
                LEFT JOIN partylists pl
                    ON c.Partylist_Id = pl.Partylist_Id
                WHERE c.Id_Number = %s
                ORDER BY c.Created_At DESC
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

    # STUDENT: UPDATE OWN PENDING CANDIDACY
    def updatecandidacy(
        self,
        candidateid: str,
        idnum: str,
        photo: str = "",
        biography: str = "",
        platform: str = ""
    ):
        cursor = None

        try:
            cursor = self.conn.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT Status
                FROM candidates
                WHERE Candidate_Id = %s
                AND Id_Number = %s
                """,
                (candidateid, idnum)
            )

            candidate = cursor.fetchone()

            if not candidate:
                return {
                    "success": False,
                    "message": "Candidacy not found or you do not own this submission."
                }

            if candidate["Status"] != "Pending":
                return {
                    "success": False,
                    "message": "Only pending candidacy requests can be updated."
                }

            cursor.close()
            cursor = self.conn.cursor()

            cursor.execute(
                """
                UPDATE candidates
                SET Photo = %s,
                    Biography = %s,
                    Platform = %s
                WHERE Candidate_Id = %s
                AND Id_Number = %s
                AND Status = 'Pending'
                """,
                (photo, biography, platform, candidateid, idnum)
            )

            self.conn.commit()

            return {
                "success": cursor.rowcount > 0,
                "message": "Candidacy information updated successfully."
                if cursor.rowcount > 0
                else "No changes were made."
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

    # ADMIN: APPROVE CANDIDACY
    def approvecandidate(self, candidateid: str):
        cursor = None

        try:
            cursor = self.conn.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT
                    c.Status,
                    c.Election_Id,
                    e.Status AS Election_Status,
                    e.Start_Date
                FROM candidates c
                JOIN elections e
                    ON c.Election_Id = e.Election_Id
                WHERE c.Candidate_Id = %s
                """,
                (candidateid,)
            )

            candidate = cursor.fetchone()

            if not candidate:
                return {
                    "success": False,
                    "message": "Candidacy request not found."
                }

            if candidate["Status"] != "Pending":
                return {
                    "success": False,
                    "message": "Only pending candidacy requests can be approved."
                }

            if candidate["Election_Status"] != "Scheduled":
                return {
                    "success": False,
                    "message": "Candidacy can only be approved for scheduled elections."
                }

            if candidate["Start_Date"] and datetime.now() >= candidate["Start_Date"]:
                return {
                    "success": False,
                    "message": "Candidacy approval is closed because the election start time has been reached."
                }

            # VERIFY STUDENT ELIGIBILITY
            cursor.close()
            cursor = None

            eligibility = self.checkcandidateeligibility(candidateid)

            if not eligibility.get("success"):
                return eligibility

            if not eligibility.get("eligible"):
                return {
                    "success": False,
                    "message": "Candidate failed the eligibility checks.",
                    "checks": eligibility.get("checks", {})
                }

            cursor = self.conn.cursor()

            cursor.execute(
                """
                UPDATE candidates
                SET Status = 'Approved'
                WHERE Candidate_Id = %s
                AND Status = 'Pending'
                """,
                (candidateid,)
            )

            self.conn.commit()

            return {
                "success": cursor.rowcount > 0,
                "message": "Candidate approved successfully."
                if cursor.rowcount > 0
                else "Candidacy status was not changed."
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

    # ADMIN: REJECT CANDIDACY
    def rejectcandidate(self, candidateid: str):
        cursor = None

        try:
            cursor = self.conn.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT Status
                FROM candidates
                WHERE Candidate_Id = %s
                """,
                (candidateid,)
            )

            candidate = cursor.fetchone()

            if not candidate:
                return {
                    "success": False,
                    "message": "Candidacy request not found."
                }

            if candidate["Status"] != "Pending":
                return {
                    "success": False,
                    "message": "Only pending candidacy requests can be rejected."
                }

            cursor.close()
            cursor = self.conn.cursor()

            cursor.execute(
                """
                UPDATE candidates
                SET Status = 'Rejected'
                WHERE Candidate_Id = %s
                AND Status = 'Pending'
                """,
                (candidateid,)
            )

            self.conn.commit()

            return {
                "success": cursor.rowcount > 0,
                "message": "Candidacy rejected successfully."
                if cursor.rowcount > 0
                else "Candidacy status was not changed."
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

    # VIEW APPROVED CANDIDATES FOR THE BALLOT
    def displayapprovedcandidates(
        self,
        electionid: str,
        positionid: str = ""
    ):
        cursor = None

        try:
            cursor = self.conn.cursor(dictionary=True)

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
                    p.Position_Name,
                    c.Partylist_Id,
                    pl.Partylist_Name,
                    c.Candidacy_Type,
                    c.Photo,
                    c.Biography,
                    c.Platform,
                    c.Status
                FROM candidates c
                JOIN elections e
                    ON c.Election_Id = e.Election_Id
                JOIN positions p
                    ON c.Position_Id = p.Position_Id
                    AND c.Election_Id = p.Election_Id
                LEFT JOIN students s
                    ON c.Id_Number = s.Id_Number
                LEFT JOIN partylists pl
                    ON c.Partylist_Id = pl.Partylist_Id
                WHERE c.Election_Id = %s
                AND c.Status = 'Approved'
                AND e.Status IN ('Scheduled', 'Ongoing')
            """

            values = [electionid]

            if positionid:
                sql += " AND c.Position_Id = %s"
                values.append(positionid)

            sql += " ORDER BY p.Position_Name, Candidate_Name"

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

    # ADMIN: VIEW CANDIDATE DETAILS
    def viewcandidatedetails(self, candidateid: str):
        cursor = None

        try:
            cursor = self.conn.cursor(dictionary=True)

            sql = """
                SELECT
                    c.Candidate_Id,
                    c.Id_Number,
                    CONCAT(
                        s.First_Name, ' ',
                        IFNULL(CONCAT(s.Middle_Name, ' '), ''),
                        s.Last_Name
                    ) AS Candidate_Name,
                    s.Program,
                    s.Year_Level,
                    s.School_Year,
                    s.Email,
                    u.Role AS Account_Role,
                    u.Status AS Account_Status,
                    s.Status AS Student_Status,
                    c.Election_Id,
                    e.Election_Name,
                    e.School_Year AS Election_School_Year,
                    e.Status AS Election_Status,
                    e.Start_Date,
                    e.End_Date,
                    c.Position_Id,
                    p.Position_Name,
                    c.Partylist_Id,
                    pl.Partylist_Name,
                    pl.Status AS Partylist_Status,
                    c.Candidacy_Type,
                    c.Photo,
                    c.Biography,
                    c.Platform,
                    c.Status AS Candidacy_Status,
                    c.Created_At
                FROM candidates c
                LEFT JOIN students s
                    ON c.Id_Number = s.Id_Number
                LEFT JOIN users u
                    ON c.Id_Number = u.Id_Number
                LEFT JOIN elections e
                    ON c.Election_Id = e.Election_Id
                LEFT JOIN positions p
                    ON c.Position_Id = p.Position_Id
                    AND c.Election_Id = p.Election_Id
                LEFT JOIN partylists pl
                    ON c.Partylist_Id = pl.Partylist_Id
                WHERE c.Candidate_Id = %s
            """

            cursor.execute(sql, (candidateid,))
            row = cursor.fetchone()

            if not row:
                return {
                    "success": False,
                    "message": "Candidate not found."
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

    # ADMIN: CHECK CANDIDATE ELIGIBILITY
    def checkcandidateeligibility(self, candidateid: str):
        cursor = None

        try:
            cursor = self.conn.cursor(dictionary=True)

            sql = """
                SELECT
                    c.Candidate_Id,
                    c.Id_Number,
                    c.Election_Id,
                    c.Status AS Candidacy_Status,
                    c.Candidacy_Type,
                    c.Partylist_Id,
                    s.Status AS Student_Status,
                    s.School_Year AS Student_School_Year,
                    u.Role AS Account_Role,
                    u.Status AS Account_Status,
                    e.School_Year AS Election_School_Year,
                    e.Status AS Election_Status,
                    e.Start_Date,
                    p.Position_Id AS Existing_Position,
                    pl.Status AS Partylist_Status
                FROM candidates c
                LEFT JOIN students s
                    ON c.Id_Number = s.Id_Number
                LEFT JOIN users u
                    ON c.Id_Number = u.Id_Number
                LEFT JOIN elections e
                    ON c.Election_Id = e.Election_Id
                LEFT JOIN positions p
                    ON c.Position_Id = p.Position_Id
                    AND c.Election_Id = p.Election_Id
                LEFT JOIN partylists pl
                    ON c.Partylist_Id = pl.Partylist_Id
                WHERE c.Candidate_Id = %s
            """

            cursor.execute(sql, (candidateid,))
            row = cursor.fetchone()

            if not row:
                return {
                    "success": False,
                    "eligible": False,
                    "message": "Candidate not found."
                }

            checks = {
                "student_record_exists": row["Student_Status"] is not None,
                "user_account_exists": row["Account_Role"] is not None,
                "account_is_student": row["Account_Role"] == "Student",
                "account_is_active": row["Account_Status"] == "Active",
                "student_is_active": row["Student_Status"] == "Active",
                "school_year_matches": (
                    row["Student_School_Year"] == row["Election_School_Year"]
                ),
                "election_exists": row["Election_Status"] is not None,
                "position_belongs_to_election": row["Existing_Position"] is not None,
                "partylist_is_approved_or_active": (
                    row["Candidacy_Type"] != "Partylist"
                    or row["Partylist_Status"] in ["Approved", "Active"]
                )
            }

            eligible = all(checks.values())

            return {
                "success": True,
                "eligible": eligible,
                "message": "Candidate passed the eligibility checks."
                if eligible
                else "One or more eligibility checks failed.",
                "candidateid": candidateid,
                "idnum": row["Id_Number"],
                "checks": checks
            }

        except Exception as e:
            return {
                "success": False,
                "eligible": False,
                "message": str(e)
            }

        finally:
            if cursor:
                cursor.close()

    # ADMIN: ASSIGN AN APPROVED CANDIDATE TO A POSITION
    def assigncandidateposition(
        self,
        candidateid: str,
        positionid: str
    ):
        cursor = None

        try:
            cursor = self.conn.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT
                    c.Status AS Candidacy_Status,
                    c.Election_Id,
                    e.Status AS Election_Status,
                    e.Start_Date
                FROM candidates c
                JOIN elections e
                    ON c.Election_Id = e.Election_Id
                WHERE c.Candidate_Id = %s
                """,
                (candidateid,)
            )

            candidate = cursor.fetchone()

            if not candidate:
                return {
                    "success": False,
                    "message": "Candidate not found."
                }

            if candidate["Candidacy_Status"] != "Approved":
                return {
                    "success": False,
                    "message": "Only approved candidates can be assigned to another position."
                }

            if candidate["Election_Status"] != "Scheduled":
                return {
                    "success": False,
                    "message": "Position assignment is only allowed for scheduled elections."
                }

            if candidate["Start_Date"] and datetime.now() >= candidate["Start_Date"]:
                return {
                    "success": False,
                    "message": "Position assignment is closed because the election start time has been reached."
                }

            cursor.execute(
                """
                SELECT Position_Id
                FROM positions
                WHERE Position_Id = %s
                AND Election_Id = %s
                """,
                (positionid, candidate["Election_Id"])
            )

            position = cursor.fetchone()

            if not position:
                return {
                    "success": False,
                    "message": "The selected position does not belong to this election."
                }

            cursor.close()
            cursor = self.conn.cursor()

            cursor.execute(
                """
                UPDATE candidates
                SET Position_Id = %s
                WHERE Candidate_Id = %s
                AND Status = 'Approved'
                """,
                (positionid, candidateid)
            )

            self.conn.commit()

            return {
                "success": cursor.rowcount > 0,
                "message": "Candidate position assigned successfully."
                if cursor.rowcount > 0
                else "Candidate position was not changed."
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
