import json
import os
import base64
import ast
import re
import requests
from bs4 import BeautifulSoup
from time import sleep
import anthropic
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ANTHROPIC_API_KEY = os.environ['ANTHROPIC_API_KEY']
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
MODEL_NAME = "claude-3-opus-20240229"

BRAVE_API_KEY = os.environ['BRAVE_API_KEY']
STABILITY_API_KEY = os.environ['STABILITY_API_KEY']

def extract_text(obj):
    if hasattr(obj, 'text'):
        return obj.text
    elif isinstance(obj, str):
        return obj
    elif isinstance(obj, list) and all(hasattr(item, 'text') for item in obj):
        return ' '.join(item.text for item in obj)
    else:
        return str(obj)

def get_completion(prompt: str, max_tokens=2048):
    try:
        message = client.messages.create(
            model=MODEL_NAME,
            max_tokens=max_tokens,
            temperature=0.5,
            system="You are a helpful AI assistant.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return extract_text(message.content)
    except Exception as e:
        print(f"Error in get_completion: {str(e)}")
        raise

def generate_search_queries(drug_name: str):
    GENERATE_QUERIES = f"""
    Generate three search queries to find top competitors for this drug. Output only the list of queries.

    Drug name: {drug_name}

    Format your response as a Python list of strings, like this:
    ["query_1", "query_2", "query_3"]
    """
    
    try:
        response = get_completion(GENERATE_QUERIES)
        print(f"Raw response from API: {response}")
        
        try:
            queries = ast.literal_eval(response.strip())
        except:
            pattern = r'"([^"]*)"'
            queries = re.findall(pattern, response)
        
        if isinstance(queries, list) and all(isinstance(q, str) for q in queries):
            print(f"Successfully parsed queries: {queries}")
            return queries
        else:
            raise ValueError("Response is not a list of strings")
    except Exception as e:
        print(f"Error in generate_search_queries: {str(e)}")
        fallback_queries = [
            f"{drug_name} alternatives",
            f"drugs similar to {drug_name}",
            f"{drug_name} competitors"
        ]
        print(f"Using fallback queries: {fallback_queries}")
        return fallback_queries

def get_search_results(search_query: str):
    headers = {"Accept": "application/json", "X-Subscription-Token": BRAVE_API_KEY}
    response = requests.get(
        "https://api.search.brave.com/res/v1/web/search",
        params={"q": search_query, "count": 5},
        headers=headers,
        timeout=60
    )
    if not response.ok:
        raise Exception(f"HTTP error {response.status_code}")
    sleep(1)  # avoid Brave rate limit
    return response.json().get("web", {}).get("results")

def get_page_content(url: str) -> str:
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text(strip=True, separator='\n')[:1500]  
    except Exception as e:
        print(f"Error fetching content from {url}: {str(e)}")
        return ""

def find_competitor_drugs(drug_name: str):
    queries = generate_search_queries(drug_name)
    urls_seen = set()
    web_search_results = []
    
    for query in queries:
        search_results = get_search_results(query)
        for result in search_results:
            url = result.get("url")
            if not url or url in urls_seen:
                continue
            urls_seen.add(url)
            web_search_results.append(result)
    
    formatted_search_results = "\n".join(
        [
            f'<item index="{i+1}">\n<source>{result.get("url")}</source>\n<page_content>\n{get_page_content(result.get("url"))}</page_content>\n</item>'
            for i, result in enumerate(web_search_results[:3])  
        ]
    )
    return formatted_search_results

def compare_drugs(original_drug: str, original_drug_details: str, competitor_info: str):
    COMPARE_PROMPT = f"""
    Analyze the following information about {original_drug} and its competitors:

    Original Drug: {original_drug}
    Original Drug Details: {original_drug_details}

    Competitor Information:
    {competitor_info}

    Provide a brief comparison between {original_drug} and its top competitors. Include:
    1. Key similarities and differences
    2. Effectiveness comparisons
    3. Side effect profiles
    4. Cost considerations (if available)
    5. Statistics that make {original_drug} outshine its competitors.
    Keep the comparison concise, focusing on the most important points.
    """
    
    try:
        return get_completion(COMPARE_PROMPT, max_tokens=1500)
    except Exception as e:
        print(f"Error in compare_drugs: {str(e)}")
        return f"An error occurred while comparing {original_drug} with its competitors. Please try again later."

def generate_blog_post(drug_name: str, drug_details: str, comparison_data: str):
    BLOG_PROMPT = f"""
    Write a concise blog post about {drug_name}. Include:
    1. Brief introduction and primary uses
    2. How it works
    3. Brief comparison with competitors
    4. Key effectiveness and side effects
    5. Conclusion

    Drug Details: {drug_details}

    Comparison Data: {comparison_data}

    Keep the post under 1000 words.
    """
    
    try:
        return get_completion(BLOG_PROMPT, max_tokens=1500)
    except Exception as e:
        print(f"Error in generate_blog_post: {str(e)}")
        return f"An error occurred while generating the blog post for {drug_name}. Please try again later."


def gen_image(prompt, height=1024, width=1024, num_samples=1):
    engine_id = "stable-diffusion-v1-6"
    api_host = 'https://api.stability.ai'

    response = requests.post(
        f"{api_host}/v1/generation/{engine_id}/text-to-image",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {STABILITY_API_KEY}"
        },
        json={
            "text_prompts": [
                {
                    "text": prompt,
                }
            ],
            "cfg_scale": 7,
            "height": height,
            "width": width,
            "samples": num_samples,
            "steps": 30,
        },
    )

    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))

    data = response.json()
    return data['artifacts'][0]['base64']

def generate_blog_image(drug_name: str, blog_content: str):
    IMAGE_PROMPT = f"""
    Based on the following blog post about {drug_name}, create a prompt for an image that would 
    effectively illustrate the key points of the blog. The image should be informative and 
    visually appealing, suitable for a medical blog. Focus on the drug's primary uses, 
    its comparison with competitors, or a visual representation of its effectiveness.
    1. Clarity and Concision: The Foundation of Effective Prompts
Successful AI art generation hinges on crafting clear, precise, and focused prompts. Think of your prompt as a concise creative brief for the AI.
Key Principles:

Eliminate ambiguity
Be brief yet content-rich
Ensure each word contributes meaningfully

Examples:

"Minimalist landscape, vast desert under a twilight sky"
"Futuristic cityscape, neon lights, towering skyscrapers"

2. Detailed Subjects and Scenes: Adding Depth to Your Vision
While maintaining concision, use detailed descriptions to create vivid, immersive scenes. Balance precision with creative freedom for the AI.
Techniques:

Set mood and atmosphere
Highlight key aspects
Define the setting without overwhelming

Examples:

"Quiet seaside at dawn, gentle waves, seagulls in distance"
"Ancient forest, moss-covered trees, dappled sunlight through leaves"

3. Contextualizing Prompts: Painting with Words
Provide rich context without causing confusion. Think of each detail as a brushstroke adding depth to your digital canvas.
Strategies:

Weave vivid yet coherent details
Allow room for AI interpretation
Focus on key elements that define the scene

Example:
Instead of "a forest," try:
"Sunlit forest, towering pines, carpet of fallen autumn leaves"
4. Balancing Detail: Avoiding Prompt Overload
Strike a balance between descriptive richness and simplicity. Overloading prompts can lead to ambiguous or cluttered results.
Guidelines:

Be descriptive yet compact
Choose words that convey the most with the least
Focus on impactful elements

Examples:

Instead of "a light wind that can barely be felt but heard," use "whispering breeze"
"Bustling marketplace at sunset, vibrant stalls, lively crowds"

Pro Tips for Prompt Engineering:

Use Specific Art Styles: Mention particular art styles or artists for distinctive results (e.g., "in the style of Van Gogh")
Experiment with Text Weights: Use (parentheses) to decrease emphasis or [brackets] to increase emphasis on certain words
Incorporate Artistic Terms: Use terms like chiaroscuro, bokeh, or golden ratio to guide the AI's artistic approach
Specify Image Parameters: Include aspect ratios, camera angles, or lighting conditions for more control

    Blog Content:
    {blog_content}

    Provide only the image prompt, without any additional explanation or context. DO NOT INCLUDE ANY WORDS INSIDE THE PICTURE.
    """
    
    try:
        image_prompt = get_completion(IMAGE_PROMPT, max_tokens=100)
        blog_image_b64 = gen_image(image_prompt)
        return blog_image_b64, image_prompt
    except Exception as e:
        print(f"Error in generate_blog_image: {str(e)}")
        return None, f"An error occurred while generating the image prompt for {drug_name}. Please try again later."

def lambda_handler(event, context):
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        if 'body' not in event:
            raise KeyError("'body' not found in event")
        
        try:
            body = json.loads(event['body'])
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse body as JSON: {str(e)}")
            raise
        
        if 'drugName' not in body or 'drugDetails' not in body:
            raise KeyError("'drugName' or 'drugDetails' not found in body")
        
        drug_name = body['drugName']
        drug_details = body['drugDetails']

        logger.info(f"Processing request for drug: {drug_name}")
        
        competitor_info = find_competitor_drugs(drug_name)
        logger.info(f"Competitor info: {competitor_info[:500]}...")  # Log first 500 chars
        
        comparison_data = compare_drugs(drug_name, drug_details, competitor_info)
        logger.info(f"Comparison data: {comparison_data[:500]}...")  # Log first 500 chars
        
        blog_post = generate_blog_post(drug_name, drug_details, comparison_data)
        logger.info(f"Blog post: {blog_post[:500]}...")  # Log first 500 chars
        
        blog_image_b64, image_prompt = generate_blog_image(drug_name, blog_post)
        logger.info(f"Image prompt: {image_prompt}")

        response_body = {
            'blogPost': blog_post,
            'blogImage': blog_image_b64,
            'imagePrompt': image_prompt
        }

        logger.info(f"Response body: {json.dumps(response_body, indent=2)}")

        return {
            'statusCode': 200,
            'body': json.dumps(response_body),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': 'https://medbloggen.xyz',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            }
        }
    except KeyError as e:
        logger.error(f"KeyError: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(e)}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': 'https://medbloggen.xyz'
            }
        }
    except json.JSONDecodeError as e:
        logger.error(f"JSONDecodeError: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid JSON in request body'}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': 'https://medbloggen.xyz'
            }
        }
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': 'https://medbloggen.xyz'
            }
        }