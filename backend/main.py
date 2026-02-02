from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from database import engine, Base, SessionLocal
from models import User
from auth import get_password_hash

from routers import auth, admin, vendor, user

# Create database tables
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup: Create default admin user
    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(User.email == "admin@admin.com").first()
        if not admin_user:
            admin_user = User(
                name="Admin",
                email="admin@admin.com",
                password_hash=get_password_hash("admin123"),
                role="admin"
            )
            db.add(admin_user)
            db.commit()
            # Only log in debug mode, don't print credentials
            if os.environ.get("DEBUG", "false").lower() == "true":
                print("✓ Default admin user created")
    finally:
        db.close()
    
    yield  # Application runs here
    
    # Shutdown: cleanup if needed
    pass


app = FastAPI(
    title="Event Management System",
    description="A full-stack event management application",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware - load origins from environment
cors_origins_str = os.environ.get("CORS_ORIGINS", "*")
if cors_origins_str == "*":
    cors_origins = ["*"]
else:
    cors_origins = [origin.strip() for origin in cors_origins_str.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(vendor.router)
app.include_router(user.router)

# Serve static files (frontend)
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")


@app.get("/")
async def root():
    return FileResponse(os.path.join(frontend_path, "index.html"))


@app.get("/login")
async def login_page():
    return FileResponse(os.path.join(frontend_path, "login.html"))


@app.get("/register")
async def register_page():
    return FileResponse(os.path.join(frontend_path, "register.html"))


@app.get("/admin")
async def admin_page():
    return FileResponse(os.path.join(frontend_path, "admin-dashboard.html"))


@app.get("/vendor")
async def vendor_page():
    return FileResponse(os.path.join(frontend_path, "vendor-dashboard.html"))


@app.get("/user")
async def user_page():
    return FileResponse(os.path.join(frontend_path, "user-dashboard.html"))


@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Event Management System is running"}
