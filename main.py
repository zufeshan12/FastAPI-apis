from fastapi import FastAPI,Path,Query, HTTPException
import json

# create an endpoint
app = FastAPI()

# utility function to load data from file
def load_data(path):
    with open(path,'r') as f:
        data = json.load(f)
    return data
# route home
@app.get("/")
def home():
    return {'message':"Welcome!"}

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
