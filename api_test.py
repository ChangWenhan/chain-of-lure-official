import os
# from openai import OpenAI
# import os

# # 初始化OpenAI客户端
# client = OpenAI(
#     # 如果没有配置环境变量，请用百炼API Key替换：api_key="sk-xxx"
#     api_key = os.getenv("API_KEY", ""),
#     base_url="https://api.deepseek.com/v1"
# )

# reasoning_content = ""  # 定义完整思考过程
# answer_content = ""     # 定义完整回复
# is_answering = False   # 判断是否结束思考过程并开始回复

# # 创建聊天完成请求
# completion = client.chat.completions.create(
#     model="deepseek-reasoner",  # 此处以 qwq-32b 为例，可按需更换模型名称
#     messages=[
#         {"role": "user", "content": "9.9和9.11谁大"}
#     ],
#     # QwQ 模型仅支持流式输出方式调用
#     stream=True,
#     # 解除以下注释会在最后一个chunk返回Token使用量
#     # stream_options={
#     #     "include_usage": True
#     # }
# )

# print("\n" + "=" * 20 + "思考过程" + "=" * 20 + "\n")

# for chunk in completion:
#     # 如果chunk.choices为空，则打印usage
#     if not chunk.choices:
#         print("\nUsage:")
#         print(chunk.usage)
#     else:
#         delta = chunk.choices[0].delta
#         # 打印思考过程
#         if hasattr(delta, 'reasoning_content') and delta.reasoning_content != None:
#             print(delta.reasoning_content, end='', flush=True)
#             reasoning_content += delta.reasoning_content
#         else:
#             # 开始回复
#             if delta.content != "" and is_answering is False:
#                 print("\n" + "=" * 20 + "完整回复" + "=" * 20 + "\n")
#                 is_answering = True
#             # 打印回复过程
#             print(delta.content, end='', flush=True)
#             answer_content += delta.content




# print("=" * 20 + "完整思考过程" + "=" * 20 + "\n")
# print(reasoning_content)
# print("=" * 20 + "完整回复" + "=" * 20 + "\n")
# print(answer_content)

# coding=utf-8

from openai import OpenAI

base_url = "https://llmapi.blsc.cn/v1" # API地址
api_key = os.getenv("API_KEY", "sk-D0GJSLmufY3Os9W_qyAtbA") # 把yourApiKey替换成已获取的API Key

client = OpenAI(api_key=api_key, base_url=base_url)

response = client.chat.completions.create(
    model = "GLM-5.2", # 模型名称
    messages = [
        {"role": "system", "content": "You are an assistant that thoroughly explores questions through a systematic long thinking process before providing the final precise and accurate solutions. This requires engaging in a comprehensive cycle of analysis, summarization, exploration, reassessment, reflection, backtracing, and iteration to develop a well-considered thinking process. Detail your reasoning process using the specified format: <think>thought with steps separated by '\n\n'</think> Each step should include detailed considerations such as analyzing questions, summarizing relevant findings, brainstorming new ideas, verifying the accuracy of the current steps, refining any errors, and revisiting previous steps. Based on various attempts, explorations, and reflections from the thoughts, you should systematically present the final solution that you deem correct. The solution should remain a logical, accurate, concise expression style and detail necessary steps needed to reach the conclusion. Now, try to solve the following question through the above guidelines."},
        {"role": "user", "content": "hello!"},
    ],
    max_tokens = 2048,
    temperature = 1,
    stream = False,
    extra_body={
        "top_k": 20, 
        "chat_template_kwargs": {"enable_thinking": True},
    },
)

print(response.choices[0].message.content)



# import os
# from openai import OpenAI

# client = OpenAI(
#     # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
#     api_key=os.getenv("API_KEY", ""), 
#     base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
# )
# completion = client.chat.completions.create(
#     model="qwen-turbo-0206", # 此处以qwen-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
#     messages=[
#         {'role': 'system', 'content': 'You are a helpful assistant.'},
#         {'role': 'user', 'content': '你是谁？'}],
#     )
    
# print(completion.model_dump_json())