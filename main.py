from astrbot.api.message_components import *
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.api.all import *
import json
import requests
import io
import base64
import PIL as pillow

@register("astrbot_plugin_for_sd_webui", "xiewoc ", "extention in astrbot for stable diffusion webui(api)", "0.0.1", "https://github.com/xiewoc/astrbot_plugin_for_sd_webui")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
    
    # 注册指令的装饰器。
    @filter.command("draw")
    async def draw(self, event: AstrMessageEvent, message: str):
        '''这是 /draw 指令'''
        
        url = "http://127.0.0.1:7860"
        prompt = message
        negative_prompt = "(worst quality:2), (low quality:2), (normal quality:2), lowres, ((monochrome)), ((grayscale)), bad anatomy,DeepNegative, skin spots, acnes, skin blemishes,(fat:1.2),facing away, looking away,tilted head, lowres,bad anatomy,bad hands, missing fingers,extra digit, fewer digits,bad feet,poorly drawn hands,poorly drawn face,mutation,deformed,extra fingers,extra limbs,extra arms,extra legs,malformed limbs,fused fingers,too many fingers,long neck,cross-eyed,mutated hands,polar lowres,bad body,bad proportions,gross proportions,missing arms,missing legs,extra digit, extra arms, extra leg, extra foot,teethcroppe,signature, watermark, username,blurry,cropped,jpeg artifacts,text,error,"
 
        payload = {
 
            # 模型设置
        "override_settings":{
              "sd_model_checkpoint": "anything-v4.0.ckpt",
              "sd_vae": "animevae.pt",
              "CLIP_stop_at_last_layers": 2,
        },
 
            # 基本参数
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "steps": 28,
        "sampler_name": "Euler a",
        "width": 512,
        "height": 512,
        "batch_size": 1,
        "n_iter": 1,
        "seed": -1,
        "CLIP_stop_at_last_layers": 2,
 
            # 面部修复 face fix
        "restore_faces": False,
 
            #高清修复 highres fix
            # "enable_hr": True,
            # "denoising_strength": 0.4,
            # "hr_scale": 2,
            # "hr_upscaler": "Latent",
     
        }
 
        response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)
        r = response.json()
        image = pillow.Image.open(io.BytesIO(base64.b64decode(r['images'][0])))
        image.save('output.png')
        chain = [
            At(qq=event.get_sender_id()), # At 消息发送者
            Plain("你要的图："), 
            Image.fromFileSystem(r"./output.png"), # 从本地文件目录发送图片
        ]
        yield event.chain_result(chain)
