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

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

if "activities" not in globals():
    activities = {}

activities.update({
    "Basketball Team": {
        "name": "Basketball Team",
        "description": "Practice shooting, passing, and game strategy with the school team.",
        "schedule": "Mondays and Thursdays at 5:00 PM",
        "participants": [],
        "category": "Sports",
    },
    "Volleyball Club": {
        "name": "Volleyball Club",
        "description": "Build teamwork and endurance through friendly matches and drills.",
        "schedule": "Tuesdays and Fridays at 4:30 PM",
        "participants": [],
        "category": "Sports",
    },
    "Drama Club": {
        "name": "Drama Club",
        "description": "Explore acting, improvisation, and stage performance in a welcoming group.",
        "schedule": "Wednesdays at 3:30 PM",
        "participants": [],
        "category": "Artistic",
    },
    "Art Studio": {
        "name": "Art Studio",
        "description": "Create paintings, sketches, and mixed-media projects with peers.",
        "schedule": "Thursdays at 4:00 PM",
        "participants": [],
        "category": "Artistic",
    },
    "Math Olympiad": {
        "name": "Math Olympiad",
        "description": "Solve advanced problem sets and compete in challenging math events.",
        "schedule": "Tuesdays at 5:00 PM",
        "participants": [],
        "category": "Intellectual",
    },
    "Debate Team": {
        "name": "Debate Team",
        "description": "Develop argumentation, research, and public speaking skills.",
        "schedule": "Fridays at 3:45 PM",
        "participants": [],
        "category": "Intellectual",
    },
})


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student is already signed up")

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/participants")
def unregister_from_activity(activity_name: str, email: str):
    """Remove a student from an activity."""
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    participants = activities[activity_name]["participants"]
    if email not in participants:
        raise HTTPException(
            status_code=404,
            detail="Student is not signed up for this activity",
        )

    activities[activity_name]["participants"] = [
        participant for participant in participants if participant != email
    ]
    return {"message": f"Unregistered {email} from {activity_name}"}
