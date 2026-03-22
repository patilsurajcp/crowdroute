from dotenv import load_dotenv
import os

load_dotenv()
key = os.getenv('OPENWEATHER_API_KEY')

if key:
    print('Key found: ' + key[:6] + '...')
else:
    print('Key is None - .env not loading')