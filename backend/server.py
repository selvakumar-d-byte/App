from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

security = HTTPBearer()

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Models
class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: EmailStr
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

class Course(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    language: str  # "tamil" or "english"
    image_url: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class Video(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    course_id: str
    title: str
    video_url: str
    duration: int  # in seconds
    order: int

class ProgressUpdate(BaseModel):
    user_id: str
    course_id: str
    video_id: str
    watched_duration: int  # in seconds
    completed: bool = False

class UserProgress(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    course_id: str
    video_id: str
    watched_duration: int
    completed: bool
    last_watched: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class Certificate(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    course_id: str
    user_name: str
    course_name: str
    issued_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await db.users.find_one({"id": user_id}, {"_id": 0, "password": 0})
    if user is None:
        raise credentials_exception
    return User(**user)

# Auth routes
@api_router.post("/auth/register", response_model=Token)
async def register(user_create: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_create.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    hashed_password = get_password_hash(user_create.password)
    user = User(name=user_create.name, email=user_create.email)
    user_dict = user.model_dump()
    user_dict["password"] = hashed_password
    
    await db.users.insert_one(user_dict)
    
    # Create token
    access_token = create_access_token(data={"sub": user.id})
    return Token(access_token=access_token, token_type="bearer", user=user)

@api_router.post("/auth/login", response_model=Token)
async def login(user_login: UserLogin):
    user = await db.users.find_one({"email": user_login.email})
    if not user or not verify_password(user_login.password, user["password"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    user_obj = User(**{k: v for k, v in user.items() if k != "password"})
    access_token = create_access_token(data={"sub": user_obj.id})
    return Token(access_token=access_token, token_type="bearer", user=user_obj)

@api_router.get("/auth/me", response_model=User)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

# Course routes
@api_router.get("/courses", response_model=List[Course])
async def get_courses(search: Optional[str] = None, language: Optional[str] = None):
    query = {}
    if search:
        query["name"] = {"$regex": search, "$options": "i"}
    if language:
        query["language"] = language.lower()
    
    courses = await db.courses.find(query, {"_id": 0}).to_list(1000)
    return courses

@api_router.get("/courses/{course_id}", response_model=Course)
async def get_course(course_id: str):
    course = await db.courses.find_one({"id": course_id}, {"_id": 0})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@api_router.get("/courses/{course_id}/videos", response_model=List[Video])
async def get_course_videos(course_id: str):
    videos = await db.videos.find({"course_id": course_id}, {"_id": 0}).sort("order", 1).to_list(1000)
    return videos

# Progress routes
@api_router.post("/progress/update")
async def update_progress(progress: ProgressUpdate, current_user: User = Depends(get_current_user)):
    # Verify user_id matches current user
    if progress.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Update or create progress
    existing_progress = await db.progress.find_one({
        "user_id": progress.user_id,
        "course_id": progress.course_id,
        "video_id": progress.video_id
    })
    
    progress_obj = UserProgress(**progress.model_dump())
    progress_dict = progress_obj.model_dump()
    
    if existing_progress:
        await db.progress.update_one(
            {"user_id": progress.user_id, "course_id": progress.course_id, "video_id": progress.video_id},
            {"$set": progress_dict}
        )
    else:
        await db.progress.insert_one(progress_dict)
    
    return {"status": "success"}

@api_router.get("/progress/user/{user_id}/course/{course_id}")
async def get_user_course_progress(user_id: str, course_id: str, current_user: User = Depends(get_current_user)):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    progress = await db.progress.find(
        {"user_id": user_id, "course_id": course_id},
        {"_id": 0}
    ).to_list(1000)
    
    return progress

# Certificate routes
@api_router.post("/certificates/generate", response_model=Certificate)
async def generate_certificate(user_id: str, course_id: str, current_user: User = Depends(get_current_user)):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Check if certificate already exists
    existing_cert = await db.certificates.find_one(
        {"user_id": user_id, "course_id": course_id},
        {"_id": 0}
    )
    if existing_cert:
        return Certificate(**existing_cert)
    
    # Get course details
    course = await db.courses.find_one({"id": course_id}, {"_id": 0})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Create certificate
    certificate = Certificate(
        user_id=user_id,
        course_id=course_id,
        user_name=current_user.name,
        course_name=course["name"]
    )
    cert_dict = certificate.model_dump()
    await db.certificates.insert_one(cert_dict)
    
    return certificate

@api_router.get("/certificates/user/{user_id}/course/{course_id}", response_model=Optional[Certificate])
async def get_certificate(user_id: str, course_id: str, current_user: User = Depends(get_current_user)):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    certificate = await db.certificates.find_one(
        {"user_id": user_id, "course_id": course_id},
        {"_id": 0}
    )
    
    if not certificate:
        return None
    
    return Certificate(**certificate)

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()