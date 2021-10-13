# Vest Endpoints with FastAPI

This project has been developed with Python 3.8, FastAPI as a backend framework and MySQL as database engine.
The main libraries used are:
- Fast API
- Uvicorn: For heping with the app execution
- sqlalchemy: For handling DB connection and queries
- pymysql: For connecting to MySQL Database
- uuid: For generating automatic uuid
- requests: For execute http requests
- fastapi-utils: For getting more functionalities

The purpouse of this API is develop 3 endpoints:
1. Buy or sell a number of shares of a certain stock via its symbol (e.g. 3 shares of AAPL)
2. Get a list of the stocks you are holding
3. Get the historic price of a stock you bought in 1-hour intervals

## Project structure

The project structure is the following:

```
src/
├── config/
│   └── db.py
│   └── settings.py
├── models/
│   └── stocks.py
├── schemas
│   └── stocks.py
├── app.py
├── requirements.txt
```

Where:
- config: Directory where the configuration and global files are
- config/db.py: File that contains the database configuration
- config/settings.py: File that contains the global variables
- models: Directory where the models are
- models/stocks.py: File where are defined the used models
- schemas: Directory where the schemas are
- schemas/stocks.py: File where are defined the used schemas for the data.
- app.py: File where are the endpoints
- requirements.txt: File where are all the dependencies


## Installation

### 1. Install Python
If you don't have python installed, downloaded and installed from the [Official page](https://www.python.org/downloads/)

### 2. Create virtual environment
Install the virtualenv library

```
pip install virtualenv
```

Navigate to the folder where you want to create the virtual environment and create it with the following command.
```
virtualenv vest-test
```

Once the virtual environment has been created, it must be activated.
```
cd vest-test/Scripts
activate
```

### 3. Install necessary libraries
```
pip install -r requirements.txt
```

### 4. Create the database "vest-test"
You will need a MySQL engine. You can install MySQL from the [official page](https://dev.mysql.com/downloads/mysql/) or install it as a container with Docker.

When the database engine is up, then create the database "vest-test".

Also, you could connect to a remote MySQL database. 

Make sure the the DB connection string is pointing to your own environment. This is in the file *config/settings.py*

```py
SQLALCHEMY_DATABASE_URI: Optional[str] = "mysql+pymysql://root:@localhost:3306/vest-test"
```

### 5. Start the application
With the virtual environment activated, execute the following command for start the application:

```
uvicorn app:app --reload
```

Navigate to the docs page for testing the endpoints: 
http://127.0.0.1:8000/docs

## Stay in touch
- Author - Almendra Estrada
- LinkedIn - [https://www.linkedin.com/in/almendra-estrada/](https://www.linkedin.com/in/almendra-estrada//)