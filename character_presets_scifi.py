# character_presets_scifi.py

def get_scifi_presets(negative_prompt):
    """获取科幻感动漫预设角色"""
    return {
        # ========== 原创/通用科幻角色 ==========
        "赛博朋克战士": {
            "prompt": "masterpiece, best quality, very aesthetic, 1girl, cyberpunk warrior, neon light, rainy city, mechanical arm, high-tech armor, future, cybernetic implants, glowing eyes, action pose",
            "negative": negative_prompt,
            "description": "赛博朋克风格，霓虹灯，机械臂，未来战士"
        },
        "义体人-素子风格": {
            "prompt": "masterpiece, best quality, very aesthetic, 1girl, ghost in the shell style, major motoko kusanagi, short purple hair, cybernetic body, tactical gear, futuristic city, dark atmosphere, strong presence",
            "negative": negative_prompt,
            "description": "致敬《攻壳机动队》草薙素子，义体人，战术装备"
        },
        "机械姬": {
            "prompt": "masterpiece, best quality, very aesthetic, 1girl, android, cyborg, elegant mechanical design, translucent panels, futuristic white and blue color scheme, humanoid robot, detailed mechanics",
            "negative": negative_prompt,
            "description": "仿生机器人，优雅的机械设计，未来科技感"
        },
        "星际牛仔": {
            "prompt": "masterpiece, best quality, very aesthetic, 1boy, space cowboy, futuristic bounty hunter, laser gun, starry background, spaceship, worn-out jacket, confident smile, sci-fi",
            "negative": negative_prompt,
            "description": "星际赏金猎人，太空牛仔风格"
        },
        "废土机械师": {
            "prompt": "masterpiece, best quality, very aesthetic, 1girl, wasteland mechanic, post-apocalyptic, welding goggles, metal armor, rusty tools, desert background, strong, resilient",
            "negative": negative_prompt,
            "description": "废土风格，机械师，末日生存者"
        },
        "虚拟偶像": {
            "prompt": "masterpiece, best quality, very aesthetic, 1girl, virtual idol, hologram, neon stage, cyberpunk city, futuristic concert, glowing hair, translucent dress, digital art",
            "negative": negative_prompt,
            "description": "全息虚拟偶像，赛博演唱会"
        },
        "神盾局特工": {
            "prompt": "masterpiece, best quality, very aesthetic, 1girl, S.H.I.E.L.D. agent, tactical suit, high-tech gadgets, spy, confident, aiming gun, helicarrier background, marvel style",
            "negative": negative_prompt,
            "description": "神盾局特工，高科技装备"
        },
        # ========== 更多角色可按需添加 ==========
    }