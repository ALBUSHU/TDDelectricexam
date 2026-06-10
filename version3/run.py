from app import app
from config import HOST, PORT, DEBUG

if __name__ == '__main__':
    print("=" * 65)
    print("📸 学生信息&成绩提取服务 已启动（无状态版）")
    print(f"🌐 服务地址: http://{HOST}:{PORT}")
    print(f"📌 核心接口: POST http://127.0.0.1:{PORT}/api/extract")
    print(f"📝 请求格式: JSON (application/json)")
    print(f"🔑 必填参数: api_key, images_base64 (图片Base64列表)")
    print(f"🖼️  单图限制: 最大10MB | 格式: jpg/jpeg/png/bmp/webp")
    print(f"🔁 自动分批: 每组最多8张，第一组提取基础信息+得分，后续组仅提取得分")
    print("=" * 65)
    print("服务运行中，关闭窗口即可停止\n")
    app.run(host=HOST, port=PORT, debug=DEBUG, threaded=True, use_reloader=False)