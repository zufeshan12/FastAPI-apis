from fastapi import FastAPI,Path,Query, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field,computed_field,EmailStr
from typing import Literal,Annotated,Optional
import json

# create an endpoint
app = FastAPI()
# create new datatype for address
class Address(BaseModel):
    address_line1: Annotated[str,Field(...,description="Address line 1")]
    address_line2: Annotated[str,Field(description="Address line 2")]
    city: Annotated[str,Field(...,description="City",max_length=100)]
    country: Annotated[str,Field(...,description="Country",max_length=100)]
    zipcode : Annotated[str,Field(...,description="Zipcode",example="90210",max_length=5)]

# create Patient schema
class Patient(BaseModel):
    id: Annotated[str,Field(...,description="Unique Identifier of the patient",examples=["P999"])]
    name: Annotated[str,Field(...,description="Name of the patient")]
    gender: Annotated[Literal["Male","Female","Other"],Field(...,description="Gender of the patient")]
    age: Annotated[int,Field(...,gt=0,le=120,description="Age of the patient")]
    height: Annotated[float,Field(...,gt=0,description="Height of the patient in meters")]
    weight: Annotated[float,Field(...,gt=0,description="Weight of the patient in kilograms")]
    email: Annotated[EmailStr,Field(description="Email address of the patient")]
    address: Annotated[Address,Field(...,description="Primary Address of the patient")]

    @computed_field
    def bmi(self) -> float:
        ht = self.height
        wt = self.weight
        return round(wt/(ht**2),2)
    
    @computed_field
    def verdict(self) -> Literal["normal","underweight","overweight","obese"]:
        if self.bmi < 18.5:
            return "underweight"
        elif 18.5 <= self.bmi <= 24.9:
            return "normal" 
        elif 25.0 <= self.bmi <= 29.9:
            return "overweight"
        elif self.bmi >= 30.0:
            return "obese"

# utility function to load data from file
def load_data(path):
    with open(path,'r') as f:
        data = json.load(f)
    return data

# utility function to save patient records to file
def save_data(data):
    with open('patient_data.json','w') as f:
        json.dump(data,f)

# route home
@app.get("/")
def home():
    return {'message':"Welcome to the Hospital Management System!"}

# route view
@app.get('/view')
def view():
    data = load_data("patient_data.json")
    return data

# route view with path parameters
@app.get('/patient/{patient_id}')
def view_patient(patient_id:str = Path(...,description="Id of the patient",example="P999")):
    data = load_data("patient_data.json")
    if patient_id in data:
        return data[patient_id]
    else:
        raise HTTPException(status_code=404,detail="Patient doesn't exist")

# route to sort by fields and order results
@app.get('/sort')
def sort_result(sortby:str = Query(...,description="sort by height,weight or age"),order:str = Query(default='asc',description="sort the records in asc or desc order")):
    sort_fields = ['age','height','weight']
    if sortby not in sort_fields:
        raise HTTPException(status_code=403,detail="Unknown value for sort by")
    
    if order not in ['asc','desc']:
        raise HTTPException(status_code=403,detail="Unknown value for order")
    
    sort_order = True if order=='desc' else False

    data = load_data('patient_data.json')
    result = sorted(data.values(),key = lambda x:x.get(sortby,0),reverse=sort_order)

    return result

@app.post("/create")
def create_patient(patient:Patient):
    data = load_data('patient_data.json')

    # check for existing patient
    if patient.id in data:
        raise HTTPException(status_code=400,detail="Patient record already exists")
    
    # create new patient
    data[patient.id] = patient.model_dump(exclude=["id"])

    # save data to file
    save_data(data)

    # display success message
    return JSONResponse(content="Patient record created successfully.",status_code=200)

    

