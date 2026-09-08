"""
Main Entrypoint for Anime Bot Factory
Executes app.py main runner.
"""
import sys
import app

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(app.main())
    except KeyboardInterrupt:
        pass
