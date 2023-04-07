#!/usr/bin/env python3

import asyncio
import random


def wait_random( max_delay: int = 10) -> float:
    """ returns a float with a random delay"""
    
    random_val = random.uniform(0, max_delay)
    asyncio.sleep(random_val)
    return random_val
