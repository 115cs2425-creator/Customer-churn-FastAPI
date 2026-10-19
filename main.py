from fastapi import FastAPI,Path,HTTPException,Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel,EmailStr, Field,field_validator, model_validator,computed_field
from typing import List ,Dict,Annotated,Literal
import json


app = FastAPI()

class Patient(BaseModel):
    id:Annotated[str,Field(...,description='ID of patient',examples=['P001'])]
    name :Annotated[str,Field(max_length=50,title='Name of the patient',description='give name'
                              ,examples=['amit'])]
    city:Annotated[str,Field(...,description='City where patient living')]
    age:Annotated[int,Field(...,gt=0,lt=120,description='Age of the patient')]
    gender:Annotated[Literal['male','female','others'],Field(...,description='Gender of patient')]
    weight :Annotated[float,Field(...,gt=0,description='Weight of patient in kg')]
    height:Annotated[float,Field(...,gt=0,description='Height of patient in mtr')]


    @computed_field
    @property
    def calculate_bmi(self) -> float:
            bmi = round(self.weight/(self.height**2),2)
            return bmi
    @computed_field
    @property
    def verdict(self) -> str:
        if self.calculate_bmi <18.5:
            return 'UnderWeight'
        elif self.calculate_bmi<25:
            return 'Normal'
        elif self.calculate_bmi<30:
                return 'Normal'
        else:
             return 'Obbesse'
                
    
def load_data():
    with open('patients.json','r') as f:
        data = json.load(f)
    return data

def save_data(data):
    with open('patients.json','w') as f:
        json.dump(data,f)

@app.get("/")
def hello():
    return {'message': "Patient managment system API"}
@app.get('/about')
def about():
    return {'message': "A fully functional API to manage your patient recoreds"}

@app.get("/view")
def view(sort_by:str =Query('height'),order:str= Query('asc')):
    data = load_data()
    sort_order = True if  order =='desc'else False
    sorted_data = sorted(data.values(),key = lambda x:x.get(sort_by,0),reverse= sort_order)
    return sorted_data

@app.post('/create')
def create_patient(patient:Patient):
    data = load_data()
    if patient.id in data:
        raise HTTPException(status_code=400,detail='Patient alrady exists')

    data[patient.id] = patient.model_dump(exclude=['id'])
    save_data(data)

    return JSONResponse(status_code=201,content={'message':'patient created sucessfully'})

@app.get('/patient/{patient_id}')
def view_patient(patient_id: str = Path(...,description = 'ID of the patient in the DB',example ='P001')):
    data = load_data()
    if patient_id in data:
       return data[patient_id]
    raise HTTPException(status_code=404,detail='Patient not found')


@app.get('/sort')
def sort_patients(sort_by: str = Query(...,description = 'Sort on the basis of height,weight or bmi')
                  ,order:str= Query('asc',description = 'sort in ascending or descending ')):
    valid_fields = ['height','weight','bmi']
    if sort_by not in valid_fields:
        raise HTTPException(status_code=404,detail=f'Invalid field select from {valid_fields}')
    if order not in ['asc','desc']:
        raise HTTPException(status_code=400,detail=' inlid order')