function DetectLanguage(texts: string[]) -> string[] {
  client "AliQwenlite"
  prompt #"
    You are a language detection expert. Analyze each input text independently and return the corresponding language code.

    SUPPORTED LANGUAGES:
    zh=Chinese, en=English, es=Spanish, pt=Portuguese, ar=Arabic, ru=Russian, 
    fr=French, de=German, th=Thai, vi=Vietnamese, id=Indonesian, ms=Malay, 
    tr=Turkish, it=Italian, nl=Dutch, pl=Polish, ja=Japanese, ko=Korean

    INPUT TEXTS:
    {% for text in texts %}
    {{ loop.index }}: "{{ text }}"
    {% endfor %}

    INSTRUCTIONS:
    - Analyze each text individually
    - Maintain the same order as input
    - Use exact codes from the list above

    OUTPUT FORMAT: ["code1", "code2", "code3"]

    {{ ctx.output_format }}
    "#
  }

  test DetectLanguage_test_case {
    functions [DetectLanguage]
    args {
      texts [
        "你好，今天的天气怎么样？",
        "Hello, how are you today?",
        "Hola, ¿cómo estás?",
        "今天天气晴朗，适合出行。"
      ]
    }
    @@assert({{ this == ["zh", "en", "es", "zh"] }})
  }

  test DetectLanguage_english_misdetection_cases {
    functions [DetectLanguage]
    args {
      texts [
        "End Route",
        "I want to listen to Kings of Leon"
      ]
    }
    @@assert({{ this[0] == "en" }})
    @@assert({{ this[1] == "en" }})
  }
  

