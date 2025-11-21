# 每日信息分析程序

这是一个用于分析每日收集信息的Python程序，专门针对从`links.txt`中收集的文章链接进行数据统计、关键词分析、时间序列分析等功能。

## 🎯 功能特点

### 基础功能
- **数据统计**: 统计总链接数、已下载文章数、下载率等基础指标
- **关键词分析**: 使用jieba分词进行中文关键词提取和频率统计
- **时间序列分析**: 分析文章发布的时间分布，识别发布规律
- **可视化报告**: 生成HTML格式的分析报告和图表

### 增强功能
- **交互式仪表板**: 使用Streamlit创建Web界面
- **详细趋势分析**: 计算活跃度指数、更新频率等指标
- **文件分析**: 分析已下载文章的文件信息
- **关键词分类**: 将关键词按政策、行业、组织等类别分类
- **综合报告**: 生成包含所有分析结果的详细报告

## 📦 安装

### 1. 安装依赖包

```bash
pip install -r requirements.txt
```

### 2. 检查依赖项

```bash
python run_analysis.py --check-deps
```

## 🚀 使用方法

### 基础分析

运行基础分析，生成简单的统计报告：

```bash
python run_analysis.py --basic
```

### 增强分析

运行增强分析，生成详细的分析报告：

```bash
python run_analysis.py --enhanced
```

### 交互式仪表板

启动Web界面的交互式仪表板：

```bash
python run_analysis.py --dashboard
```

或者直接使用Streamlit运行：

```bash
streamlit run enhanced_analyzer.py
```

### 查看帮助

```bash
python run_analysis.py --help
```

## 📁 文件结构

```
.
├── daily_info_analyzer.py      # 基础分析程序
├── enhanced_analyzer.py        # 增强版分析程序
├── run_analysis.py             # 运行器程序
├── requirements.txt            # 依赖包列表
├── README.md                   # 说明文档
├── links.txt                   # 链接数据文件
├── 文章/                        # 文章存储目录
└── reports/                    # 报告输出目录
```

## 📊 分析功能详解

### 1. 基础统计
- 总链接数量统计
- 已下载文章数量
- 下载成功率计算
- 数据覆盖时间范围
- 平均每日链接数

### 2. 时间分析
- 日度发布分布
- 月度发布分布
- 年度发布分布
- 星期发布模式
- 峰值识别

### 3. 关键词分析
- 中文分词处理
- 停用词过滤
- 词频统计
- 关键词分类（政策、行业、组织、时间）
- 词云生成

### 4. 文件分析
- 总文件大小统计
- 平均文件大小
- 文件数量统计
- 文件创建时间分布

### 5. 趋势分析
- 整体趋势判断（上升/下降/平稳）
- 活跃度指数计算
- 更新频率评估
- 近期活动分析

## 📈 输出结果

### HTML报告
- `analysis_report.html`: 基础分析报告
- `reports/report_YYYYMMDD_HHMMSS/report.html`: 增强版详细报告

### 图表文件
- `monthly_distribution.png`: 月度分布图
- `keyword_wordcloud.png`: 关键词词云图

### 交互式仪表板
- Web界面，支持实时数据探索
- 多种图表展示
- 参数调节功能

## ⚙️ 配置选项

### 分析参数
- 时间范围调节（7-365天）
- 关键词数量设置
- 图表样式选择

### 输出选项
- 报告格式选择
- 图表分辨率设置
- 输出目录配置

## 🔧 扩展功能

### 自定义停用词
可以在`enhanced_analyzer.py`中修改`get_stop_words()`方法来自定义停用词。

### 关键词分类
可以在`categorize_keywords()`方法中添加更多的分类规则。

### 图表样式
可以修改`generate_detailed_charts()`方法来自定义图表样式。

## 🐛 常见问题

### Q: 中文显示问题
A: 确保系统中安装了中文字体，或者在代码中指定正确的字体路径。

### Q: 内存不足
A: 对于大量数据，可以分批处理或者减少同时加载的数据量。

### Q: Streamlit启动失败
A: 确保已安装streamlit：`pip install streamlit`

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个程序。

## 📞 联系

如有问题或建议，请通过以下方式联系：
- 提交GitHub Issue
- 发送邮件

---

**注意**: 本程序专为分析`links.txt`中的文章链接设计，确保数据文件格式正确。