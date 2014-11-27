import model.base
from model.base import session_scope, Session
import os
from model.user import User
from model.appointment import Appointment

def create_data():
    with session_scope() as session:
        if session.query(User).filter(User.username == "admin").count() != 0:
            return

        username = "admin"
        password = "adminpw"
        fullname = "admin"
        user = User(username, password, fullname)

        assert(user.checkPassword("adminpw"))

        session.add(user)

#if os.path.isfile('test.db'):
#    os.remove('test.db')
model.base.create_engine('mysql+pymysql://admin:7NgM6Tx2JhaaJe@cs3398.coa3qiflo7sn.us-west-2.rds.amazonaws.com/cs3398', echo=True)
#model.base.create_engine('sqlite:///test.db?check_same_thread=False', echo=True)
model.base.create_schema()
create_data()
