from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import uuid4

app = FastAPI(title="API - Motos & Estoques")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

class MotoIn(BaseModel):
    title: str
    subTitle: str
    plate: str
    stockId: Optional[str] = None

class MotoOut(MotoIn):
    id: str = Field(default_factory=lambda: uuid4().hex)

class StockIn(BaseModel):
    name: str
    quantity: int = Field(ge=0)
    location: Optional[str] = ""

class StockOut(StockIn):
    id: str = Field(default_factory=lambda: uuid4().hex)

class TokenIn(BaseModel):
    token: str
    platform: Optional[str] = None
    userId: Optional[str] = None
    deviceId: Optional[str] = None

class TokenOut(TokenIn):
    id: str = Field(default_factory=lambda: uuid4().hex)

MOTOS: List[MotoOut] = []
STOCKS: List[StockOut] = []
TOKENS: List[TokenOut] = []

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/motos", response_model=List[MotoOut])
def list_motos():
    return MOTOS

@app.post("/motos", response_model=MotoOut, status_code=201)
def create_moto(m: MotoIn):
    if m.stockId and not any(s.id == m.stockId for s in STOCKS):
        raise HTTPException(status_code=400, detail="Estoque inválido")
    out = MotoOut(**m.dict())
    MOTOS.insert(0, out)
    return out

@app.put("/motos/{moto_id}", response_model=MotoOut)
def update_moto(moto_id: str, changes: MotoIn):
    if changes.stockId and not any(s.id == changes.stockId for s in STOCKS):
        raise HTTPException(status_code=400, detail="Estoque inválido")
    for i, item in enumerate(MOTOS):
        if item.id == moto_id:
            new_item = MotoOut(id=item.id, **changes.dict())
            MOTOS[i] = new_item
            return new_item
    raise HTTPException(status_code=404, detail="Moto não encontrada")

@app.delete("/motos/{moto_id}")
def delete_moto(moto_id: str):
    global MOTOS
    before = len(MOTOS)
    MOTOS = [m for m in MOTOS if m.id != moto_id]
    if len(MOTOS) == before:
        raise HTTPException(status_code=404, detail="Moto não encontrada")
    return {"ok": True}

@app.get("/stocks", response_model=List[StockOut])
def list_stocks():
    return STOCKS

@app.get("/stocks/{stock_id}", response_model=StockOut)
def get_stock(stock_id: str):
    for s in STOCKS:
        if s.id == stock_id:
            return s
    raise HTTPException(status_code=404, detail="Estoque não encontrado")

@app.post("/stocks", response_model=StockOut, status_code=201)
def create_stock(s: StockIn):
    out = StockOut(**s.dict())
    STOCKS.insert(0, out)
    return out

@app.put("/stocks/{stock_id}", response_model=StockOut)
def update_stock(stock_id: str, changes: StockIn):
    for i, item in enumerate(STOCKS):
        if item.id == stock_id:
            new_item = StockOut(id=item.id, **changes.dict())
            STOCKS[i] = new_item
            return new_item
    raise HTTPException(status_code=404, detail="Estoque não encontrado")

@app.delete("/stocks/{stock_id}")
def delete_stock(stock_id: str):
    global STOCKS
    before = len(STOCKS)
    STOCKS = [s for s in STOCKS if s.id != stock_id]
    if len(STOCKS) == before:
        raise HTTPException(status_code=404, detail="Estoque não encontrado")
    return {"ok": True}

@app.get("/push-tokens", response_model=List[TokenOut])
def list_push_tokens():
    return TOKENS

@app.post("/push-tokens", response_model=TokenOut, status_code=201)
def register_push_token(t: TokenIn):
    if not t.token or len(t.token) < 10:
        raise HTTPException(status_code=400, detail="Token inválido")
    for i, item in enumerate(TOKENS):
        if item.token == t.token or (t.userId and item.userId == t.userId) or (t.deviceId and item.deviceId == t.deviceId):
            updated = TokenOut(id=item.id, **t.dict())
            TOKENS[i] = updated
            return updated
    out = TokenOut(**t.dict())
    TOKENS.insert(0, out)
    return out

@app.delete("/push-tokens/{token_id}")
def delete_push_token(token_id: str):
    global TOKENS
    before = len(TOKENS)
    TOKENS = [x for x in TOKENS if x.id != token_id]
    if len(TOKENS) == before:
        raise HTTPException(status_code=404, detail="Token não encontrado")
    return {"ok": True}
