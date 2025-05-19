import argparse
import os
import json
import re
import shutil

def slugify(name):
    name = name.strip().lower()
    name = re.sub(r'[\\/*?:"<>|]', '', name)  # remove forbidden filename characters
    name = re.sub(r'\s+', '_', name)           # convert spaces to underscores
    name = re.sub(r'[^\w_]', '', name)         # remove remaining non-word chars
    return name

def extract_placeholders(s):
    return re.findall(r"{{\s*([^}]+)\s*}}", s)

def make_package(path):
    os.makedirs(path, exist_ok=True)
    init_path = os.path.join(path, "__init__.py")
    if not os.path.exists(init_path):
        with open(init_path, "w", encoding="utf-8") as f:
            f.write("")

def create_request_function(request_item, folder_path):
    request_info = request_item["request"]
    name = slugify(request_item["name"])
    method = request_info["method"].lower()
    url = request_info["url"]

    raw_url = url["raw"]
    url_vars = extract_placeholders(raw_url)
    formatted_url = re.sub(r"{{\s*([^}]+)\s*}}", r"{\1}", raw_url)

    headers = {h["key"]: h["value"] for h in request_info.get("header", [])}
    header_vars = []
    for k, v in headers.items():
        header_vars += extract_placeholders(v)
        headers[k] = re.sub(r"{{\s*([^}]+)\s*}}", r"{\1}", v)

    body = request_info.get("body", {})
    func_inputs = set(url_vars + header_vars)
    body_payload = ""
    json_mode = False

    if body.get("mode") == "urlencoded":
        data_dict = {}
        for item in body.get("urlencoded", []):
            if not item.get("disabled", False):
                key = item["key"]
                value = item["value"]
                data_dict[key] = key
                func_inputs.add(value)
        data_body = ",\n        ".join([f'"{k}": {k}' for k in data_dict])
        body_payload = f"data = {{\n        {data_body}\n    }}"
        body_arg = "data=data"

    elif body.get("mode") == "raw" and body.get("options", {}).get("raw", {}).get("language") == "json":
        json_mode = True
        raw = body.get("raw", "")
        body_vars = extract_placeholders(raw)
        func_inputs.update(body_vars)
        try:
            raw_json = re.sub(r"{{\s*([^}]+)\s*}}", r'""', raw)
            json_obj = json.loads(raw_json)
            body_payload = "data = " + json.dumps(json_obj, indent=4)
            for var in body_vars:
                body_payload = body_payload.replace(f'"{var}"', var)
        except Exception:
            escaped_raw = raw.replace('"""', r'\"\"\"')
            body_payload = f'data = """{escaped_raw}"""'
        body_arg = "json=data"
    else:
        body_payload = "data = {}"
        body_arg = "data=data"

    headers_code = ",\n        ".join([f'"{k}": f"{v}"' for k, v in headers.items()])
    function_code = f"""import requests

def read_file_content(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def {name}({', '.join(sorted(func_inputs))}):
    url = f"{formatted_url}"
    headers = {{
        {headers_code}
    }}
    {body_payload}
    response = requests.{method}(url, headers=headers, {body_arg})
    return response
"""
    file_path = os.path.join(folder_path, f"{name}.py")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(function_code)

def process_items(items, path):
    for item in items:
        if "request" in item:
            create_request_function(item, path)
        elif "item" in item:
            subfolder = slugify(item["name"])
            new_path = os.path.join(path, subfolder)
            make_package(new_path)
            process_items(item["item"], new_path)

def main():
    parser = argparse.ArgumentParser(description="Convert Postman collection to functional Python code.")
    parser.add_argument("collection", help="Path to Postman collection JSON file")
    parser.add_argument("--output", default="generated_code", help="Output directory (default: generated_code)")
    args = parser.parse_args()

    with open(args.collection, "r", encoding="utf-8") as f:
        postman_data = json.load(f)

    collection_name = postman_data["info"]["name"].replace(" ", "_")
    base_path = os.path.join(args.output, collection_name)

    if os.path.exists(base_path):
        shutil.rmtree(base_path)

    os.makedirs(base_path, exist_ok=True)
    make_package(base_path)
    process_items(postman_data["item"], base_path)

    print(f"✅ Code generated at: {base_path}")

if __name__ == "__main__":
    main()
