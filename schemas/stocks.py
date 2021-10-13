from typing import Optional, List
from pydantic import BaseModel
import datetime


class NasdaqPrimaryData(BaseModel):
    lastSalePrice: Optional[str]
    netChange: Optional[str]
    percentageChange: Optional[str]
    deltaIndicator: Optional[str]
    lastTradeTimestamp: Optional[str]
    isRealTime: Optional[bool]

class NasdaqData(BaseModel):
    symbol: Optional[str]
    companyName: Optional[str]
    stockType: Optional[str]
    exchange: Optional[str]
    isNasdaqListed: Optional[bool]
    isNasdaq100: Optional[bool]
    isHeld: Optional[bool]
    primaryData: Optional[NasdaqPrimaryData]
    secondaryData: Optional[NasdaqPrimaryData]
    marketStatus: Optional[str] 
    assetClass: Optional[str]
    tradingHeld: Optional[str]
    complianceStatus: Optional[str]

class NasdaqStatus(BaseModel):
    rCode: int
    bCodeMessage: Optional[List]
    developerMessage: Optional[str]

class NasdaqResponse(BaseModel):
    data: Optional[NasdaqData]
    message: Optional[str]
    status: NasdaqStatus


class Stocks(BaseModel):
    id: str
    user: str
    symbol: str
    quantity: float
    total_price: Optional[float]
    first_bought_at: Optional[datetime.datetime]
    last_bought_at: Optional[datetime.datetime]


class Transaction(BaseModel):
    id: str
    transaction_type: str
    user: str
    symbol: str
    quantity: float
    price: float
    date: Optional[datetime.datetime]


class Historical_price(BaseModel):
    id: str
    symbol: str
    price: str
    date: datetime.datetime