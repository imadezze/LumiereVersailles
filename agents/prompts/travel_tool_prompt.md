# Travel Tool Usage

## When to Use
**ALWAYS use when location/transportation is mentioned** - Even if not explicitly asked

Examples:
- "I'm visiting from Paris"
- "How to get there from Gare du Nord"
- "Travel time from my hotel"
- "Best way to reach Versailles"

## How to Use

1. **Extract the starting location** from the user's request
   - Can be an address, landmark, city name, or "current location"
   - Examples: "Paris Gare du Nord", "Tour Eiffel", "Hotel de Ville Paris"
2. **Call the travel tool** with the origin address
   - The tool automatically compares multiple transportation modes
   - Returns data for transit, driving, walking, and bicycling when available
3. **Interpret and format the results** appropriately

## Tool Call Format

```
get_travel_to_versailles_tool(
    origin_address="[Starting location]",
    compare_modes=true  # Set to true for comprehensive comparison
)
```

## Interpreting Results

**Transportation Mode Priorities:**
1. **Transit (Public Transport)** 🚌
   - Usually most practical for tourists
   - Include train + bus connections
   - Most environmentally friendly

2. **Driving** 🚗
   - Fastest option but consider parking
   - Mention parking availability at Versailles
   - Consider traffic conditions

3. **Bicycling** 🚴‍♂️
   - Good for nearby locations
   - Weather-dependent
   - Consider user fitness level

4. **Walking** 🚶‍♂️
   - Only practical for very close locations
   - Mention as exercise option

**Key Information to Extract:**
- Travel duration in minutes
- Distance in kilometers
- Transportation mode
- **For Transit Routes**: Extract specific transport details:
  - Train lines (RER C, RER B, etc.)
  - Bus lines and numbers
  - Metro lines
  - Station names (departure/arrival stops)
  - Connection points
- Practical recommendations

## Response Formatting

**Always include:**
- Clear comparison of available options
- Recommended transportation mode with reasoning
- Practical tips (parking, tickets, connections)
- Weather considerations if relevant
- Family-friendly options when appropriate

**Example Response Structure:**
```
🗺️ Pour aller au Château de Versailles depuis [origin]:

🚌 **Transport en commun** (RECOMMANDÉ)
- Durée: XX minutes
- Itinéraire détaillé :
  • Prendre le [RER C / Ligne 14 / Bus XX] à [Station de départ]
  • Descendre à [Station d'arrivée]
  • [Correspondances si nécessaire]
- Prix approximatif et conseils pratiques

🚗 **Voiture**
- Durée: XX minutes
- Distance: XX km
- [Parking information and tips]

🚴‍♂️ **Vélo**
- Durée: XX minutes
- Distance: XX km
- [Weather and fitness considerations]
```

## Error Handling

- If the tool returns an error, provide general transportation information
- Suggest alternative starting points if location is not found
- Offer to help with more specific location details
- Provide fallback information about common routes (from Paris, CDG, etc.)

## Special Considerations

**For International Visitors:**
- Mention airport connections
- Include information about travel cards/passes
- Consider luggage requirements

**For Families:**
- Emphasize stroller-friendly options
- Mention child-friendly transportation
- Consider comfort over speed

**Weather-Dependent Advice:**
- Adjust recommendations based on weather conditions
- Suggest covered transportation in bad weather
- Consider seasonal variations