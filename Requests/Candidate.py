
from fastapi import APIRouter, Form
from Class.Candidate import Candidate

router = APIRouter()


# STUDENT: SUBMIT CANDIDACY
@router.post("/candidates/add")
def addcandidate(
    idnum: str = Form(...),
    electionid: str = Form(...),
    positionid: str = Form(...),
    candidacytype: str = Form(...),
    partylistid: str = Form(""),
    photo: str = Form(""),
    biography: str = Form(""),
    platform: str = Form("")
):
    c = Candidate()

    return c.addcandidate(
        idnum,
        electionid,
        positionid,
        candidacytype,
        partylistid,
        photo,
        biography,
        platform
    )


# ADMIN: DISPLAY CANDIDATES
@router.get("/candidates")
def displaycandidates(
    search: str = "",
    status: str = "",
    electionid: str = ""
):
    c = Candidate()
    return c.displaycandidates(search, status, electionid)


# STUDENT: VIEW OWN CANDIDACY STATUS
@router.get("/candidates/status")
def viewcandidacystatus(idnum: str):
    c = Candidate()
    return c.viewcandidacystatus(idnum)


# STUDENT: UPDATE OWN PENDING CANDIDACY
@router.put("/candidates/update")
def updatecandidacy(
    candidateid: str = Form(...),
    idnum: str = Form(...),
    photo: str = Form(""),
    biography: str = Form(""),
    platform: str = Form("")
):
    c = Candidate()

    return c.updatecandidacy(
        candidateid,
        idnum,
        photo,
        biography,
        platform
    )


# ADMIN: APPROVE CANDIDACY
@router.put("/candidates/approve")
def approvecandidate(
    candidateid: str = Form(...)
):
    c = Candidate()
    return c.approvecandidate(candidateid)


# ADMIN: REJECT CANDIDACY
@router.put("/candidates/reject")
def rejectcandidate(
    candidateid: str = Form(...)
):
    c = Candidate()
    return c.rejectcandidate(candidateid)


# VIEW APPROVED CANDIDATES FOR AN ELECTION
@router.get("/candidates/approved")
def displayapprovedcandidates(
    electionid: str,
    positionid: str = ""
):
    c = Candidate()
    return c.displayapprovedcandidates(electionid, positionid)


# ADMIN: VIEW CANDIDATE DETAILS
@router.get("/candidates/details")
def viewcandidatedetails(candidateid: str):
    c = Candidate()
    return c.viewcandidatedetails(candidateid)


# ADMIN: CHECK CANDIDATE ELIGIBILITY
@router.get("/candidates/eligibility")
def checkcandidateeligibility(candidateid: str):
    c = Candidate()
    return c.checkcandidateeligibility(candidateid)


# ADMIN: ASSIGN AN APPROVED CANDIDATE TO A POSITION
@router.put("/candidates/assign-position")
def assigncandidateposition(
    candidateid: str = Form(...),
    positionid: str = Form(...)
):
    c = Candidate()
    return c.assigncandidateposition(candidateid, positionid)
