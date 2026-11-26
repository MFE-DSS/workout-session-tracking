"""Fixed Linux child entry. Install limits BEFORE application/SCI imports."""

from __future__ import annotations

import json
import sys

sys.dont_write_bytecode = True


def install_limits():
    if sys.platform != "linux":
        raise ValueError("linux_required")
    import resource

    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    resource.setrlimit(resource.RLIMIT_AS, (536870912, 536870912))
    resource.setrlimit(resource.RLIMIT_CPU, (2, 3))
    if resource.getrlimit(resource.RLIMIT_AS) != (536870912, 536870912) or resource.getrlimit(
        resource.RLIMIT_CPU
    ) != (2, 3):
        raise ValueError("limits_unavailable")
    return resource


def main():
    try:
        resource = install_limits()
        import os

        # Incidental ORM imports must not create persistent state in the readonly
        # application root. The actual owned capture URI remains separate in argv.
        os.environ["DATABASE_URL"] = "sqlite:///:memory:"
        if sys.argv[1:] == ["--qualify-cpu"]:
            while True:
                pass  # Linux-only witness after actual RLIMIT_CPU installation.
        if sys.argv[1:] == ["--qualify-limits"]:
            # Performed only on Linux after an effective OS cap, never in parent.
            refused = False
            try:
                bytearray(600 * 1024 * 1024)
            except MemoryError:
                refused = True
            proof = {
                name: resource.getrlimit(getattr(resource, "RLIMIT_" + name))
                for name in ("AS", "CPU", "CORE")
            }
            proof.update(
                memory_refused=refused,
                child_reaped_by_parent=False,
                peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            )
            print(json.dumps(proof))
            return 0
        from pathlib import Path

        root = Path(__file__).resolve().parents[3]
        sys.path.insert(0, str(root))
        from app.services.muscle_observed_load.contracts import VERSION, instant, parse_query
        from app.services.muscle_observed_load.limits import ReadLimits
        from app.services.muscle_observed_load.sqlite_source import bounded_json, open_owned_capture
        from app.services.muscle_observed_load.supervisor import load_runtime_profile

        profile_path, profile_digest, database_url, bundle_root = sys.argv[1:]
        profile, admitted_view = load_runtime_profile(profile_path, profile_digest, with_view=True)
        raw = sys.stdin.buffer.read(1025)
        if len(raw) > 1024:
            raise ValueError("job_input_limit")
        job = bounded_json(raw, ReadLimits())
        if (
            set(job) != {"owner_id", "from", "until", "as_of"}
            or type(job["owner_id"]) is not int
            or job["owner_id"] <= 0
        ):
            raise ValueError("job_invalid")
        as_of = instant(job["as_of"])
        query = parse_query({"from": job["from"], "until": job["until"]}, VERSION, as_of=as_of)
        from app.services.muscle_observed_load.projection import SourceView, project_capture
        from app.services.muscle_observed_load.provenance import CatalogueReadContext

        catalogue_context = CatalogueReadContext(job["owner_id"], profile_digest)
        catalogue_context.seed(admitted_view)

        sources = SourceView(
            root,
            expected=profile["source_pins"],
            budget=admitted_view.budget,
            catalogue_context=catalogue_context,
        )
        sources.raw = dict(admitted_view.raw)
        sources.pins = dict(admitted_view.pins)
        sources.bundle_root = bundle_root
        with open_owned_capture(database_url, job["owner_id"], query) as capture:
            response = project_capture(
                capture,
                query,
                sources,
                ReadLimits(),
                as_of=as_of,
                runtime_profile_digest=profile_digest,
            )
        # iterencode bounds output without first creating an unbounded serialized string.
        encoder = json.JSONEncoder(ensure_ascii=False, allow_nan=False, separators=(",", ":"))
        output = bytearray()
        for chunk in encoder.iterencode(response.model_dump()):
            encoded = chunk.encode("utf-8")
            if len(output) + len(encoded) > 1048576:
                raise ValueError("output_limit")
            output.extend(encoded)
        sys.stdout.buffer.write(output)
        return 0
    except Exception:
        # No paths, SQL, body measurements, credentials or worker stderr in API errors.
        sys.stdout.write('{"error":"muscle_observed_load_unavailable"}')
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
