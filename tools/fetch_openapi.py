import json, sys, urllib.request
def main():
    if len(sys.argv) != 3:
        print("Usage: python tools/fetch_openapi.py <base_url> <out_file>")
        sys.exit(2)
    base, out_file = sys.argv[1].rstrip("/"), sys.argv[2]
    candidates = ["/openapi.json", "/swagger.json", "/api/openapi.json"]
    last_err = None
    for path in candidates:
        url = base + path
        try:
            with urllib.request.urlopen(url, timeout=20) as r:
                data = r.read().decode("utf-8")
            obj = json.loads(data)
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(obj, f, indent=2, sort_keys=True)
            print(f"OK: wrote {out_file} from {url}")
            return
        except Exception as e:
            last_err = e
    print("FAILED: could not fetch openapi from common paths")
    print("Last error:", repr(last_err))
    sys.exit(1)
if __name__ == "__main__":
    main()
