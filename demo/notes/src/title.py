"""Title normalization for the NoteBox example."""


def normalize_title(value: str) -> str:
    title = value.strip()
    if not title:
        raise ValueError("title is empty")
    if len(title) > 60:
        raise ValueError("title is too long")
    return title
