from fastapi import FastAPI
from pydantic import BaseModel, Field

class RiskRequest(BaseModel):
    phone_number: str = Field(..., example="0912345678")
    device_location_region: str = Field(..., example="TW-TPE")
    ip_location_country: str = Field(..., example="VN")
    device_trust_score: int = Field(..., ge=0, le=100, example=78)
    sim_change_days: int = Field(..., ge=0, example=3)

class RiskResponse(BaseModel):
    phone_number: str
    risk_score: int
    risk_level: str
    sim_change_flag: bool
    location_match: bool
    ip_risk_flag: bool
    device_trust_score: int

app = FastAPI()

@app.post("/risk-check", response_model=RiskResponse)
def check_risk(data: RiskRequest):
    sim_change_flag = data.sim_change_days <= 7
    location_match = data.device_location_region[:2] == data.ip_location_country
    ip_risk_flag = data.ip_location_country not in ["TW", "JP", "US"]
    
    score = 0
    score += 30 if sim_change_flag else 0
    score += 30 if not location_match else 0
    score += 20 if ip_risk_flag else 0
    score += (100 - data.device_trust_score) * 0.2

    if score >= 80:
        level = "極高風險"
    elif score >= 50:
        level = "中風險"
    else:
        level = "低風險"

    return RiskResponse(
        phone_number=data.phone_number,
        risk_score=int(score),
        risk_level=level,
        sim_change_flag=sim_change_flag,
        location_match=location_match,
        ip_risk_flag=ip_risk_flag,
        device_trust_score=data.device_trust_score
    )

