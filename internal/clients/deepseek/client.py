from DeeperSeek import DeepSeek
import re
import asyncio

class Client:
    def __init__(self,  email: str, password: str, model_name: str = "deepseek-vision"):
        """
        Инициализация клиента DeepSeek.

        :param api_key: API ключ для доступа к DeepSeek API.
        :param model_name: Название модели, используемой для анализа (по умолчанию "deepseek-vision").
        """
        self.email = email
        self.password = password
        self.model_name = model_name
        self.client = DeepSeek(email = email, password = password, verbose = True, chrome_args=['--no-sandbox', '--disable-gpu'], headless = True, attempt_cf_bypass = True) # Инициализация клиента DeepSeek

    async def analyze_content(self, text: str, image: str) -> dict:
        """
        Анализирует текст и изображение с помощью DeepSeek API.

        :param text: Текст для анализа.
        :param image: Ссылка на изображение.
        :return: Словарь с результатами анализа.
        """
        # self.client.browser
        await self.client.initialize()

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

        # Формируем запрос к DeepSeek API
        response = await self.client.send_message(prompt, slow_mode = True, deepthink = False, search = False, slow_mode_delay = 0.25)
        print(response.text, response.chat_id)

        # Обрабатываем ответ
        reply = response.text.strip().split("\n")

        if len(reply) < 3:
            raise ValueError("Ответ от модели не соответствует ожидаемому формату.")

        # Извлекаем вердикт, обоснование и уверенность
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
