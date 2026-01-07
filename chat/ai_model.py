import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_NAME = "microsoft/phi-3-mini-4k-instruct"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float32,
    device_map="auto"
)

model.eval()


def format_messages(messages):
    prompt = ""
    for m in messages:
        if m["role"] == "system":
            prompt += f"<|system|>\n{m['content']}\n"
        elif m["role"] == "user":
            prompt += f"<|user|>\n{m['content']}\n"
        elif m["role"] == "assistant":
            prompt += f"<|assistant|>\n{m['content']}\n"

    prompt += "<|assistant|>\n"
    return prompt


def generate_reply(messages, max_new_tokens=256):
    prompt = format_messages(messages)

    inputs = tokenizer(prompt, return_tensors="pt")

    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
        )

    decoded = tokenizer.decode(output[0], skip_special_tokens=True)

    # return only the assistant reply
    return decoded.split("<|assistant|>")[-1].strip()
