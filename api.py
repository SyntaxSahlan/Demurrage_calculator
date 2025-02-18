from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from models import ContainerType, ContainerSize, DemurrageRequest, DemurrageResponse, ChargeBreakdown
from demurrage_calculator import calculate_demurrage
app = FastAPI(title="Demurrage Calculator API")

@app.get("/health")
async def health_check():
    return {"status": "ok"}
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve index.html at root path
@app.get("/")
async def read_root():
    return FileResponse('index.html')

# Mount static files directory if it exists
if os.path.exists('static'):
    app.mount("/static", StaticFiles(directory="static"), name="static")
@app.post("/calculate-demurrage", response_model=DemurrageResponse)
async def calculate_demurrage_charge(request: DemurrageRequest):
    total_charge, breakdown_dict = calculate_demurrage(
        request.container_type,
        request.container_size,
        request.days
    )
    
    breakdown = [
        ChargeBreakdown(
            period_name=period_name,
            days=details['days'],
            rate=details['rate'],
            charge=details['charge']
        )
        for period_name, details in breakdown_dict.items()
    ]
    
    return DemurrageResponse(
        total_charge=total_charge,
        breakdown=breakdown
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8006))
    uvicorn.run(app, host="0.0.0.0", port=port)
