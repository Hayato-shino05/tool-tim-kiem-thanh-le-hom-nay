from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import AsyncImage
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
import requests
from datetime import datetime

# API Key và URL
API_KEY = "AIzaSyC14GlOtrF7XScPuBLRhsoG6AVOqquA60U"
BASE_URL = "https://www.googleapis.com/youtube/v3/search"

class VideoSearchApp(App):
    def build(self):
        # Thiết lập kích thước cửa sổ (điển hình cho Android TV)
        Window.size = (1920, 1080)
        Window.clearcolor = (0, 0, 0, 1)  # Nền đen cho giao diện TV

        # Bố cục chính
        self.root_layout = BoxLayout(orientation='vertical')

        # Header chứa thanh tìm kiếm
        self.header = BoxLayout(size_hint_y=0.1, padding=10, spacing=10)
        self.search_input = TextInput(hint_text="Nhập từ khóa tìm kiếm", multiline=False, size_hint_x=0.8)
        self.search_button = Button(text="Tìm kiếm", size_hint_x=0.2, on_press=self.search_videos)
        self.header.add_widget(self.search_input)
        self.header.add_widget(self.search_button)

        # Danh sách video cuộn được
        self.scroll_view = ScrollView()
        self.video_list = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.video_list.bind(minimum_height=self.video_list.setter('height'))
        self.scroll_view.add_widget(self.video_list)

        self.root_layout.add_widget(self.header)
        self.root_layout.add_widget(self.scroll_view)

        # Tìm kiếm mặc định
        self.default_keyword = f"thánh lễ trực tuyến hôm nay {datetime.now().strftime('%d-%m-%Y')}"
        self.perform_search(self.default_keyword)

        return self.root_layout

    def search_videos(self, instance):
        keyword = self.search_input.text.strip()
        if keyword:
            self.perform_search(keyword)

    def perform_search(self, keyword):
        params = {
            "key": API_KEY,
            "q": keyword,
            "part": "snippet",
            "type": "video",
            "maxResults": 10,
            "order": "date",
        }

        try:
            response = requests.get(BASE_URL, params=params)
            response.raise_for_status()
            results = response.json()

            self.display_videos(results.get("items", []), keyword)

        except requests.exceptions.RequestException as e:
            self.show_popup("Lỗi", f"Không thể kết nối với API YouTube: {e}")

    def display_videos(self, videos, keyword):
        self.video_list.clear_widgets()
        if not videos:
            self.show_popup("Không có kết quả", "Không tìm thấy video nào.")
            return

        for item in videos:
            video_id = item.get("id", {}).get("videoId")
            snippet = item.get("snippet", {})

            if not video_id or not snippet:
                continue

            title = snippet.get("title", "Chưa có tiêu đề")
            thumbnail_url = snippet.get("thumbnails", {}).get("high", {}).get("url")
            description = snippet.get("description", "Không có mô tả.")

            video_url = f"https://www.youtube.com/watch?v={video_id}"

            video_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=150, padding=10)
            
            if thumbnail_url:
                thumbnail = AsyncImage(source=thumbnail_url, size_hint_x=0.3)
                video_box.add_widget(thumbnail)

            info_box = BoxLayout(orientation='vertical', padding=5)
            info_box.add_widget(Label(text=title, font_size=20, size_hint_y=0.6, color=(1, 1, 1, 1)))
            info_box.add_widget(Label(text=description[:100] + "...", font_size=16, size_hint_y=0.4, color=(0.8, 0.8, 0.8, 1)))

            play_button = Button(text="Phát", size_hint_x=0.2, on_press=lambda instance, url=video_url: self.open_video(url))
            video_box.add_widget(info_box)
            video_box.add_widget(play_button)

            self.video_list.add_widget(video_box)

    def open_video(self, url):
        import webbrowser
        webbrowser.open(url)

    def show_popup(self, title, message):
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        popup_layout.add_widget(Label(text=message, font_size=18, color=(1, 1, 1, 1)))
        close_button = Button(text="Đóng", size_hint_y=0.2, on_press=lambda instance: popup.dismiss())
        popup_layout.add_widget(close_button)
        
        popup = Popup(title=title, content=popup_layout, size_hint=(0.8, 0.4))
        popup.open()

if __name__ == '__main__':
    VideoSearchApp().run()
