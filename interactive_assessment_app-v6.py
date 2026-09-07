import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime

st.set_page_config(
    page_title="SQA Scenario-Based Assessment - Answer Sheet",
    page_icon="📝",
    layout="wide"
)

# Application Styling
st.markdown("""
<style>
    .main-title {
        color: #1F4E78;
        font-family: 'Arial', sans-serif;
        text-align: center;
        margin-bottom: 5px;
    }
    .sub-title {
        color: #555555;
        font-family: 'Arial', sans-serif;
        text-align: center;
        margin-bottom: 25px;
    }
    .scenario-box {
        background-color: #F2F4F8;
        border-left: 5px solid #2E75B6;
        padding: 15px;
        border-radius: 4px;
        margin-bottom: 10px;
    }
    .question-prompt {
        color: #C00000;
        font-weight: bold;
        font-size: 1.1em;
        margin-top: 10px;
        margin-bottom: 15px;
    }
    .rubric-text {
        font-size: 0.9em;
        color: #555555;
        line-height: 1.4;
    }
    .footer-text {
        text-align: center;
        color: #888888;
        font-size: 0.85em;
        margin-top: 50px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">แบบทดสอบประเมินผล (Scenario-Based Assessment)</h1>', unsafe_allow_html=True)
st.markdown('<h3 class="sub-title">สำหรับตำแหน่ง Software Quality Assurance / Tester </h3>', unsafe_allow_html=True)

# Instructions Sidebar
with st.sidebar:
    st.header("📝 ข้อมูลผู้เข้าสอบ")
    name = st.text_input("ชื่อ-นามสกุล", placeholder="กรอกชื่อ-นามสกุลของคุณ")
    date_input = st.text_input("วันที่สอบ", placeholder=datetime.now().strftime("%d/%m/%Y"))
    
    st.markdown("---")
    st.sidebar.markdown("### 🖼️ การตั้งค่ารูปภาพโจทย์")
    show_images = st.checkbox("แสดงรูปภาพโจทย์", value=True, help="ติ๊กออกหากไม่ต้องการแสดงรูปภาพในแต่ละข้อสอบ")
    
    st.markdown("---")
    st.sidebar.markdown("### 📏 การตั้งค่าความสูงช่องคำตอบ")
    box_height = st.slider("ปรับขนาดความสูงช่องพิมพ์ข้อความ (พิกเซล)", min_value=200, max_value=800, value=450, step=50, help="เลื่อนแถบนี้เพื่อปรับขนาดช่องพิมพ์คำตอบให้ใหญ่ขึ้นหรือเล็กลงตามที่ต้องการ")
    
    st.markdown("---")
    st.markdown("### ⚙️ สำหรับผู้คุมสอบ (Google Sheets Sync)")
    DEFAULT_WEBAPP_URL = "" 
    sheet_url = st.text_input("Google Apps Script Web App URL", value=DEFAULT_WEBAPP_URL, type="password", placeholder="https://script.google.com/macros/s/.../exec")
    
    st.markdown("---")
    st.markdown("### 💡 คำชี้แจงในการทำข้อสอบ")
    st.info("""
    1. ตอบคำถามจากสถานการณ์ (Scenario) ทั้ง 5 ข้อโดยละเอียด
    2. เน้นการอธิบายแนวคิด เหตุผลประกอบ การวิเคราะห์ความเสี่ยง และระบุแนวทางการทดสอบที่ชัดเจนและเป็นระบบ
    3. ตัวพิมพ์คำตอบจะถูกจำกัดไม่เกิน **5,000 ตัวอักษร** ต่อข้อ (มีระบบนับจำนวนตัวอักษรแบบ Real-time)
    4. เมื่อตอบเสร็จครบทุกข้อ สามารถกดปุ่ม **'ส่งใบคำตอบออนไลน์'** เพื่อบันทึกข้อมูลเข้า Google Sheets ทันที หรือกดดาวน์โหลดไฟล์สำรองเป็นปุ่มด้านล่างสุด
    """)

# Define Questions Data with custom image URLs
questions = [
    {
        "id": 1,
        "title": "ข้อที่ 1: “It works on my machine!” (คะแนนเต็ม 20 คะแนน)",
        "scenario": "ทีม Developer แจ้งว่า Feature ใหม่ทดสอบบนเครื่องตัวเองแล้วทำงานปกติ แต่เมื่อขึ้น UAT ผู้ใช้กลับเจอ Error เป็นบางครั้ง และ Tester ไม่สามารถ Reproduce ได้ทุกครั้ง",
        "prompt": "คำถาม: ถ้าคุณเป็น Tester คุณจะ Investigate ปัญหานี้อย่างไร? อธิบายข้อมูลที่ต้องเก็บ วิธีหาเงื่อนไขในการ Reproduce และสิ่งที่จะส่งให้ Developer เพื่อช่วยให้หาสาเหตุได้เร็วที่สุด",
        "image_url": "https://images.unsplash.com/photo-1607799279861-4dd421887fb3?auto=format&fit=crop&w=1200&q=80",
        "rubric": [
            "การวิเคราะห์และเปรียบเทียบ Environment (5 คะแนน)",
            "วิธี Investigate และหาเงื่อนไขในการ Reproduce (5 คะแนน)",
            "การเก็บ Evidence / Log / Test Data / Request-Response (5 คะแนน)",
            "การสื่อสารข้อมูลให้ Developer อย่างชัดเจนและนำไปใช้ได้ (5 คะแนน)"
        ]
    },
    {
        "id": 2,
        "title": "ข้อที่ 2: Bug 1 ล้านบาท (คะแนนเต็ม 20 คะแนน)",
        "scenario": "ระบบธนาคารมีฟังก์ชันโอนเงิน หาก User กดปุ่ม “Confirm” ซ้ำอย่างรวดเร็ว 2 ครั้ง พบว่ามีโอกาสสร้าง Transaction ซ้ำและหักเงินสองครั้ง",
        "prompt": "คำถาม: คุณจะออกแบบการทดสอบปัญหานี้อย่างไร? มี Scenario อะไรที่ควรทดสอบเพิ่มเติม และถ้าต้องเลือกระหว่างการ Block Release กับปล่อย Production คุณจะเลือกแบบไหน เพราะอะไร?",
        "image_url": "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?auto=format&fit=crop&w=1200&q=80",
        "rubric": [
            "การประเมิน Severity / Business Impact และความเสี่ยง (5 คะแนน)",
            "ความครอบคลุมของ Test Scenario เช่น Double Click, Retry, Concurrency (5 คะแนน)",
            "การตรวจสอบระดับ UI / API / Database และ Duplicate Transaction (5 คะแนน)",
            "เหตุผลในการตัดสินใจ Block Release หรือ Release (5 คะแนน)"
        ]
    },
    {
        "id": 3,
        "title": "ข้อที่ 3: The Midnight Bug (คะแนนเต็ม 20 คะแนน)",
        "scenario": "ระบบ E-commerce มีโปรโมชั่น “ลด 50% วันที่ 11.11 เวลา 00:00–23:59” ระบบมีทั้ง Web และ Mobile App และให้บริการลูกค้าหลายประเทศที่อยู่คนละ Time Zone",
        "prompt": "คำถาม: คุณจะออกแบบ Test Scenario สำหรับโปรโมชั่นนี้อย่างไร โดยเฉพาะกรณีเวลา 23:59 → 00:00, Time Zone, ผู้ใช้ที่เปิดหน้า Checkout ค้างไว้ก่อนหมดโปรโมชั่น และ Transaction ที่เกิดขึ้นตรงเวลาสิ้นสุดพอดี?",
        "image_url": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=1200&q=80",
        "rubric": [
            "การทดสอบ Boundary ของเวลาเริ่มต้นและสิ้นสุดโปรโมชั่น (5 คะแนน)",
            "การวิเคราะห์ Time Zone และความสอดคล้องระหว่าง Web/Mobile/API (5 คะแนน)",
            "การครอบคลุม Edge Cases เช่น Checkout ค้างหรือ Transaction ตรงเวลาสิ้นสุด (5 คะแนน)",
            "การตั้งคำถาม/ชี้จุดกำกวมของ Requirement และ Business Rule (5 คะแนน)"
        ]
    },
    {
        "id": 4,
        "title": "ข้อที่ 4: AI บอกว่า PASS แต่คุณไม่เชื่อ (คะแนนเต็ม 20 คะแนน)",
        "scenario": "บริษัทเริ่มใช้ AI สร้าง Test Case จาก Requirement โดยอัตโนมัติ AI สร้าง Test Case 100 ข้อและแจ้งว่า Requirement มี Coverage ครบแล้ว",
        "prompt": "คำถาม: ในฐานะ Software Tester คุณจะเชื่อผลนี้หรือไม่? คุณจะตรวจสอบอย่างไรว่า Test Case ที่ AI สร้างมี Coverage เพียงพอจริง และมี Test Scenario ประเภทใดที่ AI อาจมองข้าม?",
        "image_url": "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?auto=format&fit=crop&w=1200&q=80",
        "rubric": [
            "ความเข้าใจว่า Test Case จำนวนมากไม่ได้แปลว่า Coverage ครบ (5 คะแนน)",
            "วิธีตรวจสอบ Requirement / Acceptance Criteria กับ Test Coverage (5 คะแนน)",
            "การระบุ Scenario ที่ AI อาจมองข้าม เช่น Negative, Boundary, Security, Integration (5 คะแนน)",
            "การอธิบายบทบาทของ Human Tester และ Risk-based Testing (5 คะแนน)"
        ]
    },
    {
        "id": 5,
        "title": "ข้อที่ 5: Production กำลังไหม้! (คะแนนเต็ม 20 คะแนน)",
        "scenario": "เวลา 02:00 น. มีแจ้งเตือนว่า หลัง Deploy Version ใหม่ ลูกค้าประมาณ 20% ไม่สามารถ Checkout ได้ Developer เสนอให้ Hotfix ทันที ขณะที่อีกทีมเสนอให้ Rollback Version ก่อน",
        "prompt": "คำถาม: หากคุณเป็น Tester ที่อยู่ใน Incident Team คุณต้องช่วยตัดสินใจว่าจะ Hotfix, Rollback หรือ Monitor ต่ออย่างไร? ระบุข้อมูลที่ต้องตรวจสอบ ความเสี่ยงของแต่ละทางเลือก สิ่งที่ต้องทดสอบหลังแก้ไข และเกณฑ์ที่ใช้ตัดสินว่าระบบปลอดภัยพอที่จะเปิดให้ลูกค้าใช้งานต่อ",
        "image_url": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1200&q=80",
        "rubric": [
            "การประเมิน Impact / Scope / Business Risk ของ Incident (5 คะแนน)",
            "การเปรียบเทียบความเสี่ยงของ Hotfix, Rollback และ Monitor (5 คะแนน)",
            "แผนการทดสอบหลังแก้ไข เช่น Smoke Test และ Critical Flow (5 คะแนน)",
            "เกณฑ์ตัดสินว่าระบบปลอดภัยพอสำหรับใช้งานต่อ (5 คะแนน)"
        ]
    }
]

answers = {}

# Display Questions
for q in questions:
    st.markdown(f"### {q['title']}")
    
    # Optional image display
    if show_images and q.get("image_url"):
        try:
            st.image(q["image_url"], use_container_width=True, caption=f"ภาพประกอบเหตุการณ์ {q['title']}")
        except Exception as e:
            st.warning(f"⚠️ ไม่สามารถโหลดรูปภาพสำหรับ {q['title']} ได้: {e}")
            
    # Scenario block
    st.markdown(f"""
    <div class="scenario-box">
        <strong>สถานการณ์:</strong> <em>{q['scenario']}</em>
    </div>
    """, unsafe_allow_html=True)
    
    # Question Prompt
    st.markdown(f'<div class="question-prompt">{q["prompt"]}</div>', unsafe_allow_html=True)
    
    # Text Field (Max Chars 5000, Custom box_height)
    ans = st.text_area(
        label="กรอกคำตอบของคุณด้านล่างนี้ (ไม่เกิน 5,000 ตัวอักษร):",
        key=f"ans_q{q['id']}",
        max_chars=5000,
        height=box_height,
        placeholder="พิมพ์คำตอบอย่างเป็นระบบ อธิบายทีละขั้นตอน แนวคิด และความเสี่ยงประกอบ..."
    )
    
    # Character Counter & Status
    char_count = len(ans)
    st.caption(f"จำนวนตัวอักษรปัจจุบัน: **{char_count:,} / 5,000** ตัวอักษร")
    
    answers[q['id']] = ans
    
    # Show Specific Rubric
    with st.expander("🔍 ดูเกณฑ์การให้คะแนนสำหรับข้อนี้"):
        for r in q['rubric']:
            st.markdown(f"- **{r}**")
            
    st.markdown("---")

# Submit to Google Sheets Section
st.subheader("🚀 ส่งใบคำตอบออนไลน์")

if st.button("📤 ส่งคำตอบเข้า Google Sheets"):
    if not name:
        st.error("⚠️ กรุณากรอกชื่อ-นามสกุล ในแถบด้านข้าง (Sidebar) ก่อนกดส่ง")
    elif not sheet_url:
        st.error("⚠️ แอดมินยังไม่ได้กำหนดค่า 'Google Apps Script Web App URL' ในแถบด้านข้าง กรุณากรอก URL เพื่อเปิดใช้งานระบบส่งข้อมูลออนไลน์")
    else:
        with st.spinner("กำลังส่งข้อมูลไปยัง Google Sheets โปรดรอสักครู่..."):
            payload = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "name": name,
                "date_test": date_input if date_input else datetime.now().strftime("%d/%m/%Y"),
                "ans1": answers[1],
                "ans2": answers[2],
                "ans3": answers[3],
                "ans4": answers[4],
                "ans5": answers[5]
            }
            
            try:
                response = requests.post(sheet_url, json=payload, timeout=15)
                
                if response.status_code == 200:
                    st.success("🎉 ส่งใบคำตอบเรียบร้อยแล้ว! ข้อมูลได้รับการบันทึกลงใน Google Sheets เรียบร้อยแล้ว")
                    st.balloons()
                else:
                    st.error(f"⚠️ เกิดข้อผิดพลาดจากเซิร์ฟเวอร์ (Status Code: {response.status_code})")
                    st.warning("หมายเหตุ: คุณสามารถกดดาวน์โหลดไฟล์คำตอบ (TXT) สำรองไว้ด้านล่างนี้ได้ เพื่อไม่ให้คำตอบสูญหาย")
            except Exception as e:
                st.error(f"❌ ไม่สามารถเชื่อมต่อกับ Google Sheets ได้เนื่องจากเกิด Error: {e}")
                st.warning("โปรดตรวจสอบความถูกต้องของ URL หรือความเสถียรของอินเทอร์เน็ต และดาวน์โหลดไฟล์สำรองได้ที่ปุ่มด้านล่าง")

st.markdown("---")

# Generate Download File as Backup
st.subheader("💾 ดาวน์โหลดไฟล์สำรอง")

if st.button("ตรวจสอบความพร้อมและสร้างไฟล์สำรอง (TXT)"):
    if not name:
        st.warning("⚠️ กรุณากรอกชื่อ-นามสกุลก่อนดาวน์โหลดไฟล์")
    else:
        # Construct the output content
        output_txt = f"==================================================\n"
        output_txt += f"ใบงานคำตอบ: SQA Scenario-Based Assessment\n"
        output_txt += f"==================================================\n"
        output_txt += f"ชื่อ-นามสกุล: {name}\n"
        output_txt += f"วันที่ทดสอบ: {date_input if date_input else 'ไม่ได้ระบุ'}\n"
        output_txt += f"==================================================\n\n"
        
        all_answered = True
        for q in questions:
            ans_text = answers[q['id']].strip()
            output_txt += f"--------------------------------------------------\n"
            output_txt += f"ข้อที่ {q['id']}: {q['title']}\n"
            output_txt += f"--------------------------------------------------\n"
            output_txt += f"สถานการณ์: {q['scenario']}\n"
            output_txt += f"คำถาม: {q['prompt']}\n\n"
            if ans_text:
                output_txt += f"คำตอบ (ความยาว {len(ans_text)} ตัวอักษร):\n{ans_text}\n\n"
            else:
                output_txt += f"[ ไม่มีการพิมพ์คำตอบ ]\n\n"
                all_answered = False
                
        output_txt += f"==================================================\n"
        output_txt += f"--- จบใบงานคำตอบ ---"
        
        if not all_answered:
            st.info("ℹ️ หมายเหตุ: คุณยังทำข้อสอบไม่ครบทุกข้อ แต่สามารถเลือกดาวน์โหลดส่วนที่ตอบแล้วก่อนได้")
            
        st.download_button(
            label="📥 ดาวน์โหลดไฟล์ใบคำตอบ (TXT)",
            data=output_txt,
            file_name=f"SQA_Assessment_Answers_{name.replace(' ', '_')}.txt",
            mime="text/plain"
        )
        st.success("🎉 สร้างไฟล์สำรองสำเร็จ! คุณสามารถกดปุ่มดาวน์โหลดด้านบนเพื่อเซฟไฟล์ได้ทันที")

# How-to Setup for Admins
with st.expander("🛠️ วิธีตั้งค่า Google Sheets ของคุณเพื่อรับคำตอบจากระบบนี้ (สำหรับแอดมิน)"):
    st.markdown("""
    คุณสามารถสร้างระบบหลังบ้านเพื่อรับข้อมูลจากแอปนี้เข้า Google Sheets ได้ง่ายๆ ฟรีตามขั้นตอนด้านล่างนี้:
    
    1. **สร้าง Google Sheet ใหม่** จากบัญชี Google ของคุณ
    2. ออกแบบตารางในแถวแรก (Row 1) ให้มีหัวคอลัมน์ดังนี้เพื่อความสอดคล้องของข้อมูล:
       * คอลัมน์ A: `Timestamp` (วันเวลาส่งคำตอบ)
       * คอลัมน์ B: `Name` (ชื่อผู้ตอบ)
       * คอลัมน์ C: `Date_Test` (วันที่ส่งตามระบบ)
       * คอลัมน์ D: `Answer_Q1` (คำตอบข้อ 1)
       * คอลัมน์ E: `Answer_Q2` (คำตอบข้อ 2)
       * คอลัมน์ F: `Answer_Q3` (คำตอบข้อ 3)
       * คอลัมน์ G: `Answer_Q4` (คำตอบข้อ 4)
       * คอลัมน์ H: `Answer_Q5` (คำตอบข้อ 5)
    3. ไปที่เมนูด้านบน คลิก **Extensions (ส่วนขยาย)** > **Apps Script**
    4. ลบโค้ดเริ่มต้นออกทั้งหมดแล้ว **ก๊อปปี้โค้ด JavaScript ด้านล่างนี้ไปวาง**:
    ```javascript
    function doPost(e) {
      try {
        var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
        var data = JSON.parse(e.postData.contents);
        
        // Append row to active sheet
        sheet.appendRow([
          data.timestamp,
          data.name,
          data.date_test,
          data.ans1,
          data.ans2,
          data.ans3,
          data.ans4,
          data.ans5
        ]);
        
        return ContentService.createTextOutput(JSON.stringify({"status": "success"}))
          .setMimeType(ContentService.MimeType.JSON);
      } catch (err) {
        return ContentService.createTextOutput(JSON.stringify({"status": "error", "message": err.toString()}))
          .setMimeType(ContentService.MimeType.JSON);
      }
    }
    ```
    5. กดปุ่มบันทึก (แผ่นดิสก์) จากนั้นคลิกปุ่ม **Deploy (การทำงานและการใช้ประโยชน์)** > **New deployment (การติดตั้งใช้งานใหม่)**
    6. คลิกไอคอนฟันเฟือง เลือกประเภทเป็น **Web app (เว็บแอป)**
    7. ตั้งค่าที่สำคัญดังนี้:
       * **Execute as (เรียกใช้เป็น):** เลือก `Me` (บัญชีอีเมลของคุณ)
       * **Who has access (ผู้ที่มีสิทธิ์เข้าถึง):** เลือก `Anyone` (ทุกคน - สำคัญมากเพื่อให้แอปภายนอกคุยกับ Google Sheets ได้)
    8. กดปุ่ม **Deploy** จากนั้น Google จะขอให้คุณกดยินยอมสิทธิ์ (Authorize Access) ให้ทำการอนุญาตสิทธิ์จนเสร็จสิ้น
    9. **ก๊อปปี้ลิงก์ Web app URL** ที่ลงท้ายด้วย `/exec` มาใส่ในแถบด้านข้าง (Sidebar) ของแอป Streamlit นี้เพื่อเชื่อมต่อระบบได้ทันที!
    """)

with st.expander("🖼️ วิธีเปลี่ยนหรือแก้ไขรูปภาพโจทย์ในแต่ละข้อ (สำหรับนักพัฒนา)"):
    st.markdown("""
    หากต้องการเปลี่ยนรูปภาพประกอบโจทย์ทั้ง 5 ข้อในอนาคต คุณสามารถแก้ไขค่าของคีย์ `"image_url"` ในโค้ดไฟล์ `interactive_assessment_app-v6.py` ได้ง่ายๆ:
    
    * **หากใช้รูปภาพออนไลน์**: นำ URL ของรูปภาพนั้นๆ (เช่น อัปโหลดไว้บน Imgur, Google Drive แบบแชร์สาธารณะ หรือโฮสติ้งอื่นๆ) มาวางแทนที่ลิงก์ในคีย์ `"image_url"`
    * **หากใช้รูปภาพภายในเครื่องเมื่ออัปโหลดขึ้น GitHub**: คุณสามารถสร้างโฟลเดอร์ชื่อ `images` ใน GitHub ของคุณ แล้วใส่รูป เช่น `images/q1.png` จากนั้นเปลี่ยนค่าเป็น `\"image_url\": \"images/q1.png\"` ได้เลย!
    """)

st.markdown('<div class="footer-text">พัฒนาโดย Gemini Notebook — แพลตฟอร์มวิเคราะห์และประเมินคุณภาพซอฟต์แวร์อิงสถานการณ์</div>', unsafe_allow_html=True)
