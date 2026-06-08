#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
美妆产品多品牌数据分析仪表板 — Flask 后端
"""
from flask import Flask, render_template, jsonify, request
import pandas as pd
import numpy as np
import os

app = Flask(__name__)
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

# ================================================================
# 数据加载（启动时一次性加载）
# ================================================================
brand_df = pd.read_csv(os.path.join(DATA_DIR, 'brand_comparison.csv'), encoding='utf-8-sig')
kw_df = pd.read_csv(os.path.join(DATA_DIR, 'brand_keywords_tfidf.csv'), encoding='utf-8-sig')

# 品牌列表
ALL_BRANDS = sorted(brand_df['品牌'].tolist())

# 聚类特征数据（硬编码，来自分析结果）
CLUSTER_DATA = [
    {"id": 0, "name": "大众性价比市场", "count": 399, "avg_price": 160, "avg_sales": 2798,
     "avg_rating": 4.61, "avg_reviews": 521, "top_brands": "资生堂、科颜氏、悦木之源", "top_cats": "眉笔、洁面乳、爽肤水"},
    {"id": 1, "name": "中端均衡市场", "count": 367, "avg_price": 168, "avg_sales": 3150,
     "avg_rating": 3.86, "avg_reviews": 603, "top_brands": "自然堂、科颜氏、丸美", "top_cats": "口红、眉笔、防晒霜"},
    {"id": 2, "name": "高端精品市场", "count": 164, "avg_price": 731, "avg_sales": 2891,
     "avg_rating": 4.30, "avg_reviews": 550, "top_brands": "倩碧、资生堂、百雀羚", "top_cats": "眼线笔、口红、睫毛膏"},
    {"id": 3, "name": "爆款明星市场", "count": 70, "avg_price": 239, "avg_sales": 67772,
     "avg_rating": 4.20, "avg_reviews": 13483, "top_brands": "科颜氏、自然堂、兰蔻", "top_cats": "眼霜、洁面乳、眼线笔"},
]

# LDA主题数据（硬编码）
LDA_TOPICS = [
    {"id": 1, "name": "产品体验与期望", "keywords": ["质地", "适合", "入手", "失望", "皮肤", "滋润", "效果", "预期"]},
    {"id": 2, "name": "长期效果与质量", "keywords": ["值得", "购买", "皮肤", "变得", "质量", "状态", "稳定", "肤质"]},
    {"id": 3, "name": "使用效果与回购", "keywords": ["效果", "使用", "惊艳", "回购", "不错", "性价比", "味道", "包装"]},
    {"id": 4, "name": "价格与功效", "keywords": ["效果", "价格", "适合", "值得", "明显", "资生堂", "肤质", "防晒霜"]},
    {"id": 5, "name": "包装与送礼场景", "keywords": ["包装", "精美", "推荐", "不错", "朋友", "送礼", "合适", "舒服"]},
    {"id": 6, "name": "彩妆与功效推荐", "keywords": ["推荐", "眼影", "提亮", "效果", "细纹", "肤色", "保湿", "控油"]},
]

# 模型数据（硬编码）
MODEL_DATA = {
    "classification": [
        {"name": "决策树", "accuracy": 0.2687, "cv_mean": 0.4613, "cv_std": 0.0282},
        {"name": "随机森林", "accuracy": 0.4328, "cv_mean": 0.5132, "cv_std": 0.0280},
        {"name": "梯度提升", "accuracy": 0.4478, "cv_mean": 0.4485, "cv_std": 0.0459},
        {"name": "XGBoost", "accuracy": 0.4478, "cv_mean": 0.4742, "cv_std": 0.0277},
        {"name": "逻辑回归", "accuracy": 0.4776, "cv_mean": 0.4677, "cv_std": 0.0300},
    ],
    "regression": [
        {"name": "线性回归", "r2": 0.8072, "rmse": 9299.39, "mae": 3249.70},
        {"name": "Ridge回归", "r2": 0.8062, "rmse": 9322.51, "mae": 3256.01},
        {"name": "随机森林", "r2": 0.8916, "rmse": 6973.03, "mae": 2386.33},
        {"name": "梯度提升", "r2": 0.8331, "rmse": 8651.90, "mae": 2709.30},
        {"name": "XGBoost", "r2": 0.8399, "rmse": 8473.85, "mae": 2664.94},
    ],
    "brand_regression": [
        {"brand": "科颜氏", "r2": 0.8283, "rmse": 8006, "driver": "评价数"},
        {"brand": "资生堂", "r2": 0.9411, "rmse": 3484, "driver": "评价数"},
        {"brand": "自然堂", "r2": 0.9795, "rmse": 3112, "driver": "评价数"},
        {"brand": "丸美", "r2": 0.7959, "rmse": 9705, "driver": "评价数"},
        {"brand": "兰蔻", "r2": 0.8779, "rmse": 5794, "driver": "评价数"},
    ],
}

# ================================================================
# 页面路由
# ================================================================
@app.route('/')
def index():
    return render_template('index.html', active_page='index')

@app.route('/sentiment')
def sentiment():
    return render_template('sentiment.html', active_page='sentiment')

@app.route('/topics')
def topics():
    return render_template('topics.html', active_page='topics')

@app.route('/clustering')
def clustering():
    return render_template('clustering.html', active_page='clustering')

@app.route('/brands')
def brands():
    return render_template('brands.html', active_page='brands')

@app.route('/models')
def models():
    return render_template('models.html', active_page='models')

@app.route('/code')
def code_page():
    return render_template('code.html', active_page='code')

# ================================================================
# JSON API
# ================================================================
@app.route('/api/overview')
def api_overview():
    total_brands = len(ALL_BRANDS)
    total_products = int(brand_df['商品数'].sum())
    total_reviews = int(brand_df['评论数'].sum())
    avg_positive = float(brand_df['正面评论占比'].mean())
    best_brand = brand_df.nlargest(1, '综合竞争力').iloc[0]
    worst_brand = brand_df.nsmallest(1, '综合竞争力').iloc[0]

    top10 = brand_df.head(10)[['品牌', '综合竞争力', '平均情感得分', '平均评分', '评论数']].to_dict('records')
    bubble = brand_df[['品牌', '平均价格', '平均销量', '评论数', '平均情感得分']].to_dict('records')

    return jsonify({
        'kpi': {
            'brands': total_brands,
            'products': total_products,
            'reviews': total_reviews,
            'positive_rate': round(avg_positive * 100, 1),
        },
        'best_brand': {'name': best_brand['品牌'], 'score': round(best_brand['综合竞争力'], 3)},
        'worst_brand': {'name': worst_brand['品牌'], 'score': round(worst_brand['综合竞争力'], 3)},
        'top10': top10,
        'bubble': bubble,
        'brands': ALL_BRANDS,
    })

@app.route('/api/sentiment')
def api_sentiment():
    sentiment_cols = ['品牌', '平均情感得分', '正面评论占比', '中性占比', '负面占比', '平均评分', '平均点赞', '评论数']
    # 挑选可用列
    available = [c for c in sentiment_cols if c in brand_df.columns]
    data = brand_df[available].to_dict('records')
    return jsonify({'data': data, 'brands': ALL_BRANDS})

@app.route('/api/topics')
def api_topics():
    brand_filter = request.args.get('brand')
    if brand_filter:
        brand_kw = kw_df[kw_df['品牌'] == brand_filter].head(20)
        keywords = [{'word': row['关键词'], 'score': round(row['TF-IDF得分'], 2)}
                    for _, row in brand_kw.iterrows()]
        return jsonify({'brand': brand_filter, 'keywords': keywords})
    # 全量：每个品牌 Top 5 关键词
    all_keywords = {}
    for brand in ALL_BRANDS:
        bk = kw_df[kw_df['品牌'] == brand].head(5)
        all_keywords[brand] = [{'word': row['关键词'], 'score': round(row['TF-IDF得分'], 2)}
                               for _, row in bk.iterrows()]
    return jsonify({'topics': LDA_TOPICS, 'keywords': all_keywords, 'brands': ALL_BRANDS})

@app.route('/api/clustering')
def api_clustering():
    # 品牌×聚类 交叉数据（模拟）
    brand_cluster = []
    for _, row in brand_df.iterrows():
        brand_cluster.append({
            'brand': row['品牌'],
            'cluster': int(row['主流聚类']),
            'count': int(row['商品数']),
        })
    return jsonify({
        'clusters': CLUSTER_DATA,
        'best_k': 4,
        'brand_cluster': brand_cluster,
        'brands': ALL_BRANDS,
    })

@app.route('/api/brands')
@app.route('/api/brands/compare')
def api_brands():
    b1 = request.args.get('b1')
    b2 = request.args.get('b2')
    if b1 and b2:
        r1 = brand_df[brand_df['品牌'] == b1].iloc[0]
        r2 = brand_df[brand_df['品牌'] == b2].iloc[0]
        k1 = kw_df[kw_df['品牌'] == b1].head(10)[['关键词', 'TF-IDF得分']].to_dict('records')
        k2 = kw_df[kw_df['品牌'] == b2].head(10)[['关键词', 'TF-IDF得分']].to_dict('records')
        return jsonify({
            'brand1': r1.to_dict(),
            'brand2': r2.to_dict(),
            'keywords1': k1,
            'keywords2': k2,
        })
    # 全量排名数据
    data = brand_df.to_dict('records')
    return jsonify({'data': data, 'brands': ALL_BRANDS})

@app.route('/api/models')
def api_models():
    return jsonify(MODEL_DATA)

# ================================================================
# 启动（兼容本地开发 & Render 生产环境）
# ================================================================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5050))
    debug = os.environ.get('FLASK_DEBUG', 'true').lower() == 'true'
    print("✨ 美妆品牌分析仪表板启动中...")
    print(f"   品牌数: {len(ALL_BRANDS)} | 数据就绪")
    print(f"   http://localhost:{port}")
    app.run(debug=debug, host='0.0.0.0', port=port)
