from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from typing import List, Optional, Union

# Pydantic models for response

class Address(BaseModel):
    full_name: Optional[str]
    street_address: Optional[str]
    sector: Optional[str]
    nearest_place: Optional[str]
    city: Optional[str]
    province: Optional[str]
    country: Optional[str]
    country_code: Optional[str]

class CustomerDetails(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]

class OrderResponse(BaseModel):
    order_number: int
    price: str
    address: Address
    phone_number: Optional[str]
    customer_details: CustomerDetails
    tags: Optional[str]

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

@app.get("/orders", response_model=List[OrderResponse], response_description="Fetch Shopify orders with specific details")
async def get_shopify_orders():
    """Fetches and returns Shopify orders from the specified URL,
    filtering to include only specific fields."""
    
    url = "https://dashboard-shopify-backend.onrender.com/shopify/orders"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an exception for 4XX/5XX responses

        # Get the response data
        data = response.json()

        # Extract the orders list from the response
        orders = data.get("orders", [])

        if not isinstance(orders, list):
            raise HTTPException(status_code=500, detail="Unexpected response format: 'orders' is not a list")

        # Filter the orders to include only the specified fields
        filtered_orders = []
        for order in orders:
            # Extract relevant note attributes
            note_attributes = {item["name"]: item["value"] for item in order.get("note_attributes", [])}
            
            filtered_order = {
                "order_number": order.get("order_number"),
                "price": order.get("current_total_price"),
                "address": {
                    "full_name": note_attributes.get("Full Name"),
                    "street_address": note_attributes.get("Area / Mohalla / Basti"),
                    "sector": note_attributes.get("Sector / BLock"),
                    "nearest_place": note_attributes.get("Nearest Place"),
                    "city": note_attributes.get("CITY / DISTRICT"),
                    "province": note_attributes.get("Tahseel(تہسیل) / Postal Code(Optional)"),
                    "country": order.get("billing_address", {}).get("country"),
                    "country_code": order.get("billing_address", {}).get("country_code"),
                },
                "phone_number": note_attributes.get("Phone number"),
                "customer_details": {
                    "first_name": order.get("customer", {}).get("default_address", {}).get("first_name"),
                    "last_name": order.get("customer", {}).get("default_address", {}).get("last_name"),
                    "email": order.get("customer", {}).get("email"),
                },
                "tags": order.get("tags"),
            }
            filtered_orders.append(filtered_order)

        return filtered_orders  # Return the filtered orders

    except requests.exceptions.HTTPError as http_err:
        raise HTTPException(status_code=response.status_code, detail=str(http_err))
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))
