from fastapi import APIRouter, HTTPException, Request


adminRouter = APIRouter(prefix="/admin", tags=["Admin"])