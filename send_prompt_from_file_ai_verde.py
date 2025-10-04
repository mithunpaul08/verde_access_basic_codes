
# This code takes a prompt file and sends it to the llm- this was useful
# in initial stages of miki project, where we didnt want to send a huge file upload to llm, but instead can do it inline


import os
import json
from pathlib import Path
from chains.llm_proxy import build_llm_proxy
import datetime
from utils import *

human_discussions_file_name ="./output/4_discussions_sibrama_edited.docx"
prompt_stub_file_name_create_ddl="./data/all_prompts/prompt_to_create_ddl_from_discussions_with_client.txt"
prompt_stub_file_name_create_brd="./data/all_prompts/prompt_to_create_brd_from_req_doc.txt"
# output_file_name="./output/vba_created_by_chatgpt_from_discussions_with_client_sent_inline_as_prompt.vb"
output_file_name="./output/brd_created_from_req.txt"

# dict_dynamic_business_object_names= {
#     "{input_c````+
# -*
# lass_name}": "clsColors",
#     "{output_class_name}": "clsBuyers"
# }
# input_class_path="./data/color_related/clsColors.vb"

llm_url ='https://llm-api.cyverse.ai'
api_key = os.environ.get('OPENAI_API_KEY')
print(f"api_key is:{api_key}")


llm = build_llm_proxy(
    # model="anthropic/claude-3-7-sonnet-20250219",
    # model="anthropic/claude-3-7-sonnet-latest",
    model ="gpt-4o",
    # model ="gpt-4",
    # model ="gpt-4o-mini",    
    # model ="anvilgpt/llama3:70b",
    # model ="anvilgpt/codegemma:latest", 
    # model ="Qwen2.5-Coder-32B-Instruct", 
    # model ="anvilgpt/codegemma:latest", 
    url=llm_url,
    engine="OpenAI",
    temperature=0,
    api_key=api_key,
)



def inject_variables_into_template(template_file_path, variable_values):
    """
    Reads a text template from a file, replaces placeholders with 
    specified variable values, and returns the resulting text.

    Args:
        template_file_path (str): The path to the template file.
        variable_values (dict): A dictionary where keys are the 
                               placeholder names (e.g., "{variable_name}")
                               and values are the strings to inject.

    Returns:
        str: The template text with variables injected, or None if the 
             template file could not be read.
    """
    try:
        with open(template_file_path, 'r') as f:
            template_text = f.read()
    except FileNotFoundError:
        print(f"Error: Template file not found at '{template_file_path}'")
        return None
    except IOError:
        print(f"Error: Could not read template file at '{template_file_path}'")
        return None


    # Perform the variable injection.  We iterate through the dictionary 
    # and replace each placeholder in turn.
    for placeholder, value in variable_values.items():
        template_text = template_text.replace(placeholder, value)  # Important: replace all occurrences

    return template_text



def read_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            return content
    except FileNotFoundError:
        print(f"The file at {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


def save_code_to_file(code_content, filename):
    """
    Save code content to a specified file on disk
    
    Args:
        code_content (str): The VB.NET code to save
        filename (str): The path and filename to save the code to
    """
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(code_content)
        print(f"File successfully saved to {filename}")
    except IOError as e:
        print(f"Error saving file: {e}")


#reusing the same function for all button calls to call LLM. type of file decides which kinda file we are asking LLm to create. e.g DDL, or BRD
def runner(human_discussions_file_path,type_of_file):

    prompt_file = ""
    
    if type_of_file == "create_brd":
        prompt_file = prompt_stub_file_name_create_brd
    elif type_of_file == "create_ddl":
        prompt_file = prompt_stub_file_name_create_ddl

    assert prompt_file !=""
    
    # human_edited_discussions = read_uploaded_text(human_discussions_file_path)
    base_name, human_edited_discussions = read_uploaded_text(human_discussions_file_path)
    if not human_edited_discussions:
        st.stop()

    

    # prompt_without_input_class = inject_variables_into_template(prompt_template_file, dict_dynamic_business_object_names)
    with open(prompt_file, 'r') as f:
        prompt_template = f.read()
    # Concatenate prompt with user discussion
    prompt = prompt_template + "\n--------\n" + human_edited_discussions

    message = llm.invoke(prompt)

    save_code_to_file(message.content, output_file_name)
    return message.content ,output_file_name


from docx import Document

def read_docx(file_path):
    doc = Document(file_path)
    full_text = []

    for para in doc.paragraphs:
        full_text.append(para.text)

    return "\n".join(full_text)

def main():    
    content = read_docx(human_discussions_file_name)
    llm_reply,_= runner(content)
    



if __name__=="__main__":
    main()



