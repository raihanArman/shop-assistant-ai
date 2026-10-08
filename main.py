from fastapi import FastAPI

app=FastAPI(title="Shop Assistant 2.0")

@app.get("/")
async def root():
    return {"message":"Welcome to ShopAssistant 2.0"}

def main():
    print("Hello from shop-assistant-ai!")


if __name__ == "__main__":
    main()
