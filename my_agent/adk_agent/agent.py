from google.adk.agents.llm_agent import Agent

# --- Define Tools ---
def get_weather(location: str) -> str:
    """
    Gets the current weather for a specific city.
    
    Args:
        location: The city name (e.g., 'Austin, TX', 'Tokyo').
    """
    # Placeholder for live weather API logic
    return f"The weather in {location} is sunny and 75°F."

def calculate_fahrenheit_to_celsius(fahrenheit: float) -> float:
    """
    Converts a temperature from Fahrenheit to Celsius.
    
    Args:
        fahrenheit: The temperature value in degrees Fahrenheit.
    """
    celsius = (fahrenheit - 32) * 5 / 9
    return round(celsius, 1)


# --- Initialize the Agent with the Exact Import ---
weather_agent = Agent(
    model='gemini-3.6-flash',
    name='WeatherReporter',
    description='An agent that checks local weather conditions and converts units.',
    instruction='Always use your tools to check real-time weather and calculate correct temperature unit conversions.',
    tools=[get_weather, calculate_fahrenheit_to_celsius]
)

# --- Run the Agent ---
if __name__ == "__main__":
    # Drive the execution using standard runners or local terminal/web interfaces
    # e.g., run `adk web` or `adk run` via terminal to interact with this agent.
    print(f"Initialized ADK agent '{weather_agent.name}' successfully.")
