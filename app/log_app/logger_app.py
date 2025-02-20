import logging

def cof_logging(level=logging.DEBUG):
    logging.basicConfig(
        level=level,
        filename="log_app/logs.log",
        datefmt="%Y-%m-%d %H:%M:%S",
        format="[%(asctime)s.%(msecs)03d] %(module)-10s:%(lineno)-3d\r%(levelname)-5s - %(message)s|",
        encoding="utf-8",
    )

