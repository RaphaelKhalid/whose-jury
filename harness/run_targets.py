"""
Run every prompt instance against every target model. Resumable: skips
(prompt_id, model) pairs already present in results/targets.jsonl.

Usage:
  python harness/run_targets.py            # full run
  python harness/run_targets.py --limit 10 # dry run / cost check
"""
import argparse, json, os, sys, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import TARGETS, TARGET_MAX_TOKENS, TARGET_TEMPERATURE, SCENARIOS_PATH, FRAMINGS, TARGETS_OUT, CONCURRENCY
from harness.build_prompts import build
from harness.openrouter_client import chat

try:
    from tqdm import tqdm
except ImportError:
    print("pip install tqdm  (progress bars)"); raise


def _done_keys(path):
    keys = set()
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    r = json.loads(line)
                    keys.add((r["prompt_id"], r["model"]))
                except Exception:
                    pass
    return keys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="max prompt instances (0 = all)")
    args = ap.parse_args()

    prompts = list(build(SCENARIOS_PATH, FRAMINGS))
    if args.limit:
        prompts = prompts[: args.limit]
    done = _done_keys(TARGETS_OUT)
    os.makedirs(os.path.dirname(TARGETS_OUT), exist_ok=True)

    worklist = [(p, tm) for p in prompts for tm in TARGETS
                if (p["prompt_id"], tm["id"]) not in done]
    if not worklist:
        print("nothing to do — all target calls already completed."); return
    if done:
        print(f"resuming: {len(done)} calls already done, {len(worklist)} to go")

    stats = {"out": 0, "fails": 0}
    lock = threading.Lock()

    def work(p, tm):
        try:
            resp = chat(tm["id"], [{"role": "user", "content": p["prompt"]}],
                        TARGET_MAX_TOKENS, TARGET_TEMPERATURE)
        except Exception as e:
            with lock:
                stats["fails"] += 1
                tqdm.write(f"FAIL {tm['id']} {p['prompt_id']}: {str(e)[:90]}")
            return
        u = resp.get("usage", {})
        rec = {**{k: p[k] for k in
                  ("prompt_id","scenario_id","issue","test","act_type","item_type","alignment","swap","framing")},
               "model": tm["id"], "origin": tm["origin"], "answer": resp["text"], "usage": u}
        with lock:
            stats["out"] += u.get("completion_tokens", 0)
            out_f.write(json.dumps(rec, ensure_ascii=False) + "\n"); out_f.flush()

    with open(TARGETS_OUT, "a", encoding="utf-8") as out_f, \
         ThreadPoolExecutor(max_workers=CONCURRENCY) as ex:
        futures = [ex.submit(work, p, tm) for p, tm in worklist]
        bar = tqdm(as_completed(futures), total=len(futures), desc="🎯 targets", unit="call",
                   colour="cyan", dynamic_ncols=True,
                   bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]{postfix}")
        for _ in bar:
            bar.set_postfix_str(f"out={stats['out']//1000}k | fails={stats['fails']}")
    print(f"\ndone. output tokens={stats['out']:,}  fails={stats['fails']}")


if __name__ == "__main__":
    main()
