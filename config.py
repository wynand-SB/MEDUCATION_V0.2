# config.py - VERSION 11.3 - LOGO POSITIONING & BRANDING

GLOBAL_STYLE = {
    "canvas_width": "1080px",
    "font_family": "'Helvetica Neue', Helvetica, Arial, sans-serif",
    "document_bg_color": "#ffffff",
    "content_padding": "0 30px",         
    "card_radius": "10px",               
    "card_shadow": "0 2px 8px rgba(0,0,0,0.04)", 
    "section_margin_bottom": "30px",     
    "card_header_size": "28px",          
    "primary_text_size": "20px",         
    "secondary_text_size": "16px",       
    "line_height": "1.0"                 
}

HEADER_STYLE = {
    "fallback_bg_color": "#0F172A",         
    "scrim_overlay": "rgba(0, 0, 0, 0.55)", 
    "padding": "40px 50px",                 
    "title_size": "40px",
    "title_color": "#FFFFFF",
    "aka_size": "24px",
    "aka_color": "#E2E8F0",
    
    # --- PRACTICE LOGO POSITIONING (KLINIDOC) ---
    "practice_logo_max_height": "45px",
    "practice_logo_top": "20px",     # Space from top of header
    "practice_logo_right": "20px",   # Space from right of header
    
    # --- DOCTOR IMAGE POSITIONING ---
    "doctor_img_size": "160px",             
    "doctor_bottom": "0px",          # Anchors doctor to the exact bottom line
    "doctor_right": "40px"           # Anchors doctor from the right
}

FOOTER_STYLE = {
    "bg_color": "#41302C",
    "padding": "40px",
    "margin_top": "40px",
    "title_size": "16px",
    "title_color": "#FFFFFF",
    "text_size": "13px",
    "text_color": "#94A3B8",
    
    # --- MEDUCATION LOGO POSITIONING ---
    "meducation_logo_max_height": "90px"
}

CARD_STYLE_OVERRIDES = {
    "SEC_01_DEF": {
        "label_text": "WHAT IS IT?", "icon_file": "icon_def.png",
        "card_bg_color": "#F2F6F4", "border_color": "#179444", "label_color": "#179444", "p_bullet_color": "#1A1A1A", "s_bullet_color": "#475569"
    },
    "SEC_02_ETI": {
        "label_text": "WHY DOES IT HAPPEN?", "icon_file": "icon_eti.png",
        "card_bg_color": "#FFFFFF", "border_color": "#373435", "label_color": "#373435", "p_bullet_color": "#1A1A1A", "s_bullet_color": "#475569"
    },
    "SEC_03_IMP": {
        "label_text": "HOW DOES THIS IMPACT ME?", "icon_file": "icon_imp.png",
        "card_bg_color": "#F2F6F4", "border_color": "#179444", "label_color": "#179444", "p_bullet_color": "#1A1A1A", "s_bullet_color": "#475569"
    },
    "SEC_04_TX": {
        "label_text": "HOW ARE WE TREATING IT?", "icon_file": "icon_tx.png",
        "card_bg_color": "#E4E6E7", "border_color": "#042566", "label_color": "#042566", "p_bullet_color": "#000000", "s_bullet_color": "#333333"
    },
    "SEC_05_MNG": {
        "label_text": "WHAT ELSE CAN I DO?", "icon_file": "icon_mng.png",
        "card_bg_color": "#edf5fc", "border_color": "#2583e8", "label_color": "#2583e8", "p_bullet_color": "#000000", "s_bullet_color": "#333333"
    },
    "SEC_06_FLG": {
        "label_text": "WARNING SIGNS!", "icon_file": "icon_flg.png",
        "card_bg_color": "#F5E9E9", "border_color": "#EE1921", "label_color": "#EE1921", "p_bullet_color": "#5B0E15", "s_bullet_color": "#B02A37"
    },
    "SEC_07_SUC": {
        "label_text": "HOW WILL WE KNOW IT'S BETTER?", "icon_file": "icon_suc.png",
        "card_bg_color": "#F2F6F4", "border_color": "#179444", "label_color": "#179444", "p_bullet_color": "#1A1A1A", "s_bullet_color": "#2E3B32"
    }
}