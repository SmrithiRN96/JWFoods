from dataclasses import dataclass
from flask_appbuilder import Model
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

"""

You can use the extra Flask-AppBuilder fields and Mixin's

AuditMixin will add automatic timestamp of created and modified by who


"""

@dataclass
class User(Model) :
	__tablename__ = 'Coefficient'
	
	id : int
	name : str
	value : float
	
	id = Column(Integer(), primary_key = True)
	name = Column(String())
	value = Column(Integer())
