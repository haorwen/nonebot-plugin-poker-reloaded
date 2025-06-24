<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="./nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="./NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-poker-reloaded

_✨ 一个扑克对决插件 ✨_


<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/haorwen/nonebot-plugin-poker-reloaded.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-poker-reloaded">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-poker-reloaded.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">

</div>

## 📖 介绍

对[MoonofBridge24/nonebot_plugin_poker](https://github.com/MoonofBridge24/nonebot_plugin_poker)进行了重构，使用alconna以兼容几乎所有适配器


## 💿 安装

<details open>
<summary>使用 nb-cli 安装（本插件暂未发布，无法使用该方式）</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-poker-reloaded

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-poker-reloaded
</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-poker-reloaded
</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-poker-reloaded
</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-poker-reloaded
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_poker_reloaded"]

</details>


## 🎉 使用

### 规则和玩法

发送 `扑克对决` 命令发起一场对决，发送 `接受` 可以接受群里等待开始的对决(自己接受挑战可以和bot对决)

由于该小游戏需要大量交互，一个群内仅允许同时存在一场对决

游戏开始后，由系统随机选定一名玩家为先手方，后手方获得额外 5 点防御(DEF)，双方初始生命值(HP)为20，初始技能点(SP)为10

牌堆为整副扑克(除去大小王)随机打乱，从先手方开始依次进攻，进攻方抽取三张手牌，从三张手牌中选择一张打出，未打出的牌自动舍弃，防守方无手牌，不能动作

> 如果选择打出点数为ACE(1)的手牌，则发动ACE技能，进行一次六面骰判定，判定结果视为ACE牌点数，将三张手牌都作为技能牌打出

进攻方出牌后，若防守方技能点大于0，则进行一次二十面骰判定，若技能点不小于判定点数，则将牌堆顶的一张牌作为技能牌打出

所有技能牌都会扣除相应点数的技能点

结算时，攻击优先扣除对方防御值，未造成伤害也会消耗吸血附魔，无论是否受到攻击，防守方防御值大于10时，使防御值强制变为10，大于0小于等于10时，自动降低2

如果防守方技能点不小于0，则下一轮攻守交换，如果技能点小于0，触发力竭，跳过行动回合并使技能点回复至5点

每张牌的效果如下

|            | ♠黑桃 | ♥红桃 | ♣梅花 | ♦方片 |
| ---------- | ------ | ------ | ------ | ------ |
| 普通手牌   | 防御   | 回血   | 技能   | 攻击   |
| 进攻技能牌 | 盾击   | 吸血   | 吟唱   | 燃血   |
| 防守技能牌 | 碎甲   | 再生   | 打断   | 反击   |

<details>
<summary>详细解释</summary>

> 假设牌的点数为 `p`，则按照花色及牌的种类触发效果
>
> 防御：使自己的防御值(DEF)增加 `p`
>
> 回血：使自己的生命值(HP)回复 `p`
>
> 技能：使自己的技能点(SP)增加 `p`，进行一次二十面骰判定，若技能点不小于判定结果，则判定成功，将本回合其他两张手牌作为技能牌打出
>
> 攻击：本回合将对对方发动 `p`点攻击
>
> 盾击：黑桃牌作为进攻技能牌打出时，对对方发动 `p/2`点攻击，令自己防御值增加 `p/2`
>
> 吸血：回复 `p/2`点生命值，并获得吸血附魔(可叠加)，在下次发动攻击时，消耗所有附魔，若使对方生命值减少，则获得对方损失生命值一半的生命值
>
> 吟唱：使自己技能点增加 `p`，并额外打出一张随机技能牌(此牌花色一定不是梅花，点数为4到8之间)
>
> 燃血：使自己生命值降低 `p/2`点，对对方发动 `1.5*p`攻击
>
> 碎甲：使自己防御值提高 `p/2`，若该回合受到伤害，则令对方防御值减少 `p`
>
> 再生：使自己生命值回复 `p/2`，若该回合受到伤害，则额外回复 `p`
>
> 打断：此技能不消耗技能点，使对方技能点减少 `p`
>
> 反击：对对方发动 `p/2`点攻击，若该回合受到伤害，反伤 `50%`，反伤无视防御

---

</details>

任意一方血量低于 ***0*** 时游戏结束，任意一方血量保持在 ***45*** 以上超过一个回合，且作为防守方结算时血量仍大于 ***45*** ，则该玩家肉身成圣

若牌库已空时胜负未分，则血量高者获胜
