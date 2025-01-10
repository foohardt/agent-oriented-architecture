from openai import Client

from .settings import settings

openai_client = Client(api_key=settings.OAI_API_KEY)
