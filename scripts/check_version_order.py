#!/usr/bin/env python3
"""Version-order check (START-HERE step 21, plan row 0.5; owner Q29, 2026-11-09).

contract.json#version must be HIGHER than every released tag v<version> of this
repository, compared number by number (0.18.10 > 0.18.9). One exception: when
the commit being checked IS the tag of that version (a tag push), equal is
right. Second exception (2026-11-10): a change that leaves the released
contract files untouched (CHECKSUMS identical to the tag's: README, workflows,
docs) may keep the released number — nothing new is released. A number that was released, or given up (0.18.46, owner 2026-11-09),
never comes back: tags only go up.

Tags are read from the remote (git ls-remote), so a shallow CI checkout works.
With no network the local tags are used and a warning is printed.

    python3 scripts/check_version_order.py             # check this tree
    python3 scripts/check_version_order.py --self-test # the rule's own cases
"""
import json
import os
import re
import subprocess
import sys

TAG = re.compile(r"^v(\d+(?:\.\d+)*)$")


def parse(version):
    if not re.fullmatch(r"\d+(?:\.\d+)*", version):
        raise SystemExit(f"version {version!r} is not numbers and dots")
    return tuple(int(x) for x in version.split("."))


def check(version, tags, head_tags=(), unchanged=False):
    """Returns (ok, message). tags: released tag names; head_tags: the tags on the checked commit;
    unchanged: the contract files (CHECKSUMS) are identical to the tag of this version (docs-only change)."""
    released = sorted(parse(m.group(1)) for t in tags for m in [TAG.match(t)] if m)
    v = parse(version)
    if not released:
        return True, f"version {version}: no released tag yet (the first tag will be v{version})"
    top = released[-1]
    top_s = ".".join(map(str, top))
    if v > top:
        return True, f"version {version} is above the latest tag v{top_s}"
    if v == top and f"v{version}" in head_tags:
        return True, f"tag v{version} is this commit: version matches"
    if v == top and unchanged:
        return True, f"version {version} is released (tag v{top_s}) and the contract files are unchanged: docs-only change"
    if v == top:
        return False, f"version {version} is already released (tag v{top_s}); take the next number"
    return False, f"version {version} is LOWER than the latest tag v{top_s}; tags only go up (0.18.46 was given up and stays unused)"


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, check=False)


def remote_tags():
    r = git("ls-remote", "--tags", "--refs", "origin")
    if r.returncode != 0:
        print(f"::warning::could not read tags from origin ({r.stderr.strip()[:80]}); using local tags", file=sys.stderr)
        return git("tag", "-l").stdout.split()
    return [line.split("refs/tags/", 1)[1] for line in r.stdout.splitlines() if "refs/tags/" in line]


def head_tag_names():
    names = set(git("tag", "--points-at", "HEAD").stdout.split())
    ref = os.environ.get("GITHUB_REF", "")
    if ref.startswith("refs/tags/"):
        names.add(ref[len("refs/tags/"):])
    return names


def unchanged_since_tag(version):
    """True when CHECKSUMS in this tree equals CHECKSUMS at tag v<version> (fetched from origin when missing)."""
    tag = f"v{version}"
    if git("rev-parse", "-q", "--verify", f"refs/tags/{tag}").returncode != 0:
        if git("fetch", "--depth", "1", "origin", "tag", tag).returncode != 0:
            return False
    tagged = git("show", f"{tag}:CHECKSUMS")
    if tagged.returncode != 0:
        return False
    try:
        return tagged.stdout == open("CHECKSUMS").read()
    except OSError:
        return False


def self_test():
    cases = [
        ("0.18.10", ["v0.18.9"], (), True),  # number order, not text order
        ("0.18.9", ["v0.18.10"], (), False),  # a lower number fails
        ("0.18.51", ["v0.4.4"], (), True),  # today's main against today's only tag
        ("0.18.46", ["v0.18.51"], (), False),  # the given-up number never comes back
        ("0.18.51", ["v0.18.51"], ("v0.18.51",), True),  # the tag push of this very version
        ("0.18.51", ["v0.18.51"], (), False),  # re-using a released number
        ("0.19.0", ["v0.18.51", "v0.4.4", "not-a-tag"], (), True),
        ("1.0", ["v0.18.51"], (), True),
        ("0.18.52", [], (), True),  # a repository with no tags yet
        ("0.18.54", ["v0.18.54"], (), True, True),  # docs-only: released number kept, contract files unchanged
        ("0.18.53", ["v0.18.54"], (), False, True),  # unchanged files never excuse a LOWER number
    ]
    for case in cases:
        version, tags, head, want = case[:4]
        unchanged = case[4] if len(case) > 4 else False
        ok, msg = check(version, tags, head, unchanged)
        assert ok == want, f"{version} vs {tags} head={head}: got {ok} ({msg})"
    print(f"version-order self-test: {len(cases)} cases pass")


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
        sys.exit(0)
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    current = json.load(open("contract.json"))["version"]
    ok, message = check(current, remote_tags(), head_tag_names(), unchanged_since_tag(current))
    print(("OK   " if ok else "FAIL ") + message)
    sys.exit(0 if ok else 1)
