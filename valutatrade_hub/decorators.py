from functools import wraps

from logging_config import logger


def log_action(action: str, *, verbose: bool = False):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id = kwargs.get("user_id") or (args[0] if args else None)
            amount = kwargs.get("amount") or (args[2] if len(args) > 2 else None)

            currency_code = None
            if len(args) > 1:
                currency_code = args[1]
            if "currency_code" in kwargs:
                currency_code = kwargs["currency_code"]
                
            try:
                result = func(*args, **kwargs)
                msg = (f"{action} user_id={user_id} currency={currency_code} "
                       f"amount={amount} result=OK")
                if verbose:
                    msg += f" verbose={result}"
                logger.info(msg)
                return result
            except Exception as e:
                msg = (f"{action} user_id={user_id} currency={currency_code} "
                       f"amount={amount} result=ERROR error_type={type(e).__name__} "
                       f"message='{str(e).replace('→','->')}'")
                logger.error(msg)
                raise
        return wrapper
    return decorator

