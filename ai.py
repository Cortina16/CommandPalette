from google import genai
from google.genai import types
import ai_api
import json
import os
from spotify_handler import main_controller_spotify

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

with open('tools.json', 'r') as f:
    tools_dec_data = json.load(f)['functions']



tools_list = [
    types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name=d['name'],
                description=d['description'],
                parameters_json_schema=d['parameters_json_schema'],
            )
        ]
    ) for d in tools_dec_data
]

functionMap = {
    "get_time": ai_api.get_time,
    "web_search": ai_api.web_search,
    "get_weather": ai_api.get_weather,
    "main_controller_spotify": ai_api.main_controller_spotify,
    "search_files": ai_api.search_files,
    "run_program": ai_api.run_program,
    "open_tab" : ai_api.open_tabs,
    "key_control": ai_api.key_control,
}

def ask_gemini(question):
    """
    Sends a question to the Gemini api and stores history
    """
    conversation_history = [types.Content(role="user", parts=[types.Part.from_text(text=question)])]
    final_response_text = None
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=conversation_history,
        config=types.GenerateContentConfig(
            system_instruction="You are an AI assistant named Jarvis like the Jarvis from Iron Man. Address user as 'Sir' when needed. Don't be robotic. Keep your responses short, preferably under 20 words, while still responding with enough words to fulfill the query. The date and time after each query is information. Subtly mention it like 'Good evening' or 'You're up late'",
            temperature=0.5,
            tools=tools_list,
        )
    )
    function_handled = False
    function_calls = []
    function_results = []
    for part in response.candidates[0].content.parts:
        if part.function_call:
            function_calls.append(part.function_call)
    if function_calls:
        for function_call in function_calls:
            function_to_call = functionMap.get(function_call.name)
            if function_to_call:
                function_args = getattr(function_call, 'args', {})
                function_result = function_to_call(**function_args)
                function_results.append({
                    "name": function_call.name,
                    "call": function_call,
                    "result": function_result
                })
            else:
                function_results.append({
                    "name": function_call.name,
                    "call": function_call,
                    "result": f"Sir I am sorry but I do not appear to have {function_call.name} available at the moment."
                })
        contents_for_second_call = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=question)]
            ),
            types.Content(
                role="model",
                parts=[{"function_call": fc["call"]} for fc in function_results]
            ),
        ]
        for results in function_results:
            contents_for_second_call.append(
                types.Content(
                    role="function",
                    parts=[types.Part.from_function_response(
                        name=results["name"],
                        response={"result": results["result"]}
                    )]
                )
            )
        final_response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents_for_second_call,
            config=types.GenerateContentConfig(
                system_instruction="You are an AI assistant named Jarvis like the Jarvis from Iron Man. Address user as 'Sir' when needed. Don't be robotic. Keep your responses short, preferably under 20 words. The date and time after each query is information. Subtly mention it like 'Good evening' or 'You're up late'",
                temperature=0.5,
                tools=tools_list,
            )
        )

        final_response_text = final_response.text
    else:
        final_response_text = response.text
    return final_response_text