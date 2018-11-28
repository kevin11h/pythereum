#!/usr/bin/env python3

if __name__ == "__main__":
    from pythereum import start_api

    PORT = 8080
    DEBUG = False

    start_api(PORT, DEBUG)
