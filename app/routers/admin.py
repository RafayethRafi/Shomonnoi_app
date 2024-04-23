from .. import models, schemas , oauth2,send_email
from fastapi import Response,status,HTTPException,Depends,APIRouter
from sqlalchemy.orm import Session
from ..database import get_db
from typing import List
from datetime import datetime,timedelta

router = APIRouter(
    prefix= "/admins",
    tags=['Admins']
)


    

#an endpoint to find the users that are registered under an admin
@router.get("/registered_users/", status_code=status.HTTP_200_OK,response_model=List[schemas.UserInDB])
def get_registered_users(db: Session = Depends(get_db),current_user:int=Depends(oauth2.get_current_user)) -> Response:

    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only Admins can view registered users")
    
    registered_users = db.query(models.User).all()

    if not registered_users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No users registered.")
    
    return registered_users



@router.post("/invite_users/", status_code=status.HTTP_200_OK)
async def invite_users(invitations : List[schemas.InvitationBase],db: Session = Depends(get_db),current_user:int=Depends(oauth2.get_current_user)) -> Response:

    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only Admins can invite users")
    
    try:
        for invitation in invitations:
            new_invitation = models.Invitations(admin_id = current_user.user_id,**invitation.model_dump())
            try:
                db.add(new_invitation)
                db.commit()
                db.refresh(new_invitation)
            except:
                db.rollback()
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Error: Invitation not created")

            send_email.send_invitation_email(invitation.email,invitation.role)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Error: {e}")
        
    
    return f"Invited {len(invitations)} users"


# Find the emails that the admin invited but not registered yet
@router.get("/pending_invitations/", status_code=status.HTTP_200_OK,response_model=List[schemas.InvitationBase])
def get_pending_invitations(db: Session = Depends(get_db),current_user:int=Depends(oauth2.get_current_user)) -> Response:

    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only Admins can view pending invitations")
    
    pending_invitations = db.query(models.Invitations).filter(models.Invitations.is_registered == False).all()

    if not pending_invitations:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No pending invitations")
    
    return pending_invitations




# create an endpoint to deposit money and save that in the database
@router.post("/deposit/", status_code=status.HTTP_201_CREATED)
def deposit(deposit_info: schemas.DepositCreate,db:Session=Depends(get_db),current_user:int=Depends(oauth2.get_current_user)):
    
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only Admins can deposit money")
    
    deposit_info = deposit_info.model_dump()

    #get user from deposit_info.name
    user = db.query(models.User).filter(models.User.name == deposit_info['name']).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"{deposit_info['name']} not found.")
    
    #create a new deposit
    new_deposit = models.Deposits(user_id = user.user_id,**deposit_info)

    try:
        db.add(new_deposit)
        db.commit()
        db.refresh(new_deposit)
    except:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Error: Deposit not created")

    return new_deposit


#edit the deposit information
@router.put("/deposit/{deposit_id}",status_code=status.HTTP_200_OK)
def edit_deposit(deposit_id:int,deposit_info:schemas.DepositUpdate,db:Session=Depends(get_db),current_user:int=Depends(oauth2.get_current_user)) -> Response:
    
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only Admins can edit deposits")
    
    deposit_info = deposit_info.model_dump()

    #get the deposit
    deposit = db.query(models.Deposits).filter(models.Deposits.deposit_id == deposit_id).first()

    if not deposit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Deposit not found.")
    
    #get the user if the deposit_info has name
    if deposit_info['name'] is not None:
        user = db.query(models.User).filter(models.User.name == deposit_info['name']).first()

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"{deposit_info['name']} not found.")
        
        deposit_info['user_id'] = user.user_id
        # del deposit_info['name']
    #update the deposit
    for key,value in deposit_info.items():
        if value is not None:
            setattr(deposit,key,value)
    
    try:
        db.commit()
        db.refresh(deposit)
    except:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Error: Deposit not updated")

    return {"detail":"Deposit updated successfully"}


# get the last 50 deposits
@router.get("/deposits/",status_code=status.HTTP_200_OK,response_model=List[schemas.DepositInDB])
def get_deposits(db:Session=Depends(get_db),current_user:int=Depends(oauth2.get_current_user)) -> Response:

    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only Admins can view deposits")
    
    deposits = db.query(models.Deposits).order_by(models.Deposits.deposit_id.desc()).limit(50).all()

    if not deposits:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No deposits found.")
    
    return deposits



def get_dhaka_time():
    # Get the current UTC time
    utc_now = datetime.utcnow()

    # Define the UTC offset for Asia/Dhaka timezone (+6 hours ahead of UTC)
    dhaka_offset = timedelta(hours=6)

    # Calculate the time in Asia/Dhaka timezone by adding the offset
    dhaka_time = utc_now + dhaka_offset

    return dhaka_time

# create an endpoint to find the users that has been deposited at this monthy and this year
@router.get("/month_deposits/{month}/{year}",status_code=status.HTTP_200_OK,response_model=List[schemas.DepositInDB])
def month_deposits(month:int,year:int,db:Session=Depends(get_db),current_user:int=Depends(oauth2.get_current_user)) -> Response:

    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only Admins can view deposits")
    
    deposits = db.query(models.Deposits).filter(models.Deposits.payment_month == month,models.Deposits.payment_year == year).all()

    if not deposits:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No deposits found.")
    
    return deposits


#create an endpoint to find the users that has not been deposited at this month of this year
@router.get("/not_deposited/{month}/{year}",status_code=status.HTTP_200_OK,response_model=List[schemas.UserInDB])
def not_deposited(month:int,year:int,db:Session=Depends(get_db),current_user:int=Depends(oauth2.get_current_user)) -> Response:

    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only Admins can view deposits")
    
    #get the users that has not been deposited at this month
    users = db.query(models.User).filter(~models.User.user_id.in_(db.query(models.Deposits.user_id).filter(models.Deposits.payment_month == month,models.Deposits.payment_year == year))).all()

    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No users found.")
    
    return users