from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

class PortugueseAutocomplete:
    def __init__(self, model_name: str="pierreguillou/gpt2-small-portuguese", device: str="cuda"):
        self.device: str = device if torch.cuda.is_available() else "cpu"
        self.tokenizer: AutoTokenizer = AutoTokenizer.from_pretrained(model_name) # type: ignore
        self.model: AutoModelForCausalLM = AutoModelForCausalLM.from_pretrained(model_name).to(self.device) # type: ignore

    def autocomplete(self, prefix, num_suggestions=3, max_new_tokens=12) -> list[str]:
        inputs = self.tokenizer(prefix, return_tensors="pt").to(self.device) # Tokeniz the input

        # generate multiple suggestions
        outputs = self.model.generate(
            inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_new_tokens=max_new_tokens,
            do_sample=True,
            top_p=0.85,
            temperature=0.8,
            no_repeat_ngram_size=2,
            repetition_penalty=1.2,
            num_return_sequences=num_suggestions,
            pad_token_id=self.tokenizer.eos_token_id,
            early_stopping=True,
        )

        suggestions: list[str] = []
        for o in outputs:
            text = self.tokenizer.decode(o, skip_special_tokens=True) # type: ignore
            suggestion = text[len(prefix):].strip()
            if "?" in suggestion: # short until the first question mark ?
                suggestion = suggestion.split("?")[0] + "?"
            else:
                for end_char in [".", "!"]:
                    if end_char in suggestion:
                        suggestion = suggestion.split(end_char)[0] + "?"
                        break
            suggestions.append(suggestion)

        return suggestions