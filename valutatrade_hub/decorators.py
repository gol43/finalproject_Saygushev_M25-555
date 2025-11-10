from functools import wraps
from datetime import datetime
from logging_config import logger

def log_action(action: str, *, verbose: bool = False):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id = kwargs.get("user_id") or (args[0] if args else None)
            currency_code = kwargs.get("currency_code") or (args[1] if len(args) > 1 else None)
            amount = kwargs.get("amount") or (args[2] if len(args) > 2 else None)

            try:
                result = func(*args, **kwargs)
                msg = f"{action} user_id={user_id} currency={currency_code} amount={amount} result=OK"
                if verbose:
                    msg += f" verbose={result}"
                logger.info(msg)
                return result
            except Exception as e:
                msg = f"{action} user_id={user_id} currency={currency_code} amount={amount} result=ERROR error_type={type(e).__name__} message='{str(e).replace('→','->')}'"
                logger.error(msg)
                raise
        return wrapper
    return decorator

