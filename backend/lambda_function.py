import json
import anthropic
import requests
from bs4 import BeautifulSoup
import base64
import os

ANTHROPIC_API_KEY = os.environ['ANTHROPIC_API_KEY']
BRAVE_API_KEY = os.environ['BRAVE_API_KEY']
STABILITY_API_KEY = os.environ['STABILITY_API_KEY']

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
MODEL_NAME = "claude-3-opus-20240229"

def get_completion(prompt: str):
    message = client.messages.create(
        model=MODEL_NAME,
        max_tokens=2048,
        temperature=0.5,
        system="You are a helpful AI assistant.",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return message.content

def generate_search_queries(drug_name: str):
    GENERATE_QUERIES = f"""
    You are an expert at generating search queries for the Brave search engine.
    Generate three search queries to find top competitors for this drug. Output only the list of queries.

    Drug name: {drug_name}

    Format your response as a Python list of strings, like this:
    ["query_1", "query_2", "query_3"]
    """
    
    response = get_completion(GENERATE_QUERIES)
    try:
        queries = eval(response)
        if isinstance(queries, list) and all(isinstance(q, str) for q in queries):
            return queries
        else:
            raise ValueError("Response is not a list of strings")
    except:
        print("Error: Invalid response from API")
        print("Response:", response)
        return []

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
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text(strip=True, separator='\n')

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
            f'<item index="{i+1}">\n<source>{result.get("url")}</source>\n<page_content>\n{get_page_content(result.get("url"))}\n</page_content>\n</item>'
            for i, result in enumerate(web_search_results[:5])  # Limit to top 5 results
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

    Please provide a detailed comparison between {original_drug} and its top competitors. Include the following:
    1. Brief overview of each drug
    2. Key similarities and differences
    3. Effectiveness comparisons
    4. Side effect profiles
    5. Cost considerations
    6. Market share and popularity (if available)

    Present this information in a structured format that can be easily used for further analysis.
    """
    
    return get_completion(COMPARE_PROMPT)

def generate_blog_post(drug_name: str, drug_details: str, comparison_data: str):
    BLOG_PROMPT = f"""
    Using the following information, write an engaging and informative blog post about {drug_name}:

    Drug Details: {drug_details}

    Comparison with Competitors: {comparison_data}

    The blog post should:
    1. Introduce {drug_name} and its primary uses
    2. Discuss its history and development
    3. Explain how it works
    4. Compare it with top competitors
    5. Discuss its effectiveness, side effects, and cost considerations
    6. Conclude with future prospects or ongoing research related to {drug_name}

    Write in a professional yet accessible style, suitable for a general audience interested in medical information.
    """
    
    return get_completion(BLOG_PROMPT)

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
    Here is some guidance for getting the best possible images:

    <image_prompting_advice>
    Rule 1. Make Your Stable Diffusion Prompts Clear, and Concise
    Successful AI art generation in Stable Diffusion relies heavily on clear and precise prompts. It's essential to craft problem statements that are both straightforward and focused.

    Clearly written prompts acts like a guide, pointing the AI towards the intended outcome. Specifically, crafting prompts involves choosing words that eliminate ambiguity and concentrate the AI's attention on producing relevant and striking images.
    Conciseness in prompt writing is about being brief yet rich in content. This approach not only fits within the technical limits of AI systems but ensures each part of the prompt contributes meaningfully to the final image. Effective prompt creation involves boiling down complex ideas into their essence.
    Prompt Example:
    "Minimalist landscape, vast desert under a twilight sky."
    This prompt exemplifies how a few well-chosen words can paint a vivid picture. The terms 'minimalist' and 'twilight sky' work together to set a specific mood and scene, demonstrating effective prompts creation with brevity.

    Another Example:
    "Futuristic cityscape, neon lights, and towering skyscrapers."
    Here, the use of descriptive but concise language creates a detailed setting without overwhelming the AI. This example showcases the importance of balancing detail with succinctness in prompt structuring methods.

    Rule 2. Use Detailed Subjects and Scenes to Make Your Stable Diffusion Prompts More Specific
    Moving into detailed subject and scene description, the focus is on precision. Here, the use of text weights in prompts becomes important, allowing for emphasis on certain elements within the scene.

    Detailing in a prompt should always serve a clear purpose, such as setting a mood, highlighting an aspect, or defining the setting. The difference between a vague and a detailed prompt can be stark, often leading to a much more impactful AI-generated image. Learning how to add layers of details without overwhelming the AI is crucial.
    Scene setting is more than just describing physical attributes; it encompasses emotions and atmosphere as well. The aim is to provide prompts that are rich in context and imagery, resulting in more expressive AI art.
    Prompt Example:
    "Quiet seaside at dawn, gentle waves, seagulls in the distance."
    In this prompt, each element adds a layer of detail, painting a serene picture. The words 'quiet', 'dawn', and 'gentle waves' work cohesively to create an immersive scene, showcasing the power of specific prompts crafting.

    Another Example:
    "Ancient forest, moss-covered trees, dappled sunlight filtering through leaves."
    This prompt is rich in imagery and detail, guiding the AI to generate an image with depth and character. It illustrates how detailed prompts can lead to more nuanced and aesthetically pleasing results.

    Rule 3. Contextualizing Your Prompts: Providing Rich Detail Without Confusion
    In the intricate world of stable diffusion, the ability to contextualize prompts effectively sets apart the ordinary from the extraordinary. This part of the stable diffusion guide delves into the nuanced approach of incorporating rich details into prompts without leading to confusion, a pivotal aspect of the prompt engineering process.

    Contextualizing prompts is akin to painting a picture with words. Each detail added layers depth and texture, making AI-generated images more lifelike and resonant. The art of specific prompts crafting lies in weaving details that are vivid yet coherent.
    For example, when describing a scene, instead of merely stating: 
    "a forest."
    one might say,

    "a sunlit forest with towering pines and a carpet of fallen autumn leaves."
    Other Prompt Examples:
    "Starry night, silhouette of mountains against a galaxy-filled sky."
    This prompt offers a clear image while allowing room for the AI’s interpretation, a key aspect of prompt optimization. The mention of 'starry night' and 'galaxy-filled sky' gives just enough context without dictating every aspect of the scene.

    Rule 4. Do Not Overload Your Prompt Details
    While detail is desirable, overloading prompts with excessive information can lead to ambiguous results. This section of the definitive prompt guide focuses on how to strike the perfect balance.

    Descriptive Yet Compact: The challenge lies in being descriptive enough to guide the AI accurately, yet compact enough to avoid overwhelming it. For instance, a prompt like, 'A serene lake, reflecting the fiery hues of sunset, bordered by shadowy hills' paints a vivid picture without unnecessary verbosity.
    Precision in language is key in this segment of the stable diffusion styles. It's about choosing the right words that convey the most with the least, a skill that is essential in prompt optimization.
    For example, instead of using:
    "a light wind that can barely be felt but heard"
    You can make it shorter:

    whispering breeze
    More Prompt Examples:
    Sample prompt: "Bustling marketplace at sunset, vibrant stalls, lively crowds."

    By using descriptive yet straightforward language, this prompt sets a vivid scene of a marketplace without overcomplicating it. It's an example of how well-structured prompts can lead to dynamic and engaging AI art.
    </image_prompting_advice>
    Blog Content:
    {blog_content}

    Provide only the image prompt, without any additional explanation or context.
    """
    
    image_prompt_response = get_completion(IMAGE_PROMPT)
    
    # Extract the text content from the TextBlock object
    if hasattr(image_prompt_response, 'text'):
        image_prompt = image_prompt_response.text
    else:
        image_prompt = str(image_prompt_response)
    
    return gen_image(image_prompt), image_prompt

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        drug_name = body['drugName']
        drug_details = body['drugDetails']

        competitor_info = find_competitor_drugs(drug_name)
        comparison_data = compare_drugs(drug_name, drug_details, competitor_info)
        blog_post = generate_blog_post(drug_name, drug_details, comparison_data)
        blog_image_b64, image_prompt = generate_blog_image(drug_name, blog_post)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'blogPost': blog_post,
                'blogImage': blog_image_b64
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }
    