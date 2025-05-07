# Genie Mentor Agent

Genie Mentor Agent is a platform designed to automate the onboarding and continuous learning of developers within an organization. By leveraging AI agents, the system aims to:

- Guide new team members through structured learning tracks
- Answer questions about internal documentation and processes
- Track user progress and knowledge gaps
- Reduce dependency on existing team members for onboarding
- Provide proactive reminders and personalized learning experiences

## Implementation Plan

For a comprehensive overview of the project, including architecture, workflows, and implementation steps, please see the [Implementation Plan](implementation-plan.md).

## Project Structure

- **frontend/**: ReactJS application for user interfaces
- **services/**: Backend microservices (FastAPI)
- **infrastructure/**: Docker and AWS configuration files
- **docs/**: Additional documentation


## Core Features

- Learning Bot for guided course completion
- Onboarding Bot for Q&A about internal documentation
- Admin dashboard for managing users and knowledgebases
- Integration with TalentLMS and document sources (Wiki, Google Drive)
- Retrieval-augmented generation (RAG) for accurate answers with citations
