import os
from litellm import completion

def get_safe_code_snippet(full_path, line_number, context_window=10):
    """
    Reads the file LOCALLY and returns only a specific window of code.
    The AI never touches your file system directly.
    """
    if not os.path.exists(full_path):
        return f"File not found at: {full_path}"

    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            
            # Calculate the safe window (avoiding negative numbers or going past the end)
            start_index = max(0, line_number - context_window - 1)
            end_index = min(len(all_lines), line_number + context_window)
            
            snippet_lines = all_lines[start_index:end_index]
            
            # Add line numbers and an arrow pointing to the exact error line
            formatted_snippet = []
            for i, line in enumerate(snippet_lines):
                current_line_num = start_index + i + 1
                pointer = ">> " if current_line_num == line_number else "   "
                formatted_snippet.append(f"{pointer}{current_line_num}: {line.rstrip()}")
                
            return "\n".join(formatted_snippet)
            
    except Exception as e:
        return f"Error reading local file: {str(e)}"

def analyze_error(log_entry, parsed_data, config):
    """
    Constructs the prompt and sends it to the configured AI provider.
    """
    ai_config = config.get('ai_analysis', {})
    if not ai_config.get('enabled', False):
        return "AI Analysis is disabled in config."

    # 1. Base Prompt
    prompt = f"I found an error in my logs:\n`{log_entry.strip()}`\n\n"

    # 2. Add Code Context (If enabled and parser found a file)
    if ai_config.get('enable_code_context') and parsed_data:
        file_path = parsed_data['filepath']
        line_num = parsed_data['lineno']
        lang_type = parsed_data.get('type', 'text')
        
        # Resolve the full path based on the project_root in config
        project_root = ai_config.get('project_root', '.')
        full_path = os.path.join(project_root, file_path)
        
        snippet = get_safe_code_snippet(full_path, line_num)
        
        prompt += f"Here is the surrounding code from `{file_path}` around line {line_num}:\n"
        prompt += f"```{lang_type}\n{snippet}\n```\n\n"
    else:
        prompt += "(No local code context was provided. Please give a general fix based on the log message.)\n\n"

    prompt += "Please explain what might be causing this error and suggest a code fix."

    # 3. Setup API Key (from env vars if configured)
    api_key = ai_config.get('model_api_key')

    # 4. Prepare LiteLLM Call
    messages = [
        {"role": "system", "content": "You are an expert developer and debugging assistant. Provide clear, concise explanations and exact code fixes."},
        {"role": "user", "content": prompt}
    ]

    print(f" Sending request to AI ({ai_config['model']})...")
    print(f" Prompt:\n{prompt}...")  # Print the first 500 chars of the prompt for debugging
    

    try:
        # LiteLLM standardizes this call for OpenAI, Anthropic, Gemini, Ollama, etc.
        response = completion(
            model=ai_config['model'],
            messages=messages,
            api_base=ai_config.get('api_base'),
            api_key=api_key
        )
        print(f" AI response received.  { response.choices[0].message.content} ")
        return response.choices[0].message.content
    except Exception as e:
        return f"AI Analysis Failed: {str(e)}"
