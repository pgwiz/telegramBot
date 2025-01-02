from sqlalchemy import create_engine, Column, Integer, String, Date, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, unique=True)
    role = Column(Enum('admin', 'premium', 'group', 'normal', name='user_roles'))
    category = Column(String)
    subscription_end = Column(Date)

class File(Base):
    __tablename__ = 'files'
    
    id = Column(Integer, primary_key=True)
    category = Column(String)
    file_id = Column(String, unique=True)
    uploaded_by = Column(String)
    upload_date = Column(Date)

class PromoCode(Base):
    __tablename__ = 'promo_codes'
    
    code = Column(String, primary_key=True)
    validity_days = Column(Integer)
    created_by = Column(String)
    expiry_date = Column(Date)

def init_db():
    engine = create_engine('sqlite:///bot.db')
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()