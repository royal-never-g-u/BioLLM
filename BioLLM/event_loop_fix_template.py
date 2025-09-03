
# 事件循环修复模板
import asyncio
import sys

def main():
    # 设置事件循环
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # 你的主程序代码
        run_your_program()
        
    except Exception as e:
        print(f"程序执行错误: {e}")
    finally:
        # 确保事件循环正确关闭
        try:
            loop = asyncio.get_event_loop()
            if not loop.is_closed():
                loop.close()
        except Exception as e:
            print(f"关闭事件循环时出错: {e}")

if __name__ == "__main__":
    main()
