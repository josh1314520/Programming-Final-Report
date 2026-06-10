import urllib.request
import xml.etree.ElementTree as ET
from flask import Blueprint, render_template, request, jsonify
from app.models.task import check_news_read, record_news_task

news_bp = Blueprint('news', __name__)

def fetch_yahoo_finance_news():
    """從 Yahoo Finance RSS 抓取新聞"""
    url = "https://finance.yahoo.com/news/rssindex"
    news_list = []
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            
            # RSS 的項目放在 channel 底下
            for item in root.findall('./channel/item')[:10]: # 只取前 10 篇
                title = item.find('title').text if item.find('title') is not None else 'No Title'
                link = item.find('link').text if item.find('link') is not None else '#'
                pubDate = item.find('pubDate').text if item.find('pubDate') is not None else ''
                
                news_list.append({
                    'title': title,
                    'link': link,
                    'pubDate': pubDate
                })
    except Exception as e:
        print(f"Failed to fetch news: {e}")
        # 如果失敗，回傳一組預設新聞
        news_list = [
            {'title': '市場動態：今日股市創新高', 'link': 'https://finance.yahoo.com/', 'pubDate': 'Today'},
            {'title': '避險基金如何佈局下一季？', 'link': 'https://finance.yahoo.com/', 'pubDate': 'Today'}
        ]
        
    return news_list

@news_bp.route('/news')
def news_page():
    # 預設使用者 ID 為 1
    adventurer_id = 1
    news_items = fetch_yahoo_finance_news()
    
    # 檢查每篇新聞是否已閱讀
    for item in news_items:
        item['is_read'] = check_news_read(adventurer_id, item['link'])
        
    return render_template('news.html', news_items=news_items)

@news_bp.route('/api/news/read', methods=['POST'])
def read_news():
    adventurer_id = 1
    data = request.get_json()
    
    if not data or 'news_url' not in data:
        return jsonify({'success': False, 'message': 'Missing news_url'}), 400
        
    news_url = data['news_url']
    
    # 檢查是否已閱讀
    if check_news_read(adventurer_id, news_url):
        return jsonify({'success': False, 'message': '已經領取過此新聞的獎勵了！'})
        
    # 發放獎勵
    reward = 50
    success = record_news_task(adventurer_id, news_url, reward)
    
    if success:
        return jsonify({'success': True, 'reward': reward, 'message': f'恭喜！獲得 {reward} 點資產加成！'})
    else:
        return jsonify({'success': False, 'message': '系統發生錯誤，無法發放獎勵。'}), 500
