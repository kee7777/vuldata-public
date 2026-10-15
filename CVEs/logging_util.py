def configure_logging(level="INFO", log_file=None):
    # Show messages on screen and save to a file
    import logging, sys
    logging.getLogger().handlers.clear()
    log_file = log_file or "cve_fetch.log" 
    handlers = [
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_file, encoding="utf-8")
    ]
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=getattr(logging, level.upper(), logging.INFO),
        handlers=handlers
    )
