def render(payload: str) -> str:
    """Deliberately vulnerable regression fixture; never imported by production."""
    return f"<pre>{payload}</pre>"
