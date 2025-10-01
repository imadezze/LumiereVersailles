# Weather Tool Usage

## When to Use
- User mentions a specific visit date: "tomorrow", "samedi", "next week"
- User explicitly asks about weather/météo

## How to Use
1. Convert date expression to YYYY-MM-DD format
2. Call: `get_weather_for_versailles_visit(visit_date="YYYY-MM-DD")`
3. Interpret JSON results for user

## Key Output
- Temperature (min/max)
- Conditions (rain, sun, clouds)
- Visit recommendations based on weather
- Consider how weather affects outdoor vs indoor activities
- Note the days_until_visit for accuracy context

## Error Handling
- If the tool returns an error, explain the limitation clearly
- Suggest alternative dates if weather data is unavailable
- Provide general seasonal information as fallback