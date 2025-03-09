import requests
from bs4 import BeautifulSoup
import os
import re
import time
import urllib.parse
import json
from collections import defaultdict


def get_page_content(url):
    """获取网页内容"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"获取页面内容时出错: {e}")
        return None


def extract_links(soup, base_url):
    """提取页面中的链接"""
    links = []
    # 查找左侧导航栏中的链接
    nav_links = soup.select('a[href^="/document/"]')
    
    for link in nav_links:
        href = link.get('href')
        if href and href.startswith('/document/'):
            # 构建完整URL
            full_url = urllib.parse.urljoin(base_url, href)
            # 获取链接文本作为标题
            title = link.text.strip()
            if title:
                links.append({'url': full_url, 'title': title})
    
    return links


def parse_html_to_markdown(html_content, url=None):
    """将HTML内容解析为Markdown格式"""
    soup = BeautifulSoup(html_content, 'lxml')
    
    # 打印页面结构以便调试
    print(f"正在分析页面结构... {url if url else ''}")
    
    # 提取页面中的链接（仅在传入URL时执行）
    links = []
    if url:
        links = extract_links(soup, url)
    
    # 尝试多种选择器来查找主要内容区域
    main_content = soup.find('div', class_='doc-content')
    if not main_content:
        print("未找到class='doc-content'的div，尝试其他选择器...")
        main_content = soup.find('div', class_='content')
    if not main_content:
        print("未找到class='content'的div，尝试其他选择器...")
        main_content = soup.find('div', id='content')
    if not main_content:
        print("未找到id='content'的div，尝试查找主要文章区域...")
        main_content = soup.find('article')
    if not main_content:
        print("未找到article标签，尝试查找main标签...")
        main_content = soup.find('main')
    if not main_content:
        print("未找到main标签，尝试使用body作为内容区域...")
        main_content = soup.find('body')
    
    if not main_content:
        print("无法找到任何内容区域")
        # 保存HTML内容以便调试
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print("已将HTML内容保存到debug_page.html文件中以便调试")
        return None
    
    print(f"找到内容区域: {main_content.name} {main_content.get('class', [])}")
    
    markdown_content = []
    
    # 获取标题
    title = soup.find('h1', class_='doc-title')
    if not title:
        title = soup.find('h1')
    if title:
        markdown_content.append(f"# {title.text.strip()}\n")
    else:
        print("未找到标题")
        # 尝试使用页面title作为标题
        page_title = soup.find('title')
        if page_title:
            markdown_content.append(f"# {page_title.text.strip()}\n")
    
    # 处理内容区域中的所有元素
    for element in main_content.find_all(['h2', 'h3', 'h4', 'p', 'table', 'pre', 'ul', 'ol']):
        if element.name == 'h2':
            markdown_content.append(f"\n## {element.text.strip()}\n")
        elif element.name == 'h3':
            markdown_content.append(f"\n### {element.text.strip()}\n")
        elif element.name == 'h4':
            markdown_content.append(f"\n#### {element.text.strip()}\n")
        elif element.name == 'p':
            markdown_content.append(f"{element.text.strip()}\n")
        elif element.name == 'pre':
            code = element.text.strip()
            markdown_content.append(f"```python\n{code}\n```\n")
        elif element.name == 'table':
            markdown_table = convert_table_to_markdown(element)
            markdown_content.append(markdown_table)
        elif element.name in ['ul', 'ol']:
            markdown_list = convert_list_to_markdown(element)
            markdown_content.append(markdown_list)
    
    return '\n'.join(markdown_content)


def convert_table_to_markdown(table):
    """将HTML表格转换为Markdown表格"""
    markdown_table = []
    
    # 获取表头
    headers = []
    header_row = table.find('thead')
    if header_row:
        headers = [th.text.strip() for th in header_row.find_all('th')]
    else:
        # 如果没有thead，尝试从第一行获取表头
        first_row = table.find('tr')
        if first_row:
            headers = [th.text.strip() for th in first_row.find_all(['th', 'td'])]
    
    if headers:
        # 添加表头行
        markdown_table.append('| ' + ' | '.join(headers) + ' |')
        # 添加分隔行
        markdown_table.append('| ' + ' | '.join(['---'] * len(headers)) + ' |')
    
    # 获取表格内容
    rows = table.find_all('tr')
    start_index = 1 if header_row or (rows and rows[0].find('th')) else 0
    
    for row in rows[start_index:]:
        cells = row.find_all(['td', 'th'])
        if cells:
            row_content = [cell.text.strip() for cell in cells]
            markdown_table.append('| ' + ' | '.join(row_content) + ' |')
    
    return '\n'.join(markdown_table) + '\n'


def convert_list_to_markdown(list_element):
    """将HTML列表转换为Markdown列表"""
    markdown_list = []
    
    is_ordered = list_element.name == 'ol'
    
    for i, item in enumerate(list_element.find_all('li', recursive=False)):
        prefix = f"{i+1}." if is_ordered else "-"
        text = item.text.strip()
        markdown_list.append(f"{prefix} {text}")
        
        # 处理嵌套列表
        nested_lists = item.find_all(['ul', 'ol'], recursive=False)
        for nested_list in nested_lists:
            nested_markdown = convert_list_to_markdown(nested_list)
            # 为嵌套列表添加缩进
            nested_markdown = '    ' + nested_markdown.replace('\n', '\n    ')
            markdown_list.append(nested_markdown)
    
    return '\n'.join(markdown_list) + '\n'


def save_to_markdown(content, filename):
    """保存内容到Markdown文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"内容已保存到 {filename}")


def crawl_page(url, visited_urls, structure, level=1, parent_title=None):
    """递归抓取页面"""
    if url in visited_urls:
        return None
    
    print(f"正在抓取 {url}... (层级: {level})")
    visited_urls.add(url)
    
    html_content = get_page_content(url)
    if not html_content:
        print(f"获取页面内容失败: {url}")
        return None
    
    # 解析HTML内容
    soup = BeautifulSoup(html_content, 'lxml')
    
    # 获取页面标题
    title = soup.find('h1', class_='doc-title')
    if not title:
        title = soup.find('h1')
    if not title:
        page_title = soup.find('title')
        if page_title:
            title_text = page_title.text.strip()
        else:
            # 使用URL的最后部分作为标题
            title_text = url.split('/')[-1]
    else:
        title_text = title.text.strip()
    
    # 提取页面中的链接
    links = extract_links(soup, url)
    
    # 解析内容为Markdown
    markdown_content = parse_html_to_markdown(html_content, url)
    
    # 保存到结构中
    if parent_title:
        if parent_title not in structure:
            structure[parent_title] = {}
        structure[parent_title][title_text] = {
            'content': markdown_content,
            'url': url,
            'level': level,
            'children': {}
        }
        current = structure[parent_title][title_text]['children']
    else:
        structure[title_text] = {
            'content': markdown_content,
            'url': url,
            'level': level,
            'children': {}
        }
        current = structure[title_text]['children']
    
    # 递归抓取链接
    for link in links:
        # 避免重复抓取
        if link['url'] not in visited_urls:
            # 递归抓取子页面
            crawl_page(link['url'], visited_urls, current, level + 1, title_text)
    
    return markdown_content


def generate_markdown_from_structure(structure, output_file):
    """根据抓取的结构生成Markdown文档"""
    markdown_content = []
    
    def process_item(item, level=1):
        if 'content' in item and item['content']:
            # 根据层级调整标题级别
            content_lines = item['content'].split('\n')
            # 处理第一行（标题）
            if content_lines and content_lines[0].startswith('# '):
                # 替换为适当级别的标题
                content_lines[0] = '#' * level + content_lines[0][1:]
            
            # 处理其他标题行，增加层级
            for i in range(1, len(content_lines)):
                if content_lines[i].startswith('## '):
                    content_lines[i] = '#' * (level + 1) + content_lines[i][2:]
                elif content_lines[i].startswith('### '):
                    content_lines[i] = '#' * (level + 2) + content_lines[i][3:]
                elif content_lines[i].startswith('#### '):
                    content_lines[i] = '#' * (level + 3) + content_lines[i][4:]
            
            markdown_content.append('\n'.join(content_lines))
        
        # 处理子项
        if 'children' in item:
            for child_title, child_item in item['children'].items():
                process_item(child_item, level + 1)
    
    # 处理顶级项
    for title, item in structure.items():
        process_item(item)
    
    # 保存到文件
    final_content = '\n\n'.join(markdown_content)
    save_to_markdown(final_content, output_file)


def main():
    base_url = "https://tushare.pro"
    start_url = "https://tushare.pro/document/2"
    output_file = "tushare_full_doc.md"
    
    # 用于存储已访问的URL
    visited_urls = set()
    
    # 用于存储文档结构
    structure = {}
    
    print(f"开始递归抓取 {start_url}...")
    crawl_page(start_url, visited_urls, structure)
    
    print(f"抓取完成，共访问了 {len(visited_urls)} 个页面")
    print("正在生成Markdown文档...")
    
    # 生成最终的Markdown文档
    generate_markdown_from_structure(structure, output_file)
    
    print(f"文档已保存到 {output_file}")
    
    # 保存抓取的结构以便调试
    with open("tushare_structure.json", "w", encoding="utf-8") as f:
        json.dump({k: {"url": v["url"], "level": v["level"], "children": list(v["children"].keys())} 
                  for k, v in structure.items()}, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()