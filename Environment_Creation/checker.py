from dotenv import load_dotenv
import os

load_dotenv("5g.env")  # Load the .env file

# Print all loaded environment variables
for key, value in os.environ.items():
    if "srsRAN" in key:  # Filter only your related variables
        print(f"{key} = {value}")
