from pydantic import BaseModel


class DayPatient(BaseModel):
    name: str
    time: str
    patient_display_id: int | None = None


class DayVisits(BaseModel):
    date: str
    day_name: str
    count: int
    patients: list[DayPatient] = []


class DashboardStats(BaseModel):
    today_visits: int = 0
    pending_transcriptions: int = 0
    total_patients: int = 0
    total_visits: int = 0
    days: list[DayVisits] = []
