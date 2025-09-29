# Weather Tool Usage Instructions

## When to Use the Weather Tool
- User asks about weather for a specific date
- User wants to plan a visit and needs weather information
- User asks about weather conditions at Versailles

## How to Use the Weather Tool
1. Extract the date from the user's request (format: YYYY-MM-DD)
2. Call the weather tool with the extracted date
3. Interpret the results in context of visiting Versailles

## Tool Call Format
```
get_weather_for_versailles_visit(visit_date="YYYY-MM-DD")
```

## Interpreting Results
- Check the forecast_type to understand data reliability
- Focus on temperature ranges and main conditions
- Consider how weather affects outdoor vs indoor activities
- Note the days_until_visit for accuracy context

## Error Handling
- If the tool returns an error, explain the limitation clearly
- Suggest alternative dates if weather data is unavailable
- Provide general seasonal information as fallback