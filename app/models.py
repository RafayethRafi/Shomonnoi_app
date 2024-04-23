from .database import Base
from sqlalchemy import Column,Integer,String,Boolean,TIMESTAMP,text,ForeignKey,DateTime
from sqlalchemy .sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime,timedelta


# Define a function to get the current time in Asia/Dhaka timezone
def get_dhaka_time():
    # Get the current UTC time
    utc_now = datetime.utcnow()

    # Define the UTC offset for Asia/Dhaka timezone (+6 hours ahead of UTC)
    dhaka_offset = timedelta(hours=6)

    # Calculate the time in Asia/Dhaka timezone by adding the offset
    dhaka_time = utc_now + dhaka_offset

    return dhaka_time


class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer,primary_key=True,index=True)
    name = Column(String,nullable=False)
    phone_no = Column(String,nullable=False)
    email = Column(String,nullable=False,unique=True)
    password = Column(String,nullable=False)
    address = Column(String)
    role = Column(String,default='user')
    created_at = Column(DateTime, default=get_dhaka_time)

    deposits = relationship('Deposits',back_populates='user')
    

class Deposits(Base):
    __tablename__ = 'deposits'

    deposit_id = Column(Integer,primary_key=True,index=True)
    user_id = Column(Integer,ForeignKey('users.user_id'))
    name = Column(String,nullable=False)
    amount = Column(Integer,nullable=False)
    extra_charges = Column(Integer,nullable=True,default=0)
    payment_month = Column(Integer,nullable=False)
    payment_year = Column(Integer,nullable=False)
    # save the time in date/month/year format
    diposit_date = Column(DateTime, default=get_dhaka_time)
    
    user = relationship('User',back_populates='deposits')


class Invitations(Base):
    __tablename__ = "invitations"

    invitation_id = Column(Integer,primary_key=True,nullable=False)
    email = Column(String,nullable=False)
    role = Column(String,nullable=False)
    admin_id = Column(Integer,ForeignKey("users.user_id",ondelete="CASCADE"),nullable=False)
    created_at = Column(DateTime, default=get_dhaka_time)
    is_registered = Column(Boolean,nullable=False,default=False)
