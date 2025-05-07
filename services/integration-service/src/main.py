"""
Integration Service - Main Entry Point
This service integrates with external systems like TalentLMS and Slack for the Genie Mentor Agent platform.
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Integration Service",
    description="External integrations for Genie Mentor Agent",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Genie Mentor Agent Integration Service API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# TalentLMS integration endpoints will be implemented here
# Slack integration endpoints will be implemented here
# Webhook endpoints will be implemented here

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8004)
