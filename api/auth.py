from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select
import os

# FIXED IMPORTS - Remove 'app.' prefix
from api.schemas import UserCreate, UserPublic, Token
from models import User, engine
from core.auth import (
    hash_password, 
    verify_password, 
    create_access_token, 
    validate_google_token,
    get_current_user
)

router = APIRouter(tags=["auth"])

def get_session():
    with Session(engine) as session:
        yield session

@router.get("/google/login")
def google_login():
    """
    Redirects user to Google OAuth page
    """
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        "?response_type=code"
        f"&client_id={os.getenv('GOOGLE_CLIENT_ID')}"
        # FIXED: Match your Google Console redirect URI
        "&redirect_uri=http://localhost:8000/api/auth/google/callback"
        "&scope=openid%20email%20profile"
        "&access_type=offline"
        "&prompt=consent"
    )
    return RedirectResponse(url=google_auth_url)

@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register_user(new_user: UserCreate, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == new_user.email)).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed = hash_password(new_user.password)
    username = new_user.email.split("@")[0]
    hashed = hash_password(new_user.password)
    user = User(
        email=new_user.email, 
        username=username, 
        password_hash=hashed
    )
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return UserPublic(
        id=user.id, 
        email=user.email, 
        username=user.username
    )

@router.post("/login", response_model=Token)
def login_user(user_data: UserCreate, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == user_data.email)).first()
    
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=400, 
            detail="Incorrect email or password"
        )

    access_token = create_access_token(data={"sub": user.email})
    return Token(access_token=access_token)
@router.get("/me", response_model=UserPublic)
def read_current_user(current_user: User = Depends(get_current_user)):
    """
    Returns the currently authenticated user
    """
    return UserPublic(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username
    )

@router.get("/google/callback")
async def google_callback(
    code: str = Query(...), 
    session: Session = Depends(get_session)
):
    """
    Handles Google OAuth callback
    """
    try:
        user_email = await validate_google_token(code)
    except HTTPException as e:
        raise e
    
    # Find or create user
    user = session.exec(select(User).where(User.email == user_email)).first()
    
    if not user:
        username = user_email.split("@")[0]
        
        user = User(
            email=user_email,
            username=username,
            password_hash="google_oauth_user"
        )
        session.add(user)
        session.commit()
        session.refresh(user)

    jwt_token = create_access_token(data={"sub": user.email})
    
    return Token(
        access_token=jwt_token, 
        token_type="bearer"
    )
