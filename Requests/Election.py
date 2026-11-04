
from fastapi import APIRouter, Form
from Class.Election import Election

router = APIRouter()


# ADMIN: ADD ELECTION
@router.post("/elections/add")
def addelection(
    electionid: str = Form(...),
    electionname: str = Form(...),
    description: str = Form(""),
    schoolyear: str = Form(...),
    startdate: str = Form(...),
    enddate: str = Form(...),
    createdby: str = Form(...)
):
    e = Election()

    return e.addelection(
        electionid,
        electionname,
        description,
        schoolyear,
        startdate,
        enddate,
        createdby
    )


# ADMIN: DISPLAY ALL ELECTIONS
@router.get("/elections")
def displayelections(search: str = "", status: str = ""):
    e = Election()
    return e.displayelections(search, status)


# ADMIN: UPDATE ELECTION
@router.put("/elections/update")
def updateelection(
    electionid: str = Form(...),
    electionname: str = Form(...),
    description: str = Form(""),
    schoolyear: str = Form(...),
    startdate: str = Form(...),
    enddate: str = Form(...)
):
    e = Election()

    return e.updateelection(
        electionid,
        electionname,
        description,
        schoolyear,
        startdate,
        enddate
    )


# ADMIN: OPEN ELECTION MANUALLY
@router.put("/elections/open")
def openelection(electionid: str = Form(...)):
    e = Election()
    return e.openelection(electionid)


# ADMIN: CLOSE ELECTION MANUALLY
@router.put("/elections/close")
def closeelection(electionid: str = Form(...)):
    e = Election()
    return e.closeelection(electionid)


# ADMIN: LOCK ELECTION
@router.put("/elections/lock")
def lockelection(electionid: str = Form(...)):
    e = Election()
    return e.lockelection(electionid)


# STUDENT: VIEW ACTIVE ELECTIONS
@router.get("/student/active-elections")
def displayactiveelections():
    e = Election()
    return e.displayactiveelections()


# STUDENT: VIEW ELECTION DETAILS
@router.get("/student/election-details")
def viewelectiondetails(electionid: str):
    e = Election()
    return e.viewelectiondetails(electionid)
