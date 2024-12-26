from openai import AsyncOpenAI
from config import AITOKEN,AI_BASE_URL


client = AsyncOpenAI(api_key=AITOKEN,base_url=AI_BASE_URL)



async def gpt_text(prompt, model):
    completion = await client.chat.completions.create(
      model = model,
      messages=[{"role": "user", "content": prompt}],
    )
    return completion.choices[0].message.content

async def gpt_image(prompt, model):
    response = await client.images.generate(
    model=model,
    prompt=prompt,
    size="1024x1024",
    quality="standard",
    n=1,)
    return {'response':response.data[0].url}