# med_sidebar.py - VERSION 10.0 - ZERO-SCROLL TABBED ARCHITECTURE
import streamlit as st

def render_indication_selector(indications):
    st.markdown("<h2 style='text-align: center; margin-top: -20px; margin-bottom: 20px; color: white;'>🩺 MEDUCATION: Clinical Intake Form</h2>", unsafe_allow_html=True)
    
    ind_labels = {k: f"[{k}] {v['name']}" for k, v in indications.items()}
    
    # Duplicate Call Immunity Preserved
    sel_label = None
    for i in range(10):
        try:
            sel_label = st.selectbox(
                "Primary Indication Search", 
                options=list(ind_labels.values()),
                key=f"safe_indication_selector_{i}"
            )
            break 
        except Exception as e:
            if "Duplicate" in str(e) or "multiple elements" in str(e):
                continue
            raise e
            
    icd = sel_label.split(']')[0].replace('[', '')
    return icd

def render_intake(df, icd):
    audience = st.radio("Document Audience", ["Patient", "Caregiver"], horizontal=True)
    tags = []
    selected_meds = []
    
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    # THE FIX: Swapping Expanders for a Fixed-Height Tab Layout
    t1, t2, t3, t4, t5, t6 = st.tabs([
        "👤 Demographics", "❤️ Comorbidities", "⚠️ Allergies", 
        "🏃 Lifestyle", "🏡 Logistics", "💊 Medications"
    ])

    with t1:
        c1, c2, c3 = st.columns(3)
        with c1:
            age_map = {"Adult 19-64y": "Age_Adult_19_64y", "Neonate (0-28d)": "Age_Neonate_0_28d", "Infant (1-12m)": "Age_Infant_1_12m", "Toddler (1-3y)": "Age_Toddler_1_3y", "Child (4-12y)": "Age_Child_4_12y", "Adolescent (13-18y)": "Age_Adolescent_13_18y", "Elderly (65-79y)": "Age_Elderly_65_79y", "Frail/Old (>80y)": "Age_Frail_Old_80y"}
            sel_age = st.selectbox("Patient Age", list(age_map.keys()))
            tags.append(age_map[sel_age])
        with c2:
            race_map = {"Not Specified": "Race_Not_Specified", "African Descent": "Race_African_Descent", "Asian Descent": "Race_Asian_Descent", "Caucasian Descent": "Race_Caucasian_Descent"}
            sel_race = st.selectbox("Background", list(race_map.keys()))
            tags.append(race_map[sel_race])
        with c3:
            sex_map = {"Not Specified": "Sex_Not_Specified", "Biologically Male": "Sex_Male", "Biologically Female": "Sex_Female"}
            sel_sex = st.selectbox("Biological Sex", list(sex_map.keys()))
            tags.append(sex_map[sel_sex])
            if sel_sex == "Biologically Female":
                p1, p2 = st.columns(2)
                with p1:
                    if st.checkbox("Pregnancy T1"): tags.append("Pregnancy_T1")
                    if st.checkbox("Pregnancy T2"): tags.append("Pregnancy_T2")
                with p2:
                    if st.checkbox("Pregnancy T3"): tags.append("Pregnancy_T3")
                    if st.checkbox("Breastfeeding"): tags.append("Lactating_Breastfeeding")

    with t2:
        c1, c2 = st.columns(2)
        with c1:
            if st.checkbox("Renal Impaired (Mild/Mod)"): tags.append("Renal_Impaired_Mild_Mod")
            if st.checkbox("Renal Impaired (Severe/ESRD)"): tags.append("Renal_Impaired_Severe_ESRD")
            if st.checkbox("Hepatic Impaired"): tags.append("Hepatic_Impaired")
            if st.checkbox("Immunocompromised"): tags.append("Immunocompromised")
        with c2:
            if st.checkbox("Diabetic"): tags.append("Comorbidity_Diabetes")
            if st.checkbox("Hypertensive"): tags.append("Comorbidity_Hypertension")
            if st.checkbox("Asthmatic"): tags.append("Comorbidity_Asthma")
            if st.checkbox("Cardiovascular Disease"): tags.append("Comorbidity_Cardiovascular")

    with t3:
        c1, c2 = st.columns(2)
        with c1:
            if st.checkbox("Penicillin Allergy"): tags.append("Allergy_Penicillin")
            if st.checkbox("Sulfa Drug Allergy"): tags.append("Allergy_Sulfa")
        with c2:
            if st.checkbox("NSAID Allergy"): tags.append("Allergy_NSAIDs")
            if st.checkbox("Peanut/Nut Allergy"): tags.append("Allergy_Nuts")

    with t4:
        if st.checkbox("Current Smoker"): tags.append("Smoker_Current")
        if st.checkbox("High Alcohol Consumption"): tags.append("Alcohol_Consumer_High")

    with t5:
        c1, c2 = st.columns(2)
        with c1:
            if st.checkbox("Living Alone"): tags.append("Logistical_Living_Alone")
            if st.checkbox("Manual Laborer"): tags.append("Logistical_Manual_Laborer")
            if st.checkbox("Desk Job"): tags.append("Logistical_Desk_Job")
        with c2:
            if st.checkbox("No Refrigeration"): tags.append("Logistical_No_Refrigeration")
            if st.checkbox("No Clean Water"): tags.append("Logistical_No_Clean_Water")
            if st.checkbox("High Travel Distance"): tags.append("Logistical_High_Travel_Distance")

    with t6:
        med_options = df[df['Section_ID'] == 'SEC_04_TX']['Med_Class_ID'].unique()
        med_options = [str(m) for m in med_options if str(m).strip() and str(m).lower() != 'nan']
        if med_options:
            selected_meds = st.multiselect("Select Prescribed Medications", options=sorted(med_options))
            tags.extend(selected_meds)
        else:
            st.info("No medications mapped for this indication.")

    return audience == "Caregiver", tags, selected_meds