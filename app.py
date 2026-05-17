# app.py - VERSION 10.1 - VIDEO OPACITY CONTROL & ZERO-SCROLL
import streamlit as st
import pandas as pd
import json
import os
import io
import base64
from med_engine import BrandedMobileEngine, apply_hierarchical_logic, BulletNuance, BulletData, SectionBlock, InfographicContent
from med_sidebar import render_indication_selector, render_intake

with open("indication_registry.json", "r") as file:
    INDICATION_MAP = json.load(file)

PRIORITY_MAP = {
    "Pregnancy_T1": 1, "Renal_Impaired_Severe_ESRD": 2, "Hepatic_Impaired": 3,
    "Age_Infant_1_12m": 5, "Age_Toddler_1_3y": 7, "Age_Elderly_65_79y": 8
}

def load_indication_registry():
    if os.path.exists("indication_registry.json"):
        with open("indication_registry.json", "r") as f: return json.load(f)
    return {}

def inject_modern_ui():
    video_path = os.path.join("assets", "Background_Animation.mp4")
    video_html = ""
    
    if os.path.exists(video_path):
        with open(video_path, "rb") as video_file: video_bytes = video_file.read()
        encoded_video = base64.b64encode(video_bytes).decode('utf-8')
        
        # THE UPDATE: Added `opacity: 0.5;` to the inline video style
        video_html = f'''
            <div id="video-viewport-lock" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -99999; overflow: hidden; pointer-events: none; background-color: #000000;">
                <video autoplay loop muted playsinline style="min-width: 100%; min-height: 100%; width: 100vw; height: 100vh; object-fit: cover; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); opacity: 0.5;">
                    <source src="data:video/mp4;base64,{encoded_video}" type="video/mp4">
                </video>
            </div>
        '''
    else:
        video_html = '<div style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -99999; background: #0f2027;"></div>'

    custom_css = """
    <style>
        /* 1. NUCLEAR OPTION: KILL ALL SCROLLBARS GLOBALLY */
        html, body, [data-testid="stAppViewContainer"], .stApp {
            overflow: hidden !important;
            margin: 0 !important;
            padding: 0 !important;
            height: 100vh !important;
            width: 100vw !important;
            background: transparent !important;
        }
        
        /* Kill the default header bar */
        header[data-testid="stHeader"] { display: none !important; }
        
        /* 2. ABSOLUTE POSITIONING: Locked exactly to the center of the laptop screen */
        .block-container, [data-testid="stAppViewBlockContainer"], [data-testid="stMainBlockContainer"] {
            position: absolute !important;
            top: 50% !important;
            left: 50% !important;
            transform: translate(-50%, -50%) !important;
            
            height: 85vh !important;
            width: 90vw !important;
            max-width: 1100px !important; 
            
            background-color: rgba(17, 24, 39, 0.88) !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            border-radius: 20px !important;
            padding: 2rem 3rem !important;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.8) !important;
            backdrop-filter: blur(15px) !important;
            -webkit-backdrop-filter: blur(15px) !important;
            z-index: 1 !important;
            
            /* Hide internal scrollbar but allow mousewheel ONLY if on a tiny netbook */
            overflow-y: auto !important;
            -ms-overflow-style: none;
            scrollbar-width: none;
        }
        .block-container::-webkit-scrollbar { display: none; }
        
        /* Tab Styling overrides to match the dark glass */
        .stTabs [data-baseweb="tab-list"] { background-color: transparent; }
        .stTabs [data-baseweb="tab"] { color: #e2e8f0; }
    </style>
    """
    st.markdown(video_html + custom_css, unsafe_allow_html=True)

def main():
    st.set_page_config(page_title="MEDUCATION V10.1", layout="wide", initial_sidebar_state="collapsed")
    inject_modern_ui()

    if 'page' not in st.session_state: st.session_state.page = 'intake'
    if 'needs_generation' not in st.session_state: st.session_state.needs_generation = False

    branding_path = "branding.json"
    if os.path.exists(branding_path):
        with open(branding_path, "r") as f: brand_data = json.load(f)
    else:
        st.error("Branding file missing.")
        return

    FULL_INDICATION_MAP = load_indication_registry()
    AVAILABLE_INDICATIONS = {icd: data for icd, data in FULL_INDICATION_MAP.items() if os.path.exists(f"MEDUCATION_DATA_{icd}.json") or os.path.exists(os.path.join("data", f"MEDUCATION_DATA_{icd}.json"))}
            
    if not AVAILABLE_INDICATIONS:
        st.warning("No JSON dossier data found. Run the SciBorg Agent first.")
        return

    # ==========================================
    # PAGE 1: CLINICAL INTAKE (LANDING)
    # ==========================================
    if st.session_state.page == 'intake':
        icd = render_indication_selector(AVAILABLE_INDICATIONS)

        if not os.path.exists("data"): os.makedirs("data")
        target_paths = [os.path.join("data", f"MEDUCATION_DATA_{icd}.json"), f"MEDUCATION_DATA_{icd}.json"]
        json_path = next((p for p in target_paths if os.path.exists(p)), None)
        
        if not json_path:
            st.error(f"Data not found for {icd}.")
            return
            
        with open(json_path, 'r', encoding='utf-8') as f: raw_json = json.load(f)
            
        data_list = raw_json.get("Data", [])
        if not data_list: data_list = raw_json.get("data", []) 
            
        df = pd.DataFrame(data_list).fillna('')
        
        if 'Variable_Group' not in df.columns and 'Target_Group' in df.columns:
            df.rename(columns={'Target_Group': 'Variable_Group'}, inplace=True)
        elif 'Variable_Group' not in df.columns:
            df['Variable_Group'] = df['Target_Variable'].apply(lambda x: 'Universal' if x == 'Universal_Statement' else 'Nuance')
            
        if 'Caregiver_Statement' not in df.columns: df['Caregiver_Statement'] = ''
        if 'Route_Icon' not in df.columns: df['Route_Icon'] = ''
        if 'Nuance_Transition' not in df.columns: df['Nuance_Transition'] = ''
        if 'Med_Class_ID' not in df.columns: df['Med_Class_ID'] = ''
        
        df.columns = df.columns.str.strip() 
        for col in df.columns:
            if df[col].dtype == 'object': df[col] = df[col].astype(str).str.strip()

        df_f = df[df['ICD10_ID'] == icd]

        audience, selected_tags, selected_meds = render_intake(df_f, icd)
        
        # Absolute Bottom lock for the button
        st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
        if st.button("🚀 Generate Patient Dossier", type="primary", use_container_width=True):
            st.session_state.df_f = df_f
            st.session_state.icd = icd
            st.session_state.is_caregiver = (audience == "Caregiver")
            st.session_state.selected_tags = selected_tags
            st.session_state.selected_meds = selected_meds
            st.session_state.page = 'dossier'
            st.session_state.needs_generation = True
            st.rerun()

    # ==========================================
    # PAGE 2: DOSSIER RESULTS & DOWNLOAD
    # ==========================================
    elif st.session_state.page == 'dossier':
        
        if st.button("← Back to Clinical Intake", use_container_width=True):
            st.session_state.page = 'intake'
            st.rerun()
            
        st.divider()

        if st.session_state.needs_generation:
            df_f = st.session_state.df_f
            icd = st.session_state.icd
            is_caregiver = st.session_state.is_caregiver
            selected_tags = st.session_state.selected_tags
            selected_meds = st.session_state.selected_meds
            
            blocks = []
            for sid in ["SEC_01_DEF", "SEC_02_ETI", "SEC_03_IMP"]:
                section_bullets = []
                df_s = df_f[df_f['Section_ID'] == sid]
                for bid in df_s['Bullet_ID'].unique():
                    u_row = df_s[(df_s['Bullet_ID'] == bid) & (df_s['Variable_Group'].str.upper() == 'UNIVERSAL')]
                    if u_row.empty: continue
                    n_rows = df_s[(df_s['Bullet_ID'] == bid) & (df_s['Target_Variable'].isin(selected_tags))]
                    nuances = [BulletNuance(target_variable=nr['Target_Variable'], statement_text=nr['Statement_Text'], caregiver_statement=nr['Caregiver_Statement'], nuance_transition=nr['Nuance_Transition'], priority=PRIORITY_MAP.get(nr['Target_Variable'], 999)) for _, nr in n_rows.iterrows()]
                    primary, subs = apply_hierarchical_logic(u_row.iloc[0].to_dict(), sorted(nuances, key=lambda x: x.priority), is_caregiver)
                    section_bullets.append(BulletData(primary_text=primary, sub_bullets=subs))
                if section_bullets: blocks.append(SectionBlock(section_id=sid, bullets=section_bullets))

            tx_med_modules = []
            tx_prefixes = {"B1": "", "B2": "Why are we using it? ", "B3": "You can potentially experience? ", "B4": "How does the body process it? "}
            for med_id in selected_meds:
                med_contents = []
                df_med = df_f[(df_f['Section_ID'] == "SEC_04_TX") & (df_f['Med_Class_ID'].str.upper() == med_id.upper())]
                route_icon = "icon_route_oral.png"
                icon_row = df_med[df_med['Route_Icon'].astype(str).str.strip() != '']
                if not icon_row.empty: route_icon = icon_row.iloc[0]['Route_Icon']

                for bid in ["B1", "B2", "B3", "B4"]:
                    u_row = df_med[(df_med['Bullet_ID'] == bid) & (df_med['Variable_Group'].str.upper() == 'UNIVERSAL')]
                    if not u_row.empty:
                        n_rows = df_med[(df_med['Bullet_ID'] == bid) & (df_med['Target_Variable'].isin(selected_tags))]
                        nuances = [BulletNuance(target_variable=nr['Target_Variable'], statement_text=nr['Statement_Text'], caregiver_statement=nr['Caregiver_Statement'], nuance_transition=nr['Nuance_Transition'], priority=PRIORITY_MAP.get(nr['Target_Variable'], 999)) for _, nr in n_rows.iterrows()]
                        primary, subs = apply_hierarchical_logic(u_row.iloc[0].to_dict(), sorted(nuances, key=lambda x: x.priority), is_caregiver)
                        if primary or subs:
                            full_text = primary + (" " + " ".join(subs) if subs else "")
                            if bid == "B1": med_contents.append(full_text.strip())
                            else: med_contents.append(f"<strong>{tx_prefixes[bid]}</strong>{full_text.strip()}")
                        else: med_contents.append("")
                    else: med_contents.append("") 
                        
                if any(med_contents): tx_med_modules.append(BulletData(primary_text=med_id.upper(), sub_bullets=med_contents, icon_name=route_icon))
            if tx_med_modules: blocks.append(SectionBlock(section_id="SEC_04_TX", bullets=tx_med_modules))

            for sid in ["SEC_05_MNG", "SEC_06_FLG", "SEC_07_SUC"]:
                df_s = df_f[df_f['Section_ID'] == sid]
                
                if sid == "SEC_06_FLG":
                    disease_warnings = []
                    med_warnings = []
                    
                    b3_row = df_s[(df_s['Bullet_ID'] == 'B3') & (df_s['Variable_Group'].str.upper() == 'UNIVERSAL')]
                    if not b3_row.empty:
                        n_rows = df_s[(df_s['Bullet_ID'] == 'B3') & (df_s['Target_Variable'].isin(selected_tags))]
                        nuances = [BulletNuance(target_variable=nr['Target_Variable'], statement_text=nr['Statement_Text'], caregiver_statement=nr['Caregiver_Statement'], nuance_transition=nr['Nuance_Transition'], priority=PRIORITY_MAP.get(nr['Target_Variable'], 999)) for _, nr in n_rows.iterrows()]
                        hero_text, subs = apply_hierarchical_logic(b3_row.iloc[0].to_dict(), sorted(nuances, key=lambda x: x.priority), is_caregiver)
                        if subs: hero_text = hero_text + " " + " ".join(subs)
                        if hero_text: disease_warnings.append(hero_text)

                    b1_row = df_s[(df_s['Bullet_ID'] == 'B1') & (df_s['Variable_Group'].str.upper() == 'UNIVERSAL')]
                    if not b1_row.empty:
                        n_rows = df_s[(df_s['Bullet_ID'] == 'B1') & (df_s['Target_Variable'].isin(selected_tags))]
                        nuances = [BulletNuance(target_variable=nr['Target_Variable'], statement_text=nr['Statement_Text'], caregiver_statement=nr['Caregiver_Statement'], nuance_transition=nr['Nuance_Transition'], priority=PRIORITY_MAP.get(nr['Target_Variable'], 999)) for _, nr in n_rows.iterrows()]
                        b1_text, subs = apply_hierarchical_logic(b1_row.iloc[0].to_dict(), sorted(nuances, key=lambda x: x.priority), is_caregiver)
                        if subs: b1_text = b1_text + " " + " ".join(subs)
                        if b1_text: disease_warnings.append(b1_text)

                    for med_id in selected_meds:
                        b2_row = df_s[(df_s['Bullet_ID'] == 'B2') & (df_s['Med_Class_ID'].str.upper() == med_id.upper()) & (df_s['Variable_Group'].str.upper() == 'UNIVERSAL')]
                        if not b2_row.empty:
                            n_rows = df_s[(df_s['Bullet_ID'] == 'B2') & (df_s['Med_Class_ID'].str.upper() == med_id.upper()) & (df_s['Target_Variable'].isin(selected_tags))]
                            nuances = [BulletNuance(target_variable=nr['Target_Variable'], statement_text=nr['Statement_Text'], caregiver_statement=nr['Caregiver_Statement'], nuance_transition=nr['Nuance_Transition'], priority=PRIORITY_MAP.get(nr['Target_Variable'], 999)) for _, nr in n_rows.iterrows()]
                            b2_text, subs = apply_hierarchical_logic(b2_row.iloc[0].to_dict(), sorted(nuances, key=lambda x: x.priority), is_caregiver)
                            if subs: b2_text = b2_text + " " + " ".join(subs)
                            if b2_text: med_warnings.append(f"<strong>{med_id.upper()}</strong>: {b2_text}")

                    sec6_bullets = []
                    if disease_warnings: sec6_bullets.append(BulletData(primary_text="DISEASE", sub_bullets=disease_warnings))
                    if med_warnings: sec6_bullets.append(BulletData(primary_text="MEDICATION", sub_bullets=med_warnings))
                    if sec6_bullets: blocks.append(SectionBlock(section_id="SEC_06_FLG", bullets=sec6_bullets))
                
                else:
                    section_bullets = []
                    for bid in df_s['Bullet_ID'].unique():
                        u_row = df_s[(df_s['Bullet_ID'] == bid) & (df_s['Variable_Group'].str.upper() == 'UNIVERSAL')]
                        if u_row.empty: continue
                        n_rows = df_s[(df_s['Bullet_ID'] == bid) & (df_s['Target_Variable'].isin(selected_tags))]
                        nuances = [BulletNuance(target_variable=nr['Target_Variable'], statement_text=nr['Statement_Text'], caregiver_statement=nr['Caregiver_Statement'], nuance_transition=nr['Nuance_Transition'], priority=PRIORITY_MAP.get(nr['Target_Variable'], 999)) for _, nr in n_rows.iterrows()]
                        primary, subs = apply_hierarchical_logic(u_row.iloc[0].to_dict(), sorted(nuances, key=lambda x: x.priority), is_caregiver)
                        section_bullets.append(BulletData(primary_text=primary, sub_bullets=subs))
                    if section_bullets: blocks.append(SectionBlock(section_id=sid, bullets=section_bullets))

            if 'Reference_Link' in df_f.columns: raw_refs = df_f['Reference_Link'].dropna().astype(str).str.strip().unique()
            else: raw_refs = []
            references = [r for r in raw_refs if r and r.lower() != 'nan']

            content = InfographicContent(
                blocks=blocks, indication_name=INDICATION_MAP[icd]['name'], 
                indication_aka=INDICATION_MAP[icd].get('aka', ''), indication_code=icd, references=references
            )
            
            engine = BrandedMobileEngine(content, brand_data)
            with st.spinner("⚙️ Assembling High-Res Patient Dossier..."):
                final_image = engine.draw()
            
            st.session_state.final_image = final_image
            buf = io.BytesIO()
            final_image.save(buf, format="PNG")
            st.session_state.byte_im = buf.getvalue()
            st.session_state.needs_generation = False

        # Display the result inside the locked glass box
        st.markdown(f"<h3 style='text-align: center; color: white;'>Patient Dossier: {INDICATION_MAP[st.session_state.icd]['name']}</h3>", unsafe_allow_html=True)
        st.image(st.session_state.final_image, use_container_width=True)
        
        st.download_button(
            label="💾 Download Full High-Res Dossier", 
            data=st.session_state.byte_im, 
            file_name=f"Patient_Dossier_{st.session_state.icd}.png", 
            mime="image/png",
            use_container_width=True
        )

if __name__ == "__main__":
    main()