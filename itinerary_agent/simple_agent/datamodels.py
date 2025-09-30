from enum import Enum
from typing import List, Literal, Optional, Annotated
from datetime import datetime
from pydantic import BaseModel, Field, field_validator,ValidationError
from data import Interest,mijournée,WEATHER




class DailyForecast(BaseModel):
    day: Annotated[int, Field(ge=0, le=13, description="Jour entre 0 et 13 (Pour le jour même : 0, pour le lendemain : 1, etc.)")]
    datetime: Annotated[datetime, Field(description="Date en heure locale au format ISO 8601")]
    #datetime: Annotated[date, Field(description="Date locale (jour uniquement)")]
    period:Annotated[int, Field(ge=1, le=2, description="Période de la journée (1:matin ou 2:après-midi)")]
    weather: Annotated[int, Field(ge=0, le=235, description="Code temps")]
    probarain: Annotated[float, Field(ge=0, le=100, description="Probabilité de pluie")]
    temp2m: Annotated[float, Field(description="Température à 2m en Celsius")]
    rr10: Annotated[float, Field(description="Précipitations sur la tranche de 6h en mm")]
    rr1: Annotated[float, Field(description="Précipitations maximale sur la tranche de 6h en mm")]
    probafrost: Annotated[int, Field(ge=0, le=100, description="Probabilité de givre")]
    probafog: Annotated[int, Field(ge=0, le=100, description="Probabilité de brouillard")]

    @field_validator("datetime", mode="before")
    def keep_only_date(cls, v):
        if isinstance(v, datetime):
            return v.date()
        if isinstance(v, str):
            return datetime.fromisoformat(v).date()
        return v 

    def __str__(self):
        # Heading only for morning forecasts
        printout = ""
        if self.period == 1:
            printout += f"Prévisions pour le {self.datetime.strftime('%A %d %B %Y')} => "

        # Core line
        printout += f"{mijournée[self.period]}: {WEATHER.get(self.weather, 'Inconnu')} - {self.temp2m}°C"

        # Add rain info if relevant
        if self.rr10 > 0:
            printout += f" (Probabilité de pluie: {self.probarain:.0f}%, cumul précipitations: {self.rr10} mm)"

        # Optional frost/fog info
        # if self.probafrost > 0:
        #     printout += f"   Risque de givre: {self.probafrost}%\n"
        # if self.probafog > 0:
        #     printout += f"   Risque de brouillard: {self.probafog}%\n"

        return printout

        
class WeatherForecast(BaseModel):
    Forecast: list[DailyForecast]
    
    def __str__(self):
        header = "=== Prévisions météo ===\n"
        body = "\n".join(str(day) for day in self.Forecast)
        return header + body


class Activity(BaseModel):
    activity_id: str
    name: str
    start_time: datetime = Field(..., description="start time of the activity", ge=datetime(2025, 10, 1))
    end_time: datetime  = Field(..., description="end time of the activity", le=datetime(2025, 10, 15))
    location: str
    description: str
    price: int = Field(...,description="price of the activity", gt=0)
    related_interests: List[Interest]
    setting: Literal["indoor", "outdoor", "mixed"]

    @field_validator("start_time", "end_time", mode="before")
    def parse_datetime(cls, v):
        if isinstance(v, str):
            try:
                return datetime.strptime(v, "%d-%m-%Y %H:%M")
            except ValueError:
                pass  # fallback to Pydantic’s default parsing
        return v

    @field_validator("related_interests", mode="before")
    def coerce_interests(cls, v):
        if isinstance(v, list) and all(isinstance(i, str) for i in v):
            # allow either enum name or value
            coerced = []
            for i in v:
                try:
                    coerced.append(Interest[i])  # by name
                except KeyError:
                    coerced.append(Interest(i))  # by value
            return coerced
        return v



class AgentError(Exception):
    pass
