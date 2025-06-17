import io
from typing import Callable, Any
from functools import wraps
from contextlib import redirect_stdout, redirect_stderr


def print_cli_status(
    description: str,
) -> Callable[[Callable[..., None]], Callable[..., None]]:
    def decorator(fn: Callable[..., None]) -> Callable[..., None]:
        @wraps(fn)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> None:
            func_name = fn.__name__
            out = io.StringIO()
            err = io.StringIO()
            try:
                with redirect_stdout(out), redirect_stderr(err):
                    fn(self, out, err, *args, **kwargs)
            except AssertionError:
                print(f"❌ Test: {func_name}: FAIL")
                print(description)
                raise
            else:
                print(f"✅ Test: {func_name}: PASS")
                print(description)

        return wrapper

    return decorator


def print_server_status(
    description: str,
) -> Callable[[Callable[..., None]], Callable[..., None]]:
    def decorator(fn: Callable[..., None]) -> Callable[..., None]:
        @wraps(fn)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> None:
            func_name = fn.__name__
            try:
                fn(self, *args, **kwargs)
            except AssertionError:
                print(f"❌ Test: {func_name}: FAIL")
                print(description)
                raise
            else:
                print(f"✅ Test: {func_name}: PASS")
                print(description)

        return wrapper

    return decorator
