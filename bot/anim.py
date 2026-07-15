import asyncio

BRAILLE_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
DOTS_FRAMES = [".", "..", "..."]

async def animate_status(message, base_text):
    i = 0
    while True:
        braille = BRAILLE_FRAMES[i % len(BRAILLE_FRAMES)]
        dots = DOTS_FRAMES[i % len(DOTS_FRAMES)]
        
        text = f"{braille} <b>{base_text}</b>{dots}"
        
        try:
            await message.edit_text(text, parse_mode="HTML")
        except:
            break
            
        i += 1
        await asyncio.sleep(1) # Интервал обновления (минимум 0.7-1 сек)