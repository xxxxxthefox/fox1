import json
import cloudscraper
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ----- دالة لجلب بيانات تيك توك -----
def fetch_tiktok_data(username):
    try:
        scraper = cloudscraper.create_scraper()
        url = f"https://www.tiktok.com/@{username}"
        response = scraper.get(url, headers={"User-Agent": "Mozilla/5.0"})

        if response.status_code != 200:
            return {"username": username, "error": f"HTTP {response.status_code}"}

        soup = BeautifulSoup(response.text, 'html.parser')
        script_tag = soup.find('script', id='__UNIVERSAL_DATA_FOR_REHYDRATION__')
        if not script_tag:
            return {"username": username, "error": "بيانات الحساب غير متاحة"}

        data = json.loads(script_tag.text)
        user_info = data['__DEFAULT_SCOPE__']['webapp.user-detail']['userInfo']
        user = user_info['user']
        stats = user_info['stats']

        return {
            "username": username,
            "display_name": user.get('nickname', 'لا يوجد'),
            "bio": user.get('signature', 'لا يوجد'),
            "region": user.get('region', 'IQ'),
            "verified": user.get('verified', False),
            "profile_url": f"https://www.tiktok.com/@{username}",
            "statistics": {
                "followers_count": stats.get('followerCount', 0),
                "following_count": stats.get('followingCount', 0),
                "likes_count": stats.get('heartCount', 0),
                "videos_count": stats.get('videoCount', 0)
            }
        }
    except Exception as e:
        return {"username": username, "error": str(e)}

# ----- API ليوزر واحد -----
@app.route("/api/tiktok/profile", methods=["GET"])
def api_tiktok_profile():
    username = request.args.get("username")
    if not username:
        return jsonify({
            "status": "error",
            "message": "يجب إرسال ?username=اسم_المستخدم"
        }), 400

    data = fetch_tiktok_data(username)
    return jsonify({
        "status": "success",
        "profile": data
    })

# ----- صفحة رئيسية -----
@app.route("/")
def home():
    return "🚀 TikTok Profile API Running!"

# ----- تشغيل السيرفر -----
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)