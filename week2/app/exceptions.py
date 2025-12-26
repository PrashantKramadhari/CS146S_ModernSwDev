"""Custom exceptions for the application."""

from __future__ import annotations


class AppException(Exception):
    """Base exception for application errors."""
    pass


class DatabaseError(AppException):
    """Exception raised for database-related errors."""
    pass


class NotFoundError(AppException):
    """Exception raised when a resource is not found."""
    pass


class ValidationError(AppException):
    """Exception raised for validation errors."""
    pass

