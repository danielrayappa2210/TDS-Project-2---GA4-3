from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import httpx
from bs4 import BeautifulSoup

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

templates = Jinja2Templates(directory="templates")

@app.get("/api/outline")
async def get_wikipedia_outline(request: Request, country: str):
    """
    Fetches Wikipedia headings for a country and returns a Markdown outline.
    """
    try:
        wiki_url = f"https://en.wikipedia.org/wiki/{country}"
        async with httpx.AsyncClient() as client:
            response = await client.get(wiki_url)
            response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        markdown_outline = ""
        for heading_tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            for heading in soup.find_all(heading_tag):
                level = int(heading_tag[1])
                markdown_outline += "#" * level + " " + heading.text.strip() + "\n"

        return templates.TemplateResponse("outline.html", {"request": request, "markdown_outline": markdown_outline})

    except httpx.ConnectError as e:
        raise HTTPException(status_code=503, detail=f"Error connecting to Wikipedia: {e}")
    except httpx.HTTPError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
