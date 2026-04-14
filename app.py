import streamlit as st
from fractions import Fraction
from docxtpl import DocxTemplate
from datetime import datetime
import os
import re
import io

# ==========================================
# 配置區域
# ==========================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, '已生成平安紙')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# GitHub file base URL
GITHUB_RAW = "https://raw.githubusercontent.com/felixchancy-svg/Will-Drafting-System/main"
GITHUB_BLOB = "https://github.com/felixchancy-svg/Will-Drafting-System/blob/main"

# ── CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
  div[data-testid="stTextInput"] input {
    font-size: 14px !important;
    padding: 6px 10px !important;
  }
  div[data-testid="stSelectbox"] > div > div {
    font-size: 14px !important;
  }
  div[data-testid="stTextInput"] label p,
  div[data-testid="stSelectbox"] label p,
  div[data-testid="stNumberInput"] label p {
    font-size: 13px !important;
    font-weight: 600 !important;
  }
  div[data-testid="column"] {
    padding-left: 5px !important;
    padding-right: 5px !important;
  }
  h2 {
    font-size: 1.05rem !important;
    background: #f0f2f6;
    padding: 5px 10px !important;
    border-radius: 4px;
    margin: 0.5rem 0 0.3rem 0 !important;
  }
  h3 { font-size: 0.95rem !important; margin: 0.3rem 0 0.2rem 0 !important; }
  hr { margin: 0.4rem 0 !important; }
  div[data-testid="stRadio"] label { font-size: 14px !important; }
  /* Glowing download button */
  div[data-testid="stDownloadButton"] button {
    background-color: #1a3a5c !important;
    color: white !important;
    border: none !important;
    animation: glow 1.5s ease-in-out infinite !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    padding: 10px 24px !important;
  }
  @keyframes glow {
    0%   { box-shadow: 0 0 5px #c9973a, 0 0 10px #c9973a; }
    50%  { box-shadow: 0 0 20px #c9973a, 0 0 40px #c9973a; }
    100% { box-shadow: 0 0 5px #c9973a, 0 0 10px #c9973a; }
  }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────
if 'generated' not in st.session_state:
    st.session_state.generated = False
if 'downloaded' not in st.session_state:
    st.session_state.downloaded = False
if 'confirm_reset' not in st.session_state:
    st.session_state.confirm_reset = False

def parse_share(share_str):
    try:
        s = share_str.strip()
        if s in ['全部', 'all', 'ALL']:
            return 1.0
        if '%' in s:
            return float(s.replace('%', '')) / 100
        return float(Fraction(s))
    except:
        return 0

def validate_hkid(hkid):
    pattern = r'^[A-Z]{1,2}\d{6}\([0-9A]\)$'
    return re.match(pattern, hkid.strip().upper()) is not None

# ==========================================
# Sidebar
# ==========================================
with st.sidebar:
    st.markdown("## 📁 文件下載")
    st.markdown("---")

    RAW = "https://raw.githubusercontent.com/felixchancy-svg/Will-Drafting-System/main"

    st.markdown("**📖 操作手冊**")
    st.markdown(f"[社區平安紙系統_使用手冊.pdf]({RAW}/%E7%A4%BE%E5%8D%80%E5%B9%B3%E5%AE%89%E7%B4%99%E7%B3%BB%E7%B5%B1_%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8A.pdf)")
    st.markdown("")

    st.markdown("**📋 申請表格**")
    st.markdown(f"[平安紙申請人資料表.pdf]({RAW}/%E5%B9%B3%E5%AE%89%E7%B4%99%E7%94%B3%E8%AB%8B%E4%BA%BA%E8%B3%87%E6%96%99%E8%A1%A8.pdf)")
    st.markdown("")

    st.markdown("**📄 遺囑樣本參考**")
    st.markdown(f"[Will_B_S.pdf — 無物業，單一受益人]({RAW}/samples/Will_B_S.pdf)")
    st.markdown(f"[Will_B_M.pdf — 無物業，多位受益人]({RAW}/samples/Will_B_M.pdf)")
    st.markdown(f"[Will_P_S.pdf — 有物業，單一受益人]({RAW}/samples/Will_P_S.pdf)")
    st.markdown(f"[Will_P_M.pdf — 有物業，多位受益人]({RAW}/samples/Will_P_M.pdf)")
    st.markdown("")
    st.markdown("---")
    st.caption("如連結無法開啟，請聯絡系統管理員。")

# ==========================================
# 介面設計
# ==========================================
st.set_page_config(page_title="社區平安紙系統", layout="wide")
st.title("⚖️ 社區平安紙自動化草擬系統")

# ── Section 1: Testator ───────────────────────────────────────────────
st.header("1. 立遺囑人個人資料")
c1, c2, c3, c4 = st.columns([2, 2, 2, 5])
with c1:
    t_name = st.text_input("中文姓名 *")
    t_id = st.text_input("身份證號碼 * (如: A123456(7))")
with c2:
    t_en_name = st.text_input("英文姓名 *")
    marital_status = st.selectbox("婚姻狀況 *", ["未婚", "已婚", "離婚", "喪偶"])
with c3:
    st.markdown("<span style='font-size:13px;font-weight:600'>職業 *</span>", unsafe_allow_html=True)
    occ_option = st.radio("職業", ["退休", "無業", "家庭主婦", "其他"],
                          horizontal=True, label_visibility="collapsed")
    if occ_option == "其他":
        occupation = st.text_input("請輸入職業", placeholder="如：教師、律師")
    else:
        occupation = occ_option
        st.empty()
with c4:
    t_address = st.text_input("現居地址 *")

st.divider()

# ── Section 2: Executor ───────────────────────────────────────────────
st.header("2. 遺囑執行人資料")
e1, e2, e3, e4, _spacer2 = st.columns([2, 2, 2, 2, 3])
with e1: exec_name = st.text_input("執行人中文姓名 *")
with e2: exec_en_name = st.text_input("執行人英文姓名 *")
with e3: exec_id = st.text_input("執行人身份證號碼 *")
with e4: exec_rel = st.text_input("與立遺囑人關係 *", placeholder="如：妻子")

exec_over_21 = st.checkbox("✅ 確認執行人已年滿 21 歲 / Confirm executor is aged 21 or above *")

st.divider()

# ── Section 3: Distribution ───────────────────────────────────────────
st.header("3. 資產分配安排")
has_property = st.checkbox("是否有特定物業遺贈？")

prop_context = {}
prop_beneficiaries = []
if has_property:
    st.subheader("物業遺贈細節")
    pa1, _spacer3 = st.columns([4, 3])
    with pa1: p_addr = st.text_input("物業地址 *")

    num_pb = st.number_input("物業受益人人數", min_value=1, step=1, value=1)

    pbh1, pbh2, pbh3, pbh4, pbh5, _pbspacer = st.columns([2, 2, 2, 2, 2, 1])
    with pbh1: st.markdown("<span style='font-size:13px;font-weight:600'>分配比例 *</span>", unsafe_allow_html=True)
    with pbh2: st.markdown("<span style='font-size:13px;font-weight:600'>中文姓名 *</span>", unsafe_allow_html=True)
    with pbh3: st.markdown("<span style='font-size:13px;font-weight:600'>英文姓名 *</span>", unsafe_allow_html=True)
    with pbh4: st.markdown("<span style='font-size:13px;font-weight:600'>身份證號碼 *</span>", unsafe_allow_html=True)
    with pbh5: st.markdown("<span style='font-size:13px;font-weight:600'>與立遺囑人關係 *</span>", unsafe_allow_html=True)

    for i in range(int(num_pb)):
        pbc1, pbc2, pbc3, pbc4, pbc5, _pbspacer2 = st.columns([2, 2, 2, 2, 2, 1])
        with pbc1: pb_share = st.text_input(f"pb_s{i}", placeholder="全部/1/2/50%", key=f"pb_s{i}", label_visibility="collapsed")
        with pbc2: pb_name = st.text_input(f"pb_n{i}", key=f"pb_n{i}", label_visibility="collapsed")
        with pbc3: pb_en = st.text_input(f"pb_e{i}", key=f"pb_e{i}", label_visibility="collapsed")
        with pbc4: pb_id = st.text_input(f"pb_i{i}", key=f"pb_i{i}", label_visibility="collapsed")
        with pbc5: pb_rel = st.text_input(f"pb_r{i}", key=f"pb_r{i}", label_visibility="collapsed")
        prop_beneficiaries.append({'share': pb_share, 'name': pb_name, 'en_name': pb_en, 'id': pb_id, 'rel': pb_rel})

    prop_context = {
        'has_property': True,
        'property_address': p_addr,
        'prop_beneficiaries': prop_beneficiaries,
        # Keep old single fields for backward compat
        'prop_beneficiary_rel': prop_beneficiaries[0]['rel'] if prop_beneficiaries else '',
        'prop_beneficiary_name': prop_beneficiaries[0]['name'] if prop_beneficiaries else '',
        'prop_beneficiary_en_name': prop_beneficiaries[0]['en_name'] if prop_beneficiaries else '',
        'prop_beneficiary_id': prop_beneficiaries[0]['id'] if prop_beneficiaries else '',
    }

st.subheader("財產分配 (剩餘財產)")
num_b = st.number_input("受益人人數", min_value=1, step=1, value=1)
beneficiaries = []

bh1, bh2, bh3, bh4, bh5, bh6, _bspacer = st.columns([2, 2, 2, 2, 1, 2, 1])
with bh1: st.markdown("<span style='font-size:13px;font-weight:600'>分配比例 *</span>", unsafe_allow_html=True)
with bh2: st.markdown("<span style='font-size:13px;font-weight:600'>中文姓名 *</span>", unsafe_allow_html=True)
with bh3: st.markdown("<span style='font-size:13px;font-weight:600'>英文姓名</span>", unsafe_allow_html=True)
with bh4: st.markdown("<span style='font-size:13px;font-weight:600'>身份證號碼</span>", unsafe_allow_html=True)
with bh5: st.markdown("<span style='font-size:13px;font-weight:600'>年齡 *</span>", unsafe_allow_html=True)
with bh6: st.markdown("<span style='font-size:13px;font-weight:600'>與立遺囑人關係</span>", unsafe_allow_html=True)

for i in range(int(num_b)):
    bc1, bc2, bc3, bc4, bc5, bc6, _bspacer2 = st.columns([2, 2, 2, 2, 1, 2, 1])
    with bc1: b_share = st.text_input(f"s{i}", placeholder="全部/1/2/50%", key=f"s{i}", label_visibility="collapsed")
    with bc2: b_name = st.text_input(f"n{i}", key=f"n{i}", label_visibility="collapsed")
    with bc3: b_en = st.text_input(f"e{i}", key=f"e{i}", label_visibility="collapsed")
    with bc4: b_id = st.text_input(f"i{i}", key=f"i{i}", label_visibility="collapsed")
    with bc5: b_age = st.number_input(f"a{i}", min_value=0, max_value=120, step=1, key=f"a{i}", label_visibility="collapsed")
    with bc6: b_rel = st.text_input(f"r{i}", key=f"r{i}", label_visibility="collapsed")
    beneficiaries.append({'share': b_share, 'name': b_name, 'en_name': b_en, 'id': b_id, 'rel': b_rel, 'age': int(b_age)})

st.divider()

# ── Action buttons ────────────────────────────────────────────────────
col_preview, col_generate, col_clear = st.columns([1, 1, 1])

with col_preview:
    if st.button("👁 預覽摘要"):
        errors = []
        if not t_name: errors.append("立遺囑人中文姓名")
        if not t_en_name: errors.append("立遺囑人英文姓名")
        if not t_id: errors.append("身份證號碼")
        if not t_address: errors.append("地址")
        if not exec_name: errors.append("執行人姓名")
        if errors:
            st.error(f"❌ 未填寫：{', '.join(errors)}")
        else:
            st.info(
                f"**立遺囑人：** {t_name} ({t_en_name}) | {t_id} | {t_address} | {marital_status} | {occupation}\n\n"
                f"**執行人：** {exec_rel}{exec_name} ({exec_en_name}) | {exec_id}\n\n"
                f"**物業：** {'是 — ' + prop_context.get('property_address','') + ' | 受益人：' + ' / '.join([pb['rel'] + pb['name'] + ' ' + pb['share'] for pb in prop_beneficiaries if pb['name']]) if has_property else '否'}\n\n"
                f"**受益人：** " + " | ".join([f"{b['rel']}{b['name']} {b['share']} (年齡:{b['age']})" for b in beneficiaries if b['name']])
            )

with col_generate:
    if st.button("🚀 生成平安紙", type="primary"):
        st.session_state.confirm_reset = False

        # Required fields
        errors = []
        if not t_name: errors.append("立遺囑人中文姓名")
        if not t_en_name: errors.append("立遺囑人英文姓名")
        if not t_id: errors.append("立遺囑人身份證號碼")
        if not t_address: errors.append("立遺囑人現居地址")
        if not exec_name: errors.append("執行人中文姓名")
        if not exec_en_name: errors.append("執行人英文姓名")
        if not exec_id: errors.append("執行人身份證號碼")
        if not exec_rel: errors.append("執行人關係")
        if not exec_over_21: errors.append("確認執行人年齡")
        if occ_option == "其他" and not occupation: errors.append("職業")
        if has_property:
            if not p_addr: errors.append("物業地址")
            for i, pb in enumerate(prop_beneficiaries):
                if not pb['name']: errors.append(f"物業受益人{i+1}姓名")
                if not pb['en_name']: errors.append(f"物業受益人{i+1}英文姓名")
                if not pb['id']: errors.append(f"物業受益人{i+1}身份證")
                if not pb['rel']: errors.append(f"物業受益人{i+1}關係")
                if not pb['share']: errors.append(f"物業受益人{i+1}分配比例")
        for i, b in enumerate(beneficiaries):
            if not b['name']: errors.append(f"受益人{i+1}姓名")
            if not b['share']: errors.append(f"受益人{i+1}分配比例")
        if errors:
            st.error(f"❌ 未填寫：{', '.join(errors)}")
            st.stop()

        if not exec_over_21:
            st.error("❌ 請確認執行人已年滿 21 歲方可生成遺囑。")
            st.stop()

        # Minor beneficiary check
        minor_beneficiaries = [b for b in beneficiaries if b['name'] and b['age'] > 0 and b['age'] < 18]
        if minor_beneficiaries:
            names = ', '.join([b['name'] for b in minor_beneficiaries])
            st.error(f"❌ 以下受益人未滿 18 歲：{names}。如受益人未成年，須委任兩名執行人，請聯絡立遺囑人安排第二執行人，並聯絡系統管理員處理。")
            st.stop()
        hkid_errors = []
        if not validate_hkid(t_id): hkid_errors.append(f"立遺囑人：{t_id}")
        if not validate_hkid(exec_id): hkid_errors.append(f"執行人：{exec_id}")
        if has_property:
            for i, pb in enumerate(prop_beneficiaries):
                if pb['id'] and not validate_hkid(pb['id']): hkid_errors.append(f"物業受益人{i+1}：{pb['id']}")
        for i, b in enumerate(beneficiaries):
            if b['id'] and not validate_hkid(b['id']): hkid_errors.append(f"受益人{i+1}：{b['id']}")
        if hkid_errors:
            st.error("❌ 身份證格式有誤 (應為 A123456(7))：\n" + "\n".join(hkid_errors))
            st.stop()

        # Property beneficiary share validation
        if has_property and len(prop_beneficiaries) > 1:
            pb_skip = len(prop_beneficiaries) == 1 and prop_beneficiaries[0]['share'] in ['全部', 'all', 'ALL']
            if not pb_skip:
                pb_total = sum(parse_share(pb['share']) for pb in prop_beneficiaries)
                if abs(pb_total - 1.0) > 0.0001:
                    st.error(f"❌ 物業受益人比例總和為 {pb_total*100:.1f}%，必須等於 100%。")
                    st.stop()

        # Share validation
        all_shares = [b['share'].strip() for b in beneficiaries]
        skip_check = len(beneficiaries) == 1 and all_shares[0] in ['全部', 'all', 'ALL']
        if not skip_check:
            total_share = sum(parse_share(b['share']) for b in beneficiaries)
            if abs(total_share - 1.0) > 0.0001:
                st.error(f"❌ 比例總和為 {total_share*100:.1f}%，必須等於 100%。")
                st.stop()

        try:
            now = datetime.now()
            if has_property and len(beneficiaries) == 1: template_name = "Will_P_S.docx"
            elif has_property and len(beneficiaries) > 1: template_name = "Will_P_M.docx"
            elif not has_property and len(beneficiaries) == 1: template_name = "Will_B_S.docx"
            else: template_name = "Will_B_M.docx"

            doc = DocxTemplate(os.path.join(TEMPLATE_DIR, template_name))
            context = {
                **prop_context,
                'testator_name': t_name, 'testator_en_name': t_en_name, 'testator_id': t_id,
                'testator_address': t_address, 'marital_status': marital_status, 'occupation': occupation,
                'exec_name': exec_name, 'exec_en_name': exec_en_name, 'exec_id': exec_id, 'exec_rel': exec_rel,
                'beneficiaries': beneficiaries,
                'year': str(now.year), 'month': str(now.month), 'day': str(now.day)
            }
            doc.render(context)
            file_name = f"{t_name}_平安紙_{now.strftime('%Y%m%d')}.docx"

            # Save locally (USB/PC mode)
            file_path = os.path.join(OUTPUT_DIR, file_name)
            doc.save(file_path)

            # Store in session for download
            buffer = io.BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            st.session_state.generated = True
            st.session_state.downloaded = False
            st.session_state.file_name = file_name
            st.session_state.file_data = buffer.getvalue()

            st.success(f"✅ 完成！請點擊下方按鈕下載。")
            st.balloons()

        except Exception as e:
            st.error(f"系統出錯：{e}")

with col_clear:
    if st.button("🔄 清除所有欄位"):
        if st.session_state.generated and not st.session_state.downloaded:
            st.session_state.confirm_reset = True
        else:
            st.session_state.generated = False
            st.session_state.downloaded = False
            st.session_state.confirm_reset = False
            st.rerun()

# ── Download button ───────────────────────────────────────────────────
if st.session_state.generated:
    dl = st.download_button(
        label="📥 下載平安紙",
        data=st.session_state.file_data,
        file_name=st.session_state.file_name,
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        use_container_width=False
    )
    if dl:
        st.session_state.downloaded = True

# ── Reset confirmation ────────────────────────────────────────────────
if st.session_state.confirm_reset:
    st.warning("⚠️ 您尚未下載平安紙！確定要清除所有欄位嗎？")
    conf1, conf2 = st.columns([1, 5])
    with conf1:
        if st.button("✅ 確定清除", type="primary"):
            st.session_state.generated = False
            st.session_state.downloaded = False
            st.session_state.confirm_reset = False
            st.rerun()
    with conf2:
        if st.button("❌ 返回下載"):
            st.session_state.confirm_reset = False
            st.rerun()
