"""
Python Web Application Client
Demonstrates placing orders via AWS API Gateway connected to Lambda and DynamoDB
"""

import sys
import logging
from client import APIGatewayClient
from config import API_ENDPOINT, SAMPLE_ORDER, DEBUG

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_banner():
    """Print application banner"""
    print("\n" + "="*60)
    print("  AWS Serverless Order Application")
    print("  API Gateway → Lambda → DynamoDB")
    print("="*60 + "\n")


def interactive_order():
    """Interactive mode to create custom orders"""
    print("\n--- Create Custom Order ---")
    
    order_data = {
        "items": [],
        "paymentMethod": input("Payment Method (card/bank/paypal) [card]: ").strip() or "card",
        "customerEmail": input("Customer Email: ").strip() or "customer@example.com"
    }

    while True:
        print("\nAdd Item to Order:")
        product_id = input("Product ID: ").strip()
        if not product_id:
            break

        try:
            qty = int(input("Quantity: ").strip() or "1")
            price = float(input("Price: ").strip() or "0")

            order_data["items"].append({
                "productId": product_id,
                "qty": qty,
                "price": price
            })
            print(f"✓ Added {qty}x {product_id}")

        except ValueError:
            print("✗ Invalid quantity or price")

    if not order_data["items"]:
        print("No items added. Using sample order.")
        return SAMPLE_ORDER

    return order_data


def display_response(response):
    """Display formatted response"""
    print("\n" + "-"*60)
    print("Response from API Gateway:")
    print("-"*60)
    for key, value in response.items():
        print(f"  {key}: {value}")
    print("-"*60 + "\n")


def main():
    """Main application entry point"""
    print_banner()

    # Check if API endpoint is configured
    if "YOUR_API_ID" in API_ENDPOINT:
        logger.error("❌ API Gateway endpoint not configured!")
        print("\nPlease configure your API Gateway endpoint:")
        print("1. Edit the .env file")
        print("2. Or set the API_GATEWAY_URL environment variable")
        print("\nExample:")
        print("  API_GATEWAY_URL=https://abc123.execute-api.us-east-1.amazonaws.com")
        return 1

    logger.info(f"📡 Using API Endpoint: {API_ENDPOINT}")

    try:
        # Create API Gateway client
        client = APIGatewayClient()

        while True:
            print("\n--- Main Menu ---")
            print("1. Place Sample Order")
            print("2. Place Custom Order")
            print("3. Check Order Status")
            print("4. Exit")

            choice = input("\nSelect option (1-4): ").strip()

            if choice == "1":
                # Place sample order
                print("\n📦 Placing sample order...")
                response = client.place_order(SAMPLE_ORDER)
                display_response(response)

            elif choice == "2":
                # Place custom order
                order_data = interactive_order()
                print("\n📦 Placing custom order...")
                response = client.place_order(order_data)
                display_response(response)

            elif choice == "3":
                # Check order status
                order_id = input("Enter Order ID: ").strip()
                if order_id:
                    print(f"\n🔍 Checking status for order {order_id}...")
                    response = client.get_order_status(order_id)
                    display_response(response)
                else:
                    print("Order ID cannot be empty")

            elif choice == "4":
                print("\n👋 Goodbye!")
                break

            else:
                print("Invalid option. Please select 1-4.")

        client.close()
        return 0

    except KeyboardInterrupt:
        print("\n\n⚠️  Application interrupted by user")
        return 0

    except Exception as e:
        logger.error(f"❌ Application error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
