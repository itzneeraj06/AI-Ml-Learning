import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = ''
PARAGRAPH_FILE = "paragraphsNew.json"
TODAY_DATE = str(__import__("datetime").date.today())
