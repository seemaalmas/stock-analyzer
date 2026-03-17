import subprocess

def safe_run(cmd):
    print(f"\n▶️ STARTING: {cmd}", flush=True)
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"✅ FINISHED: {cmd}", flush=True)
    except Exception as e:
        print(f"⚠️ SKIPPED: {cmd} | {e}", flush=True)

def main():
    safe_run("python -m scripts.run_bhavcopy")
    safe_run("python -m fundamentals.ingestion.index_price_ingest")
    safe_run("python -m market.liquidity_daily_builder")
    safe_run("python -m market.spread_daily_builder")
    safe_run("python -m fundamentals.ingestion.stock_price_ingest")
    safe_run("python -m fundamentals.ingestion.vix_ingest")
    try:
        safe_run("python -m fundamentals.ingestion.nse_announcements")
    except Exception as e:
        print("⚠️ NSE announcements skipped:", e)

    # safe_run("python -m fundamentals.ingestion.nse_announcements")

    safe_run("python -m technicals.structure.batch_runner")
    safe_run("python -m technicals.indicators.batch_runner")

    
    safe_run("python -m market.index_state_builder") 
    safe_run("python -m market.breadth_daily_builder")
    safe_run("python -m market.batch_runner")

    safe_run("python -m strategies.weekly.batch_runner")
    safe_run("python -m scoring.batch_runner")
    safe_run("python -m risk.batch_runner")

    print("\n✅ NIGHTLY PIPELINE COMPLETED")

if __name__ == "__main__":
    main()
