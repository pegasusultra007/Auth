import jwt
import datetime
from django.conf import settings
import hashlib


def hash_password(password:str):
     return hashlib.sha256(password.encode()).hexdigest()


def generate_jwt(user_id:int):
     payload = {
          "user_id": user_id,
          "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=1)
     }
     token = jwt.encode(payload , settings.SECRET_KEY , algorithm=settings.JWT_ALGORITHM)
     return token
     