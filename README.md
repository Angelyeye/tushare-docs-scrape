# TuShare文档爬虫

## 项目简介
因为tushare官方api文档只有在线版本，我想要把它爬下来，方便自己查看，写了这个脚本。

这是一个用于抓取[TuShare Pro](https://tushare.pro)官方文档的爬虫工具。该工具可以递归地抓取TuShare文档页面，并将其转换为Markdown格式，最终生成一个完整的文档集合，方便离线阅读和查询。

## 功能特点

- 递归抓取TuShare文档页面
- 智能识别页面内容区域
- 将HTML内容转换为Markdown格式
- 保持文档的层级结构
- 支持表格、代码块、列表等复杂元素的转换
- 生成文档结构JSON文件，便于调试和分析

## 环境要求

- Python 3.6+
- 依赖包：
  - requests
  - beautifulsoup4
  - lxml

## 安装方法

1. 克隆或下载本项目代码
2. 安装依赖包：

```bash
pip install -r requirements.txt
```

## 使用方法

直接运行脚本即可开始抓取TuShare文档：

```bash
python tushare_scraper.py
```

### 输出文件

- `tushare_full_doc.md`：包含所有抓取内容的Markdown文档
- `tushare_structure.json`：文档结构的JSON文件，用于调试和分析
- `debug_page.html`：当无法识别内容区域时，会保存原始HTML用于调试

## 工作原理

1. 从入口页面开始，获取页面内容
2. 提取页面中的导航链接
3. 识别页面的主要内容区域
4. 将HTML内容转换为Markdown格式
5. 递归抓取所有链接页面
6. 根据抓取的结构生成最终的Markdown文档

### 主要函数说明

- `get_page_content(url)`：获取网页内容
- `extract_links(soup, base_url)`：提取页面中的链接
- `parse_html_to_markdown(html_content, url)`：将HTML内容解析为Markdown格式
- `convert_table_to_markdown(table)`：将HTML表格转换为Markdown表格
- `convert_list_to_markdown(list_element)`：将HTML列表转换为Markdown列表
- `crawl_page(url, visited_urls, structure, level, parent_title)`：递归抓取页面
- `generate_markdown_from_structure(structure, output_file)`：根据抓取的结构生成Markdown文档

## 自定义配置

如需抓取其他页面或修改输出文件名，可以编辑`main()`函数中的以下参数：

```python
base_url = "https://tushare.pro"  # 网站基础URL
start_url = "https://tushare.pro/document/2"  # 起始页面URL
output_file = "tushare_full_doc.md"  # 输出文件名
```

## 注意事项

- 爬虫使用了模拟浏览器的User-Agent，但仍需遵守网站的robots.txt规则
- 大量快速请求可能会被网站限制，建议适当控制抓取频率
- 网站结构变化可能导致爬虫失效，需要相应更新选择器

## 许可证

MIT