#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版每日信息分析程序
包含更详细的数据分析功能和交互式界面
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
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class EnhancedInfoAnalyzer:
    def __init__(self, links_file='links.txt', articles_dir='文章'):
        """
        初始化增强版分析器
        
        Args:
            links_file: 链接文件路径
            articles_dir: 文章存储目录
        """
        self.links_file = links_file
        self.articles_dir = articles_dir
        self.links_data = []
        self.articles_data = []
        self.df_links = None
        self.df_articles = None
        
    def load_and_process_data(self):
        """加载并处理所有数据"""
        try:
            # 加载链接数据
            self.load_links_data()
            
            # 加载文章数据
            self.load_articles_data()
            
            # 创建DataFrame便于分析
            self.create_dataframes()
            
            return True
            
        except Exception as e:
            print(f"数据加载失败：{e}")
            return False
    
    def load_links_data(self):
        """加载链接数据"""
        with open(self.links_file, 'r', encoding='utf-8') as f:
            links = f.readlines()
        
        self.links_data = []
        for link in links:
            link = link.strip()
            if link:
                article_id = self.extract_article_id(link)
                date_info = self.extract_date_from_link(link)
                
                self.links_data.append({
                    'url': link,
                    'article_id': article_id,
                    'date': date_info,
                    'year': date_info.year if date_info else None,
                    'month': date_info.strftime('%Y-%m') if date_info else None
                })
    
    def load_articles_data(self):
        """加载文章数据"""
        self.articles_data = []
        
        if not os.path.exists(self.articles_dir):
            return
        
        for file in os.listdir(self.articles_dir):
            if file.endswith('.docx'):
                file_path = os.path.join(self.articles_dir, file)
                
                # 提取标题信息
                title = file.replace('.docx', '')
                
                # 获取文件信息
                file_stat = os.stat(file_path)
                file_size = file_stat.st_size
                create_time = datetime.fromtimestamp(file_stat.st_ctime)
                modify_time = datetime.fromtimestamp(file_stat.st_mtime)
                
                self.articles_data.append({
                    'title': title,
                    'filename': file,
                    'filepath': file_path,
                    'file_size': file_size,
                    'create_time': create_time,
                    'modify_time': modify_time
                })
    
    def create_dataframes(self):
        """创建数据分析用的DataFrame"""
        self.df_links = pd.DataFrame(self.links_data)
        self.df_articles = pd.DataFrame(self.articles_data)
        
        # 数据清洗和转换
        if not self.df_links.empty:
            self.df_links['date'] = pd.to_datetime(self.df_links['date'])
        
        if not self.df_articles.empty:
            self.df_articles['create_time'] = pd.to_datetime(self.df_articles['create_time'])
            self.df_articles['modify_time'] = pd.to_datetime(self.df_articles['modify_time'])
    
    def extract_article_id(self, url):
        """从URL中提取文章ID"""
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
        """从链接中提取日期"""
        match = re.search(r'B(\d{8})', link)
        if match:
            date_str = match.group(1)
            try:
                return datetime.strptime(date_str, '%Y%m%d').date()
            except:
                pass
        
        return datetime.now().date()
    
    def get_comprehensive_stats(self):
        """获取综合统计信息"""
        stats = {
            '基础统计': self.get_basic_stats(),
            '时间分析': self.analyze_by_time(),
            '关键词分析': self.analyze_keywords(),
            '文件分析': self.analyze_files(),
            '趋势分析': self.analyze_trends()
        }
        
        return stats
    
    def get_basic_stats(self):
        """获取基础统计"""
        return {
            '总链接数': len(self.df_links) if self.df_links is not None else 0,
            '已下载文章数': len(self.df_articles) if self.df_articles is not None else 0,
            '下载率': (len(self.df_articles) / len(self.df_links) * 100) if self.df_links is not None and len(self.df_links) > 0 else 0,
            '数据覆盖天数': self.get_data_coverage_days(),
            '平均每日链接数': self.get_avg_daily_links()
        }
    
    def get_data_coverage_days(self):
        """获取数据覆盖天数"""
        if self.df_links is None or self.df_links.empty:
            return 0
        
        date_range = self.df_links['date'].max() - self.df_links['date'].min()
        return date_range.days + 1
    
    def get_avg_daily_links(self):
        """获取平均每日链接数"""
        days = self.get_data_coverage_days()
        if days == 0:
            return 0
        
        return len(self.df_links) / days if self.df_links is not None else 0
    
    def analyze_by_time(self):
        """时间序列分析"""
        if self.df_links is None or self.df_links.empty:
            return {}
        
        # 日度分析
        daily_counts = self.df_links.groupby(self.df_links['date'].dt.date).size()
        
        # 月度分析
        monthly_counts = self.df_links.groupby(self.df_links['date'].dt.to_period('M')).size()
        
        # 年度分析
        yearly_counts = self.df_links.groupby(self.df_links['date'].dt.year).size()
        
        # 星期分析
        self.df_links['weekday'] = self.df_links['date'].dt.day_name()
        weekday_counts = self.df_links['weekday'].value_counts()
        
        return {
            'daily_distribution': daily_counts.to_dict(),
            'monthly_distribution': monthly_counts.to_dict(),
            'yearly_distribution': yearly_counts.to_dict(),
            'weekday_distribution': weekday_counts.to_dict(),
            'peak_day': daily_counts.idxmax() if not daily_counts.empty else None,
            'peak_count': daily_counts.max() if not daily_counts.empty else 0
        }
    
    def analyze_keywords(self, top_n=30):
        """增强版关键词分析"""
        if not self.articles_data:
            return {}
        
        all_titles = " ".join([article['title'] for article in self.articles_data])
        
        # 分词
        words = jieba.cut(all_titles)
        
        # 过滤
        stop_words = self.get_stop_words()
        filtered_words = [word for word in words if len(word) > 1 and word not in stop_words]
        
        # 词频统计
        word_freq = Counter(filtered_words)
        
        # 关键词分类
        categories = self.categorize_keywords(word_freq.most_common(top_n))
        
        return {
            'top_keywords': word_freq.most_common(top_n),
            'total_words': len(filtered_words),
            'unique_words': len(set(filtered_words)),
            'word_density': len(filtered_words) / len(self.articles_data) if self.articles_data else 0,
            'categories': categories
        }
    
    def get_stop_words(self):
        """获取停用词列表"""
        basic_stop_words = {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '些', '个'
        }
        
        # 可以添加更多停用词
        return basic_stop_words
    
    def categorize_keywords(self, keywords):
        """关键词分类"""
        categories = {
            '政策相关': [],
            '行业相关': [],
            '组织相关': [],
            '时间相关': [],
            '其他': []
        }
        
        policy_words = ['政策', '规定', '制度', '法规', '标准', '规范', '通知', '公告', '指导意见']
        industry_words = ['行业', '产业', '市场', '企业', '公司', '业务', '服务', '产品']
        org_words = ['委员会', '协会', '组织', '机构', '部门', '单位', '团体']
        time_words = ['年', '月', '日', '季度', '年度', '月度', '周期']
        
        for word, freq in keywords:
            if any(pw in word for pw in policy_words):
                categories['政策相关'].append((word, freq))
            elif any(iw in word for iw in industry_words):
                categories['行业相关'].append((word, freq))
            elif any(ow in word for ow in org_words):
                categories['组织相关'].append((word, freq))
            elif any(tw in word for tw in time_words):
                categories['时间相关'].append((word, freq))
            else:
                categories['其他'].append((word, freq))
        
        return categories
    
    def analyze_files(self):
        """文件分析"""
        if not self.articles_data:
            return {}
        
        file_sizes = [article['file_size'] for article in self.articles_data]
        
        return {
            '总文件大小': sum(file_sizes),
            '平均文件大小': sum(file_sizes) / len(file_sizes) if file_sizes else 0,
            '最大文件': max(file_sizes) if file_sizes else 0,
            '最小文件': min(file_sizes) if file_sizes else 0,
            '文件总数': len(self.articles_data)
        }
    
    def analyze_trends(self):
        """趋势分析"""
        if self.df_links is None or self.df_links.empty:
            return {}
        
        # 计算滚动平均
        daily_counts = self.df_links.groupby(self.df_links['date'].dt.date).size()
        
        # 简单趋势判断
        if len(daily_counts) > 1:
            recent_avg = daily_counts.tail(7).mean()  # 最近7天平均
            overall_avg = daily_counts.mean()  # 总体平均
            
            trend = "上升" if recent_avg > overall_avg * 1.1 else \
                   "下降" if recent_avg < overall_avg * 0.9 else "平稳"
        else:
            trend = "数据不足"
        
        return {
            '整体趋势': trend,
            '活跃度指数': self.calculate_activity_index(),
            '更新频率': self.calculate_update_frequency()
        }
    
    def calculate_activity_index(self):
        """计算活跃度指数"""
        if self.df_links is None or self.df_links.empty:
            return 0
        
        # 基于最近30天的数据
        recent_data = self.df_links[
            self.df_links['date'] >= datetime.now() - timedelta(days=30)
        ]
        
        return len(recent_data) / 30 * 100  # 每日平均链接数 * 100
    
    def calculate_update_frequency(self):
        """计算更新频率"""
        if self.df_links is None or self.df_links.empty:
            return "无数据"
        
        days = self.get_data_coverage_days()
        total_links = len(self.df_links)
        
        if days == 0:
            return "无数据"
        
        freq = total_links / days
        
        if freq >= 5:
            return "高频"
        elif freq >= 2:
            return "中频"
        elif freq >= 0.5:
            return "低频"
        else:
            return "极低频"
    
    def create_interactive_dashboard(self):
        """创建交互式仪表板"""
        try:
            import streamlit as st
            
            st.set_page_config(
                page_title="每日信息分析仪表板",
                page_icon="📊",
                layout="wide"
            )
            
            st.title("📊 每日信息分析仪表板")
            
            # 加载数据
            if st.button("重新加载数据"):
                self.load_and_process_data()
                st.success("数据已重新加载！")
            
            # 侧边栏
            with st.sidebar:
                st.header("控制面板")
                analysis_type = st.selectbox(
                    "选择分析类型",
                    ["基础统计", "时间分析", "关键词分析", "文件分析", "趋势分析", "综合报告"]
                )
                
                time_range = st.slider(
                    "时间范围（天）",
                    min_value=7,
                    max_value=365,
                    value=30
                )
            
            # 主要内容区域
            if analysis_type == "基础统计":
                self.show_basic_stats()
            elif analysis_type == "时间分析":
                self.show_time_analysis()
            elif analysis_type == "关键词分析":
                self.show_keyword_analysis()
            elif analysis_type == "文件分析":
                self.show_file_analysis()
            elif analysis_type == "趋势分析":
                self.show_trend_analysis()
            elif analysis_type == "综合报告":
                self.show_comprehensive_report()
            
        except ImportError:
            print("Streamlit 未安装，无法创建交互式仪表板")
            print("请运行: pip install streamlit")
    
    def show_basic_stats(self):
        """显示基础统计"""
        st.header("基础统计信息")
        
        col1, col2, col3, col4 = st.columns(4)
        
        basic_stats = self.get_basic_stats()
        
        with col1:
            st.metric("总链接数", basic_stats['总链接数'])
        
        with col2:
            st.metric("已下载文章数", basic_stats['已下载文章数'])
        
        with col3:
            st.metric("下载率", f"{basic_stats['下载率']:.1f}%")
        
        with col4:
            st.metric("平均每日链接数", f"{basic_stats['平均每日链接数']:.1f}")
    
    def show_time_analysis(self):
        """显示时间分析"""
        st.header("时间分析")
        
        time_analysis = self.analyze_by_time()
        
        if time_analysis:
            # 月度分布图
            monthly_data = time_analysis['monthly_distribution']
            if monthly_data:
                months = list(monthly_data.keys())
                counts = list(monthly_data.values())
                
                fig = px.bar(x=months, y=counts, title="月度文章发布分布")
                fig.update_xaxes(title="月份")
                fig.update_yaxes(title="文章数量")
                st.plotly_chart(fig, use_container_width=True)
    
    def show_keyword_analysis(self):
        """显示关键词分析"""
        st.header("关键词分析")
        
        keyword_analysis = self.analyze_keywords()
        
        if keyword_analysis:
            # 词云
            keywords = dict(keyword_analysis['top_keywords'][:50])
            
            wordcloud = WordCloud(
                width=800, height=400,
                background_color='white',
                font_path='simhei.ttf',  # 中文字体
                colormap='viridis'
            ).generate_from_frequencies(keywords)
            
            st.image(wordcloud.to_array(), use_column_width=True)
            
            # 关键词表格
            st.subheader("热门关键词")
            keyword_df = pd.DataFrame(
                keyword_analysis['top_keywords'][:20],
                columns=['关键词', '频次']
            )
            st.dataframe(keyword_df)
    
    def show_file_analysis(self):
        """显示文件分析"""
        st.header("文件分析")
        
        file_analysis = self.analyze_files()
        
        if file_analysis:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("总文件大小", f"{file_analysis['总文件大小'] / 1024 / 1024:.2f} MB")
            
            with col2:
                st.metric("平均文件大小", f"{file_analysis['平均文件大小'] / 1024:.1f} KB")
            
            with col3:
                st.metric("文件总数", file_analysis['文件总数'])
    
    def show_trend_analysis(self):
        """显示趋势分析"""
        st.header("趋势分析")
        
        trend_analysis = self.analyze_trends()
        
        if trend_analysis:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("整体趋势", trend_analysis['整体趋势'])
            
            with col2:
                st.metric("活跃度指数", f"{trend_analysis['活跃度指数']:.1f}")
            
            with col3:
                st.metric("更新频率", trend_analysis['更新频率'])
    
    def show_comprehensive_report(self):
        """显示综合报告"""
        st.header("综合报告")
        
        # 获取所有分析结果
        comprehensive_stats = self.get_comprehensive_stats()
        
        # 创建仪表板布局
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("基础统计")
            basic_stats = comprehensive_stats['基础统计']
            for key, value in basic_stats.items():
                st.write(f"**{key}:** {value}")
        
        with col2:
            st.subheader("文件统计")
            file_stats = comprehensive_stats['文件分析']
            for key, value in file_stats.items():
                st.write(f"**{key}:** {value}")
        
        # 趋势分析
        st.subheader("趋势分析")
        trend_stats = comprehensive_stats['趋势分析']
        for key, value in trend_stats.items():
            st.write(f"**{key}:** {value}")
    
    def generate_static_report(self, output_dir='reports'):
        """生成静态报告"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_dir = os.path.join(output_dir, f'report_{timestamp}')
        os.makedirs(report_dir)
        
        # 获取分析结果
        comprehensive_stats = self.get_comprehensive_stats()
        
        # 生成HTML报告
        html_report = self.create_detailed_html_report(comprehensive_stats)
        
        with open(os.path.join(report_dir, 'report.html'), 'w', encoding='utf-8') as f:
            f.write(html_report)
        
        # 生成图表
        self.generate_detailed_charts(comprehensive_stats, report_dir)
        
        return report_dir
    
    def create_detailed_html_report(self, stats):
        """创建详细的HTML报告"""
        html = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>详细分析报告 - {datetime.now().strftime('%Y年%m月%d日')}</title>
            <style>
                body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; margin-bottom: 40px; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; }}
                .section {{ margin: 30px 0; padding: 25px; border: 1px solid #e0e0e0; border-radius: 8px; background-color: #fafafa; }}
                .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }}
                .stat-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; transition: transform 0.3s; }}
                .stat-card:hover {{ transform: translateY(-5px); }}
                .stat-number {{ font-size: 2.5em; font-weight: bold; color: #667eea; margin: 10px 0; }}
                .stat-label {{ color: #666; font-size: 1.1em; }}
                .chart-container {{ margin: 20px 0; text-align: center; }}
                .keyword-list {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px; margin: 20px 0; }}
                .keyword-item {{ background: white; padding: 10px; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); display: flex; justify-content: space-between; align-items: center; }}
                .footer {{ text-align: center; margin-top: 40px; padding: 20px; background-color: #f0f0f0; border-radius: 8px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 每日信息详细分析报告</h1>
                    <p>生成时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M')}</p>
                </div>
        """
        
        # 基础统计
        basic_stats = stats['基础统计']
        html += f"""
                <div class="section">
                    <h2>📈 基础统计信息</h2>
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-number">{basic_stats['总链接数']}</div>
                            <div class="stat-label">总链接数</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{basic_stats['已下载文章数']}</div>
                            <div class="stat-label">已下载文章数</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{basic_stats['下载率']:.1f}%</div>
                            <div class="stat-label">下载率</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{basic_stats['数据覆盖天数']}</div>
                            <div class="stat-label">数据覆盖天数</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{basic_stats['平均每日链接数']:.1f}</div>
                            <div class="stat-label">平均每日链接数</div>
                        </div>
                    </div>
                </div>
        """
        
        # 文件统计
        file_stats = stats['文件分析']
        html += f"""
                <div class="section">
                    <h2>📁 文件统计信息</h2>
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-number">{file_stats['总文件大小'] / 1024 / 1024:.2f} MB</div>
                            <div class="stat-label">总文件大小</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{file_stats['平均文件大小'] / 1024:.1f} KB</div>
                            <div class="stat-label">平均文件大小</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{file_stats['文件总数']}</div>
                            <div class="stat-label">文件总数</div>
                        </div>
                    </div>
                </div>
        """
        
        # 趋势分析
        trend_stats = stats['趋势分析']
        html += f"""
                <div class="section">
                    <h2>📊 趋势分析</h2>
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-number">{trend_stats['整体趋势']}</div>
                            <div class="stat-label">整体趋势</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{trend_stats['活跃度指数']:.1f}</div>
                            <div class="stat-label">活跃度指数</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{trend_stats['更新频率']}</div>
                            <div class="stat-label">更新频率</div>
                        </div>
                    </div>
                </div>
        """
        
        # 关键词分析
        keyword_stats = stats['关键词分析']
        if keyword_stats:
            html += f"""
                <div class="section">
                    <h2>🔤 关键词分析</h2>
                    <p>总词数：{keyword_stats['total_words']} | 独特词数：{keyword_stats['unique_words']} | 词密度：{keyword_stats['word_density']:.2f}</p>
                    <div class="keyword-list">
            """
            
            for word, freq in keyword_stats['top_keywords'][:30]:
                html += f'<div class="keyword-item"><span>{word}</span><span>{freq}</span></div>'
            
            html += """
                    </div>
                </div>
            """
        
        # 时间分析
        time_stats = stats['时间分析']
        if time_stats:
            html += f"""
                <div class="section">
                    <h2>⏰ 时间分布分析</h2>
                    <div class="chart-container">
                        <p><strong>峰值日期：</strong> {time_stats['peak_day']} ({time_stats['peak_count']} 篇)</p>
                    </div>
                    <div class="chart-container">
                        <img src="monthly_distribution.png" alt="月度分布图" style="max-width: 100%; height: auto;">
                    </div>
                </div>
            """
        
        html += f"""
                <div class="footer">
                    <p>报告生成时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}</p>
                    <p>本报告由每日信息分析程序自动生成</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def generate_detailed_charts(self, stats, output_dir):
        """生成详细图表"""
        time_stats = stats['时间分析']
        
        if time_stats and time_stats['monthly_distribution']:
            # 月度分布图
            plt.figure(figsize=(15, 8))
            
            monthly_data = time_stats['monthly_distribution']
            months = list(monthly_data.keys())
            counts = list(monthly_data.values())
            
            plt.subplot(2, 1, 1)
            plt.bar(months, counts, color='skyblue', alpha=0.7)
            plt.title('文章月度发布分布', fontsize=16, fontweight='bold')
            plt.xlabel('月份', fontsize=12)
            plt.ylabel('文章数量', fontsize=12)
            plt.xticks(rotation=45)
            plt.grid(axis='y', alpha=0.3)
            
            # 日度分布图（最近30天）
            plt.subplot(2, 1, 2)
            daily_data = time_stats['daily_distribution']
            if daily_data:
                # 只显示最近30天
                recent_days = sorted(daily_data.keys())[-30:]
                recent_counts = [daily_data[day] for day in recent_days]
                
                plt.plot(recent_days, recent_counts, marker='o', linewidth=2, markersize=4)
                plt.title('最近30天文章发布趋势', fontsize=16, fontweight='bold')
                plt.xlabel('日期', fontsize=12)
                plt.ylabel('文章数量', fontsize=12)
                plt.xticks(rotation=45)
                plt.grid(alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'monthly_distribution.png'), dpi=300, bbox_inches='tight')
            plt.close()
        
        # 关键词词云
        keyword_stats = stats['关键词分析']
        if keyword_stats:
            keywords = dict(keyword_stats['top_keywords'][:100])
            
            plt.figure(figsize=(12, 8))
            wordcloud = WordCloud(
                width=1200, height=800,
                background_color='white',
                colormap='viridis',
                max_words=100,
                relative_scaling=0.5,
                min_font_size=10
            ).generate_from_frequencies(keywords)
            
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.title('关键词词云', fontsize=20, fontweight='bold', pad=20)
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'keyword_wordcloud.png'), dpi=300, bbox_inches='tight')
            plt.close()

def main():
    """主函数"""
    print("=== 增强版每日信息分析程序 ===")
    
    # 创建分析器
    analyzer = EnhancedInfoAnalyzer()
    
    # 加载数据
    print("正在加载数据...")
    if not analyzer.load_and_process_data():
        print("数据加载失败，程序退出")
        return
    
    # 生成静态报告
    print("正在生成静态报告...")
    report_dir = analyzer.generate_static_report()
    
    print(f"\n=== 分析完成 ===")
    print(f"报告目录：{report_dir}")
    print(f"报告文件：{os.path.join(report_dir, 'report.html')}")
    print(f"图表文件：{os.path.join(report_dir, 'monthly_distribution.png')}")
    print(f"词云文件：{os.path.join(report_dir, 'keyword_wordcloud.png')}")
    
    # 可选：启动交互式仪表板
    print("\n是否启动交互式仪表板？(需要安装streamlit)")
    response = input("输入 'y' 启动，其他键退出: ")
    
    if response.lower() == 'y':
        try:
            analyzer.create_interactive_dashboard()
        except Exception as e:
            print(f"启动交互式仪表板失败：{e}")

if __name__ == "__main__":
    main()