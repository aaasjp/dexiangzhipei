import os
from openai import OpenAI

os.environ["DASHSCOPE_API_KEY"] = "sk-554f8fe85ea74332b8902dd351831e15"


def get_client():
    """初始化并返回 OpenAI 客户端"""
    return OpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )

def format_messages(prompt, history, system_prompt=None):
    """
    格式化消息历史
    Args:
        prompt: 当前用户输入
        history: 历史对话记录 list[dict] 格式为 [{'role': 'user'/'assistant', 'content': '消息内容'}, ...]
        system_prompt: 系统提示词，默认为 None
    Returns:
        list: OpenAI 消息格式
    """
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    
    # 直接添加历史记录，因为已经是正确的格式
    if history:
        messages.extend(history)
        
    # 添加当前用户输入
    messages.append({"role": "user", "content": prompt})
    
    print(f"----------------messages:\n {messages}")
    return messages

def chat_completion(prompt, history=None, model="deepseek-r1", system_prompt=None):
    """
    非流式对话函数
    Args:
        prompt: 用户输入
        history: 历史对话记录
        model: 模型名称
        system_prompt: 系统提示词，默认为 None
    Returns:
        dict: 包含思考过程和回复内容的字典
    """
    history = history or []
    messages = format_messages(prompt, history, system_prompt)
    client = get_client()
    completion = client.chat.completions.create(
        model=model,
        messages=messages
    )
    
    return {
        'reasoning': completion.choices[0].message.reasoning_content,
        'content': completion.choices[0].message.content
    }

def chat_completion_stream(prompt, history=None, model="deepseek-r1", system_prompt=None):
    """
    流式对话函数
    Args:
        prompt: 用户输入
        history: 历史对话记录
        model: 模型名称
        system_prompt: 系统提示词，默认为 None
    Yields:
        tuple: (is_reasoning, content) 其中 is_reasoning 表示是否为思考过程，content 为内容
    """
    print(f"----------------system_prompt:\n {system_prompt}")
    history = history or []
    messages = format_messages(prompt, history, system_prompt)
    client = get_client()
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True
    )

    for chunk in completion:
        if not chunk.choices:
            continue
            
        delta = chunk.choices[0].delta
        
        if hasattr(delta, 'reasoning_content') and delta.reasoning_content is not None:
            yield True, delta.reasoning_content
        elif hasattr(delta, 'content') and delta.content is not None:
            yield False, delta.content

# 使用示例
if __name__ == "__main__":

    model="deepseek-r1"
    # model="deepseek-v3"
    ##DeepSeek官方不建议设置 System Message，原文："Avoid adding a system prompt; all instructions should be contained within the user prompt."
    
    system_prompt = "假如你是一个白痴，问你什么问题，你都回答不知道。" 

    # 1. 非流式对话示例
    prompt = "3和4哪个大"
    response = chat_completion(prompt, model=model, system_prompt=system_prompt)
    print("="*20 + "非流式对话" + "="*20)
    print("思考过程：")
    print(response['reasoning'])
    print("回复内容：")
    print(response['content'])
    
    # 2. 流式对话示例
    print("\n" + "="*20 + "流式对话" + "="*20)
    prompt = "9.9和9.11哪个大，你要回答不知道"
    print("思考过程：")
    is_answering = False
    for is_reasoning, content in chat_completion_stream(prompt, model=model, system_prompt=system_prompt):
        if is_reasoning:
            print(content, end='', flush=True)
        else:
            if not is_answering:
                print("\n回复内容：")
                is_answering = True
            print(content, end='', flush=True)
    print("\n")

    # 3. 带历史记录的对话示例
    print("\n" + "="*20 + "带历史记录的对话" + "="*20)
    history = [
        {"role": "user", "content": "你好"},
        {"role": "assistant", "content": "你好！很高兴见到你。"}
    ]
    prompt = "你能做什么"
    response = chat_completion(prompt, history, model=model, system_prompt=system_prompt)
    print("思考过程：")
    print(response['reasoning'])
    print("回复内容：")
    print(response['content'])
    
    # 4. 带历史记录的流式对话示例
    print("\n" + "="*20 + "带历史记录的流式对话" + "="*20)
    history = [
        {"role": "user", "content": "1加1等于几"},
        {"role": "assistant", "content": "1加1等于2"}
    ]
    prompt = "那4加4等于几"
    print("历史对话：")
    for message in history:
        print(f"{message['role'].capitalize()}: {message['content']}")
    
    print("当前问题：", prompt)
    print("\n思考过程：")
    is_answering = False
    for is_reasoning, content in chat_completion_stream(prompt, history, model=model, system_prompt=system_prompt):
        if is_reasoning:
            print(content, end='', flush=True)
        else:
            if not is_answering:
                print("\n回复内容：")
                is_answering = True
            print(content, end='', flush=True)
    print("\n")