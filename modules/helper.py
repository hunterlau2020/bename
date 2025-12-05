# -*- coding: utf-8 -*-
"""
帮助模块 - 提供使用指导和经纬度查询方法
"""


class Helper:
    """帮助信息类"""
    
    @staticmethod
    def show_help():
        """显示帮助信息"""
        help_text = """
姓名测试软件使用说明
===================
使用方法: python bazi.py [选项]

选项:
  -h, --help     显示帮助信息
  -t, --test     开始姓名测试
  -v, --version  显示版本信息
  --reload-data  重新加载资源数据

经纬度查询方法:
八字排盘需精确到出生地级市或县，因为经度每差1度，地方时相差约4分钟。

1. 国家地理信息公共服务平台（天地图）
   网址：https://www.tianditu.gov.cn

2. 高德地图 / 百度地图（网页版或App）
   高德地图：https://www.amap.com
   搜索城市名后，URL 或页面信息中会包含经纬度（高德格式为 lng,lat）
   百度地图：https://map.baidu.com

3. 维基百科（Wikipedia）
   搜索 "[城市名] 维基百科"，如"广州 维基百科"
   在右侧信息栏中通常会列出 "坐标"，点击可查看十进制度或度分秒格式。

经纬度格式: 十进制度数，如 113.2644 (东经), 23.1291 (北纬)

示例:
  python bazi.py --test          # 开始姓名测试
  python bazi.py --reload-data   # 重新加载资源数据
  python bazi.py --version       # 查看版本信息
"""
        print(help_text)
