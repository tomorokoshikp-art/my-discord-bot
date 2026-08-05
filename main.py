import os
import requests
import discord
from discord.ext import commands
import yt_dlp

# --- ส่วนจัดการ YouTube Cookies สำหรับ Render ---
cookies_content = os.environ.get("YOUTUBE_COOKIES")
cookie_file_path = "cookie.txt"

if cookies_content:
    with open(cookie_file_path, "w", encoding="utf-8") as f:
        f.write(cookies_content)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"บอทออนไลน์แล้วในชื่อ: {bot.user}")


def upload_to_gofile(file_path):
    try:
        server_resp = requests.get("https://api.gofile.io/servers").json()
        if server_resp.get("status") != "ok":
            return None

        server_name = server_resp["data"]["servers"][0]["name"]
        upload_url = f"https://{server_name}.gofile.io/contents/uploadfile"

        with open(file_path, "rb") as f:
            upload_resp = requests.post(upload_url, files={"file": f}).json()

        if upload_resp.get("status") == "ok":
            return upload_resp["data"]["downloadPage"]
        return None
    except Exception as e:
        print(f"Upload error: {e}")
        return None


@bot.command()
async def โหลด(ctx, url: str):
    await ctx.send("⏳ **กำลังดาวน์โหลด...**")

    output_filename = "downloaded_video.mp4"

    if os.path.exists(output_filename):
        os.remove(output_filename)

    # ตั้งค่า yt-dlp Options บังคับใช้ client ios และ android_creator เลี่ยง PO Token
    ydl_opts = {
        "format": "b/best",
        "outtmpl": output_filename,
        "cookiefile": (
            cookie_file_path if os.path.exists(cookie_file_path) else None
        ),
        "extractor_args": {
            "youtube": {
                "player_client": ["ios", "android_creator", "mweb"],
            }
        },
        "check_formats": None,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if os.path.exists(output_filename):
            await ctx.send("🚀 **กำลังอัปโหลด...**")
            download_link = upload_to_gofile(output_filename)
            os.remove(output_filename)

            if download_link:
                await ctx.send(
                    f"✅ **เสร็จเรียบร้อย!** \n🔗** ลิงก์ดาวน์โหลด**: {download_link}"
                )
            else:
                await ctx.send("❌ อัปโหลดขึ้นเว็บฝากไฟล์ไม่สำเร็จ")
        else:
            await ctx.send("❌ ไม่พบไฟล์วิดีโอ")

    except Exception as e:
        await ctx.send(f"❌ เกิดข้อผิดพลาด: {e}")


bot.run(os.environ.get("DISCORD_TOKEN"))
