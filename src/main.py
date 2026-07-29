import uvicorn


def main() -> None:
    """
    Application entry point. Starts the FastAPI server using Uvicorn.
    """
    uvicorn.run(
        "src.presentation.api.app:create_app",
        host="0.0.0.0",
        port=8000,
        factory=True,
        reload=True,
    )


if __name__ == "__main__":
    main()
