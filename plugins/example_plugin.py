"""示例插件"""
intent_name = "weather"
description = "查询天气"


def execute(slots):
    city = slots.get("city", "上海")
    return f"{city} 今天天气晴朗，温度 15-22 度。"
