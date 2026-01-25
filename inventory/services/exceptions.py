"""Custom exceptions for inventory services."""


class GeocodingError(Exception):
    """Base exception for geocoding-related errors."""

    pass


class GeocodingAPIError(GeocodingError):
    """Raised when the geocoding API returns an error status."""

    def __init__(self, status: str, message: str | None = None) -> None:
        self.status = status
        self.message = message or f"Geocoding API returned error status: {status}"
        super().__init__(self.message)


class GeocodingNetworkError(GeocodingError):
    """Raised when a network error occurs during geocoding."""

    def __init__(self, message: str = "Network error during geocoding request") -> None:
        self.message = message
        super().__init__(self.message)


class GeocodingNoResultsError(GeocodingError):
    """Raised when no results are found for the given address."""

    def __init__(self, address: str) -> None:
        self.address = address
        self.message = f"No geocoding results found for address: {address}"
        super().__init__(self.message)
