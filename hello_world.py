from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def test():
    return {"message":"Hello World!"}

@app.get("/aboutus")
def AboutUs():
    return {"message":"I am an ML engineer fascinated by the world of GenAI."}