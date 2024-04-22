import transformers
import torch
from tokenizers import Tokenizer

model_id = "meta-llama/Meta-Llama-3-8B-Instruct"

pipeline = transformers.pipeline(
    "text-generation",
    model=model_id,
    model_kwargs={"torch_dtype": torch.bfloat16},
    device="cuda",
)
auto_tokenizer = transformers.AutoTokenizer.from_pretrained(model_id)
streamer = transformers.TextStreamer(auto_tokenizer, skip_prompt=True)
streamer_iterator = transformers.TextIteratorStreamer(auto_tokenizer, skip_prompt=True)
task = """
Task: Write a Python function to reverse a singly linked list.

Details:
- Input: The head node of a singly linked list.
- Output: The head node of the reversed linked list.

Requirements:
1. Function Signature: def reverse_linked_list(head: ListNode) -> ListNode
2. ListNode Class Definition:
   class ListNode:
       def __init__(self, val=0, next=None):
           self.val = val
           self.next = next
3. Explanation: Include a brief explanation of how your code works.
4. Constraints: Do not use additional data structures like lists or tuples for storage.
5. Examples:
   - Input: 1 -> 2 -> 3 -> None, Output: 3 -> 2 -> 1 -> None
   - Input: None, Output: None

Please ensure your solution is efficient and add comments where necessary for clarity.
"""
task = "Write a simple ROS2 publisher node and subscriber node in c++"
messages = [
    {"role": "system", "content": "You are a software engineer that provides the code to the respective question"},
    {"role": "user", "content": task}
]

prompt = pipeline.tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
)

terminators = [
    pipeline.tokenizer.eos_token_id,
    pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
]
# from threading import Thread
# def prompt_generator():
#     outputs = pipeline(
#         prompt,
#         max_new_tokens=1000,
#         eos_token_id=terminators,
#         do_sample=True,
#         streamer=streamer_iterator
#     )
#
# t = Thread(target=prompt_generator)
# t.start()
#
#
# for i in streamer_iterator:
#     print(i, end="")
# print(outputs[0]["generated_text"][len(prompt):])


import asyncio

async def generate_text():
    # This would be an asynchronous call if supported
    outputs = await pipeline(
        prompt,
        max_new_tokens=1000,
        eos_token_id=terminators,
        do_sample=True
    )
    return outputs

async def main():
    text = await generate_text()
    print(text)

# Run the async main function
asyncio.run(main())