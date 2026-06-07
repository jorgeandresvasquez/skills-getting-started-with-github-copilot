"""
Pytest configuration and shared fixtures for FastAPI tests.

Uses the AAA (Arrange-Act-Assert) pattern for all tests.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi import HTTPException
import os
from pathlib import Path


@pytest.fixture
def app():
    """
    Fixture: Create a fresh FastAPI app instance for testing.
    
    This fixture creates a new app with the same structure as the main app
    but with fresh in-memory data for each test to ensure isolation.
    """
    test_app = FastAPI(
        title="Mergington High School API - Test",
        description="API for viewing and signing up for extracurricular activities"
    )

    # Mount static files
    static_dir = Path(__file__).parent.parent / "src" / "static"
    if static_dir.exists():
        test_app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    # In-memory activity database - fresh for each test
    activities = {
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
            "description": "Competitive basketball team for students interested in competitive sports",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn and practice tennis skills on the courts",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["alex@mergington.edu", "jessica@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in theatrical productions and develop acting skills",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["anna@mergington.edu", "lucas@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and sculpture techniques",
            "schedule": "Mondays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["isabella@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop argumentation and public speaking skills through competitive debate",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 14,
            "participants": ["noah@mergington.edu", "ava@mergington.edu"]
        },
        "Math Club": {
            "description": "Challenge yourself with advanced mathematics and problem-solving",
            "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
            "max_participants": 18,
            "participants": ["ethan@mergington.edu", "mia@mergington.edu"]
        }
    }

    # Define endpoints
    @test_app.get("/")
    def root():
        return RedirectResponse(url="/static/index.html")

    @test_app.get("/activities")
    def get_activities():
        return activities

    @test_app.post("/activities/{activity_name}/signup")
    def signup_for_activity(activity_name: str, email: str):
        """Sign up a student for an activity"""
        if activity_name not in activities:
            raise HTTPException(status_code=404, detail="Activity not found")
        
        activity = activities[activity_name]
        
        if email in activity["participants"]:
            raise HTTPException(status_code=400, detail="Student already signed up")
        
        activity["participants"].append(email)
        return {"message": f"Signed up {email} for {activity_name}"}

    @test_app.delete("/activities/{activity_name}/participants/{email}")
    def unregister_from_activity(activity_name: str, email: str):
        """Unregister a student from an activity"""
        if activity_name not in activities:
            raise HTTPException(status_code=404, detail="Activity not found")
        
        activity = activities[activity_name]
        
        if email not in activity["participants"]:
            raise HTTPException(status_code=400, detail="Student not signed up for this activity")
        
        activity["participants"].remove(email)
        return {"message": f"Unregistered {email} from {activity_name}"}

    return test_app


@pytest.fixture
def client(app):
    """
    Fixture: Create a TestClient for making HTTP requests to the test app.
    
    The TestClient wraps FastAPI's async routes and provides a synchronous
    interface for testing endpoints.
    """
    return TestClient(app)


@pytest.fixture
def empty_app():
    """
    Fixture: Create a FastAPI app with empty activities for testing edge cases.
    
    Useful for testing behavior with no pre-populated activities.
    """
    test_app = FastAPI(title="Mergington High School API - Empty Test")
    
    # Mount static files
    static_dir = Path(__file__).parent.parent / "src" / "static"
    if static_dir.exists():
        test_app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    # Empty activities database
    activities = {}

    @test_app.get("/")
    def root():
        return RedirectResponse(url="/static/index.html")

    @test_app.get("/activities")
    def get_activities():
        return activities

    @test_app.post("/activities/{activity_name}/signup")
    def signup_for_activity(activity_name: str, email: str):
        if activity_name not in activities:
            raise HTTPException(status_code=404, detail="Activity not found")
        
        activity = activities[activity_name]
        
        if email in activity["participants"]:
            raise HTTPException(status_code=400, detail="Student already signed up")
        
        activity["participants"].append(email)
        return {"message": f"Signed up {email} for {activity_name}"}

    @test_app.delete("/activities/{activity_name}/participants/{email}")
    def unregister_from_activity(activity_name: str, email: str):
        if activity_name not in activities:
            raise HTTPException(status_code=404, detail="Activity not found")
        
        activity = activities[activity_name]
        
        if email not in activity["participants"]:
            raise HTTPException(status_code=400, detail="Student not signed up for this activity")
        
        activity["participants"].remove(email)
        return {"message": f"Unregistered {email} from {activity_name}"}

    return test_app


@pytest.fixture
def empty_client(empty_app):
    """
    Fixture: Create a TestClient for the empty app.
    """
    return TestClient(empty_app)
