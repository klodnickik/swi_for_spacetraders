from dotenv import load_dotenv
load_dotenv()

import logging
import os
logging.basicConfig(encoding='utf-8', level=logging.DEBUG)
SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'