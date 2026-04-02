#!/usr/bin/env python3
"""
Pyrogram V2 Session Generator
Run this script to generate a session string for your Telegram account
"""

from pyrogram import Client
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

print(f"{Fore.CYAN}{'='*50}")
print(f"{Fore.YELLOW}  Pyrogram V2 Session String Generator")
print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}\n")

API_ID = input("Enter your API_ID: ").strip()
API_HASH = input("Enter your API_HASH: ").strip()

if not API_ID or not API_HASH:
    print(f"\n{Fore.RED}❌ API_ID and API_HASH are required!{Style.RESET_ALL}")
    exit(1)

print(f"\n{Fore.GREEN}Starting session generation...{Style.RESET_ALL}")
print(f"{Fore.YELLOW}Note: You will receive a login code on your Telegram app{Style.RESET_ALL}\n")

try:
    async def generate_session():
        async with Client(
            "session_generator",
            api_id=int(API_ID),
            api_hash=API_HASH,
            in_memory=True,
        ) as app:
            session_string = await app.export_session_string()
            
            print(f"\n{Fore.GREEN}{'='*50}")
            print(f"{Fore.GREEN}✅ Session Generated Successfully!")
            print(f"{Fore.GREEN}{'='*50}{Style.RESET_ALL}\n")
            print(f"{Fore.CYAN}Your Session String:{Style.RESET_ALL}")
            print(f"\n{Fore.WHITE}{session_string}{Style.RESET_ALL}\n")
            print(f"{Fore.GREEN}{'='*50}{Style.RESET_ALL}")
            print(f"\n{Fore.YELLOW}📝 Copy this session string and add it to your .env file as STRING_SESSION{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}🔒 Never share your session string with anyone!{Style.RESET_ALL}\n")
            
            return session_string
    
    # Run the async function
    import asyncio
    asyncio.run(generate_session())
    
except Exception as e:
    print(f"\n{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}")
    print(f"\n{Fore.YELLOW}Please check your API credentials and try again.{Style.RESET_ALL}")
    exit(1)
