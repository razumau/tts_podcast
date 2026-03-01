from ollama import generate

def remove_empty_lines(text: str):
    return '\n'.join(line for line in text.split('\n') if line.strip())

def split_into_groups_of_paragraphs(text: str, groups_count: int = 5):
    paragraphs = text.split('\n')
    return ['\n'.join(paragraphs[i:i + groups_count]) for i in range(0, len(paragraphs), groups_count)]


def remove_image_descriptions(text: str, model):
    prompt = ("In the following text, there might be paragraphs which describe a missing image or its source. "
              "Remove such paragraphs and output everything else without changes. "
              "Output only the updated text without any additional information.")
    response = generate(model, f'{prompt}\n"{text}"')
    print(f"removal duration for {len(text)} characters: {response['total_duration'] / 1_000_000} ms")
    return response['response']


def spell_out_dates(text_without_images: str):
    pass


def cleanup(text: str):
    models = ['llama3.2', 'gemma3:1b-it-qat', 'gemma3']
    for model in models:
        print(f"Testing {model}")
        paragraphs = remove_empty_lines(text)
        groups = split_into_groups_of_paragraphs(paragraphs)
        text_without_images = "\n\n".join(remove_image_descriptions(text, model) for text in groups)
        print(text_without_images, file=open(f"{model.replace(':', '_')}.txt", "w"))
    return ""
    # text_with_spelled_out_dates = spell_out_dates(text_without_images)

