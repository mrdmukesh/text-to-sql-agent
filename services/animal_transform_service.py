import base64
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is missing. Please add it in your .env file or Streamlit secrets."
        )

    return OpenAI(api_key=api_key)


def generate_animal_transformation(uploaded_image, animal_name):
    client = get_openai_client()

    uploaded_image.seek(0)

    prompt = f"""
    Create a realistic human-to-{animal_name} face transformation.

IMPORTANT:
Do NOT replace the human face with a full animal head.
Keep the person clearly recognizable as human.
Keep the same human facial structure, eyes, nose position, mouth shape, skin tone,
expression, hairstyle, pose, lighting, clothes, and background.

Apply only partial {animal_name} features:
- {animal_name} skin/fur pattern blended onto the human face
- subtle animal ears if suitable
- light nose/mouth styling
- natural face paint / prosthetic style transformation
- keep 60% human and 40% {animal_name}

The result should look like a human portrait with {animal_name} features,
similar to artistic face transformation makeup.
Photorealistic, clean, front-facing portrait.
Do not create a full animal face.
Do not change the person into an animal.
Do not add extra objects, text, or watermark.
    """

    result = client.images.edit(
        model="gpt-image-1",
        image=uploaded_image,
        prompt=prompt,
        size="1024x1024"
    )

    image_base64 = result.data[0].b64_json
    return base64.b64decode(image_base64)