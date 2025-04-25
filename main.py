from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()

class RiskRequest(BaseModel):
    phone_number: str = Field(..., example="0912345678")
    device_location_region: str = Field(None, example="TW-TPE")
    ip_location_country: str = Field(None, example="VN")
    device_trust_score: int = Field(50, ge=0, le=100, example=78)  # 預設為中等可信度
    sim_change_days: int = Field(999, ge=0, example=999)  # 預設為999天前（很久以前）

class RiskResponse(BaseModel):
    phone_number: str
    risk_score: int
    risk_level: str
    sim_change_flag: bool
    location_match: bool
    ip_risk_flag: bool
    device_trust_score: int

@app.post("/risk-check", response_model=RiskResponse)
def check_risk(data: RiskRequest):
    sim_change_flag = data.sim_change_days <= 7
    location_match = (
        data.device_location_region and data.ip_location_country
        and data.device_location_region[:2] == data.ip_location_country
    )
    ip_risk_flag = data.ip_location_country not in ["TW", "JP", "US"]

    score = 0
    if sim_change_flag:
        score += 30
    if location_match is False:
        score += 30
    if ip_risk_flag:
        score += 20
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
        location_match=bool(location_match),
        ip_risk_flag=ip_risk_flag,
        device_trust_score=data.device_trust_score
    )

