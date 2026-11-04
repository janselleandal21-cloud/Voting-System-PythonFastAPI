
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List

from Class.Voting import Voting
from Class.Auth import get_current_user, require_role


router = APIRouter()
voting = Voting()


# VOTE SELECTION MODEL
class VoteSelection(BaseModel):
    Candidate_Id: str
    Position_Id: str


# SUBMIT VOTE REQUEST MODEL
class SubmitVoteRequest(BaseModel):
    Election_Id: str
    Selections: List[VoteSelection]


# CHECK STUDENT VOTING STATUS
@router.get("/voting/status")
def checkvotingstatus(
    electionid: str,
    current_user: dict = Depends(require_role("Student"))
):
    return voting.checkvotingstatus(
        current_user["Id_Number"],
        electionid
    )


# DISPLAY BALLOT
@router.get("/voting/ballot")
def displayballot(
    electionid: str,
    current_user: dict = Depends(require_role("Student"))
):
    # Check eligibility before returning the ballot.
    status = voting.checkvotingstatus(
        current_user["Id_Number"],
        electionid
    )

    if not status.get("can_vote"):
        return {
            "success": False,
            "message": status.get(
                "message",
                "You cannot access this ballot."
            ),
            "status": status.get("status")
        }

    return voting.displayballot(electionid)


# SUBMIT BALLOT
@router.post("/voting/submit")
def submitvote(
    request: SubmitVoteRequest,
    current_user: dict = Depends(require_role("Student"))
):
    selections = [
        {
            "Candidate_Id": selection.Candidate_Id,
            "Position_Id": selection.Position_Id
        }
        for selection in request.Selections
    ]

    return voting.submitvote(
        request.Election_Id,
        current_user["Id_Number"],
        selections
    )
