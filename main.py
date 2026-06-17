"""
δ-me13 控制台 — KiraAI 插件

注册一个科幻主题的管理面板页面，包含文件夹导航、科幻背景特效、
以及 KiraAI 系统管理视图（概览、提供商、适配器等）。

同时注册 Omphalos 模拟世界工具，允许 LLM 通过工具与翁法罗斯世界交互。
"""

import json
import os
import random
from pathlib import Path

from core.plugin import BasePlugin, register, PluginPage, PageMenu
from core.plugin import on, Priority
from core.chat import KiraMessageBatchEvent


_omphalos_locations = [
    {"id": "okhema", "name": "奥赫玛", "desc": "翁法罗斯的核心城邦，黄金裔的据点"},
    {"id": "abyss", "name": "深渊长阶", "desc": "通往深渊的长阶，泰坦的封印之地"},
    {"id": "crest", "name": "天岩山脊", "desc": "高耸入云的山脊，遍布古老遗迹"},
    {"id": "grove", "name": "星月林地", "desc": "被星光照耀的林地，资源丰富"},
    {"id": "forge", "name": "熔火锻炉", "desc": "泰坦的铸造之地，热浪滚滚"},
]

_omphalos_npcs = [
    {"id": "elder", "name": "贤者", "location": "okhema", "desc": "奥赫玛的长者，知晓许多秘密"},
    {"id": "merchant", "name": "游商", "location": "okhema", "desc": "穿梭于城邦间的商人"},
    {"id": "guard", "name": "守卫", "location": "crest", "desc": "守卫天岩山脊的战士"},
    {"id": "hermit", "name": "隐士", "location": "grove", "desc": "隐居星月林地的神秘人"},
]

_omphalos_state = {
    "day": 1,
    "current_location": "okhema",
    "embers_collected": 0,
    "dark_tide_level": "安定",
    "locations": {loc["id"]: {"visited": False} for loc in _omphalos_locations},
    "npcs_met": [],
    "log": [],
}


def _get_data_dir(plugin) -> Path:
    return plugin.ctx.get_plugin_data_dir()


def _load_state(plugin) -> dict:
    d = _get_data_dir(plugin)
    f = d / "omphalos_state.json"
    if f.exists():
        try:
            return json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            pass
    return dict(_omphalos_state)


def _save_state(plugin, state: dict):
    d = _get_data_dir(plugin)
    d.mkdir(parents=True, exist_ok=True)
    f = d / "omphalos_state.json"
    f.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def _log(plugin, state: dict, entry: str):
    state["log"].append(f"[第{state['day']}天] {entry}")
    if len(state["log"]) > 50:
        state["log"] = state["log"][-50:]
    _save_state(plugin, state)


class Me13Plugin(BasePlugin):
    """δ-me13 控制台插件"""

    # ── WebUI Page ──────────────────────────────────────────────────

    @register.page(
        route="/",
        auth=False,
        menu=PageMenu(
            label="δ-me13 控制台",
            icon="Monitor",
            order=10,
        ),
    )
    def main_page(self):
        """提供科幻主题 SPA 管理面板"""
        return PluginPage.from_folder("./web")

    # ── LLM Config API ──────────────────────────────────────────────

    @register.api(method="GET", path="/llm-config", auth=True)
    def get_llm_config(self):
        """返回插件配置中的 LLM 连接信息，供前端 iframe 使用。"""
        llm = self.plugin_cfg.get("section_llm", {})
        return {
            "api_key": llm.get("api_key", ""),
            "base_url": llm.get("base_url", ""),
            "model": llm.get("model", ""),
            "temperature": llm.get("temperature", 0.7),
        }

    # ── Omphalos Simulation Tools ──────────────────────────────────

    @register.tool(
        name="omphalos_status",
        description="查看翁法罗斯模拟世界的当前状态，包括当前地点、已收集火种、黑暗潮汐等级",
        params={
            "type": "object",
            "properties": {},
            "required": [],
        },
    )
    async def tool_omphalos_status(self, event: KiraMessageBatchEvent, *_):
        """查看翁法罗斯世界状态"""
        state = _load_state(self)
        lines = [
            f"📅 第 {state['day']} 天",
            f"📍 当前位置：{state['current_location']}",
            f"🔥 已收集火种：{state['embers_collected']}",
            f"🌊 黑暗潮汐：{state['dark_tide_level']}",
            "",
            "🏛️ 已探索地区：",
        ]
        for loc_id, info in state["locations"].items():
            loc = next((l for l in _omphalos_locations if l["id"] == loc_id), None)
            if loc:
                visited = "✅" if info["visited"] else "❌"
                lines.append(f"  {visited} {loc['name']} — {loc['desc']}")
        if state["npcs_met"]:
            lines.append("")
            lines.append("👤 已遇见的角色：")
            for nid in state["npcs_met"]:
                npc = next((n for n in _omphalos_npcs if n["id"] == nid), None)
                if npc:
                    lines.append(f"  • {npc['name']}")
        if state["log"]:
            lines.append("")
            lines.append("📝 最近事件：")
            for entry in state["log"][-5:]:
                lines.append(f"  {entry}")
        return "\n".join(lines)

    @register.tool(
        name="omphalos_move",
        description="移动到翁法罗斯世界的另一个地区",
        params={
            "type": "object",
            "properties": {
                "location_id": {
                    "type": "string",
                    "description": "目标地区ID：" + ", ".join(f'{l["id"]}({l["name"]})' for l in _omphalos_locations),
                }
            },
            "required": ["location_id"],
        },
    )
    async def tool_omphalos_move(self, event: KiraMessageBatchEvent, *_, location_id: str):
        """移动到指定地区"""
        state = _load_state(self)
        target = next((l for l in _omphalos_locations if l["id"] == location_id), None)
        if not target:
            return f"❌ 找不到地区：{location_id}。可选地区：" + ", ".join(l["id"] for l in _omphalos_locations)
        old = state["current_location"]
        state["current_location"] = location_id
        state["locations"][location_id]["visited"] = True
        state["day"] += 1
        _log(self, state, f"从 {old} 移动到 {target['name']}")
        return f"✅ 已移动到 {target['name']}（{target['desc']}）\n天数推进到第 {state['day']} 天。"

    @register.tool(
        name="omphalos_explore",
        description="探索当前所在地区，发现资源和线索",
        params={
            "type": "object",
            "properties": {},
            "required": [],
        },
    )
    async def tool_omphalos_explore(self, event: KiraMessageBatchEvent, *_):
        """探索当前地区"""
        state = _load_state(self)
        loc = next((l for l in _omphalos_locations if l["id"] == state["current_location"]), None)
        name = loc["name"] if loc else state["current_location"]
        # 随机探索结果
        outcomes = [
            f"你在{name}的废墟中发现了一些古代文献，记录了泰坦封印的秘密。",
            f"你在{name}的集市上听到旅人谈论远处黑暗潮汐的异动。",
            f"你在{name}的角落里找到了一枚闪亮的火种碎片。",
            f"你在{name}的遇到了一位本地居民，他告诉了你一些有用的情报。",
            f"你在{name}探索了一番，发现了一条通往未知区域的小径。",
        ]
        result = random.choice(outcomes)
        if "火种" in result:
            state["embers_collected"] += 1
        state["day"] += 1
        _log(self, state, result)
        return f"🔍 {result}\n天数推进到第 {state['day']} 天。"

    @register.tool(
        name="omphalos_interact",
        description="与翁法罗斯世界中的角色交谈或互动",
        params={
            "type": "object",
            "properties": {
                "npc_id": {
                    "type": "string",
                    "description": "角色ID：" + ", ".join(f'{n["id"]}({n["name"]})' for n in _omphalos_npcs),
                },
                "message": {
                    "type": "string",
                    "description": "你想对角色说的话",
                },
            },
            "required": ["npc_id", "message"],
        },
    )
    async def tool_omphalos_interact(self, event: KiraMessageBatchEvent, *_, npc_id: str, message: str):
        """与NPC互动"""
        state = _load_state(self)
        npc = next((n for n in _omphalos_npcs if n["id"] == npc_id), None)
        if not npc:
            return f"❌ 找不到角色：{npc_id}"
        if npc_id not in state["npcs_met"]:
            state["npcs_met"].append(npc_id)
        state["day"] += 1
        _log(self, state, f"与 {npc['name']} 交谈：{message}")
        responses = {
            "elder": "贤者抚须沉思道：『火种的力量在召唤你，但黑暗也在逼近。』",
            "merchant": "游商笑着说：『我听说过一些关于泰坦封印的事，也许你能在深渊长阶找到答案。』",
            "guard": "守卫挺直腰板：『天岩山脊一切安好，但最近总有些奇怪的声音从山腹中传来。』",
            "hermit": "隐士低语：『星月林地藏着古老的秘密，但我不能告诉你太多——有些路必须自己走。』",
        }
        reply = responses.get(npc_id, f"{npc['name']}看着你，微微点头。")
        return f"💬 你对 {npc['name']} 说：「{message}」\n{npc['name']}回应：{reply}\n天数推进到第 {state['day']} 天。"

    @register.tool(
        name="omphalos_advance",
        description="推进翁法罗斯世界的时间，让世界自然演化",
        params={
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": "要推进的天数，默认1天",
                }
            },
            "required": [],
        },
    )
    async def tool_omphalos_advance(self, event: KiraMessageBatchEvent, *_, days: int = 1):
        """推进世界时间"""
        state = _load_state(self)
        days = max(1, min(days, 30))
        state["day"] += days
        _log(self, state, f"时间推进了 {days} 天")
        return f"⏩ 时间推进了 {days} 天。当前是第 {state['day']} 天。"

    # ── Lifecycle ───────────────────────────────────────────────────

    async def initialize(self):
        """插件初始化"""
        self.logger.info("δ-me13 控制台插件已加载")

    async def terminate(self):
        """插件卸载"""
        self.logger.info("δ-me13 控制台插件已卸载")
