
from fastapi import APIRouter, Form
from Class.Position import Position

router = APIRouter()


# ADD POSITION
@router.post("/positions/add")
def addposition(
    positionid: str = Form(...),
    electionid: str = Form(...),
    positionname: str = Form(...),
    description: str = Form("")
):
    p = Position()

    return p.addposition(
        positionid,
        electionid,
        positionname,
        description
    )


# DISPLAY POSITIONS
@router.get("/positions")
def displaypositions(
    search: str = "",
    electionid: str = ""
):
    p = Position()

    return p.displaypositions(
        search,
        electionid
    )


# UPDATE POSITION
@router.put("/positions/update")
def updateposition(
    positionid: str = Form(...),
    positionname: str = Form(...),
    description: str = Form("")
):
    p = Position()

    return p.updateposition(
        positionid,
        positionname,
        description
    )


# DELETE POSITION
@router.delete("/positions/delete")
def deleteposition(
    positionid: str = Form(...)
):
    p = Position()

    return p.deleteposition(positionid)
