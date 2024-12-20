import dotenv
import openai
import os
import novita_client
import requests

dotenv.load_dotenv()
openai.api_key = os.environ["OPENAI_API_KEY"]


def generate_text(prompt: str):
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are an expert in analyzing song lyrics for artistic interpretation.",
            },
            {"role": "user", "content": prompt},
        ],
    )

    description = response.choices[0].message.content

    if description is None:
        raise ValueError(f"Scene description is None in response: {response}")

    return description.strip()


def generate_image(prompt: str, image_size, log_url: bool):
    response = openai.images.generate(
        prompt=prompt, model="dall-e-3", n=1, size=image_size
    )

    image_url = response.data[0].url

    if image_url is None:
        raise ValueError(f"Image url is None in response: {response}")

    if log_url:
        print(f"Image url: {image_url}")

    response = requests.get(image_url, timeout=120)

    if response.content is None:
        raise ValueError(f"Image content is None in response: {response}")

    return response.content


def generate_video(prompt: dict[str, str], log_url: bool):
    client = novita_client.NovitaClient(os.environ["NOVITA_API_KEY"])
    response = client.txt2video(
        model_name="dreamshaper_8_93211.safetensors",
        width=640,
        height=480,
        guidance_scale=7.5,
        steps=22,
        seed=-1,
        prompts=[
            {"prompt": prompt[f"frame_{i}"], "frames": 20}
            for i in range(1, len(prompt) + 1)
        ],  # type: ignore
        negative_prompt="(worst quality:2), (low quality:2), (normal quality:2), ((monochrome)), ((grayscale)), bad hands, closeups, close distance, naked, sexual, sex, seductive",
    )

    if log_url:
        print(f"Video url: {response.videos[0].video_url}")  # type: ignore

    video_bytes: bytes = response.video_bytes[0]  # type: ignore
    return video_bytes
