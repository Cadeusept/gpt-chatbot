import re

import openai

class Client:
    def __init__(self, api_key: str, model_name: str = "gpt-4-vision-preview"):
        openai.api_key = api_key
        self.model_name = model_name

    def analyze_content(self, text: str, image_base64: str) -> dict:
        prompt = (
            "Далее будет текст и фото о романе Льва Николаевича Толстого 'Анна Каренина'. "
            "Нужно ответить, правда это или ложь, обосновать и указать степень уверенности в процентах.\n"
            f"Текст: {text}\nФото: {image_base64[:100]}... (base64 обрезан)"
        )

        response = openai.ChatCompletion.create(
            model=self.model_name,
            messages=[{"role": "system", "content": "Ты эксперт по литературе."},
                      {"role": "user", "content": prompt}]
        )
        reply = response["choices"][0]["message"]["content"]

        confidence = 80  # Default confidence
        if "%" in reply:
            try:
                match = re.search(r"(\d+)%", reply)
                confidence = int(match.group()) if match else 80
            except ValueError:
                pass

        verdict = "правда" in reply.lower()
        return {"model_name": self.model_name, "verdict": verdict, "reason": reply, "confidence": confidence}
