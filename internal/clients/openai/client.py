import re
import openai
from pprint import pprint


class Client:
    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model_name = model_name

    def analyze_content(self, text: str, image: str) -> dict:
        prompt = (
            "Далее будет текст и фото о романе Льва Николаевича Толстого 'Анна Каренина'. "
            "Нужно ответить, правда это или ложь, затем обосновать свой ответ, а затем указать степень уверенности в процентах. "
            "Пояснения: если кадр не из фильма \"Анна Каренина\" (1967), то это нужно считать ложью; "
            "если кадр из фильма не соответствует описанию, то это нужно считать ложью; "
            "если текст содержит ложь, то это нужно считать ложью; "
            "если кард из фильма был модифицирован, то это нужно считать ложью. "
            "Выведи ответ в следующем формате:\n"
            "1. Вердикт (правда/ложь)\n"
            "2. Обоснование вердикта\n"
            "3. Процент уверенности\n\n"
            f"Текст: {text}\nФото: {image}"
        )

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "Ты эксперт по литературе."},
                {"role": "user", "content": prompt}
            ]
        )

        reply = response.choices[0].message.content.strip().split("\n")

        if len(reply) < 3:
            raise ValueError("Ответ от модели не соответствует ожидаемому формату.")

        verdict = reply[0].strip().lower() == "правда"
        reason = reply[1].strip()
        confidence_match = re.search(r"\d+", reply[2])
        confidence = int(confidence_match.group()) if confidence_match else 80

        return {
            "model_name": self.model_name,
            "verdict": verdict,
            "reason": reason,
            "confidence": confidence
        }


# Пример использования
if __name__ == "__main__":
    api_key = "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"
    client = Client(api_key)

    text = "Александр Вронский испытывал беспокойство за брата, но знал, что тот видел в Анне ту единственную женщину, которая могла понять глубину его чувств."
    image_base64 = "https://i.yapx.ru/Ygw0G.jpg"  # Здесь должно быть base64 изображение

    try:
        result = client.client.models.list()
        pprint('Доступные модели:', result)

        result = client.analyze_content(text, image_base64)
        print("Результат анализа:")
        print(f"Модель: {result['model_name']}")
        print(f"Вердикт: {'Правда' if result['verdict'] else 'Ложь'}")
        print(f"Обоснование: {result['reason']}")
        print(f"Уверенность: {result['confidence']}%")
    except Exception as e:
        print(f"Произошла ошибка: {e}")