import os
import glob
import requests
import json
from bs4 import BeautifulSoup


############################################################
#                      需要用到的函数
############################################################

# 函数：下载API网址
def download_webpage(url, output_file):
    try:
        # 发送HTTP GET请求
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"})

        # 检查请求是否成功
        if response.status_code == 200:
            # 将内容保存到文件
            with open(output_file, "w", encoding="utf-8") as file:
                file.write(response.text)
            print(f"网页已成功保存到 {output_file}")
        else:
            print(f"请求失败，状态码：{response.status_code}")
    except Exception as e:
        print(f"发生错误：{e}")

# 函数：评分排名
def classify_rating(rating):
    if rating >= 7.2:
        return "超模真神"
    elif 7.2 > rating >= 3.8:
        return "版本强势"
    elif 3.8 > rating >= 1.2:
        return "中规中矩"
    elif 1.2 > rating > 0:
        return "环境低谷"
    else:
        return "史"

# 函数：格式化卡牌名称
def format_card_name(name):
    return name.replace(" ", "-").replace(" Evolution", "-Evolution").lower()

# 函数：获取卡牌图片链接
def get_icon_url(formatted_name):
    # 逆向转换格式
    display_name = formatted_name.replace("-evolution", " Evolution").replace("-", " ").title()
    
    # 精确匹配逻辑
    for item in api_data["items"] + api_data["supportItems"]:
        item_name_clean = item["name"].lower().replace("-", " ")
        display_name_clean = display_name.lower().replace("-", " ")
        
        base_match = item_name_clean == display_name_clean
        evo_match = f"{item_name_clean} evolution" == display_name_clean
        
        if evo_match and "evolutionMedium" in item["iconUrls"]:
            return item["iconUrls"]["evolutionMedium"]
        elif base_match:
            return item["iconUrls"]["medium"]
    
    # 模糊匹配逻辑
    clean_name = formatted_name.replace("-ev1", "").split("-")[0]
    clean_name_processed = clean_name.replace("-", " ")
    for item in api_data["items"] + api_data["supportItems"]:
        item_name_clean = item["name"].lower().replace("-", " ")
        if clean_name_processed in item_name_clean:
            return item["iconUrls"].get("evolutionMedium", item["iconUrls"]["medium"])
    
    return "https://api-assets.clashroyale.com/error.png"


############################################################
#                         关键变量
############################################################

# 定义卡牌分级数据
card_data = {
    "超模真神": [],
    "版本强势": [],
    "中规中矩": [],
    "环境低谷": [],
    "史": []
}

# 翻译和修正数数据
Princess_Tower= 0.2
Royal_Towers= 0.4
Regular_Minor_Spells= 0.3
Universal_Major_Spell= 0.5
Unconventional_Spells= 0.9
Universal_cards1= 0.5
Universal_cards2= 0.6
God_of_Change= 0.7
Strict_System_Card= 0.9
Building_The_Core= 0.7
Win_Condition= 1

"""
公主塔：0.2
其余皇家塔楼：0.4

常规小法术（费用<=3）：0.3
泛用型中大法术：0.5
非常规法术：0.9

万金油配件（费用<=3）：0.5
万金油配件（费用=4）：0.6
变化之神：0.7

严格体系卡：0.9

组建核心：0.7
进攻核心：1
"""

translations = {
    "Zap Evolution": ("觉醒小闪", Regular_Minor_Spells),
    "Arrows": ("万箭齐发", Regular_Minor_Spells),
    "Bomber Evolution": ("觉醒投弹兵", Universal_cards1),
    "Little Prince": ("小王子", Universal_cards1),
    "The Log": ("滚木", Regular_Minor_Spells),
    "Poison": ("毒药", Universal_Major_Spell),
    "Skeletons Evolution": ("觉醒小骷髅", Universal_cards1),
    "Royal Ghost": ("皇家幽灵", Universal_cards1),
    "Goblin Drill": ("钻机", Win_Condition),
    "Tesla": ("电塔", Universal_cards2),
    "Bats Evolution": ("觉醒蝙蝠", Strict_System_Card),
    "Knight Evolution": ("觉醒骑士", Universal_cards1),
    "Graveyard": ("墓园", Win_Condition),
    "Guards": ("骷髅守卫", Universal_cards1),
    "Fire Spirit": ("火豆", God_of_Change),
    "Wall Breakers Evolution": ("觉醒炸弹人", Win_Condition),
    "Miner": ("矿工", God_of_Change),
    "Night Witch": ("暗巫", Strict_System_Card),
    "Tornado": ("飓风", Universal_Major_Spell),
    "Ice Spirit": ("冰豆", Universal_cards1),
    "Fireball": ("火球", Universal_Major_Spell),
    "Skeletons": ("小骷髅", Universal_cards1),
    "Giant": ("巨人", Win_Condition),
    "Balloon": ("气球", Win_Condition),
    "Skeleton Dragons": ("骨龙", Universal_cards2),
    "Bandit": ("刺客", Strict_System_Card),
    "Bowler": ("蓝胖", God_of_Change),
    "Elixir Collector": ("采集器", Building_The_Core),
    "Rage": ("狂暴", Regular_Minor_Spells),
    "Archers Evolution": ("觉醒AC", Universal_cards1),
    "Lava Hound": ("天狗", Win_Condition),
    "Bomb Tower": ("炸弹塔", Universal_cards2),
    "Skeleton King": ("骨王", Universal_cards2),
    "Goblin Gang": ("哥布林团伙", Universal_cards1),
    "Fisherman": ("渔夫", Universal_cards1),
    "Mega Minion": ("铁甲", Universal_cards1),
    "Valkyrie Evolution": ("觉醒武神", Universal_cards2),
    "Battle Ram": ("攻城锤", Win_Condition),
    "Baby Dragon": ("龙宝", God_of_Change),
    "Mother Witch": ("女巫婆婆", God_of_Change),
    "Tesla Evolution": ("觉醒电塔", Universal_cards2),
    "Royal Giant Evolution": ("觉醒家驹", Win_Condition),
    "Giant Snowball": ("雪球", Regular_Minor_Spells),
    "Mega Knight": ("超骑", Building_The_Core),
    "Pekka": ("大皮卡", Building_The_Core),
    "Royal Delivery": ("速递", Universal_Major_Spell),
    "Knight": ("骑士", Universal_cards1),
    "Electro Spirit": ("电豆", Universal_cards1),
    "Bomber": ("投弹兵", Universal_cards1),
    "Inferno Dragon": ("地狱龙", Universal_cards2),
    "Golem": ("石头人", Win_Condition),
    "Mighty Miner": ("威猛矿工", Universal_cards2),
    "Dark Prince": ("黑王", Universal_cards2),
    "Skeleton Barrel": ("骨球", Win_Condition),
    "Barbarian Barrel": ("滚筒", Regular_Minor_Spells),
    "Goblins": ("哥布林", Universal_cards1),
    "Barbarians Evolution": ("觉醒黄毛", God_of_Change),
    "Royal Hogs": ("家猪", Win_Condition),
    "Tombstone": ("墓碑", Universal_cards1),
    "Cannon": ("加农炮", Universal_cards1),
    "Mortar Evolution": ("觉醒迫击炮", Win_Condition),
    "Royal Recruits Evolution": ("觉醒卫队", Building_The_Core),
    "Goblin Giant": ("绿胖", Win_Condition),
    "Lightning": ("大闪", Universal_Major_Spell),
    "Valkyrie": ("武神", Universal_cards2),
    "Minion Horde": ("亡灵海", Strict_System_Card),
    "Minions": ("小亡灵", God_of_Change),
    "Goblin Barrel": ("飞桶", Win_Condition),
    "Princess": ("公主", Strict_System_Card),
    "Goblin Cage": ("牢笼", Universal_cards2),
    "Executioner": ("屠夫", Strict_System_Card),
    "Firecracker Evolution": ("觉醒烟花", Strict_System_Card),
    "Elixir Golem": ("水人", Win_Condition),
    "Phoenix": ("凤凰", God_of_Change),
    "Spear Goblins": ("投矛手", Universal_cards1),
    "Magic Archer": ("游侠", Strict_System_Card),
    "Electro Dragon": ("雷龙", Strict_System_Card),
    "Lumberjack": ("樵夫", Strict_System_Card),
    "Flying Machine": ("飞机", Strict_System_Card),
    "Wall Breakers": ("攻城炸弹人", Win_Condition),
    "Archer Queen": ("女皇", God_of_Change),
    "Hog Rider": ("野猪", Win_Condition),
    "Rocket": ("火箭", Strict_System_Card),
    "Inferno Tower": ("地狱塔", God_of_Change),
    "Zap": ("小闪", Regular_Minor_Spells),
    "Sparky": ("电车", Building_The_Core),
    "Mini Pekka": ("小皮卡", God_of_Change),
    "Earthquake": ("地震", God_of_Change),
    "Giant Skeleton": ("骷髅巨人", Building_The_Core),
    "Prince": ("王子", Strict_System_Card),
    "Hunter": ("猎人", God_of_Change),
    "Three Musketeers": ("三枪", Win_Condition),
    "Witch": ("女巫", Strict_System_Card),
    "Golden Knight": ("圣骑", Universal_cards2),
    "Ice Golem": ("冰人", Universal_cards1),
    "Ice Spirit Evolution": ("觉醒冰豆", Universal_cards1),
    "Cannon Cart": ("炮车", God_of_Change),
    "Ram Rider": ("蛮羊", Win_Condition),
    "Ice Wizard": ("冰法", Universal_cards1),
    "Dart Goblin": ("吹箭", Strict_System_Card),
    "Elite Barbarians": ("精锐", Building_The_Core),
    "Mortar": ("迫击炮", Win_Condition),
    "Heal Spirit": ("奶豆", Strict_System_Card),
    "Bats": ("蝙蝠", Strict_System_Card),
    "Musketeer": ("火枪手", God_of_Change),
    "Firecracker": ("烟花", Strict_System_Card),
    "Skeleton Army": ("骷髅海", Strict_System_Card),
    "Freeze": ("冰冻", Strict_System_Card),
    "Electro Wizard": ("电法", God_of_Change),
    "Monk": ("武僧", Strict_System_Card),
    "Battle Healer": ("天使", Strict_System_Card),
    "Battle Ram Evolution": ("觉醒攻城锤", Win_Condition),
    "Electro Giant": ("电胖", Win_Condition),
    "Wizard": ("火法", Strict_System_Card),
    "Zappies": ("小电车", Universal_cards2),
    "Rascals": ("绿林团伙", Strict_System_Card),
    "Clone": ("克隆", Strict_System_Card),
    "Void": ("虚空", Universal_Major_Spell),
    "Wizard Evolution": ("觉醒火法", Strict_System_Card),
    "Archers": ("弓箭手", Universal_cards1),
    "Goblin Drill Evolution": ("觉醒钻机", Win_Condition),
    "Goblin Barrel Evolution": ("觉醒飞桶", Win_Condition),
    "Royal Recruits": ("卫队", Building_The_Core),
    "Goblin Curse": ("诅咒", Strict_System_Card),
    "Royal Giant": ("家驹", Win_Condition),
    "Goblin Giant Evolution": ("觉醒绿胖", Win_Condition),
    "Goblin Demolisher": ("鞭炮", Strict_System_Card),
    "Tower Princess": ("公主塔", Princess_Tower),
    "Goblinstein": ("斯坦", Strict_System_Card),
    "Royal Chef": ("厨师塔", Royal_Towers),
    "P.E.K.K.A Evolution": ("觉醒大皮卡", Building_The_Core),
    "Cannoneer": ("炮塔", Royal_Towers),
    "Electro Dragon Evolution": ("觉醒雷龙", Strict_System_Card),
    "Dagger Duchess": ("刀塔", Royal_Towers),
    "Goblin Cage Evolution": ("觉醒牢笼", Universal_cards2),
    "Mega Knight Evolution": ("觉醒超骑", Building_The_Core),
    "Cannon Evolution": ("觉醒土炮", Universal_cards1),
    "Musketeer Evolution": ("觉醒女枪", God_of_Change),
    "X-Bow": ("连弩", Win_Condition),
    "Giant Snowball Evolution": ("觉醒雪球", Regular_Minor_Spells),
    "Mini P.E.K.K.A": ("小皮卡", God_of_Change),
    "P.E.K.K.A": ("大皮卡", Building_The_Core),
    "Mirror": ("镜像", Strict_System_Card),
    "Suspicious Bush": ("草丛", Win_Condition),
    "Furnace": ("锅炉", Strict_System_Card),
    "Barbarians": ("黄毛", God_of_Change),
    "Barbarian Hut": ("黄毛房", Strict_System_Card),
    "Goblin Machine": ("哥布林机甲", Strict_System_Card),
    "Goblin Hut": ("茅房", Strict_System_Card),
    "Dart Goblin Evolution": ("觉醒吹箭", Strict_System_Card),
    "Rune Giant": ("符文巨人", Strict_System_Card),
    "Lumberjack Evolution": ("觉醒樵夫", God_of_Change),
    "Berserker": ("狂战士", Universal_cards1),
    "Hunter Evolution": ("觉醒猎人", Strict_System_Card),
}


# Api数据
api_data= {
  "items": [
    {
      "name": "Knight",
      "id": 26000000,
      "maxLevel": 14,
      "maxEvolutionLevel": 1,
      "elixirCost": 3,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/jAj1Q5rclXxU9kVImGqSJxa4wEMfEhvwNQ_4jiGUuqg.png",
        "evolutionMedium": "https://api-assets.clashroyale.com/cardevolutions/300/jAj1Q5rclXxU9kVImGqSJxa4wEMfEhvwNQ_4jiGUuqg.png"
      },
      "rarity": "common"
    },
    {
      "name": "Archers",
      "id": 26000001,
      "maxLevel": 14,
      "maxEvolutionLevel": 1,
      "elixirCost": 3,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/W4Hmp8MTSdXANN8KdblbtHwtsbt0o749BbxNqmJYfA8.png",
        "evolutionMedium": "https://api-assets.clashroyale.com/cardevolutions/300/W4Hmp8MTSdXANN8KdblbtHwtsbt0o749BbxNqmJYfA8.png"
      },
      "rarity": "common"
    },
    {
      "name": "Goblins",
      "id": 26000002,
      "maxLevel": 14,
      "elixirCost": 2,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/X_DQUye_OaS3QN6VC9CPw05Fit7wvSm3XegXIXKP--0.png"
      },
      "rarity": "common"
    },
    {
      "name": "Giant",
      "id": 26000003,
      "maxLevel": 12,
      "elixirCost": 5,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/Axr4ox5_b7edmLsoHxBX3vmgijAIibuF6RImTbqLlXE.png"
      },
      "rarity": "rare"
    },
    {
      "name": "P.E.K.K.A",
      "id": 26000004,
      "maxLevel": 9,
      "maxEvolutionLevel": 1,
      "elixirCost": 7,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/MlArURKhn_zWAZY-Xj1qIRKLVKquarG25BXDjUQajNs.png",
        "evolutionMedium": "https://api-assets.clashroyale.com/cardevolutions/300/MlArURKhn_zWAZY-Xj1qIRKLVKquarG25BXDjUQajNs.png"
      },
      "rarity": "epic"
    },
    {
      "name": "Minions",
      "id": 26000005,
      "maxLevel": 14,
      "elixirCost": 3,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/yHGpoEnmUWPGV_hBbhn-Kk-Bs838OjGzWzJJlQpQKQA.png"
      },
      "rarity": "common"
    },
    {
      "name": "Balloon",
      "id": 26000006,
      "maxLevel": 9,
      "elixirCost": 5,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/qBipxLo-3hhCnPrApp2Nn3b2NgrSrvwzWytvREev0CY.png"
      },
      "rarity": "epic"
    },
    {
      "name": "Witch",
      "id": 26000007,
      "maxLevel": 9,
      "elixirCost": 5,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/cfwk1vzehVyHC-uloEIH6NOI0hOdofCutR5PyhIgO6w.png"
      },
      "rarity": "epic"
    },
    {
      "name": "Barbarians",
      "id": 26000008,
      "maxLevel": 14,
      "maxEvolutionLevel": 1,
      "elixirCost": 5,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/TvJsuu2S4yhyk1jVYUAQwdKOnW4U77KuWWOTPOWnwfI.png",
        "evolutionMedium": "https://api-assets.clashroyale.com/cardevolutions/300/TvJsuu2S4yhyk1jVYUAQwdKOnW4U77KuWWOTPOWnwfI.png"
      },
      "rarity": "common"
    },
    {
      "name": "Golem",
      "id": 26000009,
      "maxLevel": 9,
      "elixirCost": 8,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/npdmCnET7jmVjJvjJQkFnNSNnDxYHDBigbvIAloFMds.png"
      },
      "rarity": "epic"
    },
    {
      "name": "Skeletons",
      "id": 26000010,
      "maxLevel": 14,
      "maxEvolutionLevel": 1,
      "elixirCost": 1,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/oO7iKMU5m0cdxhYPZA3nWQiAUh2yoGgdThLWB1rVSec.png",
        "evolutionMedium": "https://api-assets.clashroyale.com/cardevolutions/300/oO7iKMU5m0cdxhYPZA3nWQiAUh2yoGgdThLWB1rVSec.png"
      },
      "rarity": "common"
    },
    {
      "name": "Valkyrie",
      "id": 26000011,
      "maxLevel": 12,
      "maxEvolutionLevel": 1,
      "elixirCost": 4,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/0lIoYf3Y_plFTzo95zZL93JVxpfb3MMgFDDhgSDGU9A.png",
        "evolutionMedium": "https://api-assets.clashroyale.com/cardevolutions/300/0lIoYf3Y_plFTzo95zZL93JVxpfb3MMgFDDhgSDGU9A.png"
      },
      "rarity": "rare"
    },
    {
      "name": "Skeleton Army",
      "id": 26000012,
      "maxLevel": 9,
      "elixirCost": 3,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/fAOToOi1pRy7svN2xQS6mDkhQw2pj9m_17FauaNqyl4.png"
      },
      "rarity": "epic"
    },
    {
      "name": "Bomber",
      "id": 26000013,
      "maxLevel": 14,
      "maxEvolutionLevel": 1,
      "elixirCost": 2,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/12n1CesxKIcqVYntjxcF36EFA-ONw7Z-DoL0_rQrbdo.png",
        "evolutionMedium": "https://api-assets.clashroyale.com/cardevolutions/300/12n1CesxKIcqVYntjxcF36EFA-ONw7Z-DoL0_rQrbdo.png"
      },
      "rarity": "common"
    },
    {
      "name": "Musketeer",
      "id": 26000014,
      "maxLevel": 12,
      "maxEvolutionLevel": 1,
      "elixirCost": 4,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/Tex1C48UTq9FKtAX-3tzG0FJmc9jzncUZG3bb5Vf-Ds.png",
        "evolutionMedium": "https://api-assets.clashroyale.com/cardevolutions/300/Tex1C48UTq9FKtAX-3tzG0FJmc9jzncUZG3bb5Vf-Ds.png"
      },
      "rarity": "rare"
    },
    {
      "name": "Baby Dragon",
      "id": 26000015,
      "maxLevel": 9,
      "elixirCost": 4,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/cjC9n4AvEZJ3urkVh-rwBkJ-aRSsydIMqSAV48hAih0.png"
      },
      "rarity": "epic"
    },
    {
      "name": "Prince",
      "id": 26000016,
      "maxLevel": 9,
      "elixirCost": 5,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/3JntJV62aY0G1Qh6LIs-ek-0ayeYFY3VItpG7cb9I60.png"
      },
      "rarity": "epic"
    },
    {
      "name": "Wizard",
      "id": 26000017,
      "maxLevel": 12,
      "maxEvolutionLevel": 1,
      "elixirCost": 5,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/Mej7vnv4H_3p_8qPs_N6_GKahy6HDr7pU7i9eTHS84U.png",
        "evolutionMedium": "https://api-assets.clashroyale.com/cardevolutions/300/Mej7vnv4H_3p_8qPs_N6_GKahy6HDr7pU7i9eTHS84U.png"
      },
      "rarity": "rare"
    },
    {
      "name": "Mini P.E.K.K.A",
      "id": 26000018,
      "maxLevel": 12,
      "elixirCost": 4,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/Fmltc4j3Ve9vO_xhHHPEO3PRP3SmU2oKp2zkZQHRZT4.png"
      },
      "rarity": "rare"
    },
    {
      "name": "Spear Goblins",
      "id": 26000019,
      "maxLevel": 14,
      "elixirCost": 2,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/FSDFotjaXidI4ku_WFpVCTWS1hKGnFh1sxX0lxM43_E.png"
      },
      "rarity": "common"
    },
    {
      "name": "Giant Skeleton",
      "id": 26000020,
      "maxLevel": 9,
      "elixirCost": 6,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/0p0gd0XaVRu1Hb1iSG1hTYbz2AN6aEiZnhaAib5O8Z8.png"
      },
      "rarity": "epic"
    },
    {
      "name": "Hog Rider",
      "id": 26000021,
      "maxLevel": 12,
      "elixirCost": 4,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/Ubu0oUl8tZkusnkZf8Xv9Vno5IO29Y-jbZ4fhoNJ5oc.png"
      },
      "rarity": "rare"
    },
    {
      "name": "Minion Horde",
      "id": 26000022,
      "maxLevel": 14,
      "elixirCost": 5,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/Wyjq5l0IXHTkX9Rmpap6HaH08MvjbxFp1xBO9a47YSI.png"
      },
      "rarity": "common"
    },
    {
      "name": "Ice Wizard",
      "id": 26000023,
      "maxLevel": 6,
      "elixirCost": 3,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/W3dkw0HTw9n1jB-zbknY2w3wHuyuLxSRIAV5fUT1SEY.png"
      },
      "rarity": "legendary"
    },
    {
      "name": "Royal Giant",
      "id": 26000024,
      "maxLevel": 14,
      "maxEvolutionLevel": 1,
      "elixirCost": 6,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/mnlRaNtmfpQx2e6mp70sLd0ND-pKPF70Cf87_agEKg4.png",
        "evolutionMedium": "https://api-assets.clashroyale.com/cardevolutions/300/mnlRaNtmfpQx2e6mp70sLd0ND-pKPF70Cf87_agEKg4.png"
      },
      "rarity": "common"
    },
    {
      "name": "Guards",
      "id": 26000025,
      "maxLevel": 9,
      "elixirCost": 3,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/1ArKfLJxYo6_NU_S9cAeIrfbXqWH0oULVJXedxBXQlU.png"
      },
      "rarity": "epic"
    },
    {
      "name": "Princess",
      "id": 26000026,
      "maxLevel": 6,
      "elixirCost": 3,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/bAwMcqp9EKVIKH3ZLm_m0MqZFSG72zG-vKxpx8aKoVs.png"
      },
      "rarity": "legendary"
    },
    {
      "name": "Dark Prince",
      "id": 26000027,
      "maxLevel": 9,
      "elixirCost": 4,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/M7fXlrKXHu2IvpSGpk36kXVstslbR08Bbxcy0jQcln8.png"
      },
      "rarity": "epic"
    },
    {
      "name": "Three Musketeers",
      "id": 26000028,
      "maxLevel": 12,
      "elixirCost": 9,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/_J2GhbkX3vswaFk1wG-dopwiHyNc_YiPhwroiKF3Mek.png"
      },
      "rarity": "rare"
    },
    {
      "name": "Lava Hound",
      "id": 26000029,
      "maxLevel": 6,
      "elixirCost": 7,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/unicRQ975sBY2oLtfgZbAI56ZvaWz7azj-vXTLxc0r8.png"
      },
      "rarity": "legendary"
    },
    {
      "name": "Ice Spirit",
      "id": 26000030,
      "maxLevel": 14,
      "maxEvolutionLevel": 1,
      "elixirCost": 1,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/lv1budiafU9XmSdrDkk0NYyqASAFYyZ06CPysXKZXlA.png",
        "evolutionMedium": "https://api-assets.clashroyale.com/cardevolutions/300/lv1budiafU9XmSdrDkk0NYyqASAFYyZ06CPysXKZXlA.png"
      },
      "rarity": "common"
    },
    {
      "name": "Fire Spirit",
      "id": 26000031,
      "maxLevel": 14,
      "elixirCost": 1,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/16-BqusVvynIgYI8_Jci3LDC-r8AI_xaIYLgXqtlmS8.png"
      },
      "rarity": "common"
    },
    {
      "name": "Miner",
      "id": 26000032,
      "maxLevel": 6,
      "elixirCost": 3,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/Y4yWvdwBCg2FpAZgs8T09Gy34WOwpLZW-ttL52Ae8NE.png"
      },
      "rarity": "legendary"
    },
    {
      "name": "Sparky",
      "id": 26000033,
      "maxLevel": 6,
      "elixirCost": 6,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/2GKMkBrArZXgQxf2ygFjDs4VvGYPbx8F6Lj_68iVhIM.png"
      },
      "rarity": "legendary"
    },
    {
      "name": "Bowler",
      "id": 26000034,
      "maxLevel": 9,
      "elixirCost": 5,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/SU4qFXmbQXWjvASxVI6z9IJuTYolx4A0MKK90sTIE88.png"
      },
      "rarity": "epic"
    },
    {
      "name": "Lumberjack",
      "id": 26000035,
      "maxLevel": 6,
      "maxEvolutionLevel": 1,
      "elixirCost": 4,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/E6RWrnCuk13xMX5OE1EQtLEKTZQV6B78d00y8PlXt6Q.png",
        "evolutionMedium": "https://api-assets.clashroyale.com/cardevolutions/300/E6RWrnCuk13xMX5OE1EQtLEKTZQV6B78d00y8PlXt6Q.png"
      },
      "rarity": "legendary"
    },
    {
      "name": "Battle Ram",
      "id": 26000036,
      "maxLevel": 12,
      "maxEvolutionLevel": 1,
      "elixirCost": 4,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/dyc50V2cplKi4H7pq1B3I36pl_sEH5DQrNHboS_dbbM.png",
        "evolutionMedium": "https://api-assets.clashroyale.com/cardevolutions/300/dyc50V2cplKi4H7pq1B3I36pl_sEH5DQrNHboS_dbbM.png"
      },
      "rarity": "rare"
    },
    {
      "name": "Inferno Dragon",
      "id": 26000037,
      "maxLevel": 6,
      "elixirCost": 4,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/y5HDbKtTbWG6En6TGWU0xoVIGs1-iQpIP4HC-VM7u8A.png"
      },
      "rarity": "legendary"
    },
    {
      "name": "Ice Golem",
      "id": 26000038,
      "maxLevel": 12,
      "elixirCost": 2,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/r05cmpwV1o7i7FHodtZwW3fmjbXCW34IJCsDEV5cZC4.png"
      },
      "rarity": "rare"
    },
    {
      "name": "Mega Minion",
      "id": 26000039,
      "maxLevel": 12,
      "elixirCost": 3,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/-T_e4YLbuhPBKbYnBwQfXgynNpp5eOIN_0RracYwL9c.png"
      },
      "rarity": "rare"
    },
    {
      "name": "Dart Goblin",
      "id": 26000040,
      "maxLevel": 12,
      "maxEvolutionLevel": 1,
      "elixirCost": 3,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/BmpK3bqEAviflqHCdxxnfm-_l3pRPJw3qxHkwS55nCY.png",
        "evolutionMedium": "https://api-assets.clashroyale.com/cardevolutions/300/BmpK3bqEAviflqHCdxxnfm-_l3pRPJw3qxHkwS55nCY.png"
      },
      "rarity": "rare"
    },
    {
      "name": "Goblin Gang",
      "id": 26000041,
      "maxLevel": 14,
      "elixirCost": 3,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/NHflxzVAQT4oAz7eDfdueqpictb5vrWezn1nuqFhE4w.png"
      },
      "rarity": "common"
    },
    {
      "name": "Electro Wizard",
      "id": 26000042,
      "maxLevel": 6,
      "elixirCost": 4,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/RsFaHgB3w6vXsTjXdPr3x8l_GbV9TbOUCvIx07prbrQ.png"
      },
      "rarity": "legendary"
    },
    {
      "name": "Elite Barbarians",
      "id": 26000043,
      "maxLevel": 14,
      "elixirCost": 6,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/C88C5JH_F3lLZj6K-tLcMo5DPjrFmvzIb1R2M6xCfTE.png"
      },
      "rarity": "common"
    },
    {
      "name": "Hunter",
      "id": 26000044,
      "maxLevel": 9,
      "maxEvolutionLevel": 1,
      "elixirCost": 4,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/VNabB1WKnYtYRSG7X_FZfnZjQDHTBs9A96OGMFmecrA.png",
        "evolutionMedium": "https://cdns3.royaleapi.com/cdn-cgi/image/w=150,h=180,format=auto/static/img/cards/v4-aba2f5ae/hunter-ev1.png"
      },
      "rarity": "epic"
    },
    {
      "name": "Executioner",
      "id": 26000045,
      "maxLevel": 9,
      "elixirCost": 5,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/9XL5BP2mqzV8kza6KF8rOxrpCZTyuGLp2l413DTjEoM.png"
      },
      "rarity": "epic"
    },
    {
      "name": "Bandit",
      "id": 26000046,
      "maxLevel": 6,
      "elixirCost": 3,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/QWDdXMKJNpv0go-HYaWQWP6p8uIOHjqn-zX7G0p3DyM.png"
      },
      "rarity": "legendary"
    },
    {
      "name": "Royal Recruits",
      "id": 26000047,
      "maxLevel": 14,
      "maxEvolutionLevel": 1,
      "elixirCost": 7,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/jcNyYGUiXXNz3kuz8NBkHNKNREQKraXlb_Ts7rhCIdM.png",
        "evolutionMedium": "https://api-assets.clashroyale.com/cardevolutions/300/jcNyYGUiXXNz3kuz8NBkHNKNREQKraXlb_Ts7rhCIdM.png"
      },
      "rarity": "common"
    },
    {
      "name": "Night Witch",
      "id": 26000048,
      "maxLevel": 6,
      "elixirCost": 4,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/NpCrXDEDBBJgNv9QrBAcJmmMFbS7pe3KCY8xJ5VB18A.png"
      },
      "rarity": "legendary"
    },
    {
      "name": "Bats",
      "id": 26000049,
      "maxLevel": 14,
      "maxEvolutionLevel": 1,
      "elixirCost": 2,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/EnIcvO21hxiNpoI-zO6MDjLmzwPbq8Z4JPo2OKoVUjU.png",
        "evolutionMedium": "https://api-assets.clashroyale.com/cardevolutions/300/EnIcvO21hxiNpoI-zO6MDjLmzwPbq8Z4JPo2OKoVUjU.png"
      },
      "rarity": "common"
    },
    {
      "name": "Royal Ghost",
      "id": 26000050,
      "maxLevel": 6,
      "elixirCost": 3,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/3En2cz0ISQAaMTHY3hj3rTveFN2kJYq-H4VxvdJNvCM.png"
      },
      "rarity": "legendary"
    },
    {
      "name": "Ram Rider",
      "id": 26000051,
      "maxLevel": 6,
      "elixirCost": 5,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/QaJyerT7f7oMyZ3Fv1glKymtLSvx7YUXisAulxl7zRI.png"
      },
      "rarity": "legendary"
    },
    {
      "name": "Zappies",
      "id": 26000052,
      "maxLevel": 12,
      "elixirCost": 4,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/QZfHRpLRmutZbCr5fpLnTpIp89vLI6NrAwzGZ8tHEc4.png"
      },
      "rarity": "rare"
    },
    {
      "name": "Rascals",
      "id": 26000053,
      "maxLevel": 14,
      "elixirCost": 5,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/KV48DfwVHKx9XCjzBdk3daT_Eb52Me4VgjVO7WctRc4.png"
      },
      "rarity": "common"
    },
    {
      "name": "Cannon Cart",
      "id": 26000054,
      "maxLevel": 9,
      "elixirCost": 5,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/aqwxRz8HXzqlMCO4WMXNA1txynjXTsLinknqsgZLbok.png"
      },
      "rarity": "epic"
    },
    {
      "name": "Mega Knight",
      "id": 26000055,
      "maxLevel": 6,
      "maxEvolutionLevel": 1,
      "elixirCost": 7,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/O2NycChSNhn_UK9nqBXUhhC_lILkiANzPuJjtjoz0CE.png",
        "evolutionMedium": "https://api-assets.clashroyale.com/cardevolutions/300/O2NycChSNhn_UK9nqBXUhhC_lILkiANzPuJjtjoz0CE.png"
      },
      "rarity": "legendary"
    },
    {
      "name": "Skeleton Barrel",
      "id": 26000056,
      "maxLevel": 14,
      "elixirCost": 3,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/vCB4DWCcrGbTkarjcOiVz4aNDx6GWLm0yUepg9E1MGo.png"
      },
      "rarity": "common"
    },
    {
      "name": "Flying Machine",
      "id": 26000057,
      "maxLevel": 12,
      "elixirCost": 4,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/hzKNE3QwFcrSrDDRuVW3QY_OnrDPijSiIp-PsWgFevE.png"
      },
      "rarity": "rare"
    },
    {
      "name": "Wall Breakers",
      "id": 26000058,
      "maxLevel": 9,
      "maxEvolutionLevel": 1,
      "elixirCost": 2,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/_xPphEfC8eEwFNrfU3cMQG9-f5JaLQ31ARCA7l3XtW4.png",
        "evolutionMedium": "https://api-assets.clashroyale.com/cardevolutions/300/_xPphEfC8eEwFNrfU3cMQG9-f5JaLQ31ARCA7l3XtW4.png"
      },
      "rarity": "epic"
    },
    {
      "name": "Royal Hogs",
      "id": 26000059,
      "maxLevel": 12,
      "elixirCost": 5,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/ASSQJG_MoVq9e81HZzo4bynMnyLNpNJMfSLb3hqydOw.png"
      },
      "rarity": "rare"
    },
    {
      "name": "Goblin Giant",
      "id": 26000060,
      "maxLevel": 9,
      "maxEvolutionLevel": 1,
      "elixirCost": 6,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/SoW16cY3jXBwaTDvb39DkqiVsoFVaDWbzf5QBYphJrY.png",
        "evolutionMedium": "https://api-assets.clashroyale.com/cardevolutions/300/SoW16cY3jXBwaTDvb39DkqiVsoFVaDWbzf5QBYphJrY.png"
      },
      "rarity": "epic"
    },
    {
      "name": "Fisherman",
      "id": 26000061,
      "maxLevel": 6,
      "elixirCost": 3,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/U2KZ3g0wyufcuA5P2Xrn3Z3lr1WiJmc5S0IWOZHgizQ.png"
      },
      "rarity": "legendary"
    },
    {
      "name": "Magic Archer",
      "id": 26000062,
      "maxLevel": 6,
      "elixirCost": 4,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/Avli3W7BxU9HQ2SoLiXnBgGx25FoNXUSFm7OcAk68ek.png"
      },
      "rarity": "legendary"
    },
    {
      "name": "Electro Dragon",
      "id": 26000063,
      "maxLevel": 9,
      "maxEvolutionLevel": 1,
      "elixirCost": 5,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/tN9h6lnMNPCNsx0LMFmvpHgznbDZ1fBRkx-C7UfNmfY.png",
        "evolutionMedium": "https://api-assets.clashroyale.com/cardevolutions/300/tN9h6lnMNPCNsx0LMFmvpHgznbDZ1fBRkx-C7UfNmfY.png"
      },
      "rarity": "epic"
    },
    {
      "name": "Firecracker",
      "id": 26000064,
      "maxLevel": 14,
      "maxEvolutionLevel": 1,
      "elixirCost": 3,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/c1rL3LO1U2D9-TkeFfAC18gP3AO8ztSwrcHMZplwL2Q.png",
        "evolutionMedium": "https://api-assets.clashroyale.com/cardevolutions/300/c1rL3LO1U2D9-TkeFfAC18gP3AO8ztSwrcHMZplwL2Q.png"
      },
      "rarity": "common"
    },
    {
      "name": "Mighty Miner",
      "id": 26000065,
      "maxLevel": 4,
      "elixirCost": 4,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/Cd9R56yraxTvJiD8xJ2qT2OdsHyh94FqOAarXpbyelo.png"
      },
      "rarity": "champion"
    },
    {
      "name": "Elixir Golem",
      "id": 26000067,
      "maxLevel": 12,
      "elixirCost": 3,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/puhMsZjCIqy21HW3hYxjrk_xt8NIPyFqjRy-BeLKZwo.png"
      },
      "rarity": "rare"
    },
    {
      "name": "Battle Healer",
      "id": 26000068,
      "maxLevel": 12,
      "elixirCost": 4,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/KdwXcoigS2Kg-cgA7BJJIANbUJG6SNgjetRQ-MegZ08.png"
      },
      "rarity": "rare"
    },
    {
      "name": "Skeleton King",
      "id": 26000069,
      "maxLevel": 4,
      "elixirCost": 4,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/dCd69_wN9f8DxwuqOGtR4QgWhHIPIaTNxZ1e23RzAAc.png"
      },
      "rarity": "champion"
    },
    {
      "name": "Archer Queen",
      "id": 26000072,
      "maxLevel": 4,
      "elixirCost": 5,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/p7OQmOAFTery7zCzlpDdm-LOD1kINTm42AwIHchZfWk.png"
      },
      "rarity": "champion"
    },
    {
      "name": "Golden Knight",
      "id": 26000074,
      "maxLevel": 4,
      "elixirCost": 4,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/WJd207D0O1sN-l1FTb8P9KhYL2oF5jY26vRUfTUW3FQ.png"
      },
      "rarity": "champion"
    },
    {
      "name": "Monk",
      "id": 26000077,
      "maxLevel": 4,
      "elixirCost": 5,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/2onG4t4-CxqwFVZAn6zpWxFz3_mG2ksSj4Q7zldo1SM.png"
      },
      "rarity": "champion"
    },
    {
      "name": "Skeleton Dragons",
      "id": 26000080,
      "maxLevel": 14,
      "elixirCost": 4,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/qPOtg9uONh47_NLxGhhFc_ww9PlZ6z3Ry507q1NZUXs.png"
      },
      "rarity": "common"
    },
    {
      "name": "Mother Witch",
      "id": 26000083,
      "maxLevel": 6,
      "elixirCost": 4,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/fO-Xah8XZkYKaSK9SCp3wnzwxtvIhun9NVY-zzte1Ng.png"
      },
      "rarity": "legendary"
    },
    {
      "name": "Electro Spirit",
      "id": 26000084,
      "maxLevel": 14,
      "elixirCost": 1,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/WKd4-IAFsgPpMo7dDi9sujmYjRhOMEWiE07OUJpvD9g.png"
      },
      "rarity": "common"
    },
    {
      "name": "Electro Giant",
      "id": 26000085,
      "maxLevel": 9,
      "elixirCost": 7,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/_uChZkNHAMq6tPb3v6A49xinOe3CnhjstOhG6OZbPYc.png"
      },
      "rarity": "epic"
    },
    {
      "name": "Phoenix",
      "id": 26000087,
      "maxLevel": 6,
      "elixirCost": 4,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/i0RoY1fs6ay7VAxyFEfZGIPnD002nAKcne9FtJsWBHM.png"
      },
      "rarity": "legendary"
    },
    {
      "name": "Little Prince",
      "id": 26000093,
      "maxLevel": 4,
      "elixirCost": 3,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/dY-gSseki6KBpkIG17safHH5YlB8SErFZO9OXbJxf9w.png"
      },
      "rarity": "champion"
    },
    {
      "name": "Goblin Demolisher",
      "id": 26000095,
      "maxLevel": 12,
      "elixirCost": 4,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/KVVOgdn40xasFLYuQv8Go_U_LCV7wSG9q9eE1H7f3Qk.png"
      },
      "rarity": "rare"
    },
    {
      "name": "Goblin Machine",
      "id": 26000096,
      "maxLevel": 6,
      "elixirCost": 5,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/-iLlotr6GCFndL_1BSBqWBb6DnsHBhLerd5EblZDNfU.png"
      },
      "rarity": "legendary"
    },
    {
      "name": "Suspicious Bush",
      "id": 26000097,
      "maxLevel": 12,
      "elixirCost": 2,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/vqTzGAjseQv9F5rf4tsFWeocvg0dyPw1j_nB1cmDZfI.png"
      },
      "rarity": "rare"
    },
    {
      "name": "Goblinstein",
      "id": 26000099,
      "maxLevel": 4,
      "elixirCost": 5,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/mQ20B49dXdk7Nv0lMdLw175M3YvkSpN6KNnho8UKBd8.png"
      },
      "rarity": "champion"
    },
    {
      "name": "Rune Giant",
      "id": 26000101,
      "maxLevel": 9,
      "elixirCost": 4,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/UogMnGHQXT-TOVXRxslKdAKXUPhqUvrD_hV9x8lbzdE.png"
      },
      "rarity": "epic"
    },
    {
      "name": "Berserker",
      "id": 26000102,
      "maxLevel": 14,
      "elixirCost": 2,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/NA6W8S1JBYBlOPwD3dNvJLFvVDKq-UuBs_J3i3ewLFI.png"
      },
      "rarity": "common"
    },
    {
      "name": "Cannon",
      "id": 27000000,
      "maxLevel": 14,
      "maxEvolutionLevel": 1,
      "elixirCost": 3,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/nZK1y-beLxO5vnlyUhK6-2zH2NzXJwqykcosqQ1cmZ8.png",
        "evolutionMedium": "https://api-assets.clashroyale.com/cardevolutions/300/nZK1y-beLxO5vnlyUhK6-2zH2NzXJwqykcosqQ1cmZ8.png"
      },
      "rarity": "common"
    },
    {
      "name": "Goblin Hut",
      "id": 27000001,
      "maxLevel": 12,
      "elixirCost": 5,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/l8ZdzzNLcwB4u7ihGgxNFQOjCT_njFuAhZr7D6PRF7E.png"
      },
      "rarity": "rare"
    },
    {
      "name": "Mortar",
      "id": 27000002,
      "maxLevel": 14,
      "maxEvolutionLevel": 1,
      "elixirCost": 4,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/lPOSw6H7YOHq2miSCrf7ZDL3ANjhJdPPDYOTujdNrVE.png",
        "evolutionMedium": "https://api-assets.clashroyale.com/cardevolutions/300/lPOSw6H7YOHq2miSCrf7ZDL3ANjhJdPPDYOTujdNrVE.png"
      },
      "rarity": "common"
    },
    {
      "name": "Inferno Tower",
      "id": 27000003,
      "maxLevel": 12,
      "elixirCost": 5,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/GSHY_wrooMMLET6bG_WJB8redtwx66c4i80ipi4gYOM.png"
      },
      "rarity": "rare"
    },
    {
      "name": "Bomb Tower",
      "id": 27000004,
      "maxLevel": 12,
      "elixirCost": 4,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/rirYRyHPc97emRjoH-c1O8uZCBzPVnToaGuNGusF3TQ.png"
      },
      "rarity": "rare"
    },
    {
      "name": "Barbarian Hut",
      "id": 27000005,
      "maxLevel": 12,
      "elixirCost": 6,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/ho0nOG2y3Ch86elHHcocQs8Fv_QNe0cFJ2CijsxABZA.png"
      },
      "rarity": "rare"
    },
    {
      "name": "Tesla",
      "id": 27000006,
      "maxLevel": 14,
      "maxEvolutionLevel": 1,
      "elixirCost": 4,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/OiwnGrxFMNiHetYEerE-UZt0L_uYNzFY7qV_CA_OxR4.png",
        "evolutionMedium": "https://api-assets.clashroyale.com/cardevolutions/300/OiwnGrxFMNiHetYEerE-UZt0L_uYNzFY7qV_CA_OxR4.png"
      },
      "rarity": "common"
    },
    {
      "name": "Elixir Collector",
      "id": 27000007,
      "maxLevel": 12,
      "elixirCost": 6,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/BGLo3Grsp81c72EpxLLk-Sofk3VY56zahnUNOv3JcT0.png"
      },
      "rarity": "rare"
    },
    {
      "name": "X-Bow",
      "id": 27000008,
      "maxLevel": 9,
      "elixirCost": 6,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/zVQ9Hme1hlj9Dc6e1ORl9xWwglcSrP7ejow5mAhLUJc.png"
      },
      "rarity": "epic"
    },
    {
      "name": "Tombstone",
      "id": 27000009,
      "maxLevel": 12,
      "elixirCost": 3,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/LjSfSbwQfkZuRJY4pVxKspZ-a0iM5KAhU8w-a_N5Z7Y.png"
      },
      "rarity": "rare"
    },
    {
      "name": "Furnace",
      "id": 27000010,
      "maxLevel": 12,
      "elixirCost": 4,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/iqbDiG7yYRIzvCPXdt9zPb3IvMt7F7Gi4wIPnh2x4aI.png"
      },
      "rarity": "rare"
    },
    {
      "name": "Goblin Cage",
      "id": 27000012,
      "maxLevel": 12,
      "maxEvolutionLevel": 1,
      "elixirCost": 4,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/vD24bBgK4rSq7wx5QEbuqChtPMRFviL_ep76GwQw1yA.png",
        "evolutionMedium": "https://api-assets.clashroyale.com/cardevolutions/300/vD24bBgK4rSq7wx5QEbuqChtPMRFviL_ep76GwQw1yA.png"
      },
      "rarity": "rare"
    },
    {
      "name": "Goblin Drill",
      "id": 27000013,
      "maxLevel": 9,
      "maxEvolutionLevel": 1,
      "elixirCost": 4,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/eN2TKUYbih-26yBi0xy5LVFOA0zDftgDqxxnVfdIg1o.png",
        "evolutionMedium": "https://api-assets.clashroyale.com/cardevolutions/300/eN2TKUYbih-26yBi0xy5LVFOA0zDftgDqxxnVfdIg1o.png"
      },
      "rarity": "epic"
    },
    {
      "name": "Fireball",
      "id": 28000000,
      "maxLevel": 12,
      "elixirCost": 4,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/lZD9MILQv7O-P3XBr_xOLS5idwuz3_7Ws9G60U36yhc.png"
      },
      "rarity": "rare"
    },
    {
      "name": "Arrows",
      "id": 28000001,
      "maxLevel": 14,
      "elixirCost": 3,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/Flsoci-Y6y8ZFVi5uRFTmgkPnCmMyMVrU7YmmuPvSBo.png"
      },
      "rarity": "common"
    },
    {
      "name": "Rage",
      "id": 28000002,
      "maxLevel": 9,
      "elixirCost": 2,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/bGP21OOmcpHMJ5ZA79bHVV2D-NzPtDkvBskCNJb7pg0.png"
      },
      "rarity": "epic"
    },
    {
      "name": "Rocket",
      "id": 28000003,
      "maxLevel": 12,
      "elixirCost": 6,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/Ie07nQNK9CjhKOa4-arFAewi4EroqaA-86Xo7r5tx94.png"
      },
      "rarity": "rare"
    },
    {
      "name": "Goblin Barrel",
      "id": 28000004,
      "maxLevel": 9,
      "maxEvolutionLevel": 1,
      "elixirCost": 3,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/CoZdp5PpsTH858l212lAMeJxVJ0zxv9V-f5xC8Bvj5g.png",
        "evolutionMedium": "https://api-assets.clashroyale.com/cardevolutions/300/CoZdp5PpsTH858l212lAMeJxVJ0zxv9V-f5xC8Bvj5g.png"
      },
      "rarity": "epic"
    },
    {
      "name": "Freeze",
      "id": 28000005,
      "maxLevel": 9,
      "elixirCost": 4,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/I1M20_Zs_p_BS1NaNIVQjuMJkYI_1-ePtwYZahn0JXQ.png"
      },
      "rarity": "epic"
    },
    {
      "name": "Mirror",
      "id": 28000006,
      "maxLevel": 9,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/wC6Cm9rKLEOk72zTsukVwxewKIoO4ZcMJun54zCPWvA.png"
      },
      "rarity": "epic"
    },
    {
      "name": "Lightning",
      "id": 28000007,
      "maxLevel": 9,
      "elixirCost": 6,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/fpnESbYqe5GyZmaVVYe-SEu7tE0Kxh_HZyVigzvLjks.png"
      },
      "rarity": "epic"
    },
    {
      "name": "Zap",
      "id": 28000008,
      "maxLevel": 14,
      "maxEvolutionLevel": 1,
      "elixirCost": 2,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/7dxh2-yCBy1x44GrBaL29vjqnEEeJXHEAlsi5g6D1eY.png",
        "evolutionMedium": "https://api-assets.clashroyale.com/cardevolutions/300/7dxh2-yCBy1x44GrBaL29vjqnEEeJXHEAlsi5g6D1eY.png"
      },
      "rarity": "common"
    },
    {
      "name": "Poison",
      "id": 28000009,
      "maxLevel": 9,
      "elixirCost": 4,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/98HDkG2189yOULcVG9jz2QbJKtfuhH21DIrIjkOjxI8.png"
      },
      "rarity": "epic"
    },
    {
      "name": "Graveyard",
      "id": 28000010,
      "maxLevel": 6,
      "elixirCost": 5,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/Icp8BIyyfBTj1ncCJS7mb82SY7TPV-MAE-J2L2R48DI.png"
      },
      "rarity": "legendary"
    },
    {
      "name": "The Log",
      "id": 28000011,
      "maxLevel": 6,
      "elixirCost": 2,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/_iDwuDLexHPFZ_x4_a0eP-rxCS6vwWgTs6DLauwwoaY.png"
      },
      "rarity": "legendary"
    },
    {
      "name": "Tornado",
      "id": 28000012,
      "maxLevel": 9,
      "elixirCost": 3,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/QJB-QK1QJHdw4hjpAwVSyZBozc2ZWAR9pQ-SMUyKaT0.png"
      },
      "rarity": "epic"
    },
    {
      "name": "Clone",
      "id": 28000013,
      "maxLevel": 9,
      "elixirCost": 3,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/mHVCet-1TkwWq-pxVIU2ZWY9_2z7Z7wtP25ArEUsP_g.png"
      },
      "rarity": "epic"
    },
    {
      "name": "Earthquake",
      "id": 28000014,
      "maxLevel": 12,
      "elixirCost": 3,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/XeQXcrUu59C52DslyZVwCnbi4yamID-WxfVZLShgZmE.png"
      },
      "rarity": "rare"
    },
    {
      "name": "Barbarian Barrel",
      "id": 28000015,
      "maxLevel": 9,
      "elixirCost": 2,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/Gb0G1yNy0i5cIGUHin8uoFWxqntNtRPhY_jeMXg7HnA.png"
      },
      "rarity": "epic"
    },
    {
      "name": "Heal Spirit",
      "id": 28000016,
      "maxLevel": 12,
      "elixirCost": 1,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/GITl06sa2nGRLPvboyXbGEv5E3I-wAwn1Eqa5esggbc.png"
      },
      "rarity": "rare"
    },
    {
      "name": "Giant Snowball",
      "id": 28000017,
      "maxLevel": 14,
      "maxEvolutionLevel": 1,
      "elixirCost": 2,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/7MaJLa6hK9WN2_VIshuh5DIDfGwm0wEv98gXtAxLDPs.png",
        "evolutionMedium": "https://api-assets.clashroyale.com/cardevolutions/300/7MaJLa6hK9WN2_VIshuh5DIDfGwm0wEv98gXtAxLDPs.png"
      },
      "rarity": "common"
    },
    {
      "name": "Royal Delivery",
      "id": 28000018,
      "maxLevel": 14,
      "elixirCost": 3,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/LPg7AGjGI3_xmi7gLLgGC50yKM1jJ2teWkZfoHJcIZo.png"
      },
      "rarity": "common"
    },
    {
      "name": "Void",
      "id": 28000023,
      "maxLevel": 9,
      "elixirCost": 3,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/BykyeWDqzn4PlHSszu3NbrXT1mHxW2EA8vHbQGR5LDE.png"
      },
      "rarity": "epic"
    },
    {
      "name": "Goblin Curse",
      "id": 28000024,
      "maxLevel": 9,
      "elixirCost": 2,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/OQPfGgT5mHEUvPuKKt0plZT0PNtIjCqUgQ3Rm86dQ2k.png"
      },
      "rarity": "epic"
    }
  ],
  "supportItems": [
    {
      "name": "Tower Princess",
      "id": 159000000,
      "maxLevel": 14,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/Nzo5Gjbh7NG6O3Hyu7ev54Pu5zK7vDMR2fbpGdVsS64.png"
      },
      "rarity": "common"
    },
    {
      "name": "Cannoneer",
      "id": 159000001,
      "maxLevel": 9,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/cUfU4UowRdbIiRvxv0ns4ezQUNndJTy7D2q4I_K_fzg.png"
      },
      "rarity": "epic"
    },
    {
      "name": "Dagger Duchess",
      "id": 159000002,
      "maxLevel": 6,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/MVj028nMLCmBuP3HlV503uxVAxFg7jyliJVZ5JYJ1h8.png"
      },
      "rarity": "legendary"
    },
    {
      "name": "Royal Chef",
      "id": 159000004,
      "maxLevel": 6,
      "iconUrls": {
        "medium": "https://api-assets.clashroyale.com/cards/300/CLxP2o0iX7q9peMkekI8Ki4DgWixra8L5aUbiAeBU9U.png"
      },
      "rarity": "legendary"
    }
  ]
}

# HTML网页代码
new_html_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>节奏榜</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      background-color: #1e1e1e;
      color: black;
      margin: 0;
      padding: 0;
    }}
    .ranking-table {{
      width: 100%;
      border-collapse: collapse;
      table-layout: fixed;
    }}
    .ranking-table th, 
    .ranking-table td {{
      border: 2px solid #888;
      padding: 10px;
      text-align: center;
      font-weight: bold;
    }}
    .ranking-table th:first-child,
    .ranking-table td:first-child {{
      width: 2%;
      min-width: 100px;
    }}
    .ranking-table th:last-child,
    .ranking-table td:last-child {{
      width: 98%;
    }}
    .ranking-table th {{
      background-color: #333;
      color: white;
    }}
    .超模真神 {{ background-color: #f44336; }}
    .版本强势 {{ background-color: #ff9800; }}
    .中规中矩 {{ background-color: #ffeb3b; }}
    .环境低谷 {{ background-color: #2196f3; }}
    .史 {{ background-color: #4caf50; }}
    .card-container {{
      background-color: #000;
      padding: 5px;
      border-radius: 5px;
      min-height: 110px;
    }}
    .card {{
      display: inline-block;
      margin: 1px;
    }}
    .card img {{
      width: 75px;
      height: auto;
      object-fit: cover;
      cursor: pointer;
      
    }}
    .unranked-cards {{
      padding: 10px;
      border: 2px dashed #888;
      margin-top: 20px;
    }}
    .unranked-cards h3 {{
      color: white;
      margin-top: 0;
    }}
    #floatingMenu {{
      position: absolute;
      display: none;
      background-color: #fff;
      border: 1px solid #888;
      border-radius: 3px;
      padding: 5px;
      z-index: 1000;
      box-shadow: 2px 2px 5px rgba(0,0,0,0.5);
    }}
    #floatingMenu div {{
      padding: 5px 10px;
      cursor: pointer;
      white-space: nowrap;
    }}
    #floatingMenu div:hover {{
      background-color: #eee;
    }}
  </style>
</head>
<body>
  <table class="ranking-table">
    <thead>
      <tr>
        <th>评级</th>
        <th>卡牌</th>
      </tr>
    </thead>
    <tbody>
      {rows}
    </tbody>
  </table>

  <div class="unranked-cards">
    <h3>未分级卡牌</h3>
    <div class="card-container">
      {unranked_cards}
    </div>
  </div>

  <div id="floatingMenu">
    <div data-rating="超模真神">超模真神</div>
    <div data-rating="版本强势">版本强势</div>
    <div data-rating="中规中矩">中规中矩</div>
    <div data-rating="环境低谷">环境低谷</div>
    <div data-rating="史">史</div>
  </div>

  <script>
    document.querySelectorAll('.editable-title').forEach(title => {{
      title.ondblclick = function() {{
        const newName = prompt('输入新名称：', this.textContent);
        if (newName) this.textContent = newName;
      }};
    }});
  
    // 未分级卡片显示控制
    function toggleUnranked() {{
      const unrankedDiv = document.querySelector('.unranked-cards');
      const cardCount = unrankedDiv.querySelector('.card-container').children.length;
      unrankedDiv.style.display = cardCount > 0 ? 'block' : 'none';
    }}
  
    // 右键菜单功能
    let currentCard = null;
    const floatingMenu = document.getElementById('floatingMenu');

    document.addEventListener('contextmenu', function(e) {{
      const card = e.target.closest('.card');
      if (card && document.querySelector('.unranked-cards').contains(card)) {{
        e.preventDefault();
        currentCard = card;
        floatingMenu.style.left = e.pageX + "px";
        floatingMenu.style.top = e.pageY + "px";
        floatingMenu.style.display = "block";
      }}
    }});

    // 点击关闭菜单
    document.addEventListener('click', function(e) {{
      if (!floatingMenu.contains(e.target)) {{
        floatingMenu.style.display = "none";
        currentCard = null;
      }}
    }});

    // 菜单点击事件
    floatingMenu.querySelectorAll('div').forEach(item => {{
      item.addEventListener('click', function() {{
        const rating = this.getAttribute('data-rating');
        const container = document.getElementById("rating-" + rating);
        if (container && currentCard) {{
          container.appendChild(currentCard.cloneNode(true));
          currentCard.remove();
          toggleUnranked();
        }}
        floatingMenu.style.display = "none";
        currentCard = null;
      }});
    }});

    // 拖动功能
    let draggedCard = null;
    
    document.addEventListener('dragstart', function(e) {{
      const card = e.target.closest('.card');
      if (card) {{
        draggedCard = card;
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/html', card.outerHTML);
      }}
    }});

    document.addEventListener('dragend', function() {{
      draggedCard = null;
    }});

    document.querySelectorAll('.card-container').forEach(container => {{
      container.addEventListener('dragover', function(e) {{
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
      }});
      
      container.addEventListener('drop', function(e) {{
        e.preventDefault();
        if (draggedCard && draggedCard.parentNode !== this) {{
          this.appendChild(draggedCard);
        }}
      }});
    }});

    // 初始化显示状态
    toggleUnranked();
  </script>
</body>
</html>
"""

row_template = """
<tr class="{rating_class}">
    <td><div class="editable-title">{title}</div></td>
    <td class="card-container" id="rating-{rating_id}">{cards}</td>
</tr>
"""

card_template = """
<div class="card" draggable="true">
    <img src="{icon_url}" alt="{card_name}">
</div>
"""

############################################################
#                    步骤1：下载API网址
############################################################

# 用户选择模式
print("请选择排序模式：")
print("1. 自动排序")
print("2. 手动排序")
sort_mode = input("请输入选项编号（1或2）：")
auto_mode = sort_mode == '1'

if auto_mode:
    local_files = glob.glob("Best Cards for*.html") + glob.glob("Best Cards for*.htm")
    
    if local_files:
        fallback_file = local_files[0]
        with open(fallback_file, "r", encoding="utf-8") as f:
            content = f.read()
        with open("royale_api.html", "w", encoding="utf-8") as f:
            f.write(content)
        skip_download = True
    else:
        skip_download = False
else:
    skip_download = True

if not skip_download:
    # 数据源选择
    print("\n请选择节奏榜数据参考：")
    print("(1) 名人堂Top1000")
    print("(2) 名人堂Top200")
    print("(3) 终极挑战")
    print("(4) 经典挑战")
    mode_choice = input("请输入选项编号（1-4）：")
    mode_mapping = {"1": "TopRanked1000", "2": "TopRanked200", "3": "GC", "4": "CC"}
    mode = mode_mapping.get(mode_choice, "TopRanked1000")

    # 时间范围选择
    print("\n请选择数据的时间范围：")
    print("(1) 1日")
    print("(2) 3天")
    print("(3) 7天")
    time_choice = input("请输入选项编号（1-3）：")
    time_mapping = {"1": "1d", "2": "3d", "3": "7d"}
    time = time_mapping.get(time_choice, "7d")
    
    url = f"https://royaleapi.com/cards/popular?time={time}&mode=grid&cat={mode}&sort=usage"
    download_webpage(url, "royale_api.html")

############################################################
#                    步骤2：分析卡牌数据
############################################################

if auto_mode:
    with open("royale_api.html", "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")
    
    unranked_cards = []
    for card in soup.find_all("div", class_="grid_item"):
        name_tag = card.find("div", class_="card_name")
        usage_tag = card.find("div", class_="right floated content value usage")
        win_rate_tag = card.find("div", class_="right floated content value winpercent")

        name = name_tag.text.strip() if name_tag else "N/A"
        usage = float(usage_tag.text.strip().replace('%', '') or 0) / 100
        win_rate = float(win_rate_tag.text.strip().replace('%', '') or 0) / 100

        translation, correction = translations.get(name, ("NaN", 0))
        formatted_name = format_card_name(name)

        if auto_mode and translation != "NaN":
            rating = (usage * (win_rate**2 * 2) * correction) * 100
            classification = classify_rating(rating)
            card_data[classification].append((formatted_name, rating))
        else:
            unranked_cards.append(formatted_name)
    
else:
    unranked_cards = [
        format_card_name(item["name"]) 
        for item in api_data["items"] + api_data["supportItems"]
    ]

    unranked_cards += [
        format_card_name(f"{item['name']} Evolution") 
        for item in api_data["items"] 
        if item.get("maxEvolutionLevel", 0) >= 1
    ]
    # 按原始英文名称排序
    unranked_cards.sort()

for category in card_data:
    # 按评分降序排序，同分时按字母顺序排列
    card_data[category].sort(key=lambda x: (-float(x[1]), x[0]))


############################################################
#                    步骤3：生成HTML文件
############################################################

name_to_icon = {}
for item in api_data["items"] + api_data["supportItems"]:
    base_name = item["name"]
    name_to_icon[base_name] = item["iconUrls"]["medium"]
    
    if item.get("maxEvolutionLevel", 0) >= 1:
        evo_name = f"{base_name} Evolution"
        # 优先使用evolutionMedium，没有则用medium
        name_to_icon[evo_name] = item["iconUrls"].get(
            "evolutionMedium", 
            item["iconUrls"]["medium"]
        )

# 生成表格
rows = []
for section in ["超模真神", "版本强势", "中规中矩", "环境低谷", "史"]:
    rating_id = section.replace(" ", "")
    cards = card_data[section] if auto_mode else []
    cards_html = "".join([
        card_template.format(
            icon_url=get_icon_url(card[0] if auto_mode else card),
            card_name=translations.get(
                card[0].replace("-", " ").title() if auto_mode else card.replace("-", " ").title(), 
                ("未知卡牌",)
            )[0]
        ) 
        for card in (cards if auto_mode else [])
    ])
    rows.append(row_template.format(
        rating_class=section,
        title=section,
        rating_id=rating_id,
        cards=cards_html
    ))

unranked_html = "".join([card_template.format(
    icon_url=get_icon_url(c.replace("-ev1", " Evolution")),
    card_name=c
) for c in unranked_cards])

# 生成完整HTML
html_content = new_html_template.format(
    rows="".join(rows),
    unranked_cards=unranked_html
)

# 保存文件
with open("Card_Tier.html", "w", encoding="utf-8") as file:
    file.write(html_content)
print("HTML网页已生成，文件名为：Card_Tier.html")

# 清理临时文件
if (not skip_download) or auto_mode:
    try:
        os.remove("royale_api.html")
        print("已删除临时文件：royale_api.html")
    except Exception as e:
        print(f"删除文件时发生错误：{e}")

