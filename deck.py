"""
CLI for rendering and presenting the Manim deck.
Generated with GPT Sol 6.1.
"""

import argparse
import ast
import json
import hashlib
import importlib.metadata
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent

_SPACE_BINDING = re.compile(
    r"(?://[^\n]*\n\s*)?Reveal\.addKeyBinding\(\s*\{\s*keyCode:\s*32,.*?\}\s*\);",
    re.DOTALL,
)
_SPACE_NEXT = (
    "Reveal.addKeyBinding("
    "{ keyCode: 32, key: 'SPACE', description: 'Next slide' }, "
    "() => { Reveal.next(); }"
    ");"
)

_IMG_HTML = """\
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" name="viewport"/>
<title>{title}</title>
<link href="../index_assets/reveal.css" rel="stylesheet"/>
<link href="../index_assets/black.css" rel="stylesheet"/>
</head>
<body>
<div class="reveal">
<div class="slides">
{sections}
</div>
</div>
<script src="../index_assets/reveal.js"></script>
<script>
  Reveal.initialize({{
    width: '100%', height: '100%', margin: 0.04,
    controls: true, progress: true, hash: true, history: false,
    keyboard: true, overview: true, center: true, touch: true,
    fragments: false, help: true, transition: 'none',
    backgroundTransition: 'none', slideNumber: false,
  }});
  Reveal.addKeyBinding(
    {{ keyCode: 32, key: 'SPACE', description: 'Next slide' }},
    () => {{ Reveal.next(); }},
  );
</script>
</body>
</html>
"""


def load_deck():
    with (ROOT / "deck.toml").open("rb") as source:
        deck = tomllib.load(source)
    resolution = deck.get("resolution", [1920, 1080])
    if (
        not isinstance(resolution, list)
        or len(resolution) != 2
        or any(type(value) is not int or value <= 0 for value in resolution)
    ):
        raise ValueError("resolution must be [width, height] with positive integer pixels")
    entries = deck.get("slides", [])
    if not entries:
        raise ValueError("deck.toml has no [[slides]]")
    seen = set()
    for entry in entries:
        name = entry.get("scene", "")
        if not isinstance(name, str) or not name.isidentifier():
            raise ValueError(f"bad scene name: {name!r}")
        if name in seen:
            raise ValueError(f"duplicate scene: {name}")
        seen.add(name)
        path = (ROOT / entry["file"]).resolve()
        if not path.is_relative_to(ROOT) or path.suffix != ".py" or not path.is_file():
            raise ValueError(f"bad slide file: {path}")
        classes = {
            node.name
            for node in ast.parse(path.read_text()).body
            if isinstance(node, ast.ClassDef)
        }
        if name not in classes:
            raise ValueError(f"{path.relative_to(ROOT)} missing class {name}")
    return deck


def run_module(module, *args):
    subprocess.run([sys.executable, "-m", module, *map(str, args)], cwd=ROOT, check=True)


def scene_python_inputs(source):
    """Follow local imports without executing them; _helpers.py remains opt-in."""
    root = ROOT.resolve()
    pending = [source]
    visited = set()
    while pending:
        path = pending.pop().resolve()
        if path in visited or path.name == "_helpers.py":
            continue
        visited.add(path)
        for node in ast.walk(ast.parse(path.read_text())):
            modules = []
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
                base = root
            elif isinstance(node, ast.ImportFrom):
                base = path.parent if node.level else root
                for _ in range(max(0, node.level - 1)):
                    base = base.parent
                prefix = node.module or ""
                modules = [prefix] if prefix else []
                modules += [".".join(filter(None, [prefix, alias.name]))
                            for alias in node.names if alias.name != "*"]
            else:
                continue
            for module in modules:
                stem = base.joinpath(*module.split("."))
                for candidate in [stem.with_suffix(".py"), stem / "__init__.py"]:
                    if candidate.is_file() and candidate.resolve().is_relative_to(root):
                        pending.append(candidate)
                for parent in stem.parents:
                    if parent == root or not parent.is_relative_to(root):
                        break
                    initializer = parent / "__init__.py"
                    if initializer.is_file():
                        pending.append(initializer)
    return visited


def render_fingerprint(entry, resolution):
    paths = scene_python_inputs(ROOT / entry["file"])
    paths.update({ROOT / "deck.toml", ROOT / "manim.cfg",
                  ROOT / "environment.yml", ROOT / "deck.py"})
    settings = ROOT / "scenes/_settings.py"
    if settings.is_file():
        paths.add(settings)
    paths = {path.resolve() for path in paths}
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(str(path.relative_to(ROOT.resolve())).encode())
        digest.update(path.read_bytes())
    digest.update(json.dumps([entry, resolution, sys.version, sys.executable], sort_keys=True).encode())
    for package in ("manim", "manim-slides"):
        try:
            version = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            version = "missing"
        digest.update(f"{package}={version}".encode())
    return digest.hexdigest()


def rendered_outputs(entry):
    """Hash metadata only when all referenced clips exist and are nonempty."""
    metadata = ROOT / "slides" / f"{entry['scene']}.json"
    try:
        payload = json.loads(metadata.read_text())
        clips = payload["slides"]
        if not clips:
            return None
        for clip in clips:
            for key in ("file", "rev_file"):
                path = ROOT / clip[key]
                if not path.is_file() or not path.stat().st_size:
                    return None
        return hashlib.sha256(metadata.read_bytes()).hexdigest()
    except (OSError, ValueError, KeyError, TypeError):
        return None


def render(entries, resolution, *, changed_only=False, force=False, frame_rate=None):
    state_path = ROOT / "media" / "deck-build-state.json"
    try:
        state = json.loads(state_path.read_text())
        if not isinstance(state, dict):
            state = {}
    except (OSError, ValueError):
        state = {}
    for entry in entries:
        name = entry["scene"]
        fingerprint = render_fingerprint(
            entry, resolution if frame_rate is None else [*resolution, frame_rate],
        )
        outputs = rendered_outputs(entry)
        record = {"fingerprint": fingerprint, "outputs": outputs}
        if changed_only and not force and outputs and state.get(name) == record:
            print(f"Unchanged: {name}", flush=True)
            continue
        print(f"Rendering {name}", flush=True)
        run_module(
            "manim", "render", "--resolution", ",".join(map(str, resolution)),
            *(["--fps", str(frame_rate)] if frame_rate is not None else []),
            *(["--disable_caching"] if force else []),
            ROOT / entry["file"], name,
        )
        outputs = rendered_outputs(entry)
        if outputs is None:
            raise ValueError(f"render did not produce complete slide outputs: {name}")
        state[name] = {"fingerprint": fingerprint, "outputs": outputs}
        state_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = state_path.with_suffix(".tmp")
        temporary.write_text(json.dumps(state, indent=2) + "\n")
        temporary.replace(state_path)


def playback_clips(clips, looping_level):
    """Filter loops on copied metadata, stopping reveals whose loops are omitted."""
    selected = []
    for clip in clips:
        if (looping_level < 2 and clip.get("loop")
                and not (looping_level == 1.5 and clip.get("notes") in {"opening-loop","learning-loop","thanks-loop"})):
            if selected:
                selected[-1]["auto_next"] = False
            continue
        selected.append(dict(clip))
    return selected


def export(deck):
    folder = ROOT / "slides"
    missing = [s["scene"] for s in deck["slides"] if not (folder / f"{s['scene']}.json").is_file()]
    if missing:
        raise ValueError(f"render first: {', '.join(missing)}")
    destination = ROOT / "dist" / "index.html"
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Manim Slides otherwise skips existing video filenames, even if changed.
    assets = destination.parent / "index_assets"
    if assets.is_dir():
        for video in assets.glob("*.mp4"):
            video.unlink()
    # Filter temporary metadata, preserving the original render outputs.
    with tempfile.TemporaryDirectory(prefix="mathcqm-export-") as temporary:
        metadata = Path(temporary)
        for entry in deck["slides"]:
            name = entry["scene"]
            payload = json.loads((folder / f"{name}.json").read_text())
            payload["slides"] = playback_clips(payload["slides"], deck.get("loopingLevel", 1))
            for clip in payload["slides"]:
                for key in ("file", "rev_file"):
                    if clip.get(key):
                        clip[key] = str((ROOT / clip[key]).resolve())
            (metadata / f"{name}.json").write_text(json.dumps(payload))
        run_module(
            "manim_slides", "--silent", "convert", "--folder", metadata,
            "--offline",
            "-ctitle=" + deck.get("title", "Mathematics Colloquium"),
            "-ccontrols=true", "-cprogress=true", "-chash=true",
            *[s["scene"] for s in deck["slides"]], destination,
        )
    html = destination.read_text()
    html, n = _SPACE_BINDING.subn(_SPACE_NEXT, html, count=1)
    if not n:
        raise ValueError("space keybinding missing from export")
    # Add seek/frame-hold handling from playback.js.
    assets = destination.parent / "index_assets"
    assets.mkdir(exist_ok=True)
    shutil.copyfile(ROOT / "web" / "playback.js", assets / "deck-playback.js")
    html = html.replace(
        "</body>", '<script src="index_assets/deck-playback.js"></script>\n</body>', 1,
    )
    destination.write_text(html)
    print(f"\nReady: {destination}")


def picture_clips(clips):
    """Stills for picture mode: holds always; first loop once; never auto_next."""
    selected = []
    saw_loop = False
    for clip in clips:
        path = clip.get("file")
        if not path:
            continue
        if clip.get("auto_next"):
            continue
        if clip.get("loop"):
            if saw_loop:
                continue
            saw_loop = True
        selected.append(clip)
    return selected


def extract_still(video, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Prefer a frame near the end so morphs settle; fall back to any frame.
    attempts = [
        ["-sseof", "-0.05", "-i", str(video), "-frames:v", "1"],
        ["-i", str(video), "-frames:v", "1"],
    ]
    errors = []
    for args in attempts:
        result = subprocess.run(
            ["ffmpeg", "-y", *args, "-q:v", "2", str(destination)],
            cwd=ROOT, capture_output=True, text=True,
        )
        if result.returncode == 0 and destination.is_file():
            return
        errors.append(result.stderr.strip() or f"exit {result.returncode}")
    raise ValueError(f"ffmpeg failed for {video}: {errors[-1]}")


def img(deck):
    folder = ROOT / "slides"
    reveal = ROOT / "dist" / "index_assets" / "reveal.js"
    if not reveal.is_file():
        raise ValueError("export first so Reveal assets exist under dist/index_assets")
    missing = [s["scene"] for s in deck["slides"] if not (folder / f"{s['scene']}.json").is_file()]
    if missing:
        raise ValueError(f"render first: {', '.join(missing)}")

    out_dir = ROOT / "dist" / "img"
    assets = out_dir / "assets"
    if out_dir.exists():
        shutil.rmtree(out_dir)
    assets.mkdir(parents=True)

    sections = []
    index = 0
    for entry in deck["slides"]:
        scene = entry["scene"]
        payload = json.loads((folder / f"{scene}.json").read_text())
        for clip in picture_clips(playback_clips(payload["slides"], deck.get("loopingLevel", 1))):
            video = ROOT / clip["file"]
            if not video.is_file():
                raise ValueError(f"missing clip: {video}")
            name = f"p{index:02d}_{scene}.jpg"
            extract_still(video, assets / name)
            kind = "loop" if clip.get("loop") else "hold"
            print(f"  img {index:02d} {scene:24} {kind}", flush=True)
            sections.append(
                '<section data-background-color="black" '
                'data-background-size="contain" '
                f'data-background-image="assets/{name}"></section>'
            )
            index += 1

    if not sections:
        raise ValueError("no picture clips selected")
    (out_dir / "index.html").write_text(
        _IMG_HTML.format(
            title=deck.get("title", "Mathematics Colloquium") + " (pictures)",
            sections="\n".join(sections),
        )
    )
    print(f"\nPictures: {out_dir / 'index.html'} ({index} stills)")


def resolve_scene_names(requested, entries):
    selected = set()
    for name in requested:
        key = name.casefold()
        candidates = [entry["scene"] for entry in entries
                      if entry["scene"].casefold() == key]
        if not candidates and not key.endswith("slide"):
            candidates = [entry["scene"] for entry in entries
                          if entry["scene"].casefold() == key + "slide"]
        if not candidates:
            raise ValueError(f"unknown scene: {name}")
        if len(candidates) > 1:
            raise ValueError(f"ambiguous scene: {name} ({', '.join(candidates)})")
        selected.add(candidates[0])
    return selected


def publish():
    """Publish dist/ through a temporary checkout of the deploy branch."""
    output = ROOT / "dist"
    names = ("index.html", "index_assets", "img")
    for name in names:
        if not (output / name).exists():
            raise ValueError(f"missing export: dist/{name}")
    files = [path for name in names for path in
             ([output / name] if (output / name).is_file() else (output / name).rglob("*"))
             if path.is_file()]
    if any(path.stat().st_size >= 100 * 1024**2 for path in files):
        raise ValueError("export contains a file exceeding GitHub's 100 MiB limit")
    if sum(path.stat().st_size for path in files) >= 1024**3:
        raise ValueError("export exceeds GitHub Pages' 1 GiB site limit")
    remote = subprocess.check_output(
        ["git", "remote", "get-url", "origin"], cwd=ROOT, text=True,
    ).strip()
    with tempfile.TemporaryDirectory(prefix="mathcqm-deploy-") as temporary:
        checkout = Path(temporary)

        def git(*args):
            return subprocess.run(["git", *args], cwd=checkout, check=True)

        git("init", "--initial-branch=deploy")
        git("remote", "add", "origin", remote)
        existing = subprocess.check_output(
            ["git", "ls-remote", "--heads", "origin", "deploy"], cwd=checkout, text=True,
        ).strip()
        if existing:
            git("fetch", "--depth=1", "origin", "deploy")
            git("checkout", "-B", "deploy", "FETCH_HEAD")
            git("rm", "-r", "--ignore-unmatch", ".")
        for name in names:
            source = output / name
            if source.is_dir():
                shutil.copytree(source, checkout / name)
            else:
                shutil.copy2(source, checkout / name)
        (checkout / ".nojekyll").touch()
        git("add", ".")
        git("commit", "--allow-empty", "-m", "Deploy presentation (1080p, 60 fps)")
        git("push", "origin", "HEAD:refs/heads/deploy")
    pages = "repos/charlietharas/mathcqm/pages"
    status = subprocess.run(
        ["gh", "api", pages], cwd=ROOT, capture_output=True, text=True,
    )
    if status.returncode and "404" not in status.stderr:
        raise subprocess.CalledProcessError(status.returncode, status.args, stderr=status.stderr)
    subprocess.run(
        ["gh", "api", "--method", "POST" if status.returncode else "PUT", pages,
         "-f", "build_type=legacy", "-f", "source[branch]=deploy", "-f", "source[path]=/"],
        cwd=ROOT, check=True,
    )
    print("Published deploy branch: https://charliemax.dev/mathcqm/")


def main():
    parser = argparse.ArgumentParser(
        description="Render and present the Manim deck defined in deck.toml.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Commands:
  list     List registered scene names in presentation order.
  render   Invoke Manim for named scenes, or all scenes if none are given.
           Names are case-insensitive; the Slide suffix is optional.
           Uses Manim animation caching; records successful renders for build.
           Does not export HTML or pictures.
  build    Render changed scenes or scenes with missing outputs, then export
           the HTML video deck and picture stills. First build renders all.
           Export and picture generation run even if no scenes changed.
  export   Regenerate HTML video deck and picture stills from existing renders.
  deploy   Force-render all scenes at 1920x1080, 60 fps without caching, export,
           then push the site to origin/deploy for GitHub Pages.
  img      Regenerate picture stills only; requires renders and Reveal assets
           from a previous export/build.
  serve    Serve dist/ on localhost:8000 (or --port). Video: /; pictures: /img/.

Examples:
  python deck.py list
  python deck.py build
  python deck.py build --helpers
  python deck.py build --force
  python deck.py deploy
  python deck.py render perceptron
  python deck.py render TitleSlide AgendaSlide
  python deck.py export
  python deck.py serve --port 8080

Settings and rebuilds:
  deck.toml: scene order, resolution, loopingLevel, skip_reversing.
  manim.cfg: frame_rate, quality, background, and other Manim settings.
  Build tracks project Python/config and Python/Manim versions. _helpers.py,
  image assets, and external configuration/tool changes are not tracked:
  use build --helpers to rerender all scenes with animation caching enabled,
  or explicitly render affected scenes. build --force disables animation caching.
  Build state: media/deck-build-state.json. Outputs: slides/, media/, dist/.
""",
    )
    parser.add_argument(
        "command", choices=["list", "render", "export", "img", "build", "deploy", "serve"],
        help="operation to perform (described below)",
    )
    parser.add_argument("scenes", nargs="*", metavar="SCENE", help="registered scene names; omit to render all (render only)")
    parser.add_argument("--port", type=int, default=8000, help="localhost HTTP port (serve only; default: 8000)")
    rebuild = parser.add_mutually_exclusive_group()
    rebuild.add_argument("--force", action="store_true", help="rerender all scenes without animation caching (build only)")
    rebuild.add_argument("--helpers", action="store_true", help="rerender all scenes with animation caching enabled (build only)")
    args = parser.parse_args()
    if args.force and args.command != "build":
        parser.error("--force only valid with build")
    if args.helpers and args.command != "build":
        parser.error("--helpers only valid with build")
    if args.scenes and args.command != "render":
        parser.error("scenes only valid with render")
    try:
        deck = load_deck()
        if args.command == "list":
            for index, slide in enumerate(deck["slides"], 1):
                print(f"{index:2}. {slide['scene']:24} {slide['file']}")
        elif args.command == "render":
            selected = resolve_scene_names(args.scenes, deck["slides"])
            render(
                [s for s in deck["slides"] if not args.scenes or s["scene"] in selected],
                deck.get("resolution", [1920, 1080]),
            )
        elif args.command == "img":
            img(deck)
        elif args.command in ("build", "export", "deploy"):
            if args.command == "deploy":
                try:
                    confirmed = input(
                        "Force-render all scenes at 1080p/60 fps and publish to "
                        "https://charliemax.dev/mathcqm/? [y/N] "
                    ).strip().lower() in {"y", "yes"}
                except EOFError:
                    confirmed = False
                if not confirmed:
                    print("Deployment cancelled.")
                    return
                subprocess.run(["gh", "auth", "status"], cwd=ROOT, check=True)
                subprocess.run(["git", "ls-remote", "origin", "HEAD"], cwd=ROOT, check=True)
                render(deck["slides"], [1920, 1080], force=True, frame_rate=60)
            if args.command == "build":
                render(deck["slides"], deck.get("resolution", [1920, 1080]),
                       changed_only=not args.helpers, force=args.force)
            export(deck)
            img(deck)
            if args.command == "deploy":
                publish()
                return
            print(f"Open locally: python deck.py serve")
            print(f"  video  http://localhost:8000/")
            print(f"  stills http://localhost:8000/img/")
        else:
            directory = ROOT / "dist"
            if not (directory / "index.html").is_file():
                raise ValueError("no deck yet; run build")
            handler = partial(SimpleHTTPRequestHandler, directory=str(directory))
            with ThreadingHTTPServer(("127.0.0.1", args.port), handler) as server:
                print(
                    f"Open http://localhost:{args.port}/ (video) or "
                    f"/img/ (pictures), Ctrl+C to stop",
                    flush=True,
                )
                server.serve_forever()
    except (ValueError, KeyError, OSError, SyntaxError) as error:
        parser.exit(1, f"error: {error}\n")
    except subprocess.CalledProcessError as error:
        parser.exit(error.returncode, "build failed\n")
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
