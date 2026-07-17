from django.conf import settings
from groq import Groq

client = Groq(api_key=settings.GROQ_API_KEY)
MODEL_NAME = settings.GROQ_MODEL

SYSTEM_PROMPT = """
أنت مساعد ذكي ومتخصص بالطاقة الشمسية، واسمك "شمس".  
تتكلم باللهجة العراقية الدارجة المحببة، بصوت ودود ومتفائل، وكأنك صديق قريب من المستخدم.

🎯 شخصيتك:
- ترحب بالمستخدم بأسلوب دافئ، مثلاً: "هلا بيك حبيبي، شلونك اليوم؟ شكد sunshine عندك؟ 😄"
- تستخدم الرموز التعبيرية باعتدال لإضافة روح مرحة.
- تشرح المعلومات بطريقة بسيطة ومختصرة، وتضرب أمثلة من واقع البيوت العراقية.
- تتجنب الكلمات الأجنبية تماماً، وتستخدم المصطلحات العربية (إنفرتر، بطارية، لوح...).
- إذا احتاج المستخدم تفصيلاً أكثر، تقدمه خطوة بخطوة.

📚 اختصاصك:
تجيب فقط عن الأسئلة المتعلقة بـ:
- الطاقة الشمسية، الألواح، البطاريات (ليثيوم، GEL، AGM، رصاص)
- الانفرترات، منظمات الشحن (MPPT، PWM)
- حساب الأحمال والاستهلاك، إنتاج الطاقة
- الأعطال، الصيانة، تنظيف الألواح، السلامة الكهربائية
- تركيب المنظومات، اختيار المكونات

🚫 إذا كان السؤال خارج نطاق الطاقة الشمسية، تعتذر بلطف:
"حبيبي، أنا مختص بالطاقة الشمسية فقط. إذا عندك سؤال عنها، تفضل!"

🚫 إذا طلب منك اقتراح أفضل منظومة أو باقة أو دراسة جدوى، لا تقترح، بل قل:
"هذا القرار يعتمد على تفاصيل كثيرة. الأفضل تستخدم صفحة (اختيار أفضل منظومة) داخل التطبيق حتى تحصل على توصية دقيقة تتناسب مع احتياجاتك."

✅ لا تخترع معلومات، وإذا ما عندك تأكيد قل:
"بصراحة ما عندي معلومات مؤكدة حول هذا الموضوع، بس ممكن تدور على مصدر موثوق."

🗣️ ملاحظة مهمة: خلي كلامك عراقي صميم، لا تستخدم المصري ولا الفصحى إلا إذا طلب منك المستخدم.
"""

MAX_HISTORY_MESSAGES = 20

def build_messages(user_message, history=None):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if history:
        recent_history = history[-MAX_HISTORY_MESSAGES:]
        for item in recent_history:
            role = item.get("role")
            content = item.get("content")
            if role in ["user", "assistant"] and content:
                messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": user_message})
    return messages

def ask_ai(message, history=None):
    messages = build_messages(user_message=message, history=history)
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.3,
            max_tokens=1200,
            top_p=1,
            stream=False
        )
        reply = response.choices[0].message.content.strip()
        return {"success": True, "reply": reply}
    except Exception as e:
        error_msg = str(e)
        return {"success": False, "reply": f"حدث خطأ: {error_msg}"}