import openai

def analyze_content(text: str, image_base64: str) -> dict:
    model_name = "gpt-4-vision-preview"
    prompt = (
        "Далее будет текст и фото о романе Льва Николаевича Толстого 'Анна Каренина'. "
        "Нужно ответить, правда это или ложь, обосновать и указать степень уверенности в процентах.\n"
        f"Текст: {text}\nФото: {image_base64[:100]}... (base64 обрезан)"
    )

    response = openai.ChatCompletion.create(
        model=model_name,
        messages=[{"role": "system", "content": "Ты эксперт по литературе."},
                  {"role": "user", "content": prompt}]
    )
    reply = response["choices"][0]["message"]["content"]

    # Извлекаем степень уверенности (можно доработать парсинг)
    confidence = 80  # По умолчанию, если ChatGPT не указал уверенность
    if "%" in reply:
        try:
            confidence = int(next(filter(str.isdigit, reply.split("%"))) or confidence)
        except ValueError:
            pass

    verdict = "правда" in reply.lower()
    return {"model_name": model_name, "verdict": verdict, "reason": reply, "confidence": confidence}
