# import os
# import sys
# from llama_cpp import Llama

# LLAMA_MODEL_PATH = r"C:\Users\kumar\Documents\PREP\backend\models\Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf"

# def chat_with_llama():
#     if not os.path.exists(LLAMA_MODEL_PATH):
#         print(f"Error: Model file not found at {LLAMA_MODEL_PATH}")
#         sys.exit(1)

#     print("Loading LLaMA model...")
#     llm = Llama(model_path=LLAMA_MODEL_PATH, n_ctx=131072, n_gpu_layers=2, verbose=False)
#     print("✅ LLaMA model loaded!\n")

#     conversation_history = []
#     system_prompt = "You are a helpful and knowledgeable assistant."

#     while True:
#         user_input = input("You: ")
#         if user_input.lower() in ["exit", "quit"]:
#             print("Goodbye!")
#             break

#         conversation_history.append({"role": "user", "content": user_input})

#         response_stream = llm.create_chat_completion(
#             messages=[{"role": "system", "content": system_prompt}] + conversation_history,
#             max_tokens=131072,
#             stream=True
#         )

#         print("LLM:", end="", flush=True)
#         assistant_reply = ""
#         for chunk in response_stream:
#             content = chunk.get("choices", [{}])[0].get("delta", {}).get("content")
#             if content:
#                 print(content, end="", flush=True)
#                 assistant_reply += content
#         print()

#         conversation_history.append({"role": "assistant", "content": assistant_reply})

# if __name__ == "__main__":
#     chat_with_llama()
