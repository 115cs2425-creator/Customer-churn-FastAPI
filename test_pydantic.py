
import re

from pydantic import BaseModel,EmailStr, Field,field_validator, model_validator,computed_field
from typing import List ,Dict,Annotated

class Patient(BaseModel):
    name :Annotated[str,Field(max_length=50,title='Name of patient',description='give name'
                              ,examples=['amit'])]
    email:EmailStr
    age: int
    weight :float=Field(gt=0)
    height:float
    married :bool=False
    allergies:List[str]
    contact:Dict[str,str]




    @computed_field
    @property
    def calculate_bmi(self) -> float:
        bmi = round(self.weight/(self.height**2),2)
        return bmi



    @model_validator(mode='after')
    def validate_emergency_contact(cls,model):
        if model.age>60 and 'emergency' not in model.contact:
            raise ValueError('Patients older than 60 must have an emergency contact')
        return model



    @field_validator('email')
    @classmethod
    def email_validator(cls,value):
        valid_domains = ['hdfc.com','icici.com']
        domain_name = value.split('@')[-1]
        if domain_name not in valid_domains:
            raise ValueError('Not a valid domain')
        return value

def insert_patient_data(patient:Patient):
    print(patient.name)
    print(patient.age)
    print('inserted')


patient_info ={'name':'nitish', 'email':'abc@hdfc.com' ,'married':True, 'age':45,'weight':65.5,
                'height':1.72, 'allergies':['pollen','dust']
                ,'contact':{'phone':'25843421'}}
patient1 = Patient(**patient_info)

insert_patient_data(patient1)


def update_patient_data(patient:Patient):
    print(patient.name)
    print(patient.age)
    print('BMI',patient.calculate_bmi)
    print('updated')

update_patient_data(patient1)
    