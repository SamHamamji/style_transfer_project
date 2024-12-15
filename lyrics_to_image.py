import argparse
import os
import openai
import dotenv

import src.prompts as prompts
import src.generation as generation


parser = argparse.ArgumentParser()
parser.add_argument("--lyrics_path", type=str, required=True)
parser.add_argument("--output_path", type=str, required=True)
parser.add_argument("--max_retries", type=int, default=3)
parser.add_argument("--image_size", type=str, default="1024x1024")
parser.add_argument("--log_description", action="store_true")
parser.add_argument("--log_image_url", action="store_true")
parser.add_argument("--magical_atmosphere", action="store_true")
parser.add_argument("--include_intricate_details", action="store_true")
parser.add_argument("--style_by_artist", type=str, default=None)


if __name__ == "__main__":
    args = parser.parse_args()

    dotenv.load_dotenv()
    openai.api_key = os.environ["OPENAI_API_KEY"]

    with open(args.lyrics_path, "r", encoding="utf-8") as file:
        song_lyrics = file.read()

    prompt = prompts.get_scene_description_prompt(
        song_lyrics,
        args.magical_atmosphere,
        args.include_intricate_details,
        args.style_by_artist,
    )

    for i in range(args.max_retries):
        try:
            scene_description = generation.generate_text(prompt)
            if args.log_description:
                print(f"Scene description: {scene_description}", end="\n\n")
            image = generation.generate_image(
                f"{scene_description}\n\nDo not include words in the generated image.",
                args.image_size,
                args.log_image_url,
            )
            break
        except openai.BadRequestError as e:
            if i == args.max_retries - 1:
                print("Image generation rejected. Max number of retries exceeded!")
                exit(1)

            print("Image generation rejected for content policy violation. Retrying...")
            prompt = prompts.get_scene_fixing_prompt(scene_description)

    with open(args.output_path, "wb") as file:
        file.write(image)
    print(f"Image saved successfully at {args.output_path}")
