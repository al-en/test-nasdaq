from pydantic import BaseSettings, AnyHttpUrl
from typing import List, Optional

class Settings(BaseSettings):
    # Here is defined the list of URLs allowed for CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    SQLALCHEMY_DATABASE_URI: Optional[str] = "mysql+pymysql://root:@localhost:3306/vest-test"
    
    #API_NASDAQ_URL: str = "https://api.nasdaq.com/api/quote/AAPL/info?assetclass=stocks"
    API_NASDAQ_URL: str = "https://api.nasdaq.com/api/quote/{}/info"
    # User id for testing purposes 
    GLOBAL_USER_ID = "123321"


settings = Settings()