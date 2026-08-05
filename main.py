import discord
from discord.ext import commands
import yt_dlp
import os
import requests

# ตั้งค่าสิทธิ์ของบอท
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'บอทออนไลน์แล้วในชื่อ: {bot.user}')

def upload_to_gofile(file_path):
    """ฟังก์ชันอัปโหลดไฟล์ไปที่ Gofile เพื่อเอาสปีดสูงสุด"""
    try:
        # 1. ขอความช่วยเหลือหาเซิร์ฟเวอร์ที่เร็วที่สุดจาก Gofile
        server_resp = requests.get('https://api.gofile.io/servers').json()
        if server_resp['status'] != 'ok':
            return None
        
        server_name = server_resp['data']['servers'][0]['name']
        upload_url = f'https://{server_name}.gofile.io/contents/uploadfile'
        
        # 2. อัปโหลดไฟล์
        with open(file_path, 'rb') as f:
            upload_resp = requests.post(upload_url, files={'file': f}).json()
            
        if upload_resp['status'] == 'ok':
            return upload_resp['data']['downloadPage']
        return None
    except Exception as e:
        print(f"Upload error: {e}")
        return None

@bot.command()
async def โหลด(ctx, url: str):
    await ctx.send("⏳ **กำลังดาวน์โหลด...**")
    
    output_filename = 'downloaded_video.mp4'

    # ลบไฟล์เก่าถ้ามีค้างอยู่
    if os.path.exists(output_filename):
        os.remove(output_filename)

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': output_filename,
        'merge_output_format': 'mp4',
    }

    try:
        # 1. โหลดวิดีโอด้วย yt-dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        if os.path.exists(output_filename):
            await ctx.send("🚀 **กำลังอัปโหลด...**")
            
            # 2. ส่งขึ้น Gofile
            download_link = upload_to_gofile(output_filename)
            
            # ลบไฟล์ออกจากคอมเพื่อเคลียร์พื้นที่
            os.remove(output_filename)

            if download_link:
                await ctx.send(f"✅ **เสร็จเรียบร้อย!** \n🔗** ลิงก์ดาวน์โหลด**: {download_link}")
            else:
                await ctx.send("❌ อัปโหลดขึ้นเว็บฝากไฟล์ไม่สำเร็จ")
        else:
            await ctx.send("❌ ไม่พบไฟล์วิดีโอ")
            
    except Exception as e:
        await ctx.send(f"❌ เกิดข้อผิดพลาด: {e}")

import os

bot.run(os.environ.get("DISCORD_TOKEN"))