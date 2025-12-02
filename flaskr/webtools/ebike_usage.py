from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

from ..auth import login_required
from ..db import get_db


bp = Blueprint("ebike_usage", __name__, template_folder="webtools")


@bp.route("/ebike-usage")
@login_required
def index():
    """获取使用记录，按 id 排序"""
    db = get_db()
    ebike_entrys = db.execute(
        "SELECT id, ext, date, usage FROM ebike_entry WHERE author_id = ? ORDER BY id ASC", (g.user["id"],)
    ).fetchall()
    return render_template("webtools/ebike-usage/index.html", ebike_entrys=ebike_entrys)


@bp.route("/ebike-usage/create", methods=("GET", "POST"))
@login_required
def create():
    """创建新的使用记录"""
    if request.method == "POST":
        ext = request.form["ext"]
        date = request.form["date"]
        usage = request.form["usage"]
        error = None

        if not usage:
            error = "必须输入骑行公里数"

        if usage == 0:
            ext = None

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO ebike_entry (ext, date, usage, author_id) VALUES (?, ?, ?, ?)",
                (ext, date, usage, g.user["id"]),
            )
            db.commit()
            return redirect(url_for("ebike_usage.index"))

    return render_template("webtools/ebike-usage/create.html")


def get_ebike_entry(id):
    """根据 id 获取使用记录
    :param id: 要获取的 ebike_entry 的 id
    :return: ebike_entry
    :raise 404: 记录不存在
    """
    ebike_entry = (
        get_db()
        .execute(
            "SELECT id, ext, date, usage, author_id"
            " FROM ebike_entry WHERE id = ? AND author_id = ?",
            (id, g.user["id"]),
        )
        .fetchone()
    )

    if ebike_entry is None:
        abort(404, f"条目 id {id} 不存在。")

    return ebike_entry



@bp.route("/ebike-usage/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """修改使用记录"""
    ebike_entry = get_ebike_entry(id)

    if request.method == "POST":
        ext = request.form["ext"]
        date = request.form["date"]
        usage = request.form["usage"]
        error = None

        if not usage:
            error = "必须输入骑行公里数"

        if usage == 0:
            ext = None

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE ebike_entry SET ext = ?, date = ?, usage = ? WHERE id = ? AND author_id = ?",
                (ext, date, usage, id, g.user["id"])
            )
            db.commit()
            return redirect(url_for("ebike_usage.index"))

    return render_template("webtools/ebike-usage/update.html", ebike_entry=ebike_entry)


@bp.route("/ebike-usage/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    """删除条目"""
    get_ebike_entry(id)
    db = get_db()
    db.execute("DELETE FROM ebike_entry WHERE id = ? AND author_id = ?", (id, g.user["id"]))
    db.commit()
    return redirect(url_for("ebike_usage.index"))
