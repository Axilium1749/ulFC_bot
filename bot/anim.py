import asyncio

BRAILLE_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
DOTS_FRAMES = [".", "..", "..."]
LEFT=["&gt;——", "—&gt;—", "——&gt;"]
RIGHT=["——&lt;", "—&lt;—", "&lt;——"]
FRAMES=["●", "○"]
CONTAINER=["[   ]", "[·  ]", "[·· ]", "[···]"]

async def animate_status(message, base_text):
    i = 0
    while True:
        braille = BRAILLE_FRAMES[i % len(BRAILLE_FRAMES)]
        dots = DOTS_FRAMES[i % len(DOTS_FRAMES)]
        left = LEFT[i % len(LEFT)]
        right = RIGHT[i % len(RIGHT)]
        frames = FRAMES[i % len(FRAMES)]
        container = CONTAINER[i % len(CONTAINER)]
        
        text = f"`{container}` *{base_text}*"
        
        try:
            await message.edit_text(text, parse_mode="MARKDOWN")
        except:
            break
            
        i += 1
        await asyncio.sleep(1.4) # Интервал обновления (минимум 0.7-1 сек)