from flask import Blueprint, render_template, request
from urllib.parse import unquote

bp = Blueprint("quick_iina", __name__, template_folder="webtools")

def decode_real_url(url):
    """解码 URL，去除可能的编码字符"""
    prev = url
    curr = unquote(prev)
    while curr != prev:
        prev = curr
        curr = unquote(prev)
    # 如果有多个 http(s) 前缀，保留最后一个
    http_prefixes = ["http://", "https://"]
    for prefix in http_prefixes:
        if prefix in curr:
            curr = prefix + curr.split(prefix)[-1]
    return curr

def gen_iina_cmdline(url, ext_headers):
    """根据 URL 和扩展头生成 iina-cli 命令行"""
    iina_cmdline = 'iina-cli'
    lines = ext_headers.strip().split("\n")
    for line in lines:
        k, v = line.split(":", 1)
        line = f'{k.strip()}: {v.strip()}'
        iina_cmdline += f' --mpv-http-header-fields="{line}"'
    iina_cmdline += f' "{url}"'
    return iina_cmdline

@bp.route("/quick-iina", methods=("GET", "POST"))
def index():
    """无需登录即可访问的 quick-iina 页面，根据实际 method 处理请求"""
    real_url = None
    iina_cmdline = None

    if request.method == "POST":
        input_url = request.form.get("input_url")
        if input_url.startswith("http://") or input_url.startswith("https://"):
            real_url = decode_real_url(input_url)
            ext_headers = request.form.get("ext_headers", None)
            if ext_headers:
                iina_cmdline = gen_iina_cmdline(real_url, ext_headers)
                real_url = None
        else:
            real_url = "不是有效的 URL"

    return render_template("webtools/quick-iina.html", real_url=real_url, iina_cmdline=iina_cmdline)
