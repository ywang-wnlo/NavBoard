from flask import Blueprint, render_template, request
from urllib.parse import unquote

bp = Blueprint("webtools", __name__, template_folder="webtools")

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

@bp.route("/quick-iina", methods=("GET", "POST"))
def quick_iina():
    """无需登录即可访问的 quick-iina 页面，根据实际 method 处理请求"""
    real_url = None
    if request.method == "POST":
        input_url = request.form.get("input_url")
        if input_url.startswith("http://") or input_url.startswith("https://"):
            real_url = decode_real_url(input_url)
        else:
            real_url = "不是有效的 URL"
    return render_template("webtools/quick-iina.html", real_url=real_url)
