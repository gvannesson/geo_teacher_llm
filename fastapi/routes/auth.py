from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from schemas.user import UserCreate, UserRead
from schemas.auth import Token
from models.user import User
from db.session import get_session
from core.security import get_password_hash, verify_password
from utils.jwt_handler import oauth2_scheme
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone
from core.config import SECRET_KEY, ALGORITHM
import jwt

router = APIRouter()

@router.post("/register", response_model=UserRead)
def register(user: UserCreate, session: Session = Depends(get_session)):

    statement = select(User).where(User.username == user.username)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà utilisé")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

ACCESS_TOKEN_EXPIRE_MINUTES = 90 

@router.post("/login", response_model=Token)
def login(
    form: OAuth2PasswordRequestForm = Depends(), 
    session: Session = Depends(get_session)
):
    statement = select(User).where(User.username == form.username)
    db_user = session.exec(statement).first()

    if not db_user or not verify_password(form.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": db_user.username, "id": db_user.id, "exp": expire}
    access_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": access_token, "token_type": "bearer"}
