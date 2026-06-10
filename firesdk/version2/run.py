"""
服务常驻启动入口
CMD执行：python run.py
保持窗口运行即可提供服务
"""
from app import app
from config import HOST, PORT, DEBUG

if __name__ == '__main__':
    print("=" * 65)
    print("📸 学生信息&成绩提取服务 已启动")
    print(f"🌐 服务地址: http://{HOST}:{PORT}")
    print(f"📌 核心接口: POST http://127.0.0.1:{PORT}/api/extract")
    print(f"ℹ️  客户端图片数量: 无限制（服务内部自动按每组8张分片）")
    print(f"✅ 支持类型: type1 / type2")
    print(f"🖼️  单图限制: 最大10MB | 格式: jpg/jpeg/png/bmp/webp")
    print("=" * 65)
    print("服务运行中，关闭CMD窗口即可停止服务\n")

    # 多线程启动，支持并发请求
    app.run(
        host=HOST,
        port=PORT,
        debug=DEBUG,
        threaded=True,
        use_reloader=False
    )