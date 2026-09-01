import os
import sys
import json

from dotenv import load_dotenv
from litellm import completion

load_dotenv()       
openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    print("❌ Error: Missing OpenAI API key in .env file.")
    sys.exit(1)

def get_weather(location: str):
    database = {"Shibuya, Tokyo": "Sunny, 18°C", "Tokyo, Japan": "Sunny, 18°C"}
    return database.get(location, f"Weather for {location} is unknown.")

def search_restaurants(location: str, cuisine: str, indoor_seating_only: bool = False):
    database = {
        ("Shibuya, Tokyo", "Ramen"): [{"name": "Ichiran", "indoor": True}, {"name": "Ippudo", "indoor": True}],
        ("Shibuya, Tokyo", "Sushi"): [{"name": "Sushi Zanmai", "indoor": True}]
    }
    results = database.get((location, cuisine), [])
    if indoor_seating_only:
        results = [r for r in results if r.get("indoor")]
    return results

def get_traffic_status(origin: str, destination: str):
    database = {
        ("Shibuya Crossing, Tokyo", "Ichiran ramen, Tokyo"): {"duration": "15 mins", "status": "Normal"},
        ("Shibuya Crossing, Tokyo", "Ippudo"): {"duration": "20 mins", "status": "Delayed"},
        ("Shibuya Crossing, Tokyo", "Ichiran"): {"duration": "20 mins", "status": "Delayed"},
        ("Shibuya Crossing, Tokyo", "Ichiran, Shibuya, Tokyo"): {"duration": "10 mins", "status": "Normal"}
    }
    return database.get((origin, destination), {"duration": "Unknown", "status": "Unknown"})

tools_schema = [
    {
      "type": "function",
      "function": {
        "name": "get_weather",
        "description": "Retrieves the current weather for a specified location.",
        "parameters": {
          "type": "object",
          "properties": {
            "location": {
              "type": "string",
              "description": "City and state/country, e.g., 'Tokyo, Japan'"
            },
            "unit": {
              "type": "string",
              "enum": ["celsius", "fahrenheit"],
              "default": "celsius"
            }
          },
          "required": ["location"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "search_restaurants",
        "description": "Finds nearby restaurants matching cuisine or atmosphere preferences.",
        "parameters": {
          "type": "object",
          "properties": {
            "location": {
              "type": "string",
              "description": "Neighborhood or city"
            },
            "cuisine": {
              "type": "string",
              "description": "Type of food, e.g., 'Ramen', 'Sushi', 'Italian'"
            },
            "indoor_seating_only": {
              "type": "boolean",
              "description": "Filter for restaurants with reliable indoor dining"
            }
          },
          "required": ["location", "cuisine"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "get_traffic_status",
        "description": "Checks travel times and delay status between two points.",
        "parameters": {
          "type": "object",
          "properties": {
            "origin": {
              "type": "string"
            },
            "destination": {
              "type": "string"
            }
          },
          "required": ["origin", "destination"]
        }
      }
    }
]

def use_multi_tool(model_name: str, prompt: str):
    messages = [
        {"role": "system", "content": """You are a smart travel assistant. 
                            When helping users plan meals or outings, check the weather first. 
                            If bad weather is expected, prioritize indoor spots and check traffic delays."""},
        {"role": "user", "content": prompt}
    ]
    
    # Map string names directly to your python functions
    tool_functions = {
        "get_weather": get_weather,
        "search_restaurants": search_restaurants,
        "get_traffic_status": get_traffic_status
    }

    while True:
        # A single completion call handles all steps in the cycle
        # We pass tools_schema every turn because the LLM is stateless
        response = completion(
            model=model_name,
            messages=messages,
            tools=tools_schema,
        )

        assistant_message = response.choices[0].message
        messages.append(assistant_message)
        print(f"\nAssistant: {assistant_message}")

        # Check if the model wants to call tools
        if tool_calls := assistant_message.tool_calls:
            for tool_call in tool_calls:
                func_name = tool_call.function.name
                
                if func_name in tool_functions:
                    args = json.loads(tool_call.function.arguments)
                    
                    # Execute the matched tool function dynamically
                    result = tool_functions[func_name](**args)
                    print(f"Tool Call: {func_name}({args}) => {result}")
                    
                    # Append execution context back to history
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": func_name,
                        "content": json.dumps(result) 
                    })
            # Continue the loop to let the stateless LLM look at the tool results
            continue
        else:
            # If no tool calls were requested, this is your final answer
            print("\nFinal Response:")
            print(assistant_message.content)
        break

test_prompt = """I'm near Shibuya Crossing in Tokyo right now. 
                 Can you find me a good ramen spot nearby, and 
                 tell me if I should walk or grab a taxi based 
                 on the current traffic and weather conditions?"""
use_multi_tool("openai/gpt-4o-mini", test_prompt)
