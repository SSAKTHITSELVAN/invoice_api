from fastapi import FastAPI
from app.database import Base, engine
from app.models.users import Users
from app.models.companies import Companies
from app.models.products import Products
from app.models.invoices import Invoices
from app.models.invoice_items import InvoiceItems
from app.api.endpoints import users, companies, customers, products, invoices
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

@app.get('/api')
def test_route():
    return {'message': 'Invoice API working well'}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],          # Allow all HTTP methods
    allow_headers=["*"],          # Allow all headers
)

app.include_router(users.router, prefix='/api', tags=['Users'])
app.include_router(companies.router, prefix='/api', tags=['Companies'])
app.include_router(customers.router, prefix='/api', tags=['Customers'])
app.include_router(products.router, prefix='/api', tags=['Products'])
app.include_router(invoices.router, prefix='/api', tags=['Invoices'])
# app.include_router(invoice_items., prefix='/api', tags=['Invoices'])

@app.on_event('startup')
async def create_db_tables():
    async with engine.begin() as conn:
        print("----&->   ", Base.metadata.tables.keys())
        await conn.run_sync(Base.metadata.create_all)