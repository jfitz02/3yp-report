# Joshua Fitzmaurice (U2008325) 3rd year Computer Science Dissertation
## testing_models
This folder contains the code used to create and test various machine learning models for the classification problem in this
project. Almost all training and testing was performed in jupyter notebooks. The only caveat to this is the code used to 
fetch the data from the database, as well as the code used to train the final model. This is due to it needing to be run
on DCS batch compute nodes.

## code
To run the Python application.  
1. CD into the code directory
2. (optionally) set up virtual environment
3. Install the requirements using `pip install -r requirements.txt`
4. CD into the src directory
5. run the application using `python application.py`