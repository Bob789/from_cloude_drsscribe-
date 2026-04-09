# File: Final_Project_v003/app_fastapi/services/token_service.py
"""
Token validation and deduction service.
Handles token checking and deduction for various operations.
"""

from fastapi import HTTPException
from app_fastapi import database_manager as db
from app_fastapi.services.logger_service import log_insufficient_tokens, log_token_operation


# Token costs for different operations
TOKEN_COSTS = {
    "train": 1,
    "predict": 5,
    "list_models": 0,  # Free operation
    "get_model": 0,    # Free operation
}


def validate_and_deduct_tokens(username: str, operation: str) -> bool:
    """
    Validates that user has sufficient tokens and deducts them.
    Raises HTTPException if insufficient tokens.
    Returns True if successful.
    """
    cost = TOKEN_COSTS.get(operation, 0)

    if cost == 0:
        return True  # Free operation

    # Check current balance
    current_balance = db.get_user_tokens(username)

    if current_balance is None:
        raise HTTPException(status_code=404, detail="User not found")

    if current_balance < cost:
        log_insufficient_tokens(username, operation, cost, current_balance)
        raise HTTPException(
            status_code=402,  # Payment Required
            detail=f"Insufficient tokens. Required: {cost}, Available: {current_balance}"
        )

    # Deduct tokens (negative amount)
    success = db.update_user_tokens(username, -cost)

    if not success:
        log_token_operation(username, "deduct", cost, success=False)
        raise HTTPException(status_code=500, detail="Failed to deduct tokens")

    # Log successful deduction
    log_token_operation(username, "deduct", cost, success=True)
    db.add_usage_log(
        username,
        operation.upper(),
        -cost,
        "SUCCESS",
        f"Deducted {cost} tokens for {operation}"
    )

    return True


def get_token_cost(operation: str) -> int:
    """Returns the token cost for a given operation."""
    return TOKEN_COSTS.get(operation, 0)


def refund_tokens(username: str, operation: str, reason: str = "Operation failed"):
    """
    Refunds tokens to user if operation fails after deduction.
    """
    cost = TOKEN_COSTS.get(operation, 0)

    if cost == 0:
        return  # Nothing to refund

    success = db.update_user_tokens(username, cost)

    if success:
        log_token_operation(username, "refund", cost, success=True)
        db.add_usage_log(
            username,
            f"{operation.upper()}_REFUND",
            cost,
            "SUCCESS",
            reason
        )