from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

model_name = "pierreguillou/gpt2-small-portuguese"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name).to("cuda")

def autocomplete_question(prefix, num_suggestions=3, max_new_tokens=12):
    # Tokeniziraj input
    inputs = tokenizer(prefix, return_tensors="pt").to("cuda")

    # Generiraj više prijedloga
    outputs = model.generate(
        inputs["input_ids"],
        attention_mask=inputs["attention_mask"],
        max_new_tokens=max_new_tokens,
        do_sample=True,
        top_p=0.85,
        temperature=0.8,
        no_repeat_ngram_size=2,
        repetition_penalty=1.2,
        num_return_sequences=num_suggestions,
        pad_token_id=tokenizer.eos_token_id,
        early_stopping=True
    )

    suggestions = []
    for o in outputs:
        text = tokenizer.decode(o, skip_special_tokens=True)
        # Makni prefix
        suggestion = text[len(prefix):].strip()
        # Skraćivanje do prvog upitnika
        if "?" in suggestion:
            suggestion = suggestion.split("?")[0] + "?"
        else:
            # Ako model nije generirao upitnik, pokušaj skratiti do prve točke ili uskličnika
            for end_char in [".", "!"]:
                if end_char in suggestion:
                    suggestion = suggestion.split(end_char)[0] + "?"
                    break
        suggestions.append(suggestion)

    return suggestions

# Test
q = "mudança climática"
results = autocomplete_question(q)

for i, r in enumerate(results, 1):
    print(f"Prijedlog {i}: {q} {r}")
