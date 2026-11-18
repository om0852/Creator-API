import os
import json
import time
import math
import uuid
import hashlib
import requests

CACHE_DIR = os.path.join(os.path.dirname(__file__), ".cache")
os.makedirs(CACHE_DIR, exist_ok=True)

class CreatorEngine:
    def __init__(self):
        self.api_url = "https://api-dashboard.influencers.club/discovery/preview-filter/"
        self.token = os.getenv("INFLUENCERS_TOKEN", "692aac1c64331ae91ffcb8b73a664d999fe05b53")
        self.last_rate_limit = {}

    def _get_cache_key(self, params: dict) -> str:
        s = json.dumps(params, sort_keys=True)
        return hashlib.sha256(s.encode("utf-8")).hexdigest()

    def validate_and_build_filters(self, 
                                   keyword: str = None, 
                                   location: str = None, 
                                   platform: str = "instagram",
                                   min_followers: int = None,
                                   max_followers: int = None,
                                   min_engagement: float = None,
                                   max_engagement: float = None,
                                   is_verified: bool = None,
                                   has_email: bool = True,
                                   has_done_brand_deals: bool = None,
                                   has_merch: bool = None,
                                   has_link_in_bio: bool = None,
                                   promotes_affiliate_links: bool = None,
                                   does_live_streaming: bool = None,
                                   gender: str = None,
                                   languages: list = None,
                                   biography_contains: list = None,
                                   biography_excludes: list = None,
                                   hashtags_contains: list = None,
                                   hashtags_excludes: list = None,
                                   cross_platforms: dict = None) -> tuple:
        summary = []
        df = {
            "selectedPlatform": platform,
            "has_email": bool(has_email),
            "creator_has": {f"has_{platform}": True}
        }
        if has_email:
            summary.append("Has Email: Yes")

        # Location Canonicalization
        if location:
            loc = location.strip()
            aliases = {
                "delhi": "Delhi, India",
                "new delhi": "Delhi, India",
                "mumbai": "Mumbai, India",
                "bangalore": "Bangalore, India",
                "bengaluru": "Bangalore, India",
                "hyderabad": "Hyderabad, India"
            }
            clean_loc = aliases.get(loc.lower(), loc)
            df["location"] = [clean_loc]
            summary.append(f"Location: '{clean_loc}'")

        if has_done_brand_deals is not None:
            df["has_done_brand_deals"] = bool(has_done_brand_deals)
            summary.append(f"Has Done Brand Deals: {has_done_brand_deals}")
        if has_merch is not None:
            df["has_merch"] = bool(has_merch)
            summary.append(f"Has Merch: {has_merch}")
        if has_link_in_bio is not None:
            df["has_link_in_bio"] = bool(has_link_in_bio)
            summary.append(f"Has Link in Bio: {has_link_in_bio}")
        if promotes_affiliate_links is not None:
            df["promotes_affiliate_links"] = bool(promotes_affiliate_links)
            summary.append(f"Promotes Affiliate Links: {promotes_affiliate_links}")
        if does_live_streaming is not None:
            df["does_live_streaming"] = bool(does_live_streaming)
            summary.append(f"Live Streaming: {does_live_streaming}")
        if gender:
            df["gender"] = gender.lower()
            summary.append(f"Gender: {gender}")
        if languages:
            df["speaking_language"] = languages
            summary.append(f"Languages: {languages}")

        if cross_platforms:
            for k, v in cross_platforms.items():
                flag = k if k.startswith("has_") else f"has_{k}"
                df["creator_has"][flag] = bool(v)
                summary.append(f"Cross-Platform ({flag}): {v}")

        pf = {}
        if keyword:
            pf["ai_keywords"] = keyword.strip()
            summary.append(f"AI Keyword: '{keyword}'")

        if min_followers is not None and max_followers is not None:
            if max_followers < min_followers:
                raise ValueError(f"max_followers ({max_followers}) must be >= min_followers ({min_followers})")
        if min_followers is not None:
            pf["follower_count_gt"] = str(min_followers)
            summary.append(f"Min Followers: {min_followers:,}")
        if max_followers is not None:
            pf["follower_count_lt"] = str(max_followers)
            summary.append(f"Max Followers: {max_followers:,}")

        if min_engagement is not None and max_engagement is not None:
            if max_engagement < min_engagement:
                raise ValueError(f"max_engagement ({max_engagement}%) must be >= min_engagement ({min_engagement}%)")
        if min_engagement is not None:
            pf["engagement_percent_gt"] = str(min_engagement)
            summary.append(f"Min Engagement: {min_engagement}%")
        if max_engagement is not None:
            pf["engagement_percent_lt"] = str(max_engagement)
            summary.append(f"Max Engagement: {max_engagement}%")

        if is_verified is not None:
            pf["is_verified"] = bool(is_verified)
            summary.append(f"Verified: {is_verified}")

        if biography_contains:
            pf["biography"] = biography_contains
            summary.append(f"Bio Contains: {biography_contains}")
        if biography_excludes:
            pf["not_biography"] = biography_excludes
            summary.append(f"Bio Excludes: {biography_excludes}")

        if hashtags_contains:
            pf["hashtags"] = hashtags_contains
            summary.append(f"Hashtags: {hashtags_contains}")
        if hashtags_excludes:
            pf["not_hashtags"] = hashtags_excludes
            summary.append(f"Hashtags Exclude: {hashtags_excludes}")

        if pf:
            df[platform] = pf

        return df, summary

    def search(self, 
               keyword: str = None, 
               location: str = None, 
               platform: str = "instagram",
               page: int = 1, 
               page_size: int = 10,
               sort_by: str = "relevancy",
               use_cache: bool = True,
               **filters) -> dict:
        offset = (page - 1) * page_size
        
        try:
            discoveryfilters, summary = self.validate_and_build_filters(
                keyword=keyword,
                location=location,
                platform=platform,
                **filters
            )
        except ValueError as ve:
            return {"error": True, "message": str(ve)}

        cache_params = {
            "df": discoveryfilters,
            "offset": offset,
            "page_size": page_size,
            "sort_by": sort_by
        }
        cache_file = os.path.join(CACHE_DIR, f"{self._get_cache_key(cache_params)}.json")
        if use_cache and os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cached_data = json.load(f)
                    cached_data["_cached"] = True
                    return cached_data
            except Exception:
                pass

        payload = {
            "discoveryfilters": discoveryfilters,
            "limit": min(page_size, 10),
            "offset": offset,
            "sort_by": sort_by,
            "metadata": {"requestId": str(uuid.uuid4())}
        }

        headers = {
            "Host": "api-dashboard.influencers.club",
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.9",
            "authorization": f"Token {self.token}",
            "content-type": "application/json",
            "origin": "https://dashboard.influencers.club",
            "referer": "https://dashboard.influencers.club/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36"
        }

        # Rate-limiting guard: check last searches remaining
        searches_remaining = self.last_rate_limit.get("searches_remaining", 500)
        if searches_remaining <= 2:
            reset_sec = self.last_rate_limit.get("reset_seconds", 30)
            time.sleep(min(reset_sec, 10))

        time.sleep(0.6)
        response = requests.post(self.api_url, headers=headers, json=payload, timeout=25)

        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 10))
            time.sleep(retry_after)
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=25)

        if response.status_code != 200:
            return {
                "error": True,
                "status_code": response.status_code,
                "message": response.text,
                "applied_filters": summary
            }

        data = response.json()
        total_results = data.get("total_results", 0)
        rate_info = data.get("rate_limit", {})
        searches_rem = rate_info.get("searches", {}).get("remaining")
        reset_sec = rate_info.get("reset_seconds", 3600)

        self.last_rate_limit = {
            "searches_remaining": searches_rem if searches_rem is not None else 500,
            "reset_seconds": reset_sec
        }

        raw_results = data.get("results", [])
        formatted_creators = []
        for i, c in enumerate(raw_results):
            ig = c.get("instagram", {})
            formatted_creators.append({
                "rank": offset + i + 1,
                "full_name": ig.get("full_name") or c.get("first_name", "Unknown"),
                "follower_count": ig.get("follower_count") or c.get("total_reach", 0),
                "location": ig.get("location_unified") or c.get("location", "N/A"),
                "is_verified": ig.get("is_verified") or c.get("is_verified", False),
                "has_email": c.get("has_email", False),
                "engagement_percent": c.get("engagement_percent"),
                "top_niches": [n.get("name") for n in c.get("audience_niches", [])[:3]],
                "hashtags": c.get("hashtags", [])[:6],
                "brands": c.get("brands", [])[:5],
                "profile_picture": ig.get("profile_picture") or c.get("profile_picture"),
                "creator_uid": c.get("creator_uid")
            })

        total_pages = math.ceil(total_results / page_size) if total_results else 1

        output = {
            "applied_filters": summary,
            "pagination": {
                "current_page": page,
                "page_size": page_size,
                "total_results": total_results,
                "total_pages": total_pages,
                "has_next_page": page < total_pages,
                "has_prev_page": page > 1,
                "offset": offset
            },
            "rate_limit": {
                "searches_remaining": searches_rem,
                "creators_viewed_remaining": rate_info.get("creators_viewed", {}).get("remaining"),
                "reset_seconds": reset_sec
            },
            "credits_remaining": data.get("credits_remaining"),
            "trial_searches_left": data.get("trial_searches_left"),
            "results_count": len(formatted_creators),
            "creators": formatted_creators
        }

        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(output, f, indent=2)
        except Exception:
            pass

        return output

