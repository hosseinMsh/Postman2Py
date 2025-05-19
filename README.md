# 📨 postman2py

Convert your Postman collections into structured, functional Python code using the `requests` library.

## 🚀 Features

- 📂 Converts Postman folders into Python packages.
- 🧾 Each request becomes a Python function.
- 🧱 Auto-generates module structure based on Postman folder hierarchy.
- ⚙️ Supports request methods, headers, query params, and JSON bodies.
- 🔧 Uses `requests` library for HTTP handling.

## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/your-username/postman2py.git
cd postman2py
````

(Optional) Install dependencies:

```bash
pip install -r requirements.txt
```

## 🛠️ Usage

```bash
python postman2py.py path/to/collection.json -o output_directory
```

### Arguments

| Argument         | Description                                                          |
| ---------------- | -------------------------------------------------------------------- |
| `-o`, `--output` | Output directory for generated code                                  |
| `-e`, `--env`    | Optional: Postman environment JSON to resolve variables              |
| `--flat`         | Optional: Disable folder-based structure (all functions in one file) |

## 🧪 Example

**Input:**
A Postman collection with a folder `User` and two requests: `Login`, `Profile`

**Output:**

```plaintext
output/
└── user/
    ├── __init__.py
    ├── login.py      # def login(...): ...
    └── profile.py    # def profile(...): ...
```

Each Python file includes a function like this:

```python
import requests

def login(base_url, username, password):
    url = f"{base_url}/auth/login"
    payload = {"username": username, "password": password}
    response = requests.post(url, json=payload)
    return response
```

## 📄 Supported Postman Features

* Request methods: `GET`, `POST`, `PUT`, `DELETE`, etc.
* URL parameters and query strings
* Headers
* JSON bodies
* Postman environments (optional)

## 📌 Limitations

* Only Postman Collection v2.1 supported
* Scripts and test snippets are ignored
* Binary/form-data currently unsupported

## 🤝 Contributing

Contributions are welcome! Please open an issue or pull request.

## 📃 License

MIT [License](LICENSE) © 2025 \[Hossein Masihi]
