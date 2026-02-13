import argparse
import os
import subprocess
import sys
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader
from PIL import Image

PROJECT_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = PROJECT_DIR / "templates"
LOCK_FILE = PROJECT_DIR / ".lock"

MIPMAP_SIZES = {
    "mdpi": 48,
    "hdpi": 72,
    "xhdpi": 96,
    "xxhdpi": 144,
    "xxxhdpi": 192,
}

TEMPLATE_MAP = {
    "root-build.gradle.kts.j2": PROJECT_DIR / "build.gradle.kts",
    "app-build.gradle.kts.j2": PROJECT_DIR / "app" / "build.gradle.kts",
    "settings.gradle.kts.j2": PROJECT_DIR / "settings.gradle.kts",
    "strings.xml.j2": PROJECT_DIR / "app" / "src" / "main" / "res" / "values" / "strings.xml",
    "themes.xml.j2": PROJECT_DIR / "app" / "src" / "main" / "res" / "values" / "themes.xml",
}


def render_templates(config: dict) -> None:
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), keep_trailing_newline=True)
    for template_name, output_path in TEMPLATE_MAP.items():
        output_path.parent.mkdir(parents=True, exist_ok=True)
        template = env.get_template(template_name)
        output_path.write_text(template.render(config))


def generate_icons(icon_path: str) -> None:
    img = Image.open(icon_path)
    for density, size in MIPMAP_SIZES.items():
        out_dir = PROJECT_DIR / "app" / "src" / "main" / "res" / f"mipmap-{density}"
        out_dir.mkdir(parents=True, exist_ok=True)
        resized = img.resize((size, size), Image.LANCZOS)
        resized.save(out_dir / "ic_launcher.png")


def build(config_path: str) -> None:
    if LOCK_FILE.exists():
        print(f"error: lock file exists at {LOCK_FILE}", file=sys.stderr)
        print("another build may be running — remove .lock if stale", file=sys.stderr)
        sys.exit(1)

    LOCK_FILE.touch()
    try:
        config_file = Path(config_path).resolve()
        config = yaml.safe_load(config_file.read_text())
        config.setdefault("theme_color", "#0a0a0a")
        config.setdefault("refresh_timeout_sec", 10)

        icon_path = Path(config["icon"])
        if not icon_path.is_absolute():
            icon_path = config_file.parent / icon_path

        render_templates(config)
        generate_icons(str(icon_path))

        android_home = os.environ.get("ANDROID_HOME", str(Path.home() / "Android" / "Sdk"))
        env = {**os.environ, "ANDROID_HOME": android_home}

        subprocess.run(
            [str(PROJECT_DIR / "gradlew"), "assembleDebug"],
            cwd=PROJECT_DIR,
            env=env,
            check=True,
        )

        apk_path = PROJECT_DIR / "app" / "build" / "outputs" / "apk" / "debug" / "app-debug.apk"
        print(apk_path)
    finally:
        LOCK_FILE.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(prog="webview-apk")
    subparsers = parser.add_subparsers(dest="command")

    build_parser = subparsers.add_parser("build")
    build_parser.add_argument("config", help="path to YAML config file")

    args = parser.parse_args()

    if args.command == "build":
        build(args.config)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
