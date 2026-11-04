from fastapi import APIRouter, Form
from Class.User2 import User2

router = APIRouter()


@router.post("/login")
def login(
    idnum: str = Form(...),
    pw: str = Form(...)
):
    u = User2()
    res = u.login(idnum, pw)
    return res


@router.post("/add")
def add(
    idnum: str = Form(...),
    ln: str = Form(...),
    fn: str = Form(...),
    mn: str = Form(...),
    bdate: str = Form(...),
    address: str = Form(...),
    contact: str = Form(...)
):
    u = User2()

    res = u.add(idnum,ln,fn,mn,bdate,address,contact)
    return res


@router.get("/displayall")
def displayall():
    u = User2()
    res = u.displayall()
    return res