import os
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from engine import CreatorEngine

app = FastAPI(
    title="Creator Intelligence API",
    description="High-performance microservice to discover influencers & creators with pagination, rate-limit defense, and deep filtering.",
    version="1.0.0"
)

# Enable CORS for Next.js (port 3000), mobile apps, and external callers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = CreatorEngine()

class SearchRequest(BaseModel):
    keyword: Optional[str] = Field(None, description="AI semantic keyword (e.g. gaming, tech, fashion)")
    location: Optional[str] = Field(None, description="City or Country (e.g. Delhi, India, Mumbai, US)")
    platform: Optional[str] = Field("instagram", description="instagram, tiktok, youtube")
    page: Optional[int] = Field(1, ge=1, description="Page number")
    page_size: Optional[int] = Field(10, ge=1, le=10, description="Results per page (max 10 on preview)")
    min_followers: Optional[int] = Field(None, description="Minimum follower count")
    max_followers: Optional[int] = Field(None, description="Maximum follower count")
    min_engagement: Optional[float] = Field(None, description="Minimum engagement rate %")
    max_engagement: Optional[float] = Field(None, description="Maximum engagement rate %")
    is_verified: Optional[bool] = Field(None, description="Filter verified creators only")
    has_email: Optional[bool] = Field(True, description="Filter creators with contact email")
    has_done_brand_deals: Optional[bool] = Field(None, description="Filter creators who did brand sponsorships")
    has_merch: Optional[bool] = Field(None, description="Filter creators with merchandise")
    has_link_in_bio: Optional[bool] = Field(None, description="Filter creators with bio links")
    promotes_affiliate_links: Optional[bool] = Field(None, description="Filter affiliate creators")
    does_live_streaming: Optional[bool] = Field(None, description="Filter live streamers")
    gender: Optional[str] = Field(None, description="male or female")
    languages: Optional[List[str]] = Field(None, description="e.g. ['en', 'hi']")
    biography_contains: Optional[List[str]] = Field(None, description="Keywords in bio")
    biography_excludes: Optional[List[str]] = Field(None, description="Keywords excluded from bio")
    hashtags_contains: Optional[List[str]] = Field(None, description="Hashtags in posts")
    hashtags_excludes: Optional[List[str]] = Field(None, description="Hashtags excluded")
    cross_platforms: Optional[Dict[str, bool]] = Field(None, description="Cross-platform presence (e.g. {'youtube': True})")
    sort_by: Optional[str] = Field("relevancy", description="relevancy, number_of_followers, growth_rate")
    use_cache: Optional[bool] = Field(True, description="Use local disk cache for instant responses")

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "Creator Intelligence API",
        "endpoints": {
            "search_get": "/api/creators/search",
            "search_post": "/api/creators/search",
            "docs": "/docs",
            "health": "/health"
        }
    }

@app.get("/health")
def health():
    return {"status": "ok", "token_configured": bool(engine.token)}

@app.post("/api/creators/search")
def search_creators_post(req: SearchRequest):
    filters = req.model_dump(exclude_unset=True)
    keyword = filters.pop("keyword", None)
    location = filters.pop("location", None)
    platform = filters.pop("platform", "instagram")
    page = filters.pop("page", 1)
    page_size = filters.pop("page_size", 10)
    sort_by = filters.pop("sort_by", "relevancy")
    use_cache = filters.pop("use_cache", True)

    result = engine.search(
        keyword=keyword,
        location=location,
        platform=platform,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        use_cache=use_cache,
        **filters
    )
    if result.get("error"):
        raise HTTPException(status_code=result.get("status_code", 400), detail=result.get("message"))
    return result

@app.get("/api/creators/search")
def search_creators_get(
    query: Optional[str] = Query(None, description="Keyword / Niche"),
    location: Optional[str] = Query("Delhi, India", description="Location"),
    platform: Optional[str] = Query("instagram"),
    page: Optional[int] = Query(1, ge=1),
    min_followers: Optional[int] = Query(None),
    max_followers: Optional[int] = Query(None),
    is_verified: Optional[bool] = Query(None),
    has_brand_deals: Optional[bool] = Query(None),
    sort_by: Optional[str] = Query("relevancy")
):
    result = engine.search(
        keyword=query,
        location=location,
        platform=platform,
        page=page,
        min_followers=min_followers,
        max_followers=max_followers,
        is_verified=is_verified,
        has_done_brand_deals=has_brand_deals,
        sort_by=sort_by
    )
    if result.get("error"):
        raise HTTPException(status_code=result.get("status_code", 400), detail=result.get("message"))
    return result

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)

