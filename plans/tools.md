MCP tools
get_weather: Given the day of the visit, get  the weather forecast
get_open_venues : Given the day of the visit get open to visit monuments in chateau de versailles
plan_route: Given the duration of the visit, the monuments to visit and their positions, returns an open street maps itineraries

others non mcp functions
who_are_you: asks the visiters to tell him more about themselves, their style of visiting (chill or intense), their objective from the visit (sight seeing, learn a lot ..) who are they with and do they want to take a break at a certain time, what other constraints they might have
tell_me_more: given an image, the agent identifies the monument and gives more historical information about it
adapt_tone: given the age of the intended user, the agent can customize its voice/writing style to match a young or old population (young, more storytelling, old, more historical, adult more factual)
plan_route_adv: given for each monument (a set of coordinates of the monuments, a weight (importance from 1 to 3) and a budget time,  maximize the number of monuments visited in the budget time (The Orienteering Problem (OP))
change_of_hearts: given a new request or an addition from the user about what he wants or doesn't want to do anymore, the agent relaunches the plan_route_adv to change the plan and to cross the elements that the user did see