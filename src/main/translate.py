from transformers import pipeline
pipe_en_hu = pipeline("translation", model="Helsinki-NLP/opus-mt-tc-big-en-hu")
pipe_hu_en = pipeline("translation", model="Helsinki-NLP/opus-mt-tc-big-hu-en")


def translate_sentence(sentence: str, target: str = "hu"):
    if target == "hu":
        return pipe_en_hu(sentence)[0]['translation_text']
    return pipe_hu_en(sentence)[0]['translation_text']

if __name__ == "__main__":
    text = translate_sentence("I wish I hadn't seen such a horrible film.")
    print(text)