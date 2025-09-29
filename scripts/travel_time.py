import os
import json
import datetime as dt
from datetime import timezone
from typing import Literal, Dict, Any, Tuple, Optional
from dotenv import load_dotenv
load_dotenv()
import httpx

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"
# Non-streaming, one-to-one:
ROUTES_URL = "https://routes.googleapis.com/directions/v2:computeRoutes"

Mode = Literal["transit", "driving", "walking", "bicycling"]

def _geocode(address: str) -> Tuple[float, float, str]:
    if not GOOGLE_API_KEY:
        raise RuntimeError("GOOGLE_API_KEY is not set")
    params = {"address": address, "key": GOOGLE_API_KEY}
    with httpx.Client(timeout=15) as client:
        r = client.get(GEOCODE_URL, params=params)
        r.raise_for_status()
        data = r.json()
    status = data.get("status")
    if status != "OK" or not data.get("results"):
        em = data.get("error_message", "")
        raise ValueError(f"Geocoding failed for '{address}': {status}{' — ' + em if em else ''}")
    res = data["results"][0]
    loc = res["geometry"]["location"]
    return float(loc["lat"]), float(loc["lng"]), res["formatted_address"]

def reverse_geocode(lat: float, lng: float) -> str:
    """
    Convert latitude and longitude coordinates to a formatted address/street name.
    
    Args:
        lat: Latitude coordinate
        lng: Longitude coordinate
        
    Returns:
        Formatted address string
    """
    if not GOOGLE_API_KEY:
        raise RuntimeError("GOOGLE_API_KEY is not set")
    
    params = {"latlng": f"{lat},{lng}", "key": GOOGLE_API_KEY}
    with httpx.Client(timeout=15) as client:
        r = client.get(GEOCODE_URL, params=params)
        r.raise_for_status()
        data = r.json()
    
    status = data.get("status")
    if status != "OK" or not data.get("results"):
        em = data.get("error_message", "")
        raise ValueError(f"Reverse geocoding failed for '{lat},{lng}': {status}{' — ' + em if em else ''}")
    
    # Return the most specific address (first result)
    return data["results"][0]["formatted_address"]

def _map_mode(mode: Mode) -> str:
    return {
        "driving": "DRIVE",
        "walking": "WALK",
        "bicycling": "BICYCLE",
        "transit": "TRANSIT",
    }[mode]

def get_distance_time(
    origin_address: Optional[str] = None,
    destination_address: Optional[str] = None,
    *,
    origin_latlng: Optional[Tuple[float, float]] = None,
    destination_latlng: Optional[Tuple[float, float]] = None,
    mode: Mode = "transit",
    departure_time: Optional[dt.datetime] = None,
) -> Dict[str, Any]:
    """
    Compute distance & travel time using Google Directions / Routes v2:computeRoutes (non-streaming).
    You can pass addresses (will geocode) or raw coordinates (lat,lng) to skip geocoding.
    """
    if not GOOGLE_API_KEY:
        raise RuntimeError("GOOGLE_API_KEY is not set")

    # Resolve origin
    if origin_latlng:
        o_lat, o_lng = float(origin_latlng[0]), float(origin_latlng[1])
        o_fmt = f"{o_lat:.6f},{o_lng:.6f}"
    elif origin_address:
        o_lat, o_lng, o_fmt = _geocode(origin_address)
    else:
        raise ValueError("Provide origin_address or origin_latlng")

    # Resolve destination
    if destination_latlng:
        d_lat, d_lng = float(destination_latlng[0]), float(destination_latlng[1])
        d_fmt = f"{d_lat:.6f},{d_lng:.6f}"
    elif destination_address:
        d_lat, d_lng, d_fmt = _geocode(destination_address)
    else:
        raise ValueError("Provide destination_address or destination_latlng")

    travel_mode = _map_mode(mode)

    # Build base payload
    payload: Dict[str, Any] = {
        "origin":   {"location": {"latLng": {"latitude": o_lat, "longitude": o_lng}}},
        "destination": {"location": {"latLng": {"latitude": d_lat, "longitude": d_lng}}},
        "travelMode": travel_mode,
    }

    # Add mode-specific configurations
    if travel_mode == "TRANSIT":
        # Transit requires departure time
        if departure_time is None:
            departure_time = dt.datetime.now(timezone.utc) + dt.timedelta(minutes=5)  # 5 minutes from now
        elif departure_time.tzinfo is None:
            departure_time = departure_time.replace(tzinfo=timezone.utc)

        payload["departureTime"] = departure_time.isoformat()
        payload["transitPreferences"] = {"routingPreference": "LESS_WALKING"}

    elif travel_mode == "DRIVE":
        # For driving, we can optionally include departure time for traffic-aware routing
        # But we need to be careful with timestamps
        if departure_time is not None:
            if departure_time.tzinfo is None:
                departure_time = departure_time.replace(tzinfo=timezone.utc)

            # Only add departure time if it's in the future
            now = dt.datetime.now(timezone.utc)
            if departure_time > now:
                payload["departureTime"] = departure_time.isoformat()
                # Can optionally add routing preference for traffic awareness
                # payload["routingPreference"] = "TRAFFIC_AWARE"

    # For WALK and BICYCLE, don't add departure time as it's not needed/supported

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        # Field mask is REQUIRED; list only fields you need
        "X-Goog-FieldMask": "routes.distanceMeters,routes.duration,routes.legs.steps.transitDetails,routes.legs.steps.travelMode",
    }

    # Debug logging
    print(f"🔍 Making request to Google Routes API for mode: {travel_mode}")
    print(f"📦 Payload keys: {list(payload.keys())}")

    with httpx.Client(timeout=30) as client:
        r = client.post(ROUTES_URL, headers=headers, json=payload)
        if r.status_code >= 400:
            try:
                msg = r.json()
                print(f"❌ API Error Response: {msg}")
            except Exception:
                msg = r.text
                print(f"❌ API Error (text): {msg}")
            raise httpx.HTTPStatusError(f"{r.status_code} {r.reason_phrase}: {msg}",
                                        request=r.request, response=r)

        data = r.json()
        print(f"✅ API Response received for {travel_mode}")

    routes = data.get("routes") or []
    if not routes:
        # Typically you’d also inspect data.get('error') or try alternative modes
        raise RuntimeError(f"No route found for mode={travel_mode}. Raw: {json.dumps(data)[:500]}")

    route = routes[0]
    distance_m = int(route.get("distanceMeters", 0))
    dur_iso = route.get("duration", "0s")  # e.g., "1234s"
    duration_sec = int(dur_iso[:-1]) if isinstance(dur_iso, str) and dur_iso.endswith("s") else 0

    # Extract transit details if available
    transit_steps = []
    if travel_mode == "TRANSIT" and "legs" in route:
        for leg in route["legs"]:
            if "steps" in leg:
                for step in leg["steps"]:
                    if step.get("travelMode") == "TRANSIT" and "transitDetails" in step:
                        transit_detail = step["transitDetails"]
                        step_info = {
                            "mode": transit_detail.get("transitLine", {}).get("vehicle", {}).get("type", "Unknown"),
                            "line_name": transit_detail.get("transitLine", {}).get("name", ""),
                            "short_name": transit_detail.get("transitLine", {}).get("nameShort", ""),
                            "departure_stop": transit_detail.get("departureStop", {}).get("name", ""),
                            "arrival_stop": transit_detail.get("arrivalStop", {}).get("name", ""),
                            "color": transit_detail.get("transitLine", {}).get("color", ""),
                        }

                        # Clean up the step info
                        if step_info["line_name"] or step_info["short_name"]:
                            transit_steps.append(step_info)

    result = {
        "origin": {"address": o_fmt, "lat": o_lat, "lng": o_lng},
        "destination": {"address": d_fmt, "lat": d_lat, "lng": d_lng},
        "mode": travel_mode,
        "distance_m": distance_m,
        "duration_sec": duration_sec,
        "duration_min": round(duration_sec / 60.0, 2),
        "status": "OK",
    }

    # Add transit steps if available
    if transit_steps:
        result["transit_steps"] = transit_steps

    return result

# Example
if __name__ == "__main__":
    print("Testing travel time calculation:")
    print(get_distance_time(
        origin_address="Gare du Nord, Paris",
        destination_address="Tour Eiffel, Paris",
        mode="transit",
    ))
    
    print("\nTesting reverse geocoding:")
    # Test reverse geocoding with Le Bourget coordinates
    print(reverse_geocode(48.9341, 2.4358))
