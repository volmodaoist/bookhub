# 每本书维护基本信息、库存量(每个用户借阅的时候会生成一个单号，并且更新库存量)
class Book:
    def __init__(self, title, author, isbn, stock):
        self.title = title      # 图书名称
        self.author = author    # 作者
        self.isbn = isbn        # 国际标准书号
        self.stock = stock      # 库存量

    # 更新库存量
    def update_stock(self, quantity):
        self.stock += quantity

    # 打印一本书的基本信息
    def __str__(self):
        return f"{self.title} by {self.author} (ISBN: {self.isbn}) - Stock: {self.stock}"