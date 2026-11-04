from .Database import Database
class User(Database):

    def __init__(self):
        super().__init__()

    # ADD STUDENT
    def addstudent(
        self,
        idnum: str,
        password: str,
        fn: str,
        mn: str,
        ln: str,
        program: str,
        yearlevel: str,
        schoolyear: str,
        email: str
    ):
        try:
            self.conn.start_transaction()
            cursor = self.conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT Id FROM users WHERE Id_Number = %s",
                (idnum,)
            )

            user = cursor.fetchone()
            cursor.close()

            if user:
                self.conn.rollback()
                return {
                    "success": False,
                    "message": "ID Number already exists."
                }

            cursor = self.conn.cursor()

            cursor.execute(
                """
                INSERT INTO users
                (Id_Number, Password, Role, Status, Created_At)
                VALUES (%s, %s, %s, %s, NOW())
                """,
                (idnum, password, "Student", "Active")
            )
            cursor.close()

            cursor = self.conn.cursor()

            cursor.execute(
                """
                INSERT INTO students
                (
                    Id_Number, First_Name, Middle_Name, Last_Name,
                    Program, Year_Level, School_Year, Email,
                    Status, Created_At
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                """,
                (
                    idnum, fn, mn, ln, program, yearlevel,
                    schoolyear, email, "Active"
                )
            )
            cursor.close()

            self.conn.commit()

            return {
                "success": True,
                "message": "Student added successfully."
            }

        except Exception as e:
            self.conn.rollback()
            return {
                "success": False,
                "message": str(e)
            }

    # DISPLAY STUDENTS
    def displaystudents(
        self,
        search: str = "",
        program: str = "",
        yearlevel: str = "",
        status: str = ""
    ):
        cursor = None

        try:
            sql = """
                SELECT
                    s.Id,
                    s.Id_Number,
                    s.First_Name,
                    s.Middle_Name,
                    s.Last_Name,
                    s.Program,
                    s.Year_Level,
                    s.School_Year,
                    s.Email,
                    s.Status AS Student_Status,
                    u.Role,
                    u.Status AS Account_Status,
                    s.Created_At
                FROM students s
                INNER JOIN users u
                    ON s.Id_Number = u.Id_Number
                WHERE u.Role = 'Student'
            """

            values = []

            if search:
                sql += """
                    AND (
                        s.Id_Number LIKE %s
                        OR s.First_Name LIKE %s
                        OR s.Middle_Name LIKE %s
                        OR s.Last_Name LIKE %s
                    )
                """

                searchvalue = "%" + search + "%"
                values.extend([
                    searchvalue,
                    searchvalue,
                    searchvalue,
                    searchvalue
                ])

            if program:
                sql += " AND s.Program = %s"
                values.append(program)

            if yearlevel:
                sql += " AND s.Year_Level = %s"
                values.append(yearlevel)

            if status:
                sql += " AND s.Status = %s"
                values.append(status)

            sql += " ORDER BY s.Last_Name, s.First_Name"

            cursor = self.conn.cursor(dictionary=True)
            cursor.execute(sql, tuple(values))
            result = cursor.fetchall()

            return {
                "success": True,
                "data": result
            }

        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }

        finally:
            if cursor:
                cursor.close()

    # UPDATE STUDENT INFORMATION
    def updatestudent(
        self,
        idnum: str,
        fn: str,
        mn: str,
        ln: str,
        program: str,
        yearlevel: str,
        schoolyear: str,
        email: str
    ):
        cursor = None

        try:
            self.conn.start_transaction()

            cursor = self.conn.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT Id_Number
                FROM users
                WHERE Id_Number = %s
                AND Role = 'Student'
                """,
                (idnum,)
            )

            user = cursor.fetchone()
            cursor.close()
            cursor = None

            if not user:
                self.conn.rollback()
                return {
                    "success": False,
                    "message": "Student account not found."
                }

            cursor = self.conn.cursor()

            cursor.execute(
                """
                UPDATE students
                SET First_Name = %s,
                    Middle_Name = %s,
                    Last_Name = %s,
                    Program = %s,
                    Year_Level = %s,
                    School_Year = %s,
                    Email = %s
                WHERE Id_Number = %s
                """,
                (
                    fn, mn, ln, program, yearlevel,
                    schoolyear, email, idnum
                )
            )

            self.conn.commit()

            return {
                "success": True,
                "message": "Student information updated successfully."
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

    # UPDATE STUDENT STATUS
    def updatestatus(self, idnum: str, status: str):
        cursor = None

        try:
            status = status.strip().title()

            if status not in ["Active", "Inactive", "Graduated"]:
                return {
                    "success": False,
                    "message": "Invalid student status. Choose Active, Inactive, or Graduated."
                }

            self.conn.start_transaction()

            cursor = self.conn.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT Id_Number
                FROM users
                WHERE Id_Number = %s
                AND Role = 'Student'
                """,
                (idnum,)
            )

            user = cursor.fetchone()
            cursor.close()
            cursor = None

            if not user:
                self.conn.rollback()
                return {
                    "success": False,
                    "message": "Student account not found."
                }

            # Update the student's academic eligibility status.
            cursor = self.conn.cursor()

            cursor.execute(
                """
                UPDATE students
                SET Status = %s
                WHERE Id_Number = %s
                """,
                (status, idnum)
            )
            cursor.close()
            cursor = None

            # Graduated students cannot use their student accounts.
            # Inactive students are also prevented from logging in.
            accountstatus = (
                "Inactive" if status in ["Inactive", "Graduated"]
                else "Active"
            )

            cursor = self.conn.cursor()

            cursor.execute(
                """
                UPDATE users
                SET Status = %s
                WHERE Id_Number = %s
                AND Role = 'Student'
                """,
                (accountstatus, idnum)
            )

            self.conn.commit()

            return {
                "success": True,
                "message": "Student status updated successfully."
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

    # CHECK STUDENT VOTING ELIGIBILITY
    def checkeligibility(self, idnum: str, electionid: str):
        cursor = None

        try:
            cursor = self.conn.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT
                    s.Id_Number,
                    s.First_Name,
                    s.Middle_Name,
                    s.Last_Name,
                    s.Program,
                    s.Year_Level,
                    s.Status AS Student_Status,
                    u.Status AS Account_Status,
                    e.Election_Id,
                    e.Election_Name,
                    e.Status AS Election_Status,
                    CASE
                        WHEN s.Status = 'Active'
                            AND u.Status = 'Active'
                            AND e.Status = 'Ongoing'
                            AND v.Id IS NULL
                        THEN 'Eligible'
                        ELSE 'Not Eligible'
                    END AS Eligibility
                FROM students s
                INNER JOIN users u
                    ON s.Id_Number = u.Id_Number
                INNER JOIN elections e
                    ON e.Election_Id = %s
                LEFT JOIN votes v
                    ON v.Election_Id = e.Election_Id
                    AND v.Id_Number = s.Id_Number
                WHERE s.Id_Number = %s
                    AND u.Role = 'Student'
                """,
                (electionid, idnum)
            )

            result = cursor.fetchone()

            if not result:
                return {
                    "success": False,
                    "message": "Student or election not found."
                }

            return {
                "success": True,
                "data": result
            }

        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }

        finally:
            if cursor:
                cursor.close()
