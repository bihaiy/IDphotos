import sys
import os

def debug_excepthook(type, value, traceback):
    """自定义异常处理"""
    import traceback as tb
    print('=' * 80)
    print('发生错误！详细信息：')
    print('-' * 80)
    print(f'错误类型: {type.__name__}')
    print(f'错误信息: {str(value)}')
    print('-' * 80)
    print('调用堆栈:')
    print(''.join(tb.format_tb(traceback)))
    print('=' * 80)
    
    # 打印更多环境信息
    print('\n系统信息:')
    print(f'操作系统: {os.name}')
    print(f'Python版本: {sys.version}')
    print(f'可执行文件路径: {sys.executable}')
    print(f'工作目录: {os.getcwd()}')
    
    input('按回车键继续...')

# 设置异常处理器
sys.excepthook = debug_excepthook

# 打印启动信息
print('程序启动...')
print(f'Python路径: {sys.executable}')
print(f'工作目录: {os.getcwd()}')
print('模块搜索路径:')
for p in sys.path:
    print(f'  {p}') 