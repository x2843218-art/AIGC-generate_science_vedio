import json
import os
import time
from pathlib import Path
from typing import Any, Optional
from urllib.request import urlopen

from volcenginesdkarkruntime import Ark


BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
MODEL = "doubao-seedance-2-0-260128"
DEFAULT_PROMPT_FILE = Path("prompts") / "chapter03.json"
FALLBACK_PROMPT_FILE = Path("prompts") / "chapter03" / "chapter03.json"
OUTPUT_DIR = Path("outputs_2") / "shots03_2"
POLL_INTERVAL_SECONDS = 3
MAX_RETRIES = 3


def load_prompts(json_path: Path = DEFAULT_PROMPT_FILE) -> list[dict[str, Any]]:
    if not json_path.exists() and FALLBACK_PROMPT_FILE.exists():
        json_path = FALLBACK_PROMPT_FILE

    if not json_path.exists():
        raise FileNotFoundError(f"Prompt JSON not found: {json_path}")

    with json_path.open("r", encoding="utf-8-sig") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(f"Prompt JSON must be an array: {json_path}")

    for index, shot in enumerate(data, start=1):
        if not isinstance(shot, dict):
            raise ValueError(f"Shot #{index} must be a JSON object.")
        if not str(shot.get("shot_id", "")).strip():
            raise ValueError(f"Shot #{index} is missing shot_id.")
        if not str(shot.get("prompt", "")).strip():
            raise ValueError(f"Shot #{index} is missing prompt.")

    print(f"Loaded prompt file: {json_path}")
    print(f"Loaded {len(data)} shots")
    return data


def create_client() -> Ark:
    api_key = os.environ.get("ARK_API_KEY")
    if not api_key:
        raise RuntimeError("ARK_API_KEY is not set. Please set it before running this script.")

    return Ark(
        base_url=BASE_URL,
        api_key=api_key,
    )


def build_seedance_prompt(shot: dict[str, Any]) -> str:
    return f"""
场景：
{shot.get("scene", "")}

画面描述：
{shot["prompt"]}

声音设计：
{shot.get("audio_prompt", "")}

注意事项：
{shot.get("notes", "")}

镜头连接：
上一镜头：
{shot.get("previous_connection", "")}

下一镜头：
{shot.get("next_connection", "")}
""".strip()


def generate_video(client: Ark, shot: dict[str, Any], duration: Optional[int] = None) -> str:
    content_text = build_seedance_prompt(shot)

    print("========== Seedance Prompt ==========")
    print(content_text)
    print("=====================================")

    create_kwargs: dict[str, Any] = {
        "model": MODEL,
        "content": [
            {
                "type": "text",
                "text": content_text,
            }
        ],
        "generate_audio": True,
    }

    if duration:
        create_kwargs["duration"] = duration

    create_result = client.content_generation.tasks.create(**create_kwargs)
    task_id = create_result.id
    print("Task created:")
    print(f"task_id {task_id}")
    return task_id


def wait_for_task(client: Ark, task_id: str) -> str:
    print("Waiting for generation to finish...")

    while True:
        result = client.content_generation.tasks.get(task_id=task_id)
        status = result.status
        print(f"Current status: {status}")

        if status == "succeeded":
            video_url = extract_video_url(result)
            if not video_url:
                raise RuntimeError(f"Task succeeded, but no video URL was found: {result}")
            return video_url

        if status == "failed":
            error = getattr(result, "error", None)
            raise RuntimeError(f"Task failed: {error}")

        time.sleep(POLL_INTERVAL_SECONDS)


def download_video(video_url: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with urlopen(video_url) as response:
        with output_path.open("wb") as file:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                file.write(chunk)

    print("Download finished:")
    print(output_path.as_posix())


def extract_video_url(result: Any) -> Optional[str]:
    content = getattr(result, "content", None)
    direct_url = getattr(content, "video_url", None)
    if direct_url:
        return str(direct_url)

    plain = to_plain_data(result)
    urls: list[str] = []

    def walk(value: Any) -> None:
        if isinstance(value, str):
            if value.startswith(("http://", "https://")):
                urls.append(value)
            return

        if isinstance(value, dict):
            for child in value.values():
                walk(child)
            return

        if isinstance(value, list):
            for child in value:
                walk(child)

    walk(plain)

    for url in urls:
        lowered = url.lower()
        if ".mp4" in lowered or "video" in lowered:
            return url

    return urls[0] if urls else None


def to_plain_data(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, dict):
        return {key: to_plain_data(item) for key, item in value.items()}

    if isinstance(value, (list, tuple)):
        return [to_plain_data(item) for item in value]

    if hasattr(value, "model_dump"):
        return to_plain_data(value.model_dump())

    if hasattr(value, "dict"):
        return to_plain_data(value.dict())

    if hasattr(value, "__dict__"):
        return to_plain_data(vars(value))

    return str(value)


def main() -> None:
    client = create_client()
    shots = load_prompts()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for shot in shots:
        shot_id = str(shot["shot_id"]).strip()
        scene = str(shot.get("scene", "")).strip()
        duration = shot.get("duration")
        output_path = OUTPUT_DIR / f"{shot_id}.mp4"

        print("\n" + "=" * 32)
        print(f"Start generating {shot_id}")
        if scene:
            print(f"Scene: {scene}")

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                if attempt > 1:
                    print(f"Retry {attempt}/{MAX_RETRIES} for {shot_id}")

                task_id = generate_video(
                    client=client,
                    shot=shot,
                    duration=int(duration) if duration else None,
                )
                video_url = wait_for_task(client, task_id)
                download_video(video_url, output_path)
                break

            except Exception as exc:
                print(f"{shot_id} failed on attempt {attempt}: {exc}")
                if attempt >= MAX_RETRIES:
                    print(f"{shot_id} reached max retries. Skipping this shot.")
                else:
                    time.sleep(2)

        print("=" * 32)


if __name__ == "__main__":
    main()
