#!/usr/bin/env python
"""
Script to help convert .env file to Heroku config vars
Usage: python convert_env_to_heroku.py
"""

import os
from dotenv import load_dotenv

def convert_env_to_heroku():
    """Convert .env variables to Heroku config set commands"""
    
    # Load environment variables from .env file
    if not os.path.exists('.env'):
        print("Error: .env file not found!")
        print("Please create a .env file based on .env.example")
        return
    
    load_dotenv('.env')
    
    # Define the environment variables we want to set on Heroku
    heroku_vars = [
        'SECRET_KEY',
        'DEBUG',
        'ALLOWED_HOSTS',
        'EMAIL_HOST',
        'EMAIL_PORT',
        'EMAIL_HOST_USER',
        'EMAIL_HOST_PASSWORD',
        'GOOGLE_OAUTH2_CLIENT_ID',
        'GOOGLE_OAUTH2_CLIENT_SECRET',
        'RECAPTCHA_PUBLIC_KEY',
        'RECAPTCHA_PRIVATE_KEY',
        'IMGBB_API_KEY'
    ]
    
    print("# Heroku config commands:")
    print("# Copy and paste these commands to set your Heroku config vars\n")
    
    for var in heroku_vars:
        value = os.getenv(var)
        if value:
            # Escape quotes in the value
            escaped_value = value.replace('"', '\\"')
            print(f'heroku config:set {var}="{escaped_value}"')
        else:
            print(f'# {var} not found in .env file')
    
    print("\n# Remember to also update ALLOWED_HOSTS with your actual Heroku app domain:")
    print("# heroku config:set ALLOWED_HOSTS=\"your-app-name.herokuapp.com\"")

if __name__ == "__main__":
    convert_env_to_heroku()
