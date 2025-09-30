import os
import json
from datetime import datetime
import inspect
import locale
locale.setlocale(locale.LC_TIME, 'French_France.1252')
from contextlib import closing
from urllib.request import urlopen
from rich.console import Console
console = Console()
from data import ACTIVITY_CALENDAR, WEATHER, mijournée
from datamodels import (
    Activity,
    WeatherForecast,
    DailyForecast
    )

from data import tips

from dotenv import load_dotenv
load_dotenv()

def rag_tool(query:str)->list[str]:
    """
    Returns a list of documents relevant to the query.
    Args:
        query: The query to search for.
    Returns:
        A list of documents relevant to the query.
    """
    console.print(f"== FUNC call rag_tool queyring: {query} ==", style="bold cyan") 
    return {"content":[tips]}



def call_activities_api_mocked(
    date: str | None = None, activity_ids: list[str] | None = None
) -> list[dict[str, str | int]]:
    """Calls the mocked activities API to get a list of activities for a given date.
    This function simulates an API call to retrieve activities based on the provided date.

    Args:
        date: The date to get activities for. Must be in the format DD-MM-YYYY.
        activity_ids: A list of activity IDs to filter the results. If None, all activities for the date will be returned.

    Returns:
        A list of activities for the given date. Currently only returns activities
        between 01-10-2025 and 15-10-2025.
    """

    # Verify the date format
    if date:
        try:
            datetime.strptime(date, "%d-%m-%Y")
        except ValueError:
            print(f"Invalid date format: {date}")
            return []

    # If the date is not between 2025-06-10 and 2025-06-15, return an empty list
    if date and (date < "01-10-2025" or date > "15-10-2025"):
        print(f"Date {date} is outside the valid range (01-10-2025 - 15-10-2025)")
        return []

    activities = ACTIVITY_CALENDAR

    if date:
        # select appropriate format depending on how the dates appear in the database
        #date = datetime.strptime(date, "%d-%m-%Y").strftime("%Y-%m-%d")
        activities = [event for event in activities if event["start_time"].startswith(date)]

    if activity_ids:
        activities = [event for event in activities if event["activity_id"] in activity_ids]

    if not activities:
        print(f"No activities found for {date}.")
    return activities




def bulletin_meteo() -> dict:
    """
    provides Weather forecast over next 14 days for mornings and afternoons
    returns a dictionary with the following keys:
    - city: the name of the city
    - updated: the date and time the forecast was updated
    - forecasts: a list of forecasts for the next 14 days
    """

    console.print(f"== FUNC call bulletin_meteo ==", style="bold cyan") 
    METEO_TOKEN = os.getenv("METEOCONCEPT_TOKEN")

    with closing(urlopen(
        f'https://api.meteo-concept.com/api/forecast/daily/periods?token={METEO_TOKEN}&insee=78646'
    )) as f:
        decoded = json.loads(f.read())


    forecasts = []; _forecasts = []
    for i in range(len(decoded['forecast'])):
        # mornings + afternoons only
        forecasts.extend(decoded['forecast'][i][1:3])    

        # DailyForecast model type
        _forecasts.extend([DailyForecast(**d) for d in decoded['forecast'][i][1:3]])    

    # plain text bulletin météo format
    wf = WeatherForecast(Forecast=[f.model_dump() for f in _forecasts])

    return {
        "city": decoded['city']['name'],
        "updated": decoded['update'],
        "forecasts": forecasts
    }



def get_activities_by_date_tool(date: str) -> list[Activity]:
    """
    Returns all activities available on a given date and a city
    Args:
        date: a date with string format DD-MM-YYYY
    Returns:
        list of activities available in the city for selected date.
    Each activity is a dictionary with key,value pairs based on Activity class pydantic model
    """
    console.print(f"== FUNC call get_activities_by_date_tool {date} ==", style="bold cyan")
    resp = call_activities_api_mocked(date=date)

    return [Activity.model_validate(activity).model_dump(mode="json") for activity in resp]



def final_answer_tool(itinerary: str) -> str:
    """
    Returns the final itinerary proposal.
    Args:
        itinerary: a string containing the itinerary proposal.
    Returns:
        the final itinerary proposal.
    """
    console.print(f"== FUNC call final_answer_tool {len(itinerary)} characters ==", style="bold cyan") 
    return itinerary

def build_tools_from_functions(fns):
    """
    Build OpenAI-compatible tool definitions from a list of functions.
    Uses the function signature + docstring.
    """
    tools = []
    for fn in fns:
        sig = inspect.signature(fn)
        params = {
            "type": "object",
            "properties": {},
            "required": []
        }

        for name, param in sig.parameters.items():
            # Basic typing info (string, integer, etc.)
            annotation = "string"
            if param.annotation in [int, "int"]:
                annotation = "integer"
            elif param.annotation in [float, "float"]:
                annotation = "number"
            elif param.annotation in [bool, "bool"]:
                annotation = "boolean"

            params["properties"][name] = {
                "type": annotation,
                "description": f"(from signature) parameter '{name}'"
            }
            if param.default is param.empty:
                params["required"].append(name)

        tools.append({
            "type": "function",
            "function": {
                "name": fn.__name__,
                "description": fn.__doc__ or "No description provided.",
                "parameters": params
            }
        })
    return tools