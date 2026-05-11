import customtkinter as ctk
import json
import shlex
from urllib.parse import urlparse, parse_qs

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


# ==============================================
# 支持：-d / --data-raw / --data-binary → POST
# ==============================================
def parse_curl(curl_cmd):
    curl = curl_cmd.replace("`", "").strip()
    tokens = shlex.split(curl)

    method = "GET"
    url = ""
    headers = {}
    body = None
    has_body = False
    idx = 1

    while idx < len(tokens):
        opt = tokens[idx]

        if opt in ("-X", "--request"):
            method = tokens[idx + 1].upper()
            idx += 2

        elif opt in ("-H", "--header"):
            line = tokens[idx + 1]
            if ":" in line:
                k, v = line.split(":", 1)
                headers[k.strip()] = v.strip()
            idx += 2

        elif opt in ("-d", "--data", "--data-raw", "--data-binary"):
            has_body = True
            body_str = tokens[idx + 1]
            try:
                body = json.loads(body_str)
            except:
                body = body_str
            idx += 2

        elif opt.startswith("http"):
            url = opt
            idx += 1
        else:
            idx += 1

    if has_body:
        method = "POST"

    parsed = urlparse(url)
    query = {}
    if parsed.query:
        qs = parse_qs(parsed.query)
        for k, v in qs.items():
            query[k] = v[0]

    pure_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    return method, pure_url, headers, body, query


# ==============================================
# 生成代码（POST 不拼 params，GET 才拼）
# ==============================================
def generate_code(method, url, headers, body, query, use_assert, ok_codes):
    code = [
        "import requests",
        "import json",
        "",
        f'url = "{url}"',
        f"headers = {headers}",
        ""
    ]

    # ✅ 只有 GET 才加 params
    if method == "GET" and query:
        code.append(f"params = {query}")

    if body is not None:
        code.append(f"payload = {body}")

    ct = str(headers.get("Content-Type", "")).lower()

    if method == "GET":
        code.append("res = requests.get(url, headers=headers)" + (", params=params" if query else ""))
    else:
        if "json" in ct:
            code.append(f"res = requests.{method.lower()}(url, headers=headers, json=payload)")
        else:
            code.append(f"res = requests.{method.lower()}(url, headers=headers, data=payload)")

    code.append("\nprint('状态码：', res.status_code)")

    if use_assert:
        code.append(f"ok_list = [{ok_codes}]")
        code.append("assert res.status_code in ok_list, '状态码异常'")

    code.extend([
        "\ntry:",
        "    print(json.dumps(res.json(), ensure_ascii=False, indent=2))",
        "except:",
        "    print(res.text)"
    ])
    return "\n".join(code)


# ==============================================
# GUI
# ==============================================
class CurlTool(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Curl转Requests ✅ 最终规范版")
        self.geometry("1050x880")

        # CURL输入
        ctk.CTkLabel(self, text="请输入你的-Curl：").pack(anchor="w", padx=15, pady=(10, 2))
        self.txt_curl = ctk.CTkTextbox(self, height=6)
        self.txt_curl.pack(fill="x", padx=15)

        # 工具栏
        bar = ctk.CTkFrame(self)
        bar.pack(fill="x", padx=15, pady=8)
        ctk.CTkButton(bar, text="🔍 一键解析", command=self.parse).grid(row=0, column=0, padx=4)
        ctk.CTkButton(bar, text="📝 生成代码", command=self.build).grid(row=0, column=1, padx=4)
        ctk.CTkButton(bar, text="🧹 清空", command=self.clear).grid(row=0, column=2, padx=4)

        self.assert_switch = ctk.BooleanVar()
        ctk.CTkCheckBox(bar, text="开启断言", variable=self.assert_switch).grid(row=0, column=3, padx=10)
        ctk.CTkLabel(bar, text="状态码：").grid(row=0, column=4)
        self.entry_code = ctk.CTkEntry(bar, width=130)
        self.entry_code.insert(0, "200,201,204")
        self.entry_code.grid(row=0, column=5)

        # 请求方式+URL
        base = ctk.CTkFrame(self)
        base.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(base, text="请求方式：").grid(row=0, column=0)
        self.method_var = ctk.StringVar(value="GET")
        self.cb_method = ctk.CTkComboBox(base, values=["GET", "POST", "PUT", "DELETE", "PATCH"],
                                         variable=self.method_var, width=110)
        self.cb_method.grid(row=0, column=1, padx=5)
        ctk.CTkLabel(base, text="URL：").grid(row=0, column=2)
        self.entry_url = ctk.CTkEntry(base)
        self.entry_url.grid(row=0, column=3, sticky="ew", padx=5)
        base.columnconfigure(3, weight=1)

        # Query
        ctk.CTkLabel(self, text="🔎 GET参数：").pack(anchor="w", padx=15)
        self.txt_query = ctk.CTkTextbox(self, height=4)
        self.txt_query.pack(fill="both", padx=15, expand=True)

        # Headers
        ctk.CTkLabel(self, text="📌 Headers：").pack(anchor="w", padx=15)
        self.txt_header = ctk.CTkTextbox(self, height=6)
        self.txt_header.pack(fill="both", padx=15, expand=True)

        # Body
        ctk.CTkLabel(self, text="📦 Body：").pack(anchor="w", padx=15)
        self.txt_body = ctk.CTkTextbox(self, height=4)
        self.txt_body.pack(fill="both", padx=15, expand=True)

        # 代码
        ctk.CTkLabel(self, text="💻 生成代码：").pack(anchor="w", padx=15)
        self.txt_code = ctk.CTkTextbox(self, height=12)
        self.txt_code.pack(fill="both", padx=15, expand=True)

    def parse(self):
        try:
            curl = self.txt_curl.get("1.0", "end").strip()
            method, url, headers, body, query = parse_curl(curl)
            self.method_var.set(method)
            self.entry_url.delete(0, "end")
            self.entry_url.insert(0, url)

            # ==============================================
            # ✅ 最终修复：POST/PUT/DELETE/PATCH → Query 清空
            # ==============================================
            self.txt_query.delete("1.0", "end")
            if method == "GET":
                self.txt_query.insert("end", json.dumps(query, indent=4, ensure_ascii=False))

            self.txt_header.delete("1.0", "end")
            self.txt_header.insert("end", json.dumps(headers, indent=4, ensure_ascii=False))
            self.txt_body.delete("1.0", "end")
            if body is not None:
                if isinstance(body, (dict, list)):
                    self.txt_body.insert("end", json.dumps(body, indent=4, ensure_ascii=False))
                else:
                    self.txt_body.insert("end", str(body))
        except Exception as e:
            print("解析错误：", e)

    def build(self):
        try:
            m = self.method_var.get()
            u = self.entry_url.get()
            h = eval(self.txt_header.get("1.0", "end").strip() or "{}")
            q = eval(self.txt_query.get("1.0", "end").strip() or "{}")
            b = self.txt_body.get("1.0", "end").strip()
            try:
                b = eval(b)
            except:
                pass
            a = self.assert_switch.get()
            s = self.entry_code.get()
            code = generate_code(m, u, h, b, q, a, s)
            self.txt_code.delete("1.0", "end")
            self.txt_code.insert("end", code)
        except Exception as e:
            print("生成错误：", e)

    def clear(self):
        self.txt_curl.delete("1.0", "end")
        self.method_var.set("GET")
        self.entry_url.delete(0, "end")
        self.txt_query.delete("1.0", "end")
        self.txt_header.delete("1.0", "end")
        self.txt_body.delete("1.0", "end")
        self.txt_code.delete("1.0", "end")


if __name__ == "__main__":
    app = CurlTool()
    app.mainloop()