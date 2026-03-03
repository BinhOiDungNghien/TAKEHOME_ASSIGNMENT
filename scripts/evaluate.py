import asyncio
import json
import uuid
import time
import httpx
from typing import List, Dict

API_URL = "http://localhost:8000/api/v1"

async def run_test_case(test_case: Dict):
    session_id = str(uuid.uuid4())
    user_id = test_case.get("user_id", "eval-user")
    message = test_case["input"]
    
    print(f"Running Test [{test_case['id']}]: {test_case['description']}")
    
    start_time = time.perf_counter()
    ttft = None
    full_text = ""
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST", 
                f"{API_URL}/chat/stream", 
                json={"session_id": session_id, "user_id": user_id, "message": message}
            ) as response:
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        if ttft is None:
                            ttft = (time.perf_counter() - start_time) * 1000
                        
                        try:
                            data = json.loads(line[6:])
                            if "text" in data:
                                full_text += data["text"]
                        except:
                            pass
                
                total_latency = (time.perf_counter() - start_time) * 1000
                
                return {
                    "id": test_case["id"],
                    "status": "PASS",
                    "ttft_ms": ttft,
                    "total_latency_ms": total_latency,
                    "char_count": len(full_text)
                }
    except Exception as e:
        return {
            "id": test_case["id"],
            "status": "FAIL",
            "error": str(e)
        }

async def main():
    with open("tests/eval/golden_set.json", "r") as f:
        golden_set = json.load(f)
    
    print("=== AI Service Evaluation Pipeline ===")
    results = []
    for tc in golden_set:
        res = await run_test_case(tc)
        results.append(res)
        print(f"Result: {res['status']} | TTFT: {res.get('ttft_ms', 0):.2f}ms | Total: {res.get('total_latency_ms', 0):.2f}ms")

    # Summary
    passed = len([r for r in results if r["status"] == "PASS"])
    avg_ttft = sum([r["ttft_ms"] for r in results if "ttft_ms" in r]) / passed if passed else 0
    
    print("=== Final Summary ===")
    print(f"Total Tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {len(results) - passed}")
    print(f"Average TTFT: {avg_ttft:.2f}ms")

if __name__ == "__main__":
    asyncio.run(main())
