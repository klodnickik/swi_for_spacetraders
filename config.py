from dotenv import load_dotenv
load_dotenv()

import logging
import os
logging.basicConfig(encoding='utf-8', level=logging.DEBUG)

bearer_token = os.environ.get('BEARER_TOKEN')
SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'