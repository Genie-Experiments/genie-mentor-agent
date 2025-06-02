import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db.database import Base, engine
from .onboarding_team.team import initialize_agent, shutdown_agent
from .routes import route
load_dotenv(override=True)

app = FastAPI(
    title='Genie Mentor Agent Swagger',
    description='Agent orchestration service for Genie Mentor Agent',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(route.router)

@app.on_event('startup')
async def on_startup():
    Base.metadata.create_all(bind=engine)
    await initialize_agent()  

@app.on_event('shutdown')
async def on_shutdown():
    await shutdown_agent()  

@app.get('/')
async def root():
    return {'message': 'Genie Mentor Agent Service API'}

@app.get('/health')
async def health_check():
    return {'status': 'healthy'}

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8001)