from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, Field
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
import uuid
import motor.motor_asyncio

# Initialize FastAPI app
app = FastAPI()

# OAuth2 Password Bearer for authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# MongoDB setup
client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")  # Replace with your MongoDB URI
db = client["user_service"]
users_collection = db["users"]
products_collection = db["products"]


# Helper functions for password hashing
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


# Pydantic models for data validation
class User(BaseModel):
    id: str = Field(default=None)  # Add id field to the model
    name: str
    email: str
    password: str

    class Config:
        orm_mode = True


class UserInDB(User):
    hashed_password: str


class Product(BaseModel):
    name: str
    description: str
    user_id: str  # Foreign key to the user


# Helper function to simulate getting user by email
async def get_user_by_email(email: str):
    return await users_collection.find_one({"email": email})


async def create_access_token(data: dict):
    return str(uuid.uuid4())  # Simulate a JWT for simplicity


# Endpoints
@app.post("/register", response_model=User)
async def register_user(user: User):
    existing_user = await get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    new_user = {
        "name": user.name,
        "email": user.email,
        "hashed_password": hashed_password
    }

    # Insert new user into MongoDB
    result = await users_collection.insert_one(new_user)

    # Fetch the inserted user with the id
    inserted_user = await users_collection.find_one({"_id": result.inserted_id})

    # Return user with the id
    return User(id=str(inserted_user["_id"]), name=inserted_user["name"], email=inserted_user["email"],
                password=user.password)


class LoginRequest(BaseModel):
    email: str
    password: str


@app.post("/token")
async def login_for_access_token(login_request: LoginRequest):
    # Get the user by email (ensure this is awaited)
    user = await get_user_by_email(login_request.email)

    # If user doesn't exist or password doesn't match, raise an error
    if not user or not verify_password(login_request.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Generate the access token (ensure it's awaited if needed)
    access_token = create_access_token(data={"sub": login_request.email})

    # Return the access token
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/create-product", response_model=Product)
async def create_product(product: Product, token: str = Depends(oauth2_scheme)):
    user = await get_user_by_email(token)  # Retrieve user by token
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    new_product = {
        "name": product.name,
        "description": product.description,
        "user_id": user["email"]
    }

    result = await products_collection.insert_one(new_product)
    product.id = str(result.inserted_id)
    return product
