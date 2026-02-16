import asyncio
from downloader import downloader

async def test():
    queries = [
        "Xcho Gde zhe ty",
        "Sherali Jo'rayev Karvon",
        "Billie Eilish bad guy slowed",
        "Interstellar theme 8D"
    ]
    
    for q in queries:
        print(f"\n--- Testing query: {q} ---")
        if "slowed" in q or "8D" in q:
            # Test version search
            res = await downloader.search_music_versions(q)
            for k, v in res.items():
                status = "✅ Found" if v else "❌ Not found"
                print(f"{k}: {status} - {v['title'] if v else ''}")
        else:
            # Test general search
            res = await downloader.search_music(q, limit=3)
            if res:
                print(f"✅ Found {len(res)} results:")
                for r in res:
                    print(f"- {r['title']} ({r.get('uploader')})")
            else:
                print("❌ Nothing found")

if __name__ == "__main__":
    asyncio.run(test())
