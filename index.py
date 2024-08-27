from fastapi import FastAPI, HTTPException
import requests

app = FastAPI(
    title="Shopify API",
    description="API to interact with Shopify",
    version="1.0.0",
    servers=[
        {
            "url": "https://dashboard-shopify-backend2.onrender.com",
            "description": "Shopify API"
        }
        
    ]
)

@app.get("/orders",response_description="The URL to fetch orders from shopify")
async def get_shopify_orders():
    """Fetches and return shopify order from the specifeid URL
    This endpoint make a fetch call to the url and get the orders from the shopify which is then converted to json and return as a json"""
    url = "https://dashboard-shopify-backend.onrender.com/shopify/orders"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an exception for 4XX/5XX responses
        print(response.json())
        return response.json()  # Return the JSON response from Shopify
    except requests.exceptions.HTTPError as http_err:
        raise HTTPException(status_code=response.status_code, detail=str(http_err))
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))

