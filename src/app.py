"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
from copy import deepcopy

# Default in-memory activity database
DEFAULT_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Competitive basketball team for interscholastic play",
        "schedule": "Tuesdays and Thursdays, 4:30 PM - 6:00 PM",
        "max_participants": 15,
        "participants": ["james@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Outdoor soccer team with practice and games",
        "schedule": "Mondays, Wednesdays, Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": ["alex@mergington.edu", "chris@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore painting, drawing, and various art techniques",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 16,
        "participants": ["isabella@mergington.edu"]
    },
    "Drama Club": {
        "description": "Perform in theatrical productions and develop acting skills",
        "schedule": "Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["lucas@mergington.edu", "ava@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop argumentation and public speaking skills through competitive debate",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["sophia@mergington.edu"]
    },
    "Science Club": {
        "description": "Conduct experiments and explore scientific concepts",
        "schedule": "Fridays, 3:30 PM - 4:30 PM",
        "max_participants": 14,
        "participants": ["mason@mergington.edu", "zoe@mergington.edu"]
    }
}


def create_app(activities_data=None):
    """
    Create and configure a FastAPI app instance.
    
    Args:
        activities_data: Optional dictionary of activities. Defaults to DEFAULT_ACTIVITIES.
                        Each test can provide fresh data for isolation.
    
    Returns:
        FastAPI app instance with all routes configured
    """
    if activities_data is None:
        activities_data = deepcopy(DEFAULT_ACTIVITIES)
    
    app_instance = FastAPI(
        title="Mergington High School API",
        description="API for viewing and signing up for extracurricular activities"
    )
    
    # Mount the static files directory
    app_instance.mount(
        "/static",
        StaticFiles(directory=os.path.join(Path(__file__).parent, "static")),
        name="static"
    )
    
    # ARRANGE: Store activities in the local scope for the route handlers
    activities = activities_data
    
    @app_instance.get("/")
    def root():
        """Redirect to static index page"""
        return RedirectResponse(url="/static/index.html")
    
    @app_instance.get("/activities")
    def get_activities():
        """Get all activities with their participants"""
        return activities
    
    @app_instance.post("/activities/{activity_name}/signup")
    def signup_for_activity(activity_name: str, email: str):
        """
        ACT: Sign up a student for an activity
        
        Args:
            activity_name: Name of the activity
            email: Student email address
            
        Returns:
            Success message with signup confirmation
        """
        # ARRANGE: Validate activity exists
        if activity_name not in activities:
            raise HTTPException(status_code=404, detail="Activity not found")
        
        # ARRANGE: Get the specific activity
        activity = activities[activity_name]
        
        # ARRANGE: Validate student is not already signed up
        if email in activity["participants"]:
            raise HTTPException(status_code=400, detail="Student is already signed up for this activity")
        
        # ACT: Add student
        activity["participants"].append(email)
        return {"message": f"Signed up {email} for {activity_name}"}
    
    @app_instance.delete("/activities/{activity_name}/signup")
    def unregister_for_activity(activity_name: str, email: str):
        """
        ACT: Remove a student from an activity
        
        Args:
            activity_name: Name of the activity
            email: Student email address
            
        Returns:
            Success message with unregister confirmation
        """
        # ARRANGE: Validate activity exists
        if activity_name not in activities:
            raise HTTPException(status_code=404, detail="Activity not found")
        
        # ARRANGE: Get the activity
        activity = activities[activity_name]
        
        # ARRANGE: Validate student is signed up
        if email not in activity["participants"]:
            raise HTTPException(status_code=404, detail="Student is not signed up for this activity")
        
        # ACT: Remove student
        activity["participants"].remove(email)
        return {"message": f"Unregistered {email} from {activity_name}"}
    
    return app_instance


# Create the default app instance for production/standalone use
app = create_app()
