from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
import httpx
from bs4 import BeautifulSoup

app = FastAPI()

@app.get("/api/outline", response_class=PlainTextResponse)
async def get_wikipedia_outline(country: str):
    """
    Fetches Wikipedia headings for a country and returns a Markdown outline as plain text.
    """
    try:
        wiki_url = f"https://en.wikipedia.org/wiki/{country}"
        async with httpx.AsyncClient() as client:
            response = await client.get(wiki_url)
            
            # Check for a 404 response before raising for status
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Country not found, please check the country spelling")
            
            response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        markdown_outline = ""
        for heading in headings:
            level = int(heading.name[1])
            markdown_outline += "#" * level + " " + heading.get_text(strip=True) + "\n"

        return markdown_outline

    except httpx.ConnectError as e:
        raise HTTPException(status_code=503, detail=f"Error connecting to Wikipedia: {e}")
    except httpx.HTTPError as e:
        # In case of other HTTP errors
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
