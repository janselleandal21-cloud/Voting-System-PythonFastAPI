from fastapi import APIRouter, Form
from Class.Partylist import Partylist
router = APIRouter()


# STUDENT: SUBMIT PARTYLIST
@router.post("/partylist/add")
def addpartylist(
    partylistname: str = Form(...),
    description: str = Form(""),
    platform: str = Form(""),
    logo: str = Form(""),
    idnum: str = Form(...)
):
    p = Partylist()
    return p.addpartylist(
        partylistname,
        description,
        platform,
        logo,
        idnum
    )


# ADMIN: DISPLAY PARTYLlSTS
@router.get("/partylist")
def displaypartylists(
    search: str = "",
    status: str = ""
):
    p = Partylist()
    return p.displaypartylists(search, status)


# STUDENT: VIEW OWN SUBMISSIONS
@router.get("/partylist/student/status")
def viewpartylistsubmissions(idnum: str):
    p = Partylist()
    return p.viewpartylistsubmissions(idnum)


# STUDENT: UPDATE OWN PENDING PARTYLIST
@router.put("/partylist/update")
def updatepartylist(
    partylistid: str = Form(...),
    idnum: str = Form(...),
    partylistname: str = Form(...),
    description: str = Form(""),
    platform: str = Form(""),
    logo: str = Form("")
):
    p = Partylist()
    return p.updatepartylist(
        partylistid,
        idnum,
        partylistname,
        description,
        platform,
        logo
    )


# ADMIN: APPROVE OR REJECT PENDING PARTYLIST
@router.put("/partylist/status")
def updatestatus(
    partylistid: str = Form(...),
    status: str = Form(...)
):
    p = Partylist()
    return p.updatestatus(partylistid, status)


# ADMIN: VIEW PARTYLIST DETAILS
@router.get("/partylist/details")
def viewpartylistdetails(partylistid: str):
    p = Partylist()
    return p.viewpartylistdetails(partylistid)


# ADMIN: ACTIVATE OR DEACTIVATE AN APPROVED PARTYLIST
@router.put("/partylist/update-status")
def updatepartyliststatus(
    partylistid: str = Form(...),
    status: str = Form(...)
):
    p = Partylist()
    return p.updatepartyliststatus(partylistid, status)


# ADMIN: VIEW PARTYLIST MEMBERS AND CANDIDATES
@router.get("/partylist/members")
def viewpartylistmembers(partylistid: str):
    p = Partylist()
    return p.viewpartylistmembers(partylistid)
