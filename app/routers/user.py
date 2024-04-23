from .. import models, schemas , utils,oauth2,send_email
from fastapi import Response,status,HTTPException,Depends,APIRouter
from sqlalchemy.orm import Session
from ..database import get_db
from typing import List

router = APIRouter(
    prefix= "/users",
    tags=['Users']
)

@router.post("/register_user/{email}_{role}",status_code=status.HTTP_201_CREATED,response_model=schemas.UserInDB)
def create_user(email:str,role:str,user:schemas.UserCreate, db: Session = Depends(get_db)):

    hashed_password = utils.hash(user.password)
    user.password = hashed_password

    if db.query(models.User).filter(models.User.email == email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"{email} already registered")
    
    
    invitation_query =  db.query(models.Invitations).filter(models.Invitations.email == email).first()


    if not invitation_query:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"{email} not invited")
    elif invitation_query.is_registered == True:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"{email} already registered")
    elif invitation_query.role != role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Role does not match")
    
    
    new_user = models.User(role=role,**user.model_dump()) 

    if(new_user.email != email):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Email does not match")

    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Error: User not created")

    #update invitation is_registered to True
    invitation_query.is_registered = True
    try:
        db.commit()
        db.refresh(invitation_query)
    except:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Error: Invitation not updated")

    return new_user



#forgot password and recovery
@router.post("/forgot_password/", status_code=status.HTTP_200_OK)
def forgot_password(data:schemas.ForgotPassword,db: Session = Depends(get_db)) -> Response:

    user = db.query(models.User).filter(models.User.email == data.email).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"{data.email} not registered")

    send_email.send_pass_recovery_email(user.user_id,data.email)

    return f"Recovery email sent to {data.email}"



# create an endpoint to see if the user is deposited for a selected month or year
@router.get("/user_deposited/{month}/{year}", status_code=status.HTTP_200_OK)
def user_deposited(month:int,year:int,db: Session = Depends(get_db),current_user:int=Depends(oauth2.get_current_user)) -> Response:

    depopsit_info = db.query(models.Deposits).filter(models.Deposits.payment_month==month,models.Deposits.payment_year==year,models.Deposits.user_id==current_user.user_id).first()

    if not depopsit_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No deposit found for {month}/{year}")
    
    return depopsit_info