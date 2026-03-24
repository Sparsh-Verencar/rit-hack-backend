from contextlib import asynccontextmanager
from fastapi import FastAPI
from prisma import Prisma

# Initialize Prisma database client
db = Prisma()

# Modern FastAPI lifecycle manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Code here runs on STARTUP ---
    print("Connecting to database...")
    await db.connect()
    
    # Hand control back to FastAPI to run the server
    yield  
    
    # --- Code here runs on SHUTDOWN ---
    print("Disconnecting from database...")
    await db.disconnect()

# Pass the lifespan function to the FastAPI app
app = FastAPI(lifespan=lifespan)

@app.post("/projects")
async def create_project(user_id: str, name: str, r2_key: str):
    # Create the project in Postgres
    project = await db.project.create(
        data={
            "user_id": user_id,
            "name": name,
            "original_r2_key": r2_key,
            "row_count": 1000,  # We will dynamically calculate this later!
            "col_count": 5,     # Same for this
        }
    )
    return project