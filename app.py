from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from passlib.context import CryptContext
from Core.core import find_best_route

import jwt
from pymongo import MongoClient
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()
CORS = os.getenv("CORS", ["*"]).split(",")
METHODS = os.getenv("METHODS", ["*"]).split(",")
HEADERS = os.getenv("HEADERS", ["*"]).split(",")

app = FastAPI()
app.add_middleware(
	CORSMiddleware,
	allow_origins=CORS,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client[os.getenv("MONGO_DB", "auth_db")]
users_collection = db[os.getenv("MONGO_COLLECTION", "users")]


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


class User(BaseModel):
	username: str
	password: str


class Token(BaseModel):
	access_token: str
	token_type: str


class routing(BaseModel):
	access_token: str = Depends(oauth2_scheme)
	source: str
	destination: str


def hash_password(password: str) -> str:
	"""Hash a password for storage.

	Args:
	    password (str): The password to hash

	Returns:
	    str: The hashed password
	"""
	return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
	"""Verify a password against a hashed password.

	Args:
	    plain_password (str): The password to verify
	    hashed_password (str): The hashed password to compare against

	Returns:
	    bool: True if the password is valid, False otherwise
	"""
	return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str):
	"""Authenticate a user against the database.

	Args:
	    username (str): The username to authenticate
	    password (str): The password to authenticate

	Returns:
	    dict: The user document if the authentication is successful, False otherwise
	"""
	user = users_collection.find_one({"username": username})
	if not user or not verify_password(password, user["password"]):
		return False
	return user


def create_access_token(data: dict, expires_delta: timedelta = None):
	"""Generate an access token from a dictionary of data.

	Args:
	    data (dict): The data to encode in the token
	    expires_delta (timedelta): The time delta for which the token is valid.
	        Defaults to ACCESS_TOKEN_EXPIRE_MINUTES minutes.

	Returns:
	    str: The encoded JWT token
	"""
	to_encode = data.copy()
	expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
	to_encode.update({"exp": expire})
	encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
	return encoded_jwt


def verify_access_token(token: str):
	"""Verify an access token and return the username if valid.

	Args:
	    token (str): The token to verify

	Returns:
	    str: The username if the token is valid

	Raises:
	    HTTPException: If the token is invalid or has expired
	"""
	try:
		payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
		username: str = payload.get("sub")
		if username is None:
			raise HTTPException(status_code=401, detail="Invalid token")
		return username
	except jwt.ExpiredSignatureError:
		raise HTTPException(status_code=401, detail="Token has expired")
	except jwt.InvalidTokenError:
		raise HTTPException(status_code=401, detail="Invalid token")


@app.post("/signup")
async def signup(user: User):
	"""Create a new user.

	Args:
	    user (User): The user to create. Must contain username and password.

	Returns:
	    dict: A message indicating that the user was created successfully

	Raises:
	    HTTPException: If the username already exists
	"""
	if users_collection.find_one({"username": user.username}):
		raise HTTPException(status_code=400, detail="Username already exists")
	hashed_password = hash_password(user.password)
	users_collection.insert_one({"username": user.username, "password": hashed_password})
	return {"message": "User created successfully"}


@app.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
	"""
	Authenticate a user and return an access token.

	Args:
	    form_data (OAuth2PasswordRequestForm): The form data containing username and password.

	Returns:
	    dict: A dictionary containing the access token and token type.

	Raises:
	    HTTPException: If the authentication fails due to invalid credentials.
	"""

	user = authenticate_user(form_data.username, form_data.password)
	if not user:
		raise HTTPException(status_code=400, detail="Invalid credentials")
	access_token = create_access_token({"sub": form_data.username})
	return {"access_token": access_token, "token_type": "bearer"}


@app.post("/route")
async def routing(routing: routing, token: str = Depends(oauth2_scheme)):
	current_user = verify_access_token(token)
	user = users_collection.find_one({"username": current_user})
	if not user:
		raise HTTPException(status_code=404, detail="roule not found")

	return find_best_route(source=routing.source, destination=routing.destination, time="14:00")


@app.delete("/delete")
async def delete_user(username: str, token: str = Depends(oauth2_scheme)):
	"""
	Delete a user.

	Args:
	    username (str): The username of the user to delete.
	    token (str): The access token to verify the user's identity.

	Raises:
	    HTTPException: If the user is not authorized to delete the user, or if the user does not exist.

	Returns:
	    dict: A message indicating that the user was deleted successfully.
	"""
	current_user = verify_access_token(token)
	if current_user != username:
		raise HTTPException(status_code=403, detail="You are not authorized to delete this user")

	user = users_collection.find_one({"username": username})
	if not user:
		raise HTTPException(status_code=404, detail="User not found")

	users_collection.delete_one({"username": username})
	return {"message": "User deleted successfully"}
