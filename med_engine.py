# med_engine.py - VERSION 11.6 - CLOUD-READY & IMPORT PATCH
import os
import jinja2
import base64
import json
import uuid
import platform
from pydantic import BaseModel
from typing import List, Dict, Any, Tuple
from html2image import Html2Image
from PIL import Image, ImageChops
from config import CARD_STYLE_OVERRIDES, GLOBAL_STYLE, HEADER_STYLE, FOOTER_STYLE

class BulletNuance(BaseModel):
    target_variable: str; statement_text: str; caregiver_statement: str; nuance_transition: str; priority: int = 999

class BulletData(BaseModel):
    primary_text: str; sub_bullets: List[str]; icon_name: str = None

class SectionBlock(BaseModel):
    section_id: str; bullets: List[BulletData]

class InfographicContent(BaseModel):
    blocks: List[SectionBlock]; indication_name: str; indication_aka: str = ""; indication_code: str; references: List[str] = []

def apply_hierarchical_logic(u_row: Dict[str, Any], nuances: List[BulletNuance], is_cg: bool) -> Tuple[str, List[str]]:
    primary = ""
    if is_cg:
        cg_text = str(u_row.get('Caregiver_Statement', "")).strip()
        primary = cg_text if cg_text and cg_text.lower() != 'nan' else str(u_row.get('Statement_Text', "")).strip()
    else:
        primary = str(u_row.get('Statement_Text', "")).strip()
        
    subs = []
    if nuances:
        top_n = nuances[0]
        t_text = str(top_n.caregiver_statement).strip() if is_cg else str(top_n.statement_text).strip()
        if not t_text or t_text.lower() == 'nan': t_text = str(top_n.statement_text).strip()
        t_trans = str(top_n.nuance_transition).strip()
        if t_text and t_text.lower() != 'nan':
            if t_trans and t_trans.lower() != 'nan': primary = primary + " " + t_trans + " " + t_text
            else: primary = primary + " " + t_text
        for n in nuances[1:]:
            s_text = str(n.caregiver_statement).strip() if is_cg else str(n.statement_text).strip()
            if not s_text or s_text.lower() == 'nan': s_text = str(n.statement_text).strip()
            if s_text and s_text.lower() != 'nan': subs.append(s_text)
    return primary, subs

class BrandedMobileEngine:
    def __init__(self, content: InfographicContent, brand_data: dict = None):
        self.content = content
        self.brand_data = brand_data or {}

        # Aggressive search for the brand logos
        self.b64_assets = {
            "logo": self._get_base64_image(self.brand_data.get("assets", {}).get("practice_logo", "logo.png")),
            "doctor": self._get_base64_image(self.brand_data.get("assets", {}).get("doctor_headshot", "doctor.png")),
            "header_bg": self._get_base64_image(self.brand_data.get("assets", {}).get("header_bg", "header_bg.png")),
            "meducation_logo": self._get_base64_image("brand_logo.png") or self._get_base64_image("meducation_logo.png") or self._get_base64_image("brand_logo.jpg.jpg")
        }

        icon_list = ["icon_def.png", "icon_eti.png", "icon_imp.png", "icon_tx.png", "icon_mng.png", 
                     "icon_flg.png", "icon_suc.png", "icon_diet.png", "icon_active.png", "icon_env.png", "icon_warning.png", "icon_route_oral.png"]
        self.all_icons = {icon: self._get_base64_image(icon) for icon in icon_list}

        template_loader = jinja2.FileSystemLoader(searchpath=os.path.dirname(os.path.abspath(__file__)))
        self.env = jinja2.Environment(loader=template_loader)

    def _get_base64_image(self, filename: str) -> str:
        if not filename: return ""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        cwd = os.getcwd()
        search_paths = [os.path.join(cwd, filename), os.path.join(cwd, "assets", filename),
                        os.path.join(cwd, "data", filename), os.path.join(base_dir, filename), 
                        os.path.join(base_dir, "assets", filename), filename]
        for path in search_paths:
            if os.path.exists(path):
                with open(path, "rb") as img_file:
                    b64_string = base64.b64encode(img_file.read()).decode('utf-8')
                    mime = "image/jpeg" if path.lower().endswith(('.jpg', '.jpeg')) else "image/png"
                    return f"data:{mime};base64,{b64_string}"
        return "" 

    def draw(self, output_filename="render_output.png") -> Image.Image:
        template = self.env.get_template("infographic_template.html")
        
        safe_config = {}
        for sec_id, cfg in CARD_STYLE_OVERRIDES.items():
            safe_config[sec_id] = {}
            for key, val in cfg.items():
                if "color" in key and isinstance(val, list) and len(val) == 3:
                    safe_config[sec_id][key] = f"rgb({val[0]}, {val[1]}, {val[2]})"
                else: safe_config[sec_id][key] = val
            
            if sec_id == "SEC_06_FLG" and "s_bullet_color" not in safe_config[sec_id]:
                safe_config[sec_id]["s_bullet_color"] = safe_config[sec_id].get("p_bullet_color", "#DC3545")

        html_string = template.render(
            content=self.content, brand=self.brand_data, assets=self.b64_assets,
            config=safe_config, all_icons=self.all_icons,
            global_style=GLOBAL_STYLE, header_style=HEADER_STYLE, footer_style=FOOTER_STYLE
        )
        
        # OS-Agnostic Headless Browser Configuration
        if platform.system() == "Windows":
            chrome_path, edge_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe", r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
            hti = Html2Image(browser_executable=chrome_path) if os.path.exists(chrome_path) else Html2Image(browser_executable=edge_path) if os.path.exists(edge_path) else Html2Image()
        else:
            hti = Html2Image(browser_executable='/usr/bin/chromium')
            
        hti.size = (1080, 4000) 
        unique_id = uuid.uuid4().hex
        temp_html_path = os.path.abspath(f"temp_render_{unique_id}.html")
        unique_output_png = f"render_output_{unique_id}.png"
        
        with open(temp_html_path, "w", encoding="utf-8") as f: f.write(html_string)
        
        if platform.system() == "Windows":
            file_url = "file:///" + temp_html_path.replace("\\", "/")
        else:
            file_url = "file://" + temp_html_path
        
        try:
            hti.screenshot(url=file_url, save_as=unique_output_png)
            with Image.open(unique_output_png) as temp_img: img = temp_img.convert("RGB")
        finally:
            for temp_file in [temp_html_path, unique_output_png]:
                if os.path.exists(temp_file):
                    try: os.remove(temp_file)
                    except: pass
                    
        # Crop empty space at the bottom (Now properly using ImageChops)
        bg = Image.new(img.mode, img.size, (255, 255, 255))
        diff = ImageChops.difference(img, bg)
        diff = ImageChops.add(diff, diff, 2.0, -100)
        bbox = diff.getbbox()
        if bbox: img = img.crop((0, 0, 1080, bbox[3] + 40))
            
        return img
