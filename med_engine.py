# med_engine.py - VERSION 11.5 - CLOUD-READY OS-AGNOSTIC PATHING
import os
import jinja2
import base64
import json
import uuid
import platform
from pydantic import BaseModel
from typing import List, Dict, Any, Tuple
from html2image import Html2Image
from PIL import Image
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
    def __init__(self, content: InfographicContent, brand_data: Dict[str, Any]):
        self.content = content
        self.brand = brand_data
        self.template_loader = jinja2.FileSystemLoader(searchpath="./")
        self.template_env = jinja2.Environment(loader=self.template_loader)
        self.all_icons = self._hunt_for_assets()

    def _hunt_for_assets(self) -> Dict[str, str]:
        found = {}
        assets_dir = "assets"
        if not os.path.exists(assets_dir): return found
        
        for file in os.listdir(assets_dir):
            if file.lower().endswith(('.png', '.svg', '.jpg', '.jpeg')):
                path = os.path.join(assets_dir, file)
                with open(path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode('utf-8')
                    ext = file.split('.')[-1].lower()
                    mime = "image/svg+xml" if ext == 'svg' else f"image/{ext}"
                    found[file] = f"data:{mime};base64,{b64}"
        return found

    def draw(self) -> Image.Image:
        template = self.template_env.get_template("infographic_template.html")
        
        safe_config = {}
        for block in self.content.blocks:
            sid = block.section_id
            safe_config[sid] = {
                "label_text": str(CARD_STYLE_OVERRIDES.get(sid, {}).get("label_text", sid)),
                "icon_file": str(CARD_STYLE_OVERRIDES.get(sid, {}).get("icon_file", "")),
                "card_bg_color": str(CARD_STYLE_OVERRIDES.get(sid, {}).get("card_bg_color", "#FFFFFF")),
                "border_color": str(CARD_STYLE_OVERRIDES.get(sid, {}).get("border_color", "#E2E8F0")),
                "label_color": str(CARD_STYLE_OVERRIDES.get(sid, {}).get("label_color", "#1E293B")),
                "p_bullet_color": str(CARD_STYLE_OVERRIDES.get(sid, {}).get("p_bullet_color", "#1A1A1A")),
                "s_bullet_color": str(CARD_STYLE_OVERRIDES.get(sid, {}).get("s_bullet_color", "#475569"))
            }

        html_string = template.render(
            content=self.content, assets=self.all_icons, config=safe_config, all_icons=self.all_icons,
            global_style=GLOBAL_STYLE, header_style=HEADER_STYLE, footer_style=FOOTER_STYLE
        )
        
        # THE FIX: OS-Agnostic Headless Browser Configuration
        if platform.system() == "Windows":
            chrome_path, edge_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe", r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
            hti = Html2Image(browser_executable=chrome_path) if os.path.exists(chrome_path) else Html2Image(browser_executable=edge_path) if os.path.exists(edge_path) else Html2Image()
        else:
            # Streamlit Cloud (Debian Linux) path mapping
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
                    
        # Crop empty space at the bottom
        bg = Image.new(img.mode, img.size, img.getpixel((0, img.height - 1)))
        diff = ImageChops.difference(img, bg)
        diff = ImageChops.add(diff, diff, 2.0, -100)
        bbox = diff.getbbox()
        if bbox: img = img.crop((0, 0, img.width, bbox[3] + 40))
            
        return img