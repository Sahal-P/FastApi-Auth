from fastapi import APIRouter,Depends
from models.user import Users
from config.db import connection
from bson import ObjectId
from bson.raw_bson import RawBSONDocument
from fastapi.responses import JSONResponse

from config.db import get_connection,MongoClient
from schemas.user import userEntity, usersEntity

user = APIRouter()


@user.get('/sockets/{id}')
async def find_all_users():
    return JSONResponse(status_code=HTTP_200_OK,detail="connected")

@user.get('/')
async def find_all_users(db:MongoClient = Depends(get_connection)):
    return usersEntity(db['Users'].find())

@user.post('/')
async def create_user(user:Users,conn:MongoClient = Depends(get_connection)):
    print(user)
    a = conn['Users'].insert_one(dict(user))
    print(a)
    return  usersEntity(conn['Users'].find())
        #  b = conn['Users'].find()

@user.put('/{id}')
async def update_user(id, user:Users,conn:MongoClient = Depends(get_connection)):
    a = conn["Users"].find_one_and_update({"_id": ObjectId(id)},{"$set":dict(user)})

    return userEntity(conn["Users"].find_one({"_id":ObjectId(id)}))

@user.delete('/{id}')
async def delete_user(id,conn:MongoClient=Depends(get_connection)):
    return userEntity(conn['Users'].find_one_and_delete({"_id":ObjectId(id)}))


