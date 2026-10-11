"""Verify selectively disclosed protocol bytes and RFC 3161 attestations offline."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if not __debug__:
        raise RuntimeError("Run without -O: integrity assertions must remain enabled")
    parser = argparse.ArgumentParser()
    parser.add_argument("--openssl", default=shutil.which("openssl") or r"C:\Program Files\Git\usr\bin\openssl.exe")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1] / "evidence/frozen-protocol"
    index = json.loads((root / "export_index.json").read_text())
    reports = []
    previous = None
    for entry in index["versions"]:
        base = root / entry["version"]
        auth = json.loads((base / "authorization_record.json").read_text())
        bundle = auth["authorized_bundle"]
        assert sha(base / "SHA256SUMS") == bundle["sha256sums_sha256"]
        assert sha(base / "IMMUTABLE_BUNDLE_SHA256SUMS") == bundle["immutable_bundle_sha256sums_sha256"]
        target = (f"COMMIT:{bundle['commit_sha']}\nTAG:{bundle['tag_name']}\n"
                  f"TAG_OBJECT:{bundle['tag_object_sha']}\nSHA256SUMS_SHA256:{bundle['sha256sums_sha256']}\n"
                  f"IMMUTABLE_BUNDLE_SHA256SUMS_SHA256:{bundle['immutable_bundle_sha256sums_sha256']}\n")
        digest = hashlib.sha256(target.encode()).hexdigest()
        assert digest == bundle["bundle_sha256"]
        manifest = {}
        for line in (base / "IMMUTABLE_BUNDLE_SHA256SUMS").read_text().splitlines():
            expected, name = line.split(None, 1)
            manifest[name.strip()] = expected
        for name in entry["exported_snapshot_paths"]:
            assert sha(base / "snapshot" / name) == manifest[name], name
        times = {}
        for provider in ("digicert", "sectigo", "freetsa"):
            receipt = base / "timestamps" / f"bundle_{provider}.tsr"
            cmd = [args.openssl, "ts", "-verify", "-in", str(receipt), "-digest", digest,
                   "-CAfile", str(base / "trust" / ("freetsa_cacert.pem" if provider == "freetsa" else "ca-bundle.crt"))]
            if provider == "freetsa":
                cmd += ["-untrusted", str(base / "trust/freetsa_tsa.crt")]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode:
                times[provider] = {"status": "FAILED", "error": (result.stdout + result.stderr).replace(str(root.parents[2]), "<checkout>")}
                continue
            info = subprocess.run([args.openssl, "ts", "-reply", "-in", str(receipt), "-text"], capture_output=True, text=True, check=True)
            times[provider] = next(line.strip() for line in info.stdout.splitlines() if "Time stamp:" in line)
        selected = {name: manifest[name] for name in entry["exported_snapshot_paths"]}
        changed = [] if previous is None else [name for name in selected if previous.get(name) != selected[name]]
        reports.append({"version": entry["version"], "verified_snapshot_files": len(selected), "timestamps": times, "changed_since_previous": changed})
        previous = selected
    failed = any(isinstance(t, dict) for r in reports for t in r["timestamps"].values())
    print(json.dumps({"status": "FAILED" if any(isinstance(t, dict) for r in reports for t in r["timestamps"].values()) else "VERIFIED", "scope": "Byte integrity and RFC3161 signatures only; not public-registration or pre-start proof", "versions": reports}, indent=2))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

