from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import os

app = FastAPI(title="Selenium MCP Profile API")

# Setup CORS to allow Vite UI to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROFILES_FILE = "profiles.json"

class Profile(BaseModel):
    id: str
    name: str
    headless: bool = True
    disable_images: bool = False
    user_data_dir: Optional[str] = None
    user_agent: Optional[str] = None
    proxy: Optional[str] = None

def load_profiles() -> List[dict]:
    if not os.path.exists(PROFILES_FILE):
        return []
    try:
        with open(PROFILES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_profiles(profiles: List[dict]):
    with open(PROFILES_FILE, 'w', encoding='utf-8') as f:
        json.dump(profiles, f, indent=4)

@app.get("/profiles", response_model=List[Profile])
def get_profiles():
    return load_profiles()

@app.post("/profiles", response_model=Profile)
def create_profile(profile: Profile):
    profiles = load_profiles()
    if any(p['id'] == profile.id for p in profiles):
        raise HTTPException(status_code=400, detail="Profile ID already exists")
    profiles.append(profile.model_dump())
    save_profiles(profiles)
    return profile

@app.put("/profiles/{profile_id}", response_model=Profile)
def update_profile(profile_id: str, updated_profile: Profile):
    profiles = load_profiles()
    for i, p in enumerate(profiles):
        if p['id'] == profile_id:
            profiles[i] = updated_profile.model_dump()
            save_profiles(profiles)
            return updated_profile
    raise HTTPException(status_code=404, detail="Profile not found")

@app.delete("/profiles/{profile_id}")
def delete_profile(profile_id: str):
    profiles = load_profiles()
    profiles_filtered = [p for p in profiles if p['id'] != profile_id]
    if len(profiles) == len(profiles_filtered):
        raise HTTPException(status_code=404, detail="Profile not found")
    save_profiles(profiles_filtered)
    return {"message": "Profile deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
