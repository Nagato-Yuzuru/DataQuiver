# TODO: The Verbs (Read)
# 有顶层信封（树结构）QueryIntent
# FilterNode（过滤条件）
# WindowNode: 窗口定义 (TUMBLE, HOP)，用于流计算或时序分析。
# SortNode / LimitNode: 后处理逻辑。
# 需要支持 Aggregation  和 Transformation，支持函数调用

# INFO: 对于海量数据（比如geo-气象计算时间窗口区域平均）计算下推是刚需。IR需要可以描述计算/函数调用
# 提供 bare 表达式，但是大部分计算模式应该由 catalog 抽象，插件提供计算抽象和实现定义


# TODO: design how to select data shape and compute(call func)

"""
表达式节点 ExprNode：

引用Ref，字面量（Literal，需要描述类型），函数调用（需要考虑抽象描述，多源后端签名不一定一致）

聚合节点 Aggregation
分组节点 GroupBy，需要支持滚动窗口等

这里需要支持Monads吗？

先协商再下推（也就是需要表达式重写，这个感觉会非常麻烦）
"""

"""
PLANNER:

先做语义替换（Analyzer），查catalog把语义翻译到执行表达式，按执行插件分桶
能力标注，自底向上查询插件能力范围，cut为两部分
先用贪心算法一刀切，暂时不做基于代价的优化器，优先下推filter算子
生成物理ir
"""
