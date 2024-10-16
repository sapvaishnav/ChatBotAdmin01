from sys import exit
from decouple import config
from app import create_app
 
# Load configuration for the app
#DEBUG =True # config('DEBUG', default=True, cast=bool)
#get_config_mode = 'Development' if DEBUG else 'Production'  # Updated line

# Create the application instance
#app_config = config_dict[get_config_mode]  # Ensure you define config_dict in config.py
app = create_app()

# Run the application
if __name__ == "__main__":
    app.run(port=5001, debug=True)  # Start the application with debug mode
