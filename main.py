import flet as ft
import json
import urllib.request
import urllib.error

def fetch_json_from_url(url):
    try:
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.URLError as e:
        print(f"Error fetching data: {e}")
        return None

def load_area_data():
    url = "https://www.jma.go.jp/bosai/common/const/area.json"
    return fetch_json_from_url(url)

def load_weather_data(area_code):
    url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json"
    return fetch_json_from_url(url)

def create_area_mapping(data):
    code_to_name = {}
    if data and isinstance(data, dict):
        offices = data.get("offices", {})
        for code, info in offices.items():
            code_to_name[code] = info.get("name", "不明")
    return code_to_name

def main(page: ft.Page):
    page.title = "Weather Areas"
    page.window.width = 1500
    page.window.height = 1000
    page.padding = 0

    area_data = load_area_data()
    if not area_data:
        page.add(ft.Text("エリアデータの読み込みに失敗しました"))
        return

    code_to_name = create_area_mapping(area_data)
    
    # サイドバーの作成
    left_panel = ft.Column(
        controls=[],
        width=300,
        scroll=ft.ScrollMode.AUTO,
        spacing=10,
        height=page.window.height,
    )
    
    for center_key, center_value in area_data.get("centers", {}).items():
        expansion_tile = ft.ExpansionTile(
            title=ft.Text(center_value["name"]),
            subtitle=ft.Text(center_value.get("enName", "")),
            trailing=ft.Icon(ft.icons.ARROW_DROP_DOWN),
            collapsed_text_color=ft.colors.GREEN,
            text_color=ft.colors.GREEN,
            controls=[]
        )

        for child in center_value.get("children", []):
            area_name = code_to_name.get(child, f"Area {child}")
            expansion_tile.controls.append(
                ft.ListTile(
                    title=ft.Text(f"{area_name} ({child})"),
                    on_click=lambda e, code=child: show_weather_data(e, code)
                )
            )
        left_panel.controls.append(expansion_tile)

    # メインコンテンツエリアの作成
    right_panel = ft.Column(
        controls=[
            ft.Text("地域を選択すると天気データが表示されます", size=24)
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        spacing=10,
    )

    def show_weather_data(e, area_code):
        weather_data = load_weather_data(area_code)
        if weather_data:
            right_panel.controls = [
                ft.Text(f"エリアコード {area_code} の天気情報:", size=24),
                ft.Text(json.dumps(weather_data, indent=2, ensure_ascii=False))
            ]
        else:
            right_panel.controls = [
                ft.Text("天気データの取得に失敗しました", size=24)
            ]
        page.update()

    # 固定サイドバーとスクロール可能なメインコンテンツを含むレイアウト
    layout = ft.Row(
        controls=[
            # 固定サイドバー
            ft.Container(
                content=left_panel,
                border=ft.border.all(1, ft.colors.GREY_400),
                padding=10,
                height=page.window.height,
            ),
            # スクロール可能なメインコンテンツ
            ft.Container(
                content=right_panel,
                expand=True,
                border=ft.border.all(1, ft.colors.GREY_400),
                padding=10,
                height=page.window.height,
            ),
        ],
        spacing=0,
        height=page.window.height,
    )

    page.add(layout)
    page.update()

ft.app(target=main)