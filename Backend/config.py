import os
from dotenv import load_dotenv

load_dotenv()


def get_config():
    upload_folder = os.path.join(os.getcwd(), "upload")
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    return {
        "SECRET_KEY": os.getenv("SECRET_KEY", "your-default-secret"),
        "UPLOAD_FOLDER": upload_folder,
        "MAX_CONTENT_LENGTH": int(os.getenv("MAX_CONTENT_LENGTH", 50 * 1024 * 1024)),
        # Cognito and other configurations
        "COGNITO_REGION": os.getenv("COGNITO_REGION"),
        "COGNITO_USER_POOL_ID": os.getenv("COGNITO_USER_POOL_ID"),
        "COGNITO_USERPOOL_ID" : os.getenv("COGNITO_USER_POOL_ID"),
        "COGNITO_CLIENT_ID": os.getenv("COGNITO_CLIENT_ID"),
        "COGNITO_CLIENT_SECRET": os.getenv("COGNITO_CLIENT_SECRET"),
        "COGNITO_DOMAIN": os.getenv("COGNITO_DOMAIN"),
        "COGNITO_REDIRECT_URI": os.getenv("COGNITO_REDIRECT_URI"),
        "COGNITO_SIGNOUT_URI": os.getenv("COGNITO_SIGNOUT_URI"),
        "ERROR_REDIRECT_URI": os.getenv("ERROR_REDIRECT_URI"),
        "DEBUG": True,
        "SESSION_COOKIE_SECURE":True,
        "SESSION_COOKIE_SECURE":True,
        "SESSION_COOKIE_HTTPONLY":True,
        "SESSION_COOKIE_SAMESITE":"Lax",
        "secret_key" : os.urandom(24)
    }
