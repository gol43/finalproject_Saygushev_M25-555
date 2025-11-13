import logging

logger = logging.getLogger("actions")

def log_action(action: str, *, verbose: bool = False):
    def decorator(func):
        def wrapper(*args, **kwargs):
            user_id = kwargs.get("user_id")
            if not user_id and len(args) > 0:
                user_id = args[0]
            amount = kwargs.get("amount")
            if amount is None and len(args) > 2:
                amount = args[2]
            currency_code = kwargs.get("currency_code")
            if not currency_code and len(args) > 1:
                currency_code = args[1]
            try:
                result = func(*args, **kwargs)
                msg = (f"{action} user_id={user_id} "
                       f"currency={currency_code} amount={amount} result=OK")
                if verbose and isinstance(result, str):
                    clean_result = result.replace("\n", " ").replace("'", '"')
                    msg += f" verbose={clean_result}"
                logger.info(msg)
                return result
            except Exception as e:
                msg = (
                    f"{action} user_id={user_id} currency={currency_code} "
                    f"amount={amount} result=ERROR "
                    f"error_type={type(e).__name__} message='{str(e)}'")
                logger.error(msg)
                raise
        return wrapper
    return decorator