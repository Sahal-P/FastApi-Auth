from fastapi import APIRouter, Depends, Body, Request
from models import user
from pydantic import EmailStr
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from bson import ObjectId
from config.db import MongoClient, get_connection
from schemas.user import userEntity, usersEntity
from starlette.exceptions import HTTPException
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY, HTTP_201_CREATED, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_200_OK, HTTP_401_UNAUTHORIZED
from typing import Optional
from routes.jwt import JWTAuthenicateHandler
import datetime

auth = APIRouter()


@auth.post("/register")
async def UserRegisterAPIView(
    conn: MongoClient = Depends(get_connection), userDetails: user.Users = Body(...)
) -> JSONResponse:
    user_dict = jsonable_encoder(userDetails)
    await checkNameEmail(
        conn,
        email=user_dict["email"],
        name=user_dict["username"],
        phone=user_dict["phone_number"],
    )
    saveUser = await UserRegister(conn, user_dict)
    return saveUser

async def UserRegister(conn: MongoClient, userDetails) -> JSONResponse:
    authUser = JWTAuthenicateHandler()

    hashPassword = authUser.ecodePassword(user["password"])
    # check = authUser.checkPassword('12345',hashPassword)
    userDetails["password"] = hashPassword
    newUser = conn["Users"].insert_one(userDetails)
    try:
        newUser = await getSingleUser(conn, phone=userDetails["phone_number"])
        response = jsonable_encoder(userEntity(newUser))
        
        return JSONResponse(status_code=HTTP_201_CREATED, content=response)
    
    except Exception as err:
        
        return JSONResponse(status_code=HTTP_500_INTERNAL_SERVER_ERROR, content={'error':'We faced unexpected error.' , 'message': err})

async def checkNameEmail(
    conn: MongoClient,
    name: Optional[str] = None,
    email: Optional[EmailStr] = None,
    phone: Optional[str] = None,
) -> None:
    if name:
        userByName = await getSingleUser(conn, name=name)
        if userByName:
            raise HTTPException(
                status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                detail="User with this username already Exits.",
            )
    if email:
        userByEmail = await getSingleUser(conn, email=email)
        if userByEmail:
            raise HTTPException(
                status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                detail="User with this email already Exits.",
            )
    if phone:
        userByPhone = await getSingleUser(conn, phone=phone)
        if userByPhone:
            raise HTTPException(
                status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                detail="User with this phone number already Exits.",
            )


async def getSingleUser(
    conn: MongoClient, name: str = "", email: str = "", phone: str = ""
) -> dict:
    if email:
        dbUser = conn["Users"].find_one({"email": email})
        if dbUser:
            return dbUser
    if name:
        dbUser = conn["Users"].find_one({"username": name})
        if dbUser:
            return dbUser
    if phone:
        dbUser = conn["Users"].find_one({"phone_number": phone})
        if dbUser:
            return dbUser

@auth.post("/login")
async def UserLoginAPIView(conn: MongoClient = Depends(get_connection), details: user.UserLogin = Body(...)) -> JSONResponse:
    User = jsonable_encoder(details)
    loginUser = JWTAuthenicateHandler()
    
    getUser = await getSingleUser(conn, email=User["email"])
    
    userId = jsonable_encoder(userEntity(getUser))
    
    if getUser:
        if loginUser.checkPassword(User["password"],getUser["password"]):
            AccessToken = loginUser.createAccessToken(userId["id"])
            RefreshToken = loginUser.createRefreshToken(userId["id"])
            
            await saveUserToken(conn, token=RefreshToken, userId=userId["id"])
            response = JSONResponse(status_code=HTTP_200_OK ,content={"token":AccessToken})
            response.set_cookie(
				key="access_token",
				value=AccessToken,
				httponly=True
			)
            response.set_cookie(
				key="refresh_token",
				value=RefreshToken,
				httponly=True
			)
            return response
        
    return JSONResponse(status_code=HTTP_401_UNAUTHORIZED, content="unauthenticated")

async def saveUserToken(conn: MongoClient, token: str="", userId: str="") -> None:
    time = datetime.datetime.utcnow() + datetime.timedelta(days=7)
    userToken = user.UserToken(user_id=userId, token=token, created_at=time)
    # userToken.userId = userId
    # userToken.token = token
    saveToken = conn["UserToken"].insert_one(dict(userToken))
    	
@auth.post("/refresh")
async def RefreshTokenAPIView(request: Request,conn:MongoClient = Depends(get_connection)):
    try:
        token = request.cookies.get('refresh_token')
        authHandle = JWTAuthenicateHandler()
        id = authHandle.decodeRefreshToken(token)
        await checkRefreshToken(conn, token=token, id=id)
        AccessToken = authHandle.createAccessToken(id)
        
        response = JSONResponse(status_code=HTTP_201_CREATED, content={"token":AccessToken})
        response.set_cookie(
				key="access_token",
				value=AccessToken,
				httponly=True
			)
        return response
        
    except:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="unauthenticated")
    
    
async def checkRefreshToken(conn:MongoClient, token: str=None, id: str=None) -> None:
    time = datetime.datetime.now(tz=datetime.timezone.utc)
    
    check = list(conn["UserToken"].find({"token":token,"user_id":id, "created_at":{"$gt":time}}))
    if not check:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="unauthenticated")
    
    