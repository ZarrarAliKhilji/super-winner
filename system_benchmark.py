import asyncio
import httpx
import time
import json
import os

TARGET_URLS = [
    "https://httpbin.org/delay/1",
    "https://httpbin.org/json",
    "https://httpbin.org/uuid",
    "https://httpbin.org/user-agent",
    "https://vyronsocial.com"
] * 4  # Total 20 concurrent requests test karne ke liye

async def fetch_target(client, url, index):
    start_time = time.time()
    try:
        response = await client.get(url, timeout=10.0, follow_redirects=True)
        duration = time.time() - start_time
        return {
            "id": index,
            "url": url,
            "status": response.status_code,
            "latency_sec": round(duration, 3),
            "success": True
        }
    except Exception as e:
        duration = time.time() - start_time
        return {
            "id": index,
            "url": url,
            "status": 500,
            "error": str(e),
            "latency_sec": round(duration, 3),
            "success": False
        }

async def run_benchmark():
    print("=" * 50)
    print("🚀 STARTING ASYNC ENGINE STRESS TEST...")
    print("=" * 50)
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) EnterpriseScraper/2.0"}
    
    total_start = time.time()
    async with httpx.AsyncClient(headers=headers) as client:
        tasks = [fetch_target(client, url, i+1) for i, url in enumerate(TARGET_URLS)]
        results = await asyncio.gather(*tasks)
    total_duration = time.time() - total_start
    
    successful = sum(1 for r in results if r["success"])
    failed = len(results) - successful
    avg_latency = sum(r["latency_sec"] for r in results) / len(results)
    
    report = {
        "total_requests": len(TARGET_URLS),
        "successful": successful,
        "failed": failed,
        "total_time_sec": round(total_duration, 3),
        "avg_latency_sec": round(avg_latency, 3),
        "results": results
    }
    
    os.makedirs("data", exist_ok=True)
    with open("data/benchmark_results.json", "w") as f:
        json.dump(report, f, indent=4)
        
    print(f"\n[📊] BENCHMARK RESULTS SUMMARY:")
    print(f"----------------------------------------")
    print(f"🔥 Total Requests Sent : {len(TARGET_URLS)}")
    print(f"✅ Successful Responses: {successful}")
    print(f"❌ Failed / Blocked     : {failed}")
    print(f"⚡ Total Execution Time : {round(total_duration, 3)} seconds")
    print(f"⏱️ Average Latency      : {round(avg_latency, 3)} s/req")
    print(f"💾 Report saved to      : data/benchmark_results.json")
    print("=" * 50)
    print("[✨] System is running at Enterprise Grade Speed!")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
