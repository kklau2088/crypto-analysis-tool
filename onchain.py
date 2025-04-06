# models/onchain.py
class OnchainAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
    
    def test(self):
        return "模块导入成功！"

# 测试代码
if __name__ == "__main__":
    print("OnchainAnalyzer 模块测试:")
    analyzer = OnchainAnalyzer("test")
    print(analyzer.test())
