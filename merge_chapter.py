import argparse
import shutil
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SHOT_DIR = PROJECT_ROOT / "outputs" / "shots"
DEFAULT_OUTPUT = PROJECT_ROOT / "outputs" / "chapter01.mp4"
DEFAULT_SHOTS = tuple(f"shot{index:03d}.mp4" for index in range(1, 13))


def ffmpeg_concat_path(path: Path) -> str:
    normalized = path.resolve().as_posix()
    return normalized.replace("'", r"'\''")


def build_concat_file(shots: list[Path], concat_file: Path) -> None:
    lines = [f"file '{ffmpeg_concat_path(shot)}'" for shot in shots]
    concat_file.write_text("\n".join(lines) + "\n", encoding="utf-8")


def merge_chapter(ffmpeg: str, shot_dir: Path, output_path: Path, shot_names: tuple[str, ...]) -> None:
    if not shutil.which(ffmpeg):
        raise RuntimeError(
            f"Cannot find ffmpeg executable: {ffmpeg}. Install ffmpeg or pass --ffmpeg with its full path."
        )

    shots = [shot_dir / name for name in shot_names]
    missing = [shot for shot in shots if not shot.exists()]
    if missing:
        missing_text = "\n".join(str(path) for path in missing)
        raise FileNotFoundError(f"Missing input video(s):\n{missing_text}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    concat_file = output_path.parent / "chapter01_concat.txt"
    build_concat_file(shots, concat_file)

    command = [
        ffmpeg,
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_file),
        "-c",
        "copy",
        str(output_path),
    ]

    print("Running:", " ".join(command))
    try:
        subprocess.run(command, check=True)
    finally:
        concat_file.unlink(missing_ok=True)

    print(f"Saved: {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Merge chapter 01 shots into one MP4 with ffmpeg.")
    parser.add_argument("--ffmpeg", default="ffmpeg", help="ffmpeg executable name or full path.")
    parser.add_argument("--shot-dir", type=Path, default=DEFAULT_SHOT_DIR, help="Directory containing shot MP4 files.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output chapter MP4 path.")
    parser.add_argument(
        "--shot-count",
        type=int,
        default=len(DEFAULT_SHOTS),
        help="Number of sequential shots to merge, starting at shot001.mp4.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.shot_count < 1:
        raise ValueError("--shot-count must be at least 1")
    merge_chapter(
        ffmpeg=args.ffmpeg,
        shot_dir=args.shot_dir,
        output_path=args.output,
        shot_names=tuple(f"shot{index:03d}.mp4" for index in range(1, args.shot_count + 1)),
    )
