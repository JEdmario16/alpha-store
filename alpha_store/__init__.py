# Description: This file contains a simple hack to run the app from the command line. 
# It adds the parent directory to the path so we can import the alpha_store package. 

import sys
import os

# Add the parent directory to the path so we can import the alpha_store package 
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


if __name__ == "__main__":
    
    from alpha_store.main import create_app

    create_app().run(debug=True)
