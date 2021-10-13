from fastapi import FastAPI, HTTPException, BackgroundTasks
from config.settings import settings
from schemas.stocks import NasdaqResponse, Stocks
from models import stocks
from typing import List
from pydantic import parse_obj_as
from uuid import uuid4 as uuid
#Utils
from fastapi_utils.tasks import repeat_every

import requests
import datetime
import time

app = FastAPI(
    title="Vest test API",
    description="",
    version="1.0.0"
)

# Buy / Sell shares
@app.post("/shares/{transaction_type}",status_code=200)
def shares_transactions(transaction_type:str,symbol:str,shares_qty:float):
    # If path parameter is 'buy'
    if transaction_type == "buy":
        try:
            nasdaq_data: NasdaqResponse = get_nasdaq_data(symbol)
            #print(nasdaq_data)
            if nasdaq_data.status.rCode == 400:
                raise HTTPException(status_code=400,detail=nasdaq_data)
            if nasdaq_data.status.rCode == 200:
                bought = buy_shares(nasdaq_data,shares_qty)
                # If stock was created or updated
                if bought == True:
                    return {
                        "message": "Share bought"
                    }
                else:
                    raise HTTPException(status_code=400,detail=bought)
        except Exception as err:
            print("Excepcion en shares_transactions", str(err))
            raise HTTPException(status_code=400,detail=str(err))
    # If path parameter is 'sell'
    elif transaction_type == "sell":
        print("sell shares")
        try:
            nasdaq_data = get_nasdaq_data(symbol)
            if nasdaq_data.status.rCode == 200:
                return sell_shares(nasdaq_data,symbol,shares_qty)
                
        except Exception as err:
            print(err)
            return HTTPException(status_code=400,detail=str(err))
    # If the path parameter is not a valid one
    else:
        print("Transaction not allowed. Use 'buy' or 'sell' instead.")
        raise HTTPException(status_code=400,detail="Transaction not allowed. Use 'buy' or 'sell' instead.")


# Get Holding Stocks
@app.get("/holding-stocks")
def get_holding_stocks():
    try:
        holding_list:List = []
        stocks_list:List[Stocks] = stocks.get_stocks_by_user(settings.GLOBAL_USER_ID)
        for item in stocks_list:
            item = parse_obj_as(Stocks, item)
            nasdaq_data: NasdaqResponse = get_nasdaq_data(item.symbol)
            price=float(nasdaq_data.data.primaryData.lastSalePrice.replace("$", ""))
            historical_prices = stocks.get_today_historical_prices_per_symbol(item.symbol)
            prices_list = [ p['price'] for p in historical_prices]
            new_item = {}

            if len(prices_list) > 0:
                daily_prices = {
                    "max":max(prices_list),
                    "min":min(prices_list),
                    "avg":sum(prices_list) / len(prices_list)
                }
            else:
                daily_prices = {
                    "max":None,
                    "min":None,
                    "avg":None
                }

            new_item['symbol'] = item.symbol
            new_item['held_shares'] = item.quantity
            new_item['current_value'] = price * item.quantity 
            new_item['profit_loss'] = get_profit_loss_percentage(price, item.total_price, item.quantity)
            new_item['daily_prices'] = daily_prices
            
            holding_list.append(new_item)
        return holding_list
    except Exception as err:
        print(err)
        raise HTTPException(status_code=400,detail="Error getting holding stocks")


# Schedule 
# Every hour the price of the stocks will be registered
#@app.on_event("startup")
@repeat_every(seconds=60*60)
@app.get("/register_historical_prices",tags=['Schedule'])
def register_historical_price():
    """Register the current price of the stocks already bought"""
    try:
        print("register_historical_price execution")
        stocks_list:List[Stocks] = stocks.get_stocks_by_user(settings.GLOBAL_USER_ID)
        for s in stocks_list:
            nasdaq_data: NasdaqResponse = get_nasdaq_data(s.symbol)
            price=float(nasdaq_data.data.primaryData.lastSalePrice.replace("$", ""))
            stocks.create_historical_price(s.symbol, price, datetime.datetime.now())
        return {
            "message": "Historical prices registered"
        }
    except Exception as err:
        print("An error has occurred trying to register historic price ",err)
        raise HTTPException(status_code=400,detail=str(err))


# Nasdaq API
def get_nasdaq_data(symbol:str):
    """Return the response obtained from the Nasdaq API"""
    try:
        headers = {
            "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"
        }
        response = requests.get(settings.API_NASDAQ_URL.format(symbol),params={"assetclass":"stocks"},headers=headers,timeout=10)
        #return response.json()
        return parse_obj_as(NasdaqResponse, response.json())
    except Exception as err:
        print("An error has occurred", err)
        raise HTTPException(status_code=400,detail="Error getting data from nasdaq API")


def buy_shares(nasdaq_data:NasdaqResponse,shares_qty:float):
    try:
        user_id = settings.GLOBAL_USER_ID
        price=float(nasdaq_data.data.primaryData.lastSalePrice.replace("$", ""))
        new_stock = Stocks(
            id=str(uuid()),
            user=user_id,
            symbol=nasdaq_data.data.symbol,
            quantity=shares_qty,
        )
        #print("new_stock",new_stock)
        return stocks.create_stock(new_stock,price) 
    except Exception as err:
        print(err)
        raise err


def sell_shares(nasdaq_data:NasdaqResponse,symbol:str,quantity_to_sell:int):
    """
    When a share is sold, the quantity available decrease and the sell price is substract from the money invested.
    When all the shares are sold, it is deleted from the list of stocks.
    The sell transaction is saved in the transactions table.
    """
    print("in sell_shares function")
    try:
        user_id = settings.GLOBAL_USER_ID
        current_stock = stocks.get_stocks_by_symbol(user_id,symbol)
        print("current_stock",current_stock)
        if current_stock:
            new_price = float(nasdaq_data.data.primaryData.lastSalePrice.replace("$", ""))
            if current_stock.quantity < quantity_to_sell:
                print("current_stock.quantity < quantity_to_sell")
                return {"message": "Not enough shares to sell"}
        
            elif current_stock.quantity > quantity_to_sell:
                print("current_stock.quantity > quantity_to_sell")
                price_to_update = current_stock.total_price - (quantity_to_sell * new_price)
                stocks.update_stock(user_id, current_stock, quantity_to_sell, price_to_update, new_price)
            elif current_stock.quantity == quantity_to_sell:
                print("current_stock.quantity == quantity_to_sell")
                stocks.delete_stock(user_id, current_stock, new_price,quantity_to_sell)
            return {"message":"Shares sold"}
        
        else:
            raise Exception("Current stock not found")
    except Exception as err:
        print("Error in sell_shares",err)
        raise err


# Functions for /holding-stocks endpoint
def get_profit_loss_percentage(current_unit_price:float,my_total_price:float,quantity:float):
    """Return the profit or loss percentage of how much the stock price has changed since you bought it"""
    try:   
        print(current_unit_price,quantity,my_total_price)
        current_total_price = quantity * current_unit_price
        percentage = (current_total_price - my_total_price)/current_total_price * 100
        return percentage
    except Exception as err:
        print(err)
        return None
