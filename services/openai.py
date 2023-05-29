import openai
import config
import requests
from PIL import Image
from io import BytesIO
from config import Config
from aiohttp import ClientSession

openai.api_key = Config().OPENAI_TOKEN

def url_to_png(url):
    response = requests.get(url)
    byte_array = BytesIO(response.content)
    
    # Read the image file from byte array and resize it
    image = Image.open(byte_array)
    width, height = 256, 256
    image = image.resize((width, height))
    # image = image.convert('RGBA')

    # Convert the image to a BytesIO object
    byte_stream = BytesIO()
    image.save(byte_stream, format='PNG')
    return byte_stream.getvalue()


class OpenAIService:
    __instance = None

    @staticmethod 
    def getInstance():
        if OpenAIService.__instance == None:
            OpenAIService()
        return OpenAIService.__instance

    def __init__(self):
        self.openai = openai
        
        if OpenAIService.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            OpenAIService.__instance = self

    def create_image(self, prompt): 
        result = openai.Image.create(
            prompt=prompt,
            n=1,
            size="256x256"
        )

        return result['data'][0]['url']
    
    def edit_image(self, url: str, prompt: str):
        result = openai.Image.create_edit(
            image=url_to_png(url),                
            prompt=prompt,
            n=1,
            size="256x256",
            response_format="url"
        )
        return result['data'][0]['url']
    
    def create_variant(self, url: str):
        result = openai.Image.create_variation(
            image=url_to_png(url),            
            n=1,
            size="256x256",
            response_format="url"
        )
        return result['data'][0]['url']
    
    
    async def chat_gpt(self, gpt_messages, max_tokens=2000):
        openai.aiosession.set(ClientSession())
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=gpt_messages,
            max_tokens=max_tokens
        )
        await openai.aiosession.get().close()

        return response.choices[0].message.content.strip()

    
    def summarize_chat(self, text, style="a conversational analyst"):
        prompt = "Summarize the following conversation: "

        gpt_messages = [
            {"role": "system", "content": f"You are a conversation summarizer who answers in the style of {style}"},
            {"role": "user", "content": f"{prompt}\n\n \"{text}\"\n\n - in the style of {style}" }
        ]

        return self.chat_gpt(gpt_messages)
    
    
    def summarize_chat_review(self, text):
        prompt = "Summarize the following conversation: "

        gpt_messages = [
            {"role": "system", "content": f"You are a conversation summarizer who will create a report for a chat log. The log should include Key topics discussed an overall summary of what was talked about and the mood of the conversation."},
            {"role": "user", "content": f"{prompt}\n\n \"{text}\"" }
        ]

        return self.chat_gpt(gpt_messages)
    
    def executive_summary(self, text):
        prompt = "Create a rap in the style of Eminem about this group chat using the following as context: "

        gpt_messages = [
            {"role": "system", "content": f"You are a conversation summarizer will create an executive summary of daily chatlog summaries."},
            {"role": "user", "content": f"{prompt}\n\n \"{text}\"" }
        ]

        return self.chat_gpt(gpt_messages)
        
    
    def create_image_prompt(self, text):        
        gpt_messages = [
            {"role": "system", "content": "You are a helpful assistant to take some text and generate a prompt to use with the Dall-E api to generate an accompanying image."},
            {"role": "user", "content": f"{text}" }
        ]

        return self.chat_gpt(gpt_messages)