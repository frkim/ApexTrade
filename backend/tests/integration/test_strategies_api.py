"""Integration tests for strategies API endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.strategy import Strategy
from app.models.user import User


class TestStrategiesAPI:
    """Test cases for strategies API endpoints."""

    @pytest.mark.asyncio
    async def test_create_strategy(
        self,
        async_client: AsyncClient,
        auth_headers: dict[str, str],
        sample_strategy_data: dict,
    ):
        """Test creating a new strategy."""
        response = await async_client.post(
            "/api/v1/strategies",
            json=sample_strategy_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_strategy_data["name"]
        assert data["symbols"] == sample_strategy_data["symbols"]
        assert data["timeframe"] == sample_strategy_data["timeframe"]
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_strategy_unauthorized(
        self,
        async_client: AsyncClient,
        sample_strategy_data: dict,
    ):
        """Test creating strategy without authentication."""
        response = await async_client.post(
            "/api/v1/strategies",
            json=sample_strategy_data,
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_list_strategies(
        self,
        async_client: AsyncClient,
        auth_headers: dict[str, str],
    ):
        """Test listing strategies."""
        response = await async_client.get(
            "/api/v1/strategies",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_get_strategy(
        self,
        async_client: AsyncClient,
        auth_headers: dict[str, str],
        sample_strategy_data: dict,
    ):
        """Test getting a specific strategy."""
        create_response = await async_client.post(
            "/api/v1/strategies",
            json=sample_strategy_data,
            headers=auth_headers,
        )
        strategy_id = create_response.json()["id"]

        response = await async_client.get(
            f"/api/v1/strategies/{strategy_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["id"] == strategy_id

    @pytest.mark.asyncio
    async def test_get_strategy_not_found(
        self,
        async_client: AsyncClient,
        auth_headers: dict[str, str],
    ):
        """Test getting a non-existent strategy."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await async_client.get(
            f"/api/v1/strategies/{fake_id}",
            headers=auth_headers,
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_strategy(
        self,
        async_client: AsyncClient,
        auth_headers: dict[str, str],
        sample_strategy_data: dict,
    ):
        """Test updating a strategy."""
        create_response = await async_client.post(
            "/api/v1/strategies",
            json=sample_strategy_data,
            headers=auth_headers,
        )
        strategy_id = create_response.json()["id"]

        update_data = {"name": "Updated Strategy Name"}
        response = await async_client.put(
            f"/api/v1/strategies/{strategy_id}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["name"] == "Updated Strategy Name"

    @pytest.mark.asyncio
    async def test_delete_strategy(
        self,
        async_client: AsyncClient,
        auth_headers: dict[str, str],
        sample_strategy_data: dict,
    ):
        """Test deleting a strategy."""
        create_response = await async_client.post(
            "/api/v1/strategies",
            json=sample_strategy_data,
            headers=auth_headers,
        )
        strategy_id = create_response.json()["id"]

        response = await async_client.delete(
            f"/api/v1/strategies/{strategy_id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

        get_response = await async_client.get(
            f"/api/v1/strategies/{strategy_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_activate_strategy(
        self,
        async_client: AsyncClient,
        auth_headers: dict[str, str],
        sample_strategy_data: dict,
    ):
        """Test activating a strategy."""
        create_response = await async_client.post(
            "/api/v1/strategies",
            json=sample_strategy_data,
            headers=auth_headers,
        )
        strategy_id = create_response.json()["id"]

        response = await async_client.post(
            f"/api/v1/strategies/{strategy_id}/activate",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["is_active"] is True

    @pytest.mark.asyncio
    async def test_deactivate_strategy(
        self,
        async_client: AsyncClient,
        auth_headers: dict[str, str],
        sample_strategy_data: dict,
    ):
        """Test deactivating a strategy."""
        create_response = await async_client.post(
            "/api/v1/strategies",
            json=sample_strategy_data,
            headers=auth_headers,
        )
        strategy_id = create_response.json()["id"]

        await async_client.post(
            f"/api/v1/strategies/{strategy_id}/activate",
            headers=auth_headers,
        )

        response = await async_client.post(
            f"/api/v1/strategies/{strategy_id}/deactivate",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["is_active"] is False

    @pytest.mark.asyncio
    async def test_list_strategies_with_filter(
        self,
        async_client: AsyncClient,
        auth_headers: dict[str, str],
        sample_strategy_data: dict,
    ):
        """Test listing strategies with active filter."""
        await async_client.post(
            "/api/v1/strategies",
            json=sample_strategy_data,
            headers=auth_headers,
        )

        response = await async_client.get(
            "/api/v1/strategies?is_active=false",
            headers=auth_headers,
        )

        assert response.status_code == 200
        strategies = response.json()
        assert all(not s["is_active"] for s in strategies)

    @pytest.mark.asyncio
    async def test_list_strategies_pagination(
        self,
        async_client: AsyncClient,
        auth_headers: dict[str, str],
        sample_strategy_data: dict,
    ):
        """Test strategies pagination."""
        for i in range(5):
            data = sample_strategy_data.copy()
            data["name"] = f"Strategy {i}"
            await async_client.post(
                "/api/v1/strategies",
                json=data,
                headers=auth_headers,
            )

        response = await async_client.get(
            "/api/v1/strategies?skip=0&limit=2",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert len(response.json()) <= 2
