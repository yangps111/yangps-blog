#!/usr/bin/env python3
"""使用 Playwright 为 Hugo 博客截图"""

from playwright.sync_api import sync_playwright
import time

def take_screenshots():
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(headless=True)
        
        # 创建页面并设置窗口大小
        page = browser.new_page(viewport={'width': 1440, 'height': 900})
        
        # 截图首页
        print("正在访问首页 http://localhost:1313/zh/ ...")
        page.goto('http://localhost:1313/zh/', wait_until='networkidle')
        time.sleep(1)  # 等待页面完全渲染
        
        # 保存首页截图
        page.screenshot(path='/Users/Zhuanz/Desktop/my-blog/preview-home.png', full_page=True)
        print("✅ 首页截图已保存: /Users/Zhuanz/Desktop/my-blog/preview-home.png")
        
        # 截图文章页面
        print("正在访问文章页面 http://localhost:1313/zh/p/hello-world/ ...")
        page.goto('http://localhost:1313/zh/p/hello-world/', wait_until='networkidle')
        time.sleep(1)  # 等待页面完全渲染
        
        # 保存文章页截图
        page.screenshot(path='/Users/Zhuanz/Desktop/my-blog/preview-article.png', full_page=True)
        print("✅ 文章页截图已保存: /Users/Zhuanz/Desktop/my-blog/preview-article.png")
        
        browser.close()
        print("\n🎉 所有截图已完成！")

if __name__ == '__main__':
    take_screenshots()
