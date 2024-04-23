from fastapi import APIRouter,Depends,status,HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import database , schemas,models,utils,oauth2


router = APIRouter(tags=['Authentication'])

@router.post('/login',response_model=schemas.Token)
async def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    #user_credentials will return only usename and password
    
    # user = db.query(models.User).filter(models.User.email == user_credentials.email).first()

    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
    
    if not utils.verify(user_credentials.password,user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials") 

    access_token = oauth2.create_access_token(data = {"user_id" : user.user_id})


    return {"access_token" : access_token, "token_type":"bearer"}



@router.put('/password_reset/{email_special_string}',status_code=status.HTTP_200_OK)
def password_reset(email_special_string:str,password:schemas.PassReset,db: Session = Depends(database.get_db)):


    
    email = f"{email_special_string.split('#%#%')[3]}@{email_special_string.split('#%#%')[1]}"
    user_id = int(email_special_string.split('#%#%')[2])


    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if user.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    
    hashed_password = utils.hash(**password.model_dump())
    user.password = hashed_password
    try:
        db.commit()
        db.refresh(user)
    except:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Error: Password not updated")
    

    return {"detail":"Password updated successfully"}
