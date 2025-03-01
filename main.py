from astrbot.api.message_components import *
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.api.all import *
import json
import requests
import io
import base64
import re
from PIL import Image as pillow

# 定义全局变量
global url, model_name, step, sampler, height, width, CLIP, seed, prompt, negtive_prompt

url = ''
model_name = ''
step = 0
sampler = ''
height = 0
width = 0
CLIP = 0
seed = 0
prompt = ''
negtive_prompt = ''

def text2image(url, model_name, step, sampler, height, width, CLIP, seed, prompt, negtive_prompt): 
    payload = {
        # 模型设置
        "override_settings": {
            "sd_model_checkpoint": model_name,
            "sd_vae": "",
            "CLIP_stop_at_last_layers": CLIP,
        },
        # 基本参数
        "prompt": prompt,
        "negative_prompt": negtive_prompt,
        "steps": step,
        "sampler_name": sampler,
        "width": width,
        "height": height,
        "batch_size": 1,
        "n_iter": 1,
        "seed": seed,
        "CLIP_stop_at_last_layers": CLIP,
    }

    response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)
    r = response.json()
    image = pillow.open(io.BytesIO(base64.b64decode(r['images'][0])))
    image.save(os.path.join(os.path.dirname(os.path.abspath(__file__)),'output.png'))

@register("astrbot_plugin_for_sd_webui", "xiewoc ", "extention in astrbot for stable diffusion webui(api)", "1.0.0", "https://github.com/xiewoc/astrbot_plugin_for_sd_webui")
class astrbot_plugin_for_sd_webui(Star):
    def __init__(self, context: Context, config: dict):
        super().__init__(context)
        self.config = config

        # 获取顶级配置
        global url
        url = self.config.get('api_address', 'http://127.0.0.1:7860')

        # 获取子配置
        sub_config = self.config.get('sub_config', {})

        global model_name, step, sampler, height, width, CLIP, seed, negtive_prompt
        model_name = sub_config.get('model', '')
        step = sub_config.get('step', 28)
        sampler = sub_config.get('sampler', 'Euler a')
        height = sub_config.get('height', 512)
        width = sub_config.get('width', 512)
        CLIP = sub_config.get('CLIP', 2)
        seed = sub_config.get('seed', -1)
        negtive_prompt = sub_config.get('negtive_prompt', 'nsfw')

    @filter.command("draw")
    async def draw(self, event: AstrMessageEvent):
        '''这是 /draw 指令'''
        global url, model_name, step, sampler, height, width, CLIP, seed, prompt, negtive_prompt
        for item in event.message_obj.message:
            if isinstance(item, Plain):
                result = re.sub(r'\b/draw\b', '', item.text)
                prompt =  result # 使用传入的消息作为提示词

        text2image(url, model_name, step, sampler, height, width, CLIP, seed, prompt, negtive_prompt)

        chain = [
            At(qq=event.get_sender_id()),  # At 消息发送者
            Plain("你要的图："),
            Image.fromFileSystem(os.path.join(os.path.dirname(os.path.abspath(__file__)),'output.png')),  # 从本地文件目录发送图片
        ]
        yield event.chain_result(chain)
