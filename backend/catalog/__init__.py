"""catalog app：商品主檔、採購批次、倉庫與庫存位置（AD-1）。

依賴方向（AD-2）：本 app 只 import ``core``，不 import 其他領域 app；
未來 ``stock``／``sales`` 可 import 本 app 的公開查詢 use case，反向不可。
"""
