from sqlalchemy import Table, Column
from sqlalchemy.sql.sqltypes import Integer, String, Float, DateTime
from sqlalchemy.sql import func
from config.db import meta, engine, conn
from schemas.stocks import Stocks, Transaction, Historical_price
from uuid import uuid4 as uuid
import datetime


# This table contains all the stocks bought 
stocks = Table("stocks", meta,
    Column("id", String(50), primary_key=True), 
    Column("user", String(20)),
    Column("symbol", String(10)),
    Column("quantity", Float),
    Column("total_price", Float),
    Column("first_bought_at", DateTime, server_default=func.now()),
    Column("last_bought_at", DateTime),
)

# This table contains all the transactions (buys/sells)
transactions = Table("transactions",meta,
    Column("id", String(50), primary_key=True), 
    Column("transaction_type", String(5)),
    Column("user",String(20)),
    Column("symbol", String(10)),
    Column("quantity",Float),
    Column("price",Float),
    Column("date",DateTime)
)

# This table
historical_prices = Table("historical_prices",meta,
    Column("id", String(50), primary_key=True), 
    Column("symbol", String(10)),
    Column("price", Float),
    Column("date",DateTime)
)

## <START Functions for Stocks model
# Get all stocks
def get_stocks_by_user(user:str):
    """Return the list of stocks by user"""
    return conn.execute(stocks.select().where(stocks.c.user==user)).fetchall()

# Get one stock by symbol
def get_stocks_by_symbol(user:str,symbol:str):
    """Return one stock by user and symbol"""
    try:
        return conn.execute(stocks.select().where(stocks.c.user==user,stocks.c.symbol==symbol)).first()
    except Exception as err:
        raise err

# Create new stock
def create_stock(new_stock:Stocks,price:float):
    """Return True if the stock is created or updated successfully, otherwise return the error"""
    try:
        transaction_type = 'buy'
        current_stock = get_stocks_by_symbol(new_stock.user,new_stock.symbol)
        # If the stock already exist, we need to update
        if current_stock:
            new_stock.total_price = current_stock.total_price + price * new_stock.quantity
            new_stock.quantity += current_stock.quantity
            new_stock.last_bought_at = datetime.datetime.now()
            date = new_stock.last_bought_at
            conn.execute(stocks.update().values(quantity=new_stock.quantity,total_price=new_stock.total_price,last_bought_at=date).where(stocks.c.user == new_stock.user, stocks.c.symbol==new_stock.symbol))
        else:
            new_stock.first_bought_at = datetime.datetime.now()
            new_stock.total_price = price * new_stock.quantity
            date = new_stock.first_bought_at
            conn.execute(stocks.insert().values(new_stock.dict()))
        # Create the new 'buy' transaction
        create_transaction(new_stock,transaction_type,price,date)
        # Create the first register for the historic price
        create_historical_price(new_stock.symbol,price,date) 
        return True
    except Exception as err:
        print(err)
        return err

# Delete stock
def delete_stock(user:str,stock:Stocks,new_price:float,new_quantity:float):
    try:
        transaction_type = 'sell'
        conn.execute(stocks.delete().where(stocks.c.user == user, stocks.c.symbol == stock.symbol))
        create_transaction(stock, transaction_type, new_price, datetime.datetime.now(),new_quantity)
    except Exception as err:
        raise err

# Update stock
def update_stock(user:str,stock:Stocks,quantity_to_sell:float,price_to_update:float,new_price:float):
    try:
        transaction_type = 'sell'
        quantity_to_update = stock.quantity - quantity_to_sell
        conn.execute(stocks.update().values(quantity=quantity_to_update,total_price=price_to_update).where(stocks.c.user == user, stocks.c.symbol==stock.symbol))
        # In Transactions is saved the quantity to sell 
        create_transaction(stock, transaction_type, new_price, datetime.datetime.now(),quantity_to_sell)
        return True
    except Exception as err:
        print(err)
        raise err

## END> Functions for 'stocks' model


## <START Functions for 'transactions' model 
def create_transaction(stock:Stocks,transaction_type:str,price:float,date:datetime.datetime,new_quantity:float=None):
    new_trans = Transaction(
        id=str(uuid()),
        transaction_type=transaction_type,
        user=stock.user,
        symbol=stock.symbol,
        quantity=stock.quantity if new_quantity is None else new_quantity,
        price=price,
        date=date
    )
    return conn.execute(transactions.insert().values(new_trans.dict()))
## END> Functions for 'transactions' model 


## <START Functions for 'historical_prices' model 
def create_historical_price(symbol:str,price:float,date:datetime.datetime):
    new_historical_price = Historical_price(
        id=str(uuid()),
        symbol=symbol,
        price=price,
        date=date
    )
    return conn.execute(historical_prices.insert().values(new_historical_price.dict()))    


def get_today_historical_prices_per_symbol(symbol:str):
    tday = datetime.date.today()
    return conn.execute(historical_prices.select().where(historical_prices.c.symbol == symbol, historical_prices.c.date > tday)).fetchall()

## END> Functions for 'historical_prices' model 

# For creating the tables in the DB
meta.create_all(engine)