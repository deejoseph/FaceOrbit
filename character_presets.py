# character_presets.py - 预设角色库
# 独立维护，添加/修改角色不影响主程序

def get_character_presets(negative_prompt):
    """获取所有预设角色
    Args:
        negative_prompt: 基础负向提示词
    Returns:
        dict: 角色名称到角色数据的映射
    """
    return {
        # ========== 男生角色 ==========
        "火影忍者 - 漩涡鸣人": {
            "prompt": "masterpiece, best quality, very aesthetic, 1boy, Naruto Uzumaki, naruto, blonde spiky hair, blue eyes, whisker marks, orange jumpsuit, ninja headband, shuriken, confident smile, action pose, konoha village background",
            "negative": negative_prompt + ", deformed, ugly, bad anatomy",
            "description": "金色刺猬头、蓝色眼睛、胡须纹、橙色连体衣、木叶护额"
        },
        "火影忍者 - 宇智波佐助": {
            "prompt": "masterpiece, best quality, very aesthetic, 1boy, Sasuke Uchiha, naruto, black hair, black eyes, sharingan, dark blue shirt, white shorts, ninja headband, cold expression, standing, uchiha clan symbol",
            "negative": negative_prompt + ", deformed, ugly, bad anatomy",
            "description": "黑色刺猬头、写轮眼、深蓝色上衣、白色短裤"
        },
        "海贼王 - 蒙奇·D·路飞": {
            "prompt": "masterpiece, best quality, very aesthetic, 1boy, Monkey D Luffy, one piece, black hair, straw hat, red vest, blue shorts, sandals, scar on chest, big smile, rubber powers, sunny background",
            "negative": negative_prompt + ", deformed, ugly, bad anatomy",
            "description": "黑色短发、草帽、红色马甲、蓝色短裤、胸前伤疤"
        },
        "海贼王 - 索隆": {
            "prompt": "masterpiece, best quality, very aesthetic, 1boy, Roronoa Zoro, one piece, green hair, bandana, haramaki, three swords, demon aura, muscular, serious expression, dojo background",
            "negative": negative_prompt + ", deformed, ugly, bad anatomy",
            "description": "绿色头发、头巾、三刀流、严肃表情"
        },
        "咒术回战 - 五条悟": {
            "prompt": "masterpiece, best quality, very aesthetic, 1boy, Gojo Satoru, jujutsu kaisen, white hair, blindfold, black suit, infinity, six eyes, smug smile, jujutsu high background",
            "negative": negative_prompt + ", deformed, ugly, bad anatomy",
            "description": "白发、眼罩、黑色西装、六眼"
        },
        "鬼灭之刃 - 灶门炭治郎": {
            "prompt": "masterpiece, best quality, very aesthetic, 1boy, Kamado Tanjiro, demon slayer, dark red hair, scar on forehead, hanafuda earrings, green checkered haori, water breathing, determined expression",
            "negative": negative_prompt + ", deformed, ugly, bad anatomy",
            "description": "深红色头发、额头伤疤、花牌耳饰、绿色格子羽织"
        },
        "进击的巨人 - 利威尔兵长": {
            "prompt": "masterpiece, best quality, very aesthetic, 1boy, Levi Ackerman, attack on titan, black hair, undercut, cravat, survey corps uniform, ODM gear, cold eyes, cleaning, titan background",
            "negative": negative_prompt + ", deformed, ugly, bad anatomy",
            "description": "黑色短发、领巾、调查兵团制服、立体机动装置"
        },
        "死神 - 黑崎一护": {
            "prompt": "masterpiece, best quality, very aesthetic, 1boy, Ichigo Kurosaki, bleach, orange hair, substitute shinigami badge, zangetsu, bankai, hollow mask, soul reaper uniform, determined",
            "negative": negative_prompt + ", deformed, ugly, bad anatomy",
            "description": "橙色头发、斩魄刀、代理死神徽章"
        },

        # ========== 女生角色 ==========
        "火影忍者 - 春野樱": {
            "prompt": "masterpiece, best quality, very aesthetic, 1girl, Haruno Sakura, naruto, pink hair, green eyes, forehead protector, red qipao, black gloves, medical ninja, strong pose, konoha village",
            "negative": negative_prompt + ", deformed, ugly, bad anatomy",
            "description": "粉色短发、绿色眼睛、红色旗袍、医疗忍者"
        },
        "火影忍者 - 日向雏田": {
            "prompt": "masterpiece, best quality, very aesthetic, 1girl, Hyuga Hinata, naruto, long dark blue hair, lavender eyes, pale purple jacket, shy expression, byakugan, gentle smile, konoha village",
            "negative": negative_prompt + ", deformed, ugly, bad anatomy",
            "description": "深蓝色长发、淡紫色眼睛、白色外衣、害羞表情"
        },
        "鬼灭之刃 - 灶门祢豆子": {
            "prompt": "masterpiece, best quality, very aesthetic, 1girl, Kamado Nezuko, demon slayer, long black hair, pink ribbon, bamboo mouthpiece, pink kimono, demon form, sleeping in box, cute expression",
            "negative": negative_prompt + ", deformed, ugly, bad anatomy",
            "description": "黑色长发、粉色丝带、竹筒嘴、粉色和服"
        },
        "鬼灭之刃 - 蝴蝶忍": {
            "prompt": "masterpiece, best quality, very aesthetic, 1girl, Shinobu Kocho, demon slayer, purple eyes, black hair with purple tips, butterfly haori, insect breathing, gentle smile, wisteria flowers",
            "negative": negative_prompt + ", deformed, ugly, bad anatomy",
            "description": "紫色眼睛、黑紫色渐变发尾、蝴蝶羽织、虫之呼吸"
        },
        "原神 - 胡桃": {
            "prompt": "masterpiece, best quality, very aesthetic, 1girl, Hu Tao, genshin impact, dark brown hair, twintails, red eyes, witch hat, ghost companion, cheerful, mischievous smile",
            "negative": negative_prompt + ", deformed, ugly, bad anatomy",
            "description": "棕色双马尾、红色眼睛、巫师帽、幽灵伙伴"
        },
        "原神 - 刻晴": {
            "prompt": "masterpiece, best quality, very aesthetic, 1girl, Keqing, genshin impact, purple hair, twintails, lightning element, sword, cat ear hair, confident expression, liyue background",
            "negative": negative_prompt + ", deformed, ugly, bad anatomy",
            "description": "紫色双马尾、雷元素、剑、猫耳发型"
        },
        "原神 - 纳西妲": {
            "prompt": "masterpiece, best quality, very aesthetic, 1girl, Nahida, genshin impact, white hair, green eyes, small stature, dendro element, radish theme, flower crown, floating, dreamy, sumeru",
            "negative": negative_prompt + ", deformed, ugly, bad anatomy, mature",
            "description": "白发、绿色眼睛、草神、小吉祥草王"
        },
        "Fate - 阿尔托莉雅 (Saber)": {
            "prompt": "masterpiece, best quality, very aesthetic, 1girl, Artoria Pendragon, fate, blonde hair, blue eyes, ahoge, invisible sword, armor, blue dress, kingly aura, serious expression, castle background",
            "negative": negative_prompt + ", deformed, ugly, bad anatomy",
            "description": "金色头发、蓝色眼睛、呆毛、铠甲、王者气质"
        },
        "EVA - 绫波丽": {
            "prompt": "masterpiece, best quality, very aesthetic, 1girl, Rei Ayanami, evangelion, pale blue hair, red eyes, white plugsuit, emotionless expression, eva unit, nerv background",
            "negative": negative_prompt + ", deformed, ugly, bad anatomy",
            "description": "淡蓝色头发、红色眼睛、白色驾驶服、无表情"
        },
        "间谍过家家 - 约尔·福杰": {
            "prompt": "masterpiece, best quality, very aesthetic, 1girl, Yor Forger, spy x family, long black hair, red eyes, black dress, stiletto, assassin, elegant pose",
            "negative": negative_prompt + ", deformed, ugly, bad anatomy",
            "description": "黑色长发、红色眼睛、黑色连衣裙、杀手"
        },

        # ========== Z世代热门角色 ==========
        "VOCALOID - 初音未来": {
            "prompt": "masterpiece, best quality, very aesthetic, 1girl, Hatsune Miku, vocaloid, long turquoise hair, twintails, black hair ties, turquoise eyes, school uniform, leek, singing on stage, neon lights, virtual singer, cyber, newest",
            "negative": negative_prompt + ", deformed, ugly, bad anatomy",
            "description": "蓝绿色双马尾、葱、虚拟歌姬"
        },
        "BanG Dream - 高松灯": {
            "prompt": "masterpiece, best quality, very aesthetic, 1girl, Takamatsu Tomori, bang dream mygo, gray hair, pink eyes, short hair, asymmetrical bangs, hoodie, sneakers, penguin band-aid, shy expression, holding notebook, school uniform, starlight",
            "negative": negative_prompt + ", deformed, ugly, bad anatomy, smiling",
            "description": "灰色短发、粉色眼睛、企鹅创可贴"
        },
        "BanG Dream - 千早爱音": {
            "prompt": "masterpiece, best quality, very aesthetic, 1girl, Chihaya Anon, bang dream mygo, pink hair, pink eyes, twin tails, cute, fashionable, school uniform, guitar, confident smile, social butterfly",
            "negative": negative_prompt + ", deformed, ugly, bad anatomy",
            "description": "粉色双马尾、吉他、社交达人"
        },
        "孤独摇滚 - 后藤一里": {
            "prompt": "masterpiece, best quality, very aesthetic, 1girl, Hitori Gotoh, bocchi the rock, pink hair, yellow hair accessory, school uniform, guitar, shy expression, sitting in box, introvert",
            "negative": negative_prompt + ", deformed, ugly, bad anatomy, confident",
            "description": "粉色长发、吉他、小孤独"
        },
        "间谍过家家 - 安妮亚": {
            "prompt": "masterpiece, best quality, very aesthetic, 1girl, Anya Forger, spy x family, pink hair, green eyes, black dress, white collar, school uniform, cute face, telepath, peanuts, smiling",
            "negative": negative_prompt + ", deformed, ugly, bad anatomy, mature, grown up",
            "description": "粉色头发、绿色眼睛、读心术、花生"
        },
        "星穹铁道 - 卡芙卡": {
            "prompt": "masterpiece, best quality, very aesthetic, 1girl, Kafka, honkai star rail, purple hair, sunglasses, spider theme, elegant mature woman, leather coat, confident smile",
            "negative": negative_prompt + ", deformed, ugly, bad anatomy",
            "description": "紫色头发、墨镜、蜘蛛主题"
        },

        # ========== 原创/风格角色 ==========
        "新海诚风格 - 原创角色": {
            "prompt": "masterpiece, best quality, very aesthetic, 1girl, shinkai style, makoto shinkai, your name style, realistic background, clouds, sunset, beautiful sky, emotional, detailed",
            "negative": negative_prompt + ", deformed, ugly, bad anatomy",
            "description": "新海诚电影风格：真实系背景、美丽天空、情感氛围"
        },
        "原创角色 - 魔女": {
            "prompt": "masterpiece, best quality, very aesthetic, 1girl, witch, original, purple eyes, witch hat, black robe, magic staff, starry night, magical girl, cute",
            "negative": negative_prompt + ", deformed, ugly, bad anatomy",
            "description": "原创角色：魔女、紫色眼睛、魔女帽"
        },
        "原创角色 - 骑士": {
            "prompt": "masterpiece, best quality, very aesthetic, 1girl, knight, original, silver armor, long hair, sword and shield, determined expression, castle background, fantasy",
            "negative": negative_prompt + ", deformed, ugly, bad anatomy",
            "description": "原创角色：骑士、银色铠甲、剑与盾"
        }
    }