def userEntity(item)-> dict:
    return {
        "id":str(item["_id"]),
        "first_name":item["first_name"],
        "last_name":item["last_name"],
        "phone_number":item["phone_number"],
        "username":item["username"],
        "is_admin":str2bool(str(item["is_admin"])),
        "is_superuser":str2bool(str(item["is_superuser"])),
        "is_blocked":str2bool(str(item["is_blocked"])),
        "email":item["email"],
        "password":item["password"]
    }
    
def usersEntity(entity) -> list:
    return [userEntity(item) for item in entity]


def str2bool(v):
  return v.lower() in ("True", "true", "t", "T")