import asyncio
from nonebot import get_driver, require
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import on_alconna, Alconna, Args, Match
from nonebot_plugin_uninfo import Uninfo
from zhenxun.utils.message import MessageUtils
from .utils import *

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

__plugin_meta__ = PluginMetadata(
    name="扑克对决",
    description="对[MoonofBridge24/nonebot_plugin_poker](https://github.com/MoonofBridge24/nonebot_plugin_poker)进行了重构，使用alconna以兼容几乎所有适配器，详细请见仓库",
    usage="扑克对决/卡牌对决/接受：发起或接受对决\n重置对决：允许参与者或者群管重置本群对决\n出牌 1/2/3：出牌命令",
    type="application",
    homepage="https://github.com/haorwen/nonebot-plugin-poker-reloaded",
    supported_adapters={"~"},
)

poker_state = {}
async def reset(group: int = 0):
    '数据初始化'
    global poker_state
    if not group: poker_state = {}
    else: poker_state[group] = {
        'time': int(time.time()),
        'player1': {
            'uin': 0,
            'name': '',
            'HP': 20.0,
            'ATK': 0,
            'DEF': 0.0,
            'SP': 10,
            'suck': 0,
            'hand': []
        },
        'player2': {
            'uin': 0,
            'name': '',
            'HP': 20.0,
            'ATK': 0,
            'DEF': 5.0,
            'SP': 10,
            'suck': 0,
            'hand': []
        },
        'deck': [],
        'winer': ''
    }

driver = get_driver()
@driver.on_startup
async def on_startup_():
    await reset()

# 定时清理超时对决
@scheduler.scheduled_job("interval", minutes=1, id="poker_timeout_clean")
async def clear_timeout():
    now_time = int(time.time())
    keys = [key for key in poker_state.keys() if (now_time - poker_state[key]['time'] > 90)]
    for key in keys:
        del poker_state[key]

# 发起/接受对决
poker = on_alconna(
    Alconna("卡牌对决", Args["action?", str]),
    aliases={"接受", "扑克对决"},
    use_cmd_start=True,
)

@poker.handle()
async def _(session: Uninfo, action: Match[str]):
    group_id = session.group.id
    user_id = session.user.id
    nickname = session.user.name
    if not group_id in poker_state:
        await reset(group_id)
    state = poker_state[group_id]
    if state['player1']['hand']:
        await MessageUtils.build_message('有人正在对决呢，等会再来吧~').send()
        return
    state['time'] = int(time.time())
    await start_game(session, group_id, user_id, nickname, state)

# 出牌
hand_out = on_alconna(
    Alconna("出牌", Args["choice", int]),
    use_cmd_start=True,
)

@hand_out.handle()
async def _(session: Uninfo, choice: Match[int]):
    group_id = session.group.id
    user_id = session.user.id
    if not group_id in poker_state:
        await reset(group_id)
    state = poker_state[group_id]
    if not state['player1']['hand']:
        await MessageUtils.build_message('对决还没开始呢，发起一轮新对决吧~').send()
        return
    if state['player1']['uin'] != user_id:
        await MessageUtils.build_message('没牌的瞎出干什么').send()
        return
    if not choice.result or not (choice.result in range(1, len(state['player1']['hand'])+1)):
        await MessageUtils.build_message('请正确输入出牌序号').send()
        return
    state['time'] = int(time.time())
    await process_hand_out(session, group_id, choice.result, state)

# 重置对决
reset_game = on_alconna(
    Alconna("重置对决"),
    use_cmd_start=True,
)

@reset_game.handle()
async def _(session: Uninfo):
    group_id = session.group.id
    user_id = session.user.id
    if not group_id in poker_state:
        await reset(group_id)
    state = poker_state[group_id]
    if user_id not in [state['player1']['uin'], state['player2']['uin']]:
        await MessageUtils.build_message('你无权操作，请稍后再试').send()
        return
    await reset(group_id)
    await MessageUtils.build_message('重置成功，再来一局吧').send()

# 业务逻辑迁移
async def start_game(session: Uninfo, group_id: int, user_id: int, nickname: str, state: PokerState):
    if not state['player1']['uin']:
        state['player1']['uin'] = user_id
        state['player1']['name'] = nickname
        await MessageUtils.build_message(f'{nickname} 发起了一场对决，正在等待群友接受对决...\n(1分钟后自动超时)').send()
        return
    state['player2']['name'] = nickname
    if state['player1']['uin'] == user_id:
        state['player2']['name'] = 'BOT'
    else:
        state['player2']['uin'] = user_id
    if random.randint(0, 1):
        state['player1']['name'], state['player2']['name'], state['player1']['uin'], state['player2']['uin'] = state['player2']['name'], state['player1']['name'], state['player2']['uin'], state['player1']['uin']
    await MessageUtils.build_message('唰唰唰 正在洗牌...').send()
    await asyncio.sleep(0.5)
    msg = await info_show(state)
    if not state['player1']['uin']:
        pick = random.randint(1, len(state['player1']['hand']))
        await MessageUtils.build_message(msg).send()
        await process_hand_out(session, group_id, pick, state)
        return
    await MessageUtils.build_message(msg).send()

async def process_hand_out(session: Uninfo, group_id: int, choice: int, state: PokerState):
    msgs = await play_poker(state, choice - 1)
    msg = await info_show(state)
    while not state['player1']['uin'] and not state['winer']:
        msgs.append(msg)
        pick = random.randint(1, len(state['player1']['hand']))
        msgs += await play_poker(state, pick - 1)
        msg = await info_show(state)
    for i in msgs:
        await MessageUtils.build_message(i).send()
    if state['winer']:
        await reset(group_id)
        await MessageUtils.build_message(msg).send()
    else:
        await MessageUtils.build_message(msg).send()

