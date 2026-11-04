from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from Requests.User import router as user_router
from Requests.Election import router as election_router
from Requests.Candidate import router as candidate_router
from Requests.Partylist import router as partylist_router
from Requests.Position import router as position_router
from Requests.Voting import router as voting_router
from Requests.Authentication import router as authentication_router


api = FastAPI()
api.include_router(user_router)
api.include_router(election_router)
api.include_router(position_router)
api.include_router(partylist_router)
api.include_router(candidate_router)
api.include_router(voting_router)
api.include_router(authentication_router)

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

