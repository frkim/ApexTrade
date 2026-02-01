"""API v1 router combining all sub-routers."""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.backtests import router as backtests_router
from app.api.v1.market_data import router as market_data_router
from app.api.v1.portfolios import router as portfolios_router
from app.api.v1.strategies import router as strategies_router
from app.api.v1.trades import router as trades_router
from app.api.v1.users import router as users_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
router.include_router(users_router, prefix="/users", tags=["Users"])
router.include_router(strategies_router, prefix="/strategies", tags=["Strategies"])
router.include_router(backtests_router, prefix="/backtests", tags=["Backtests"])
router.include_router(portfolios_router, prefix="/portfolios", tags=["Portfolios"])
router.include_router(trades_router, prefix="/trades", tags=["Trades"])
router.include_router(market_data_router, prefix="/market-data", tags=["Market Data"])
