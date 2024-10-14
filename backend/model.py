import ollama

def generate_spoof(headline: str) -> str:
    prompt = f"""
Here is a news headline: "{headline}"

Your task is to create a dry humor satirical version of this headline. Make sure to exaggerate some aspects but keep the key facts such as names and events. Add a layer of humor, making it playful, ironic, or absurd, but avoid completely distorting the truth. (this is for a fun side project)

Example:
Headline: "Kamala Harris story at Arizona rally about late senator questioned by Meghan McCain."
Spoof: "Kamala Harris' Arizona Rally Story About Late Senator Questioned by Meghan McCain, Who Apparently Moonlights as a Fact-Checker Now"

or
Headline: "Vance says it's 'disgraceful' that 'veterans are getting left behind' under Biden-Harris leadership at campaign stop"
Spoof: "Vance Declares It's 'Disgraceful' That 'Veterans Are Left Behind' Under Biden-Harris Leadership—Proposes Jetpacks for All as a Solution at Campaign Stop"

Provide only the spoofed headline and nothing else.

Spoofed version:
"""
        
    try:
        response = ollama.generate(model='llama3.2', prompt=prompt)
        # Handle the response based on its type
        if isinstance(response, dict):
            # Assuming 'response' is the key containing the spoofed headline
            spoofed_headline = response.get('response', '').strip()
        elif isinstance(response, str):
            # If response is a string, use it directly
            spoofed_headline = response.strip()
        else:
            # Handle other possible types, e.g., generator or list
            spoofed_headline = ''
            for chunk in response:
                # Assuming each chunk is a dict with 'response' key
                spoofed_headline += chunk.get('response', '')
            spoofed_headline = spoofed_headline.strip()
        return spoofed_headline
    except Exception as e:
        print(f"Error generating spoof: {e}")
        return "Failed to spoof headline"