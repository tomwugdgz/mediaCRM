#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日信息分析程序
用于分析从links.txt中收集的文章信息，提供数据统计、关键词分析等功能
"""

import os
import re
import json
import pandas as pd
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import jieba
from bs4 import BeautifulSoup
import requests

class DailyInfoAnalyzer:
    def __init__(self, links_file='links.txt', articles_dir='文章'):
        """
        初始化分析器
        
        Args:
            links_file: 链接文件路径
            articles_dir: 文章存储目录
        """
        self.links_file = links_file
        self.articles_dir = articles_dir
        self.links_data = []
        self.articles_data = []
        
    def load_links_data(self):
        """加载链接数据"""
        try:
            with open(self.links_file, 'r', encoding='utf-8') as f:
                links = f.readlines()
            
            # 解析链接，提取信息
            for link in links:
                link = link.strip()
                if link:
                    # 提取文章ID和日期信息
                    article_id = self.extract_article_id(link)
                    date_info = self.extract_date_from_link(link)
                    
                    self.links_data.append({
                        'url': link,
                        'article_id': article_id,
                        'date': date_info
                    })
            
            print(f"成功加载 {len(self.links_data)} 条链接数据")
            return True
            
        except FileNotFoundError:
            print(f"错误：找不到文件 {self.links_file}")
            return False
        except Exception as e:
            print(f"加载链接数据时出错：{e}")
            return False
    
    def extract_article_id(self, url):
        """从URL中提取文章ID"""
        # 匹配URL中的ID模式
        patterns = [
            r'B(\d+)\.html',
            r'([a-f0-9-]{36})\.html'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return "unknown"
    
    def extract_date_from_link(self, link):
        """尝试从链接中提取日期信息"""
        # 从B开头的ID中提取可能的日期信息
        match = re.search(r'B(\d{8})', link)
        if match:
            date_str = match.group(1)
            try:
                return datetime.strptime(date_str, '%Y%m%d').date()
            except:
                pass
        
        return datetime.now().date()
    
    def load_articles_data(self):
        """加载已下载的文章数据"""
        if not os.path.exists(self.articles_dir):
            print(f"文章目录 {self.articles_dir} 不存在")
            return False
        
        article_files = [f for f in os.listdir(self.articles_dir) if f.endswith('.docx')]
        
        for file in article_files:
            file_path = os.path.join(self.articles_dir, file)
            try:
                # 这里可以添加读取docx文件内容的代码
                # 暂时只获取文件名信息
                title = file.replace('.docx', '')
                
                self.articles_data.append({
                    'title': title,
                    'filename': file,
                    'filepath': file_path
                })
                
            except Exception as e:
                print(f"读取文件 {file} 时出错：{e}")
        
        print(f"成功加载 {len(self.articles_data)} 篇文章数据")
        return True
    
    def get_basic_stats(self):
        """获取基础统计信息"""
        stats = {
            'total_links': len(self.links_data),
            'total_articles': len(self.articles_data),
            'download_rate': len(self.articles_data) / len(self.links_data) * 100 if self.links_data else 0,
            'date_range': self.get_date_range(),
            'recent_activity': self.get_recent_activity()
        }
        
        return stats
    
    def get_date_range(self):
        """获取日期范围"""
        if not self.links_data:
            return None
        
        dates = [item['date'] for item in self.links_data if item['date']]
        if not dates:
            return None
        
        return {
            'start': min(dates),
            'end': max(dates),
            'span': (max(dates) - min(dates)).days
        }
    
    def get_recent_activity(self, days=30):
        """获取近期活动情况"""
        if not self.links_data:
            return None
        
        cutoff_date = datetime.now().date() - timedelta(days=days)
        recent_links = [item for item in self.links_data if item['date'] and item['date'] >= cutoff_date]
        
        return {
            'recent_links': len(recent_links),
            'recent_articles': len([article for article in self.articles_data 
                                  if self.is_recent_article(article, days)]),
            'period': f"最近{days}天"
        }
    
    def is_recent_article(self, article, days=30):
        """判断文章是否为近期文章"""
        # 这里可以根据文件修改时间或其他逻辑判断
        return True  # 简化处理
    
    def analyze_keywords(self, top_n=20):
        """关键词分析"""
        if not self.articles_data:
            print("没有文章数据可供分析")
            return None
        
        all_text = ""
        for article in self.articles_data:
            all_text += article['title'] + " "
        
        # 使用jieba进行分词
        words = jieba.cut(all_text)
        
        # 过滤停用词和短词
        filtered_words = []
        stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '些', '个', '为', '与', '及', '或', '但', '而', '因为', '所以', '如果', '虽然', '然而', '但是', '不过', '只是', '仍然', '还', '又', '再', '更', '最', '比较', '相当', '很', '非常', '极', '最', '顶', '挺', '真', '正', '刚', '才', '总', '老', '常', '永', '决', '绝', '终', '始', '纯', '净', '素', '空', '虚', '满', '实', '齐', '全', '都', '共', '总', '统', '通', '普', '遍', '凡', '大凡', '大凡', '凡是', '是', '凡', '大凡', '大凡', '凡是', '是', '凡', '大凡', '大凡', '凡是', '是'}
        
        for word in words:
            if len(word) > 1 and word not in stop_words:
                filtered_words.append(word)
        
        # 统计词频
        word_freq = Counter(filtered_words)
        
        return {
            'top_keywords': word_freq.most_common(top_n),
            'total_words': len(filtered_words),
            'unique_words': len(set(filtered_words))
        }
    
    def analyze_by_time(self):
        """时间序列分析"""
        if not self.links_data:
            print("没有链接数据可供分析")
            return None
        
        # 按日期分组统计
        daily_stats = defaultdict(int)
        monthly_stats = defaultdict(int)
        
        for item in self.links_data:
            if item['date']:
                date = item['date']
                daily_stats[date] += 1
                monthly_stats[date.strftime('%Y-%m')] += 1
        
        return {
            'daily_distribution': dict(daily_stats),
            'monthly_distribution': dict(monthly_stats),
            'peak_day': max(daily_stats.items(), key=lambda x: x[1]) if daily_stats else None,
            'peak_month': max(monthly_stats.items(), key=lambda x: x[1]) if monthly_stats else None
        }
    
    def generate_report(self, output_file='analysis_report.html'):
        """生成分析报告"""
        print("开始生成分析报告...")
        
        # 获取各项分析结果
        basic_stats = self.get_basic_stats()
        keywords_analysis = self.analyze_keywords()
        time_analysis = self.analyze_by_time()
        
        # 生成HTML报告
        html_content = self.create_html_report(basic_stats, keywords_analysis, time_analysis)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"分析报告已生成：{output_file}")
        
        # 生成图表
        self.generate_charts(time_analysis)
        
        return output_file
    
    def create_html_report(self, basic_stats, keywords_analysis, time_analysis):
        """创建HTML报告内容"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>每日信息分析报告</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
                .stat-card {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; text-align: center; }}
                .keyword-list {{ columns: 2; column-gap: 20px; }}
                .keyword-item {{ margin: 5px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>每日信息分析报告</h1>
                <p>生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="section">
                <h2>基础统计信息</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>总链接数</h3>
                        <p>{basic_stats['total_links']}</p>
                    </div>
                    <div class="stat-card">
                        <h3>已下载文章</h3>
                        <p>{basic_stats['total_articles']}</p>
                    </div>
                    <div class="stat-card">
                        <h3>下载率</h3>
                        <p>{basic_stats['download_rate']:.1f}%</p>
                    </div>
                </div>
            </div>
        """
        
        # 添加关键词分析
        if keywords_analysis:
            html += f"""
            <div class="section">
                <h2>关键词分析</h2>
                <p>总词数：{keywords_analysis['total_words']} | 独特词数：{keywords_analysis['unique_words']}</p>
                <div class="keyword-list">
            """
            
            for word, freq in keywords_analysis['top_keywords']:
                html += f'<div class="keyword-item">{word}: {freq}</div>'
            
            html += """
                </div>
            </div>
            """
        
        # 添加时间分析
        if time_analysis:
            html += f"""
            <div class="section">
                <h2>时间分布分析</h2>
            """
            
            if time_analysis['peak_day']:
                html += f"<p>最高发布日：{time_analysis['peak_day'][0]} ({time_analysis['peak_day'][1]} 篇)</p>"
            
            if time_analysis['peak_month']:
                html += f"<p>最高发布月：{time_analysis['peak_month'][0]} ({time_analysis['peak_month'][1]} 篇)</p>"
            
            html += """
            </div>
            """
        
        html += """
        </body>
        </html>
        """
        
        return html
    
    def generate_charts(self, time_analysis):
        """生成图表"""
        if not time_analysis or not time_analysis['monthly_distribution']:
            return
        
        # 月度分布图
        plt.figure(figsize=(12, 6))
        
        months = list(time_analysis['monthly_distribution'].keys())
        counts = list(time_analysis['monthly_distribution'].values())
        
        plt.bar(months, counts)
        plt.title('文章月度发布分布')
        plt.xlabel('月份')
        plt.ylabel('文章数量')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        plt.savefig('monthly_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("图表已生成：monthly_distribution.png")

def main():
    """主函数"""
    print("=== 每日信息分析程序 ===")
    
    # 创建分析器实例
    analyzer = DailyInfoAnalyzer()
    
    # 加载数据
    print("正在加载数据...")
    if not analyzer.load_links_data():
        return
    
    analyzer.load_articles_data()
    
    # 生成分析报告
    print("正在生成分析报告...")
    report_file = analyzer.generate_report()
    
    print(f"\n分析完成！")
    print(f"报告文件：{report_file}")
    print("图表文件：monthly_distribution.png")

if __name__ == "__main__":
    main()