import os

if os.getenv("DD_TRACER_TEST_UVLOOP") == "1":
    import asyncio
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
