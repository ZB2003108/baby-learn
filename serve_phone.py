#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""宝贝学习乐园 —— 手机访问启动器

双击「启动手机访问.bat」即可：
1. 在本机 8080 端口提供页面服务
2. 自动识别局域网地址，生成手机可扫的二维码
3. 打开一个说明页（含二维码和访问地址）

手机与电脑连同一个 Wi-Fi 就能玩。关闭黑窗口即停止服务。
"""
import http.server
import os
import socket
import socketserver
import sys
import threading
import webbrowser

PORT = 8080
ROOT = os.path.dirname(os.path.abspath(__file__))


def lan_ip() -> str:
    """取本机在局域网中的 IPv4 地址（不产生真实流量）。"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def make_qr(url: str) -> bool:
    try:
        import segno  # type: ignore
    except ImportError:
        return False
    try:
        segno.make(url, error="m").save(
            os.path.join(ROOT, "qr-lan.png"), scale=8, border=2, dark="#4B3A5C"
        )
        return True
    except Exception:
        return False


PHONE_PAGE = """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>手机访问 · 宝贝学习乐园</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:"PingFang SC","Microsoft YaHei",system-ui,sans-serif;
background:radial-gradient(circle at 12% 8%,#FFE3EE,transparent 42%),radial-gradient(circle at 88% 14%,#E2F3FF,transparent 40%),radial-gradient(circle at 50% 104%,#FFF3D6,transparent 52%),#FFFBF7;
min-height:100vh;display:flex;align-items:center;justify-content:center;padding:24px;color:#4B3A5C}}
.card{{width:min(560px,100%);background:#fff;border-radius:32px;padding:32px 30px 28px;text-align:center;
box-shadow:0 18px 50px rgba(150,115,175,.16);border:3px solid #fff}}
h1{{font-size:26px;letter-spacing:2px;margin:6px 0 6px}}
.sub{{font-size:13px;color:#9A89AB;font-weight:700;letter-spacing:1px}}
.qr{{margin:22px auto 14px;width:min(280px,72vw);aspect-ratio:1;border-radius:24px;padding:12px;
background:linear-gradient(135deg,#FFF6FB,#F1F8FF);box-shadow:inset 0 0 0 3px #FFF0F7;display:grid;place-items:center}}
.qr img{{width:100%;height:100%;display:block}}
.url{{font-family:ui-monospace,Consolas,monospace;font-size:17px;font-weight:800;color:#E0678F;
background:#FFF3F8;border-radius:14px;padding:12px 14px;margin:6px 0 14px;word-break:break-all}}
ol{{text-align:left;font-size:14px;line-height:2;color:#6E5C80;padding-left:22px;background:#FAF7FD;
border-radius:16px;padding:14px 16px 14px 34px;margin-top:6px}}
ol b{{color:#8B5FB4}}
.warn{{margin-top:12px;font-size:12.5px;color:#B4A4C2;line-height:1.8}}
</style></head><body>
<div class="card">
  <div style="font-size:44px">🌈</div>
  <h1>宝贝学习乐园</h1>
  <div class="sub">手机扫一扫，和电脑一起玩</div>
  {qr_block}
  <div class="url">{url}</div>
  <ol>
    <li>手机连上<b>和电脑同一个 Wi-Fi</b></li>
    <li>用相机 / 微信<b>扫描上面的二维码</b>，或直接在浏览器输入地址</li>
    <li>第一次打开若弹出“是否允许访问网络”，点<b>允许</b></li>
  </ol>
  <div class="warn">关掉那个黑色窗口，手机就访问不了了。<br>电脑上直接双击 index.html 也能玩，不需要这个窗口。</div>
</div></body></html>
"""


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def log_message(self, *args):  # 静音，避免刷屏
        pass


def main():
    ip = lan_ip()
    url = f"http://{ip}:{PORT}/"
    has_qr = make_qr(url)
    qr_block = (
        f'<div class="qr"><img src="qr-lan.png" alt="手机访问二维码"></div>'
        if has_qr
        else '<div class="qr" style="font-size:13px;color:#B4A4C2;display:flex;align-items:center;'
        'justify-content:center;text-align:center;padding:20px">二维码未生成<br>（缺少 segno 库）<br>请直接输入下面的地址</div>'
    )
    with open(os.path.join(ROOT, "phone.html"), "w", encoding="utf-8") as f:
        f.write(PHONE_PAGE.format(qr_block=qr_block, url=url))

    socketserver.TCPServer.allow_reuse_address = True
    try:
        httpd = socketserver.ThreadingTCPServer(("0.0.0.0", PORT), Handler)
    except OSError:
        print(f"\n[×] 端口 {PORT} 被占用了。请关掉其他占用 8080 的程序，或改本文件里的 PORT。")
        input("\n按回车键退出...")
        sys.exit(1)

    line = "=" * 52
    print(line)
    print("  🌈 宝贝学习乐园 已启动")
    print(line)
    print(f"  电脑打开：http://127.0.0.1:{PORT}/")
    print(f"  手机打开：{url}")
    print()
    print("  手机需与电脑连同一个 Wi-Fi，扫二维码或输入上面地址。")
    print("  如果手机打不开：Windows 弹窗要选“允许访问”，")
    print("  或在防火墙里放行“专用网络”的 Python。")
    print()
    print("  ★ 不要关闭这个窗口；按 Ctrl+C 或直接关窗口即停止服务。")
    print(line)

    threading.Timer(1.2, lambda: webbrowser.open(f"http://127.0.0.1:{PORT}/phone.html")).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止服务。")


if __name__ == "__main__":
    main()
