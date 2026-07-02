import argparse
import os
from xai_sdk import Client
from xai_sdk.chat import user, image
import json
import base64


class SimpleXAIClient():
    def __init__(self, api_key: str, timeout=3600):
        self.client = Client(
        api_key=api_key,
        timeout=3600,
    )

    def extract_image_raw(self, prompt: str, image_in_base64: str, model:str="grok-4.3"):
        chat = self.client.chat.create(model=model)
        # chat = client.chat.create(model="grok-4.20-0309-reasoning")
        # chat = client.chat.create(model="grok-4-1-fast-non-reasoning")
        chat.append(
            user(
                prompt,
                image(image_url=f"data:image/jpeg;base64,{image_in_base64}", detail="high"),
            )
        )
        return chat.sample()
    
    def extract_image_content(self, prompt: str, image_in_base64: str):
        return self.extract_image_raw(prompt, image_in_base64).content


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')




def extract_info_from_image(client, image_path):
    print(f"Extracting information from image: {image_path}")

    base64_image = encode_image(image_path)
    response = extract_image(client, base64_image)

    output_path = f"{image_path}.extract-response"
    with open(output_path, "w", encoding="utf-8") as output_file:
        output_file.write(str(response))

    print(f"Saved full response to: {output_path}")

    output_path = f"{image_path}.extract-response-content.json"
    with open(output_path, "w", encoding="utf-8") as output_file:
        output_file.write(json.dumps(json.loads(str(response.content)), ensure_ascii=False, indent=2))

    print(f"Saved full response content JSON to: {output_path}")
    return response, json.loads(str(response.content))
