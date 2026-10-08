#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
多后端生图脚本（brand-social-media-workflow 通用版）
纯标准库实现，无需 pip install。

用法:
  文生图:     python gen_image.py "提示词" output.png [尺寸]
  参考图编辑: python gen_image.py --ref product.jpg [--ref model.jpg] "提示词" output.png [尺寸]
  换后端:     python gen_image.py --backend openai "提示词" out.png 1024x1024
  只出 prompt: python gen_image.py --backend none "提示词" out.png 1024x1536

后端:
  none     不调用任何 API，只打印最终 prompt（无 key 也能用，配合 --save-prompt 落盘）
  1xm      1XM.AI gpt-image-2（异步任务接口，支持 4K）
  openai   OpenAI 官方（gpt-image-1 / dall-e，同步接口）
  custom   任意 OpenAI 兼容端点（先试异步任务，失败回落同步）

配置（优先级：命令行 > 环境变量 > 后端预设）:
  IMAGE_API_KEY    API Key
  IMAGE_BASE_URL   Base URL（留空用后端预设）
  IMAGE_MODEL      模型名（留空用后端预设）
  HTTPS_PROXY      代理；设 GEN_PROXY="" 可强制禁用
  GEN_NO_PROXY=1   同 GEN_PROXY=""，禁用代理

退出码: 0 成功 / 1 用法错误 / 2 配置缺失 / 3 调用失败
"""
import sys, os, io, re, json, time, base64, mimetypes, urllib.request, urllib.error

# ---------------- 后端预设 ----------------
PRESETS = {
    "1xm":    {"base": "https://api.1xm.ai/v1",     "model": "gpt-image-2", "mode": "async"},
    "openai": {"base": "https://api.openai.com/v1", "model": "gpt-image-1", "mode": "sync"},
    "wanxiang": {"base": "", "model": "wanx2.1-t2i-turbo", "mode": "sync"},
    "jimeng": {"base": "", "model": "", "mode": "sync"},
}

# ---------------- 尺寸校验 ----------------
MAX_SIDE = 3840
MIN_PX, MAX_PX = 655_360, 8_294_400


def check_size(size):
    m = re.match(r"^\s*(\d+)\s*[xX]\s*(\d+)\s*$", size or "")
    if not m:
        return False, "尺寸格式应为 宽x高，例 1024x1536"
    w, h = int(m.group(1)), int(m.group(2))
    if w % 16 or h % 16:
        return False, "宽高必须是 16 的倍数（1080 不是！竖版用 1024x1536 或 1088x1920，3:4 用 1088x1440）"
    if max(w, h) > MAX_SIDE:
        return False, f"边长不得超过 {MAX_SIDE}px"
    if max(w, h) / min(w, h) > 3:
        return False, "长宽比不得超过 3:1"
    if not (MIN_PX <= w * h <= MAX_PX):
        return False, f"总像素须在 {MIN_PX}–{MAX_PX} 之间（当前 {w*h}）"
    return True, ""


# ---------------- 代理 ----------------
def _detect_proxy():
    if os.environ.get("GEN_PROXY") == "" or os.environ.get("GEN_NO_PROXY"):
        return None
    env = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    if env:
        return env
    try:  # Windows 注册表系统代理
        import winreg
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                           r"Software\Microsoft\Windows\CurrentVersion\Internet Settings")
        if winreg.QueryValueEx(k, "ProxyEnable")[0]:
            return "http://" + winreg.QueryValueEx(k, "ProxyServer")[0]
    except Exception:
        pass
    return None


PROXY = _detect_proxy()
DIRECT_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))
UA_HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"),
}


def _opener(use_proxy):
    if use_proxy and PROXY:
        return urllib.request.build_opener(
            urllib.request.ProxyHandler({"http": PROXY, "https": PROXY}))
    return DIRECT_OPENER


def _request(url, data=None, headers=None, timeout=60, use_proxy=True):
    req = urllib.request.Request(url, data=data, headers=headers or {})
    return _opener(use_proxy).open(req, timeout=timeout)


# ---------------- 工具 ----------------
def _data_url(path):
    mime = mimetypes.guess_type(path)[0] or "image/png"
    with open(path, "rb") as f:
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode()


def _multipart(fields, files):
    """fields: {name: str}; files: [(name, filename, mime, bytes)]"""
    boundary = "----genimage" + str(int(time.time() * 1000))
    buf = io.BytesIO()
    for k, v in fields.items():
        buf.write(f"--{boundary}\r\n".encode())
        buf.write(f'Content-Disposition: form-data; name="{k}"\r\n\r\n'.encode())
        buf.write(str(v).encode("utf-8") + b"\r\n")
    for name, fn, mime, blob in files:
        buf.write(f"--{boundary}\r\n".encode())
        buf.write(f'Content-Disposition: form-data; name="{name}"; filename="{fn}"\r\n'.encode())
        buf.write(f"Content-Type: {mime}\r\n\r\n".encode())
        buf.write(blob + b"\r\n")
    buf.write(f"--{boundary}--\r\n".encode())
    return buf.getvalue(), f"multipart/form-data; boundary={boundary}"


def _save(out_path, blob):
    os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(blob)
    print(f"已保存: {out_path}  ({len(blob)/1024:.0f} KB)")


def _fetch(url, out_path):
    """下载结果：先带 UA 直连，403 再退回代理。"""
    last = None
    for use_proxy in (False, True):
        try:
            with _request(url, headers=UA_HEADERS, timeout=180, use_proxy=use_proxy) as r:
                _save(out_path, r.read())
            return
        except Exception as e:
            last = e
    raise RuntimeError(f"下载失败: {last}")


def _collect_urls(result):
    urls, blobs = [], []
    for d in result.get("data") or []:
        if d.get("url"):
            urls.append(d["url"])
        elif d.get("b64_json"):
            blobs.append(base64.b64decode(d["b64_json"]))
    return urls, blobs


# ---------------- 调用 ----------------
def call_async(base, key, model, payload):
    """POST /images/tasks → 轮询 GET /images/tasks/{id}"""
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    with _request(base + "/images/tasks", data=json.dumps(payload).encode("utf-8"),
                  headers=headers, timeout=60) as r:
        task = json.loads(r.read())
    tid = task.get("id") or task.get("task_id")
    if not tid:
        raise RuntimeError(f"任务创建返回异常: {json.dumps(task)[:400]}")
    print(f"任务已创建: {tid}（{'编辑模式' if payload.get('image') else '文生图'}，{payload.get('size')}）")
    wait = task.get("poll_after", 5)
    for _ in range(120):
        time.sleep(wait)
        with _request(f"{base}/images/tasks/{tid}",
                      headers={"Authorization": f"Bearer {key}"}, timeout=60) as r:
            cur = json.loads(r.read())
        st = cur.get("status")
        print(f"  状态: {st}")
        if st in ("succeeded", "success", "completed"):
            return _collect_urls(cur)
        if st in ("failed", "error"):
            raise RuntimeError(json.dumps(cur.get("error", cur))[:400])
        wait = cur.get("poll_after", wait)
    raise TimeoutError("任务超时未完成（已轮询 120 次）")


def call_sync(base, key, model, prompt, size, refs, n, quality):
    """无参考图 → /images/generations（JSON）；有参考图 → /images/edits（multipart）"""
    if refs:
        fields = {"model": model, "prompt": prompt, "size": size, "n": n}
        if quality:
            fields["quality"] = quality
        files = []
        for p in refs:
            mime = mimetypes.guess_type(p)[0] or "image/png"
            with open(p, "rb") as f:
                files.append(("image[]", os.path.basename(p), mime, f.read()))
        body, ctype = _multipart(fields, files)
        headers = {"Authorization": f"Bearer {key}", "Content-Type": ctype}
        url = base + "/images/edits"
    else:
        payload = {"model": model, "prompt": prompt, "size": size, "n": n}
        if quality:
            payload["quality"] = quality
        body, ctype = json.dumps(payload).encode("utf-8"), "application/json"
        headers = {"Authorization": f"Bearer {key}", "Content-Type": ctype}
        url = base + "/images/generations"
    with _request(url, data=body, headers=headers, timeout=180) as r:
        return _collect_urls(json.loads(r.read()))


def generate(prompt, out_path, size="1024x1024", refs=None, n=1, quality="high",
             backend="none", base_url="", model="", api_key=None, save_prompt=None):
    ok, why = check_size(size)
    if not ok:
        sys.exit(f"尺寸不合法: {why}")

    if backend == "none":
        print("=" * 60)
        print("【backend=none】未调用任何 API。以下是最终 prompt，可直接贴到任意生图工具：\n")
        print(prompt)
        print("=" * 60)
        if save_prompt:
            with open(save_prompt, "w", encoding="utf-8") as f:
                f.write(prompt)
            print(f"prompt 已写入: {save_prompt}")
        if refs:
            print("参考图（需手动上传）: " + ", ".join(refs))
        return []

    preset = PRESETS.get(backend, {})
    base = (base_url or preset.get("base") or "").rstrip("/")
    model = model or preset.get("model") or ""
    key = api_key or os.environ.get("IMAGE_API_KEY", "")
    if not base:
        sys.exit(f"后端 {backend} 需要 base_url（用 --base-url 或环境变量 IMAGE_BASE_URL 指定）")
    if not model:
        sys.exit(f"后端 {backend} 需要模型名（用 --model 或环境变量 IMAGE_MODEL 指定）")
    if not key:
        sys.exit("缺少 API Key：设置环境变量 IMAGE_API_KEY，或用 --api-key 传入")

    payload = {"model": model, "prompt": prompt, "size": size,
               "quality": quality, "output_format": "png", "n": n}
    if refs:
        payload["image"] = [_data_url(p) for p in refs]

    mode = preset.get("mode", "sync")
    if mode == "async":
        urls, blobs = call_async(base, key, model, payload)
    else:
        urls, blobs = call_sync(base, key, model, prompt, size, refs, n, quality)

    for i, b in enumerate(blobs):
        p = out_path if len(blobs) == 1 else out_path.replace(".png", f"_{i+1}.png")
        _save(p, b)
    for i, u in enumerate(urls):
        p = out_path if len(urls) == 1 else out_path.replace(".png", f"_{i+1}.png")
        _fetch(u, p)
    if not urls and not blobs:
        raise RuntimeError("接口未返回任何图片数据")
    return urls


def main():
    argv = sys.argv[1:]
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0

    refs, opts = [], {}
    while argv and argv[0].startswith("--"):
        k = argv.pop(0)
        if k == "--ref":
            if not argv:
                sys.exit("--ref 缺少路径")
            refs.append(argv.pop(0))
        elif k == "--backend":
            opts["backend"] = argv.pop(0)
        elif k == "--base-url":
            opts["base_url"] = argv.pop(0)
        elif k == "--model":
            opts["model"] = argv.pop(0)
        elif k == "--api-key":
            opts["api_key"] = argv.pop(0)
        elif k == "--n":
            opts["n"] = int(argv.pop(0))
        elif k == "--quality":
            opts["quality"] = argv.pop(0)
        elif k == "--save-prompt":
            opts["save_prompt"] = argv.pop(0)
        else:
            sys.exit(f"未知参数: {k}")

    if len(argv) < 1:
        sys.exit("缺少 prompt。用法见 --help")

    prompt = argv[0]
    out = argv[1] if len(argv) > 1 else "output.png"
    size = argv[2] if len(argv) > 2 else os.environ.get("IMAGE_DEFAULT_SIZE", "1024x1536")

    backend = opts.get("backend") or os.environ.get("IMAGE_BACKEND", "none")
    try:
        generate(prompt, out, size, refs=refs or None,
                 n=opts.get("n", 1), quality=opts.get("quality", "high"),
                 backend=backend,
                 base_url=opts.get("base_url") or os.environ.get("IMAGE_BASE_URL", ""),
                 model=opts.get("model") or os.environ.get("IMAGE_MODEL", ""),
                 api_key=opts.get("api_key"),
                 save_prompt=opts.get("save_prompt"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "ignore")[:400]
        print(f"HTTP {e.code}: {detail}", file=sys.stderr)
        print("提示：任务创建超时通常是代理问题，试试显式 HTTPS_PROXY=http://127.0.0.1:<port>",
              file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
