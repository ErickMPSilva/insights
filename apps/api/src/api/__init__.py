def main() -> None:
    import uvicorn

    uvicorn.run("api.main:app", reload=True, port=8000)
