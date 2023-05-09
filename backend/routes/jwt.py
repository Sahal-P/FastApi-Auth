import jwt, os, datetime
from typing import Dict, Union, Any
from pathlib import Path
from dotenv import load_dotenv
import bcrypt
from starlette.exceptions import HTTPException
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY, HTTP_201_CREATED, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_200_OK, HTTP_401_UNAUTHORIZED



dotEnvPath = Path(".env")
load_dotenv(dotenv_path=dotEnvPath)


class JWTAuthenicateHandler:
    def __init__(self) -> None:
        self.jwt_secret_a = os.getenv("JWT_ACCESS_SECRET")
        self.jwt_secret_r = os.getenv("JWT_REFRESH_SECRET")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM")

        # self.hasher = CryptContext(schemes=['bcrypt'])

    def authenticate(self):
        return self.jwt_algorithm

    def ecodePassword(self, password):
        hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        return hash

    def checkPassword(self, password, hash1):
        check = bcrypt.checkpw(password.encode("utf-8"), hash1)
        return check
    
    def createAccessToken(self, id: str) -> Dict[str, str]:
        return jwt.encode(
            {
                "user_id": id,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=30),
                "iat": datetime.datetime.utcnow(),
            },
            self.jwt_secret_a,
            algorithm=self.jwt_algorithm,
        )

    def decodeAccessToken(self,token:str) -> Dict[str,str]:
        try:
            payload = jwt.decode(token, self.jwt_secret_a, algorithms=self.jwt_algorithm)

            return payload["user_id"]
        except Exception as e:
            print(e)
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED,detail="unauthenticated")

    def decodeRefreshToken(self,token):
        try:
            payload = jwt.decode(token, self.jwt_secret_r, algorithms=self.jwt_algorithm)

            return payload["user_id"]
        except Exception as e:
            print(e)
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED,detail="unauthenticated")

    def createRefreshToken(self,id):
        return jwt.encode(
            {
                "user_id": id,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7),
                "iat": datetime.datetime.utcnow(),
            },
            self.jwt_secret_r,
            algorithm=self.jwt_algorithm,
        )

    def getUser(self,token):
        id = decodeAccessToken(self,token)
        try:
            user = UserAccount.objects.get(pk=id)
            return user
        except:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED,detail="unauthenticated")
