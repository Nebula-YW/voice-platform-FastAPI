// Learn more about clients at https://docs.boundaryml.com/docs/snippets/clients/overview

client<llm> ProxyGeminiFlash {
  provider google-ai
  options {
    model "gemini-2.5-flash"
    base_url "https://ai-proxy.nebula-tech.site/gemini/v1beta"
    api_key env.GOOGLE_API_KEY
  }
}

client<llm> ProxyGeminiFlashLite {
  provider google-ai
  options {
    model "gemini-2.5-flash-lite"
    base_url "https://ai-proxy.nebula-tech.site/gemini/v1beta"
    api_key env.GOOGLE_API_KEY
  }
}

client MyDeepseekV3 {
  provider openai-generic
  options {
    model "deepseek-chat" //model name: deepseek-reasoner or deepseek-chat
    base_url "https://api.deepseek.com/v1"
    api_key env.DEEPSEEK_API_KEY
  }
}
client MyDeepseekR1 {
  provider openai-generic
  options {
    model "deepseek-reasoner" //model name: deepseek-reasoner or deepseek-chat
    base_url "https://api.deepseek.com/v1"
    api_key env.DEEPSEEK_API_KEY
  }
}

client AliQwen235BA22B {
  provider openai-generic
  options {
    model "qwen3-235b-a22b-instruct-2507" //model name: deepseek-reasoner or deepseek-chat
    base_url "https://dashscope.aliyuncs.com/compatible-mode/v1"
    api_key env.QWEN_API_KEY
  }
}

client AliQwenlite {
  provider openai-generic
  options {
    model "qwen3-1.7b" //model name: deepseek-reasoner or deepseek-chat
    base_url "https://dashscope.aliyuncs.com/compatible-mode/v1"
    api_key env.QWEN_API_KEY
  }
}

client<llm> DoubaoDeepseekV3 {
  provider openai-generic
  options {
    model "deepseek-v3-250324"
    base_url "https://ark.cn-beijing.volces.com/api/v3"
    api_key env.DOUBAO_API_KEY
  }
}

client<llm> Doubaoseedthinking {
  provider openai-generic
  options {
    model "Doubao-Seed-1.6-thinking"
    base_url "https://ark.cn-beijing.volces.com/api/v3"
    api_key env.DOUBAO_API_KEY
  }
}

client GLM45 {
  provider openai-generic
  options {
    model "glm-4.5-x" //model name: deepseek-reasoner or deepseek-chat
    base_url "https://open.bigmodel.cn/api/paas/v4"
    api_key env.ZHUPU_API_KEY
  }
}

client GLM45air {
  provider openai-generic
  options {
    model "glm-4.5-airx" //model name: deepseek-reasoner or deepseek-chat
    base_url "https://open.bigmodel.cn/api/paas/v4"
    api_key env.ZHUPU_API_KEY
  }
}



client<llm> DoubaoDeepseekR1 {
  provider openai-generic
  options {
    model "deepseek-r1-250528"
    base_url "https://ark.cn-beijing.volces.com/api/v3"
    api_key env.DOUBAO_API_KEY
  }
}

// https://docs.boundaryml.com/docs/snippets/clients/retry
retry_policy Constant {
  max_retries 3
  // Strategy is optional
  strategy {
    type constant_delay
    delay_ms 200
  }
}

retry_policy Exponential {
  max_retries 2
  // Strategy is optional
  strategy {
    type exponential_backoff
    delay_ms 300
    multiplier 1.5
    max_delay_ms 10000
  }
}