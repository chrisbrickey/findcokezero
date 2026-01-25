"""Custom exceptions for inventory app"""

class SerializerError(Exception):
    """Base exception for serializer-related errors."""

    pass


class NonNumericPostcodeError(SerializerError):
    """
    Raised when the geocoding API returns a postcode that cannot be converted to integer.

    As of 2026, the inventory app can only process numeric postcodes.
    Retailer model expects an integer for the postcode. This would need to be changed
    in order to accept postcodes that use letters (e.g., United Kingdom)
    """

    def __init__(self, message: str | None = None) -> None:
        self.message = message or "Non-numerical postcodes are not yet tolerated by the Retailer model."
        super().__init__(self.message)
