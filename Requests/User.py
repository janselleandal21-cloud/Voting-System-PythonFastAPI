from fastapi import APIRouter, Form
from Class.User import User

router = APIRouter()


# ADMIN: ADD STUDENT
@router.post("/students/add")
def addstudent(
    idnum: str = Form(...),
    password: str = Form(...),
    fn: str = Form(...),
    mn: str = Form(""),
    ln: str = Form(...),
    program: str = Form(...),
    yearlevel: str = Form(...),
    schoolyear: str = Form(...),
    email: str = Form(...)
):
    u = User()

    return u.addstudent(
        idnum,
        password,
        fn,
        mn,
        ln,
        program,
        yearlevel,
        schoolyear,
        email
    )


# ADMIN: DISPLAY STUDENTS
@router.get("/students")
def displaystudents(
    search: str = "",
    program: str = "",
    yearlevel: str = "",
    status: str = ""
):
    u = User()

    return u.displaystudents(
        search,
        program,
        yearlevel,
        status
    )


# ADMIN: UPDATE STUDENT INFORMATION
@router.put("/students/update")
def updatestudent(
    idnum: str = Form(...),
    fn: str = Form(...),
    mn: str = Form(""),
    ln: str = Form(...),
    program: str = Form(...),
    yearlevel: str = Form(...),
    schoolyear: str = Form(...),
    email: str = Form(...)
):
    u = User()

    return u.updatestudent(
        idnum,
        fn,
        mn,
        ln,
        program,
        yearlevel,
        schoolyear,
        email
    )


# ADMIN: UPDATE STUDENT STATUS
@router.put("/students/status")
def updatestatus(
    idnum: str = Form(...),
    status: str = Form(...)
):
    u = User()

    return u.updatestatus(idnum, status)


# CHECK STUDENT VOTING ELIGIBILITY
@router.get("/students/eligibility")
def checkeligibility(
    idnum: str,
    electionid: str
):
    u = User()

    return u.checkeligibility(
        idnum,
        electionid
    )
