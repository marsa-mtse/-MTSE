import streamlit as st
from groq import Groq
import pandas as pd
import sqlite3
import hashlib
import datetime

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
page_title="MTSE Marketing Engine",
page_icon="🚀",
layout="wide"
)

# =========================
# LANGUAGE SYSTEM
# =========================

if "lang" not in st.session_state:
    st.session_state.lang="en"

def t(ar,en):
    return ar if st.session_state.lang=="ar" else en

def ai_lang():
    return "Respond in Arabic. " if st.session_state.lang=="ar" else "Respond in English. "

# =========================
# DATABASE
# =========================

conn = sqlite3.connect("mtse.db",check_same_thread=False)
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS users(
username TEXT,
password TEXT,
plan TEXT,
expiry TEXT,
is_admin INTEGER
)""")

c.execute("""CREATE TABLE IF NOT EXISTS leads(
name TEXT,
email TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS ai_logs(
user TEXT,
prompt TEXT,
result TEXT,
date TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS usage_logs(
user TEXT,
tool TEXT,
date TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS projects(
name TEXT,
owner TEXT
)""")

conn.commit()

# =========================
# PASSWORD HASH
# =========================

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# =========================
# AI LIMIT SYSTEM
# =========================

def check_limit():

    user=st.session_state.user

    data=c.execute(
    "SELECT plan FROM users WHERE username=?",
    (user,)
    ).fetchone()

    plan=data[0]

    today=str(datetime.date.today())

    usage=len(pd.read_sql(
    "SELECT * FROM usage_logs WHERE user=? AND date=?",
    conn,
    params=(user,today)
    ))

    if plan=="free" and usage>=20:
        return False

    return True

# =========================
# AI ENGINE
# =========================

def ai_generate(prompt,tool="general"):

    if not check_limit():
        return t("لقد وصلت للحد اليومي","Daily AI limit reached")

    try:

        api_key=st.secrets["GROQ_API_KEY"]

        client=Groq(api_key=api_key)

        response=client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role":"user","content":ai_lang()+prompt}]
        )

        result=response.choices[0].message.content

        c.execute(
        "INSERT INTO ai_logs VALUES(?,?,?,?)",
        (st.session_state.user,prompt,result,str(datetime.datetime.now()))
        )

        c.execute(
        "INSERT INTO usage_logs VALUES(?,?,?)",
        (st.session_state.user,tool,str(datetime.date.today()))
        )

        conn.commit()

        return result

    except Exception as e:
        return str(e)

# =========================
# LOGIN STATE
# =========================

if "logged" not in st.session_state:
    st.session_state.logged=False

# =========================
# LOGIN
# =========================

def login():

    st.title(t("تسجيل الدخول","Login"))

    user=st.text_input(t("اسم المستخدم","Username"),key="login_user")

    pw=st.text_input(t("كلمة المرور","Password"),type="password",key="login_pass")

    if st.button(t("دخول","Login"),key="login_btn"):

        pw_hash=hash_pw(pw)

        res=c.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (user,pw_hash)
        ).fetchone()

        if res:

            st.session_state.logged=True
            st.session_state.user=user
            st.rerun()

        else:

            st.error(t("بيانات خاطئة","Invalid login"))

# =========================
# REGISTER
# =========================

def register():

    st.title(t("إنشاء حساب","Create Account"))

    user=st.text_input(t("اسم المستخدم","Username"),key="reg_user")

    pw=st.text_input(t("كلمة المرور","Password"),type="password",key="reg_pass")

    if st.button(t("إنشاء","Register"),key="reg_btn"):

        c.execute(
        "INSERT INTO users VALUES(?,?,?,?,?)",
        (user,hash_pw(pw),"free","",0)
        )

        conn.commit()

        st.success(t("تم إنشاء الحساب","Account created"))

# =========================
# AUTH
# =========================

if not st.session_state.logged:

    tab1,tab2=st.tabs([t("تسجيل الدخول","Login"),t("إنشاء حساب","Register")])

    with tab1:
        login()

    with tab2:
        register()

    st.stop()

# =========================
# SIDEBAR
# =========================

with st.sidebar:

    st.title("🚀 MTSE")

    col1,col2=st.columns(2)

    if col1.button("English"):
        st.session_state.lang="en"
        st.rerun()

    if col2.button("العربية"):
        st.session_state.lang="ar"
        st.rerun()

    st.divider()

    if st.button(t("تسجيل خروج","Logout")):
        st.session_state.logged=False
        st.rerun()

    page=st.radio(
    t("القائمة","Navigation"),
    [
    "Dashboard",
    "AI Strategy",
    "Campaign Generator",
    "TikTok Analyzer",
    "Ads Generator",
    "Landing Page Builder",
    "Viral Content Engine",
    "AI Marketing Brain",
    "Auto Marketing System",
    "AI Chat",
    "Projects",
    "CRM",
    "Revenue Dashboard",
    "Admin Panel"
    ]
    )

# =========================
# DASHBOARD
# =========================

if page=="Dashboard":

    st.title(t("لوحة التحكم","Dashboard"))

    col1,col2,col3,col4=st.columns(4)

    col1.metric("Users",len(pd.read_sql("SELECT * FROM users",conn)))
    col2.metric("Leads",len(pd.read_sql("SELECT * FROM leads",conn)))
    col3.metric("AI Requests",len(pd.read_sql("SELECT * FROM ai_logs",conn)))
    col4.metric("Projects",len(pd.read_sql("SELECT * FROM projects",conn)))

# =========================
# AI STRATEGY
# =========================

elif page=="AI Strategy":

    st.title(t("استراتيجية التسويق","Marketing Strategy"))

    product=st.text_input(t("المنتج","Product"),key="product")

    audience=st.text_input(t("الجمهور","Audience"),key="audience")

    if st.button(t("توليد الاستراتيجية","Generate Strategy"),key="strategy_btn"):

        st.write(ai_generate(
        f"Create marketing strategy for {product} targeting {audience}",
        "strategy"
        ))

# =========================
# CAMPAIGN
# =========================

elif page=="Campaign Generator":

    st.title(t("مولد الحملات","Campaign Generator"))

    product=st.text_input(t("المنتج","Product"),key="camp_product")

    if st.button(t("إنشاء حملة","Generate Campaign"),key="campaign_btn"):

        st.write(ai_generate(
        f"Create advertising campaign for {product}",
        "campaign"
        ))

# =========================
# AI CHAT
# =========================

elif page=="AI Chat":

    st.title(t("دردشة الذكاء التسويقي","AI Marketing Chat"))

    prompt=st.text_area(t("اكتب سؤالك","Prompt"),key="chat_prompt")

    if st.button(t("إرسال","Send"),key="chat_btn"):

        st.write(ai_generate(prompt,"chat"))

# =========================
# PROJECTS
# =========================

elif page=="Projects":

    st.title(t("المشاريع","Projects"))

    name=st.text_input(t("اسم المشروع","Project Name"),key="project")

    if st.button(t("إنشاء مشروع","Create Project"),key="project_btn"):

        c.execute(
        "INSERT INTO projects VALUES(?,?)",
        (name,st.session_state.user)
        )

        conn.commit()

    st.dataframe(pd.read_sql("SELECT * FROM projects",conn))

# =========================
# CRM
# =========================

elif page=="CRM":

    st.title("CRM")

    name=st.text_input(t("الاسم","Name"),key="lead_name")

    email=st.text_input(t("الايميل","Email"),key="lead_email")

    if st.button(t("إضافة عميل","Add Lead"),key="lead_btn"):

        c.execute(
        "INSERT INTO leads VALUES(?,?)",
        (name,email)
        )

        conn.commit()

    st.dataframe(pd.read_sql("SELECT * FROM leads",conn))
# =========================
# TIKTOK ANALYZER
# =========================

elif page=="TikTok Analyzer":

    st.title(t("تحليل تيك توك","TikTok Analyzer"))

    topic=st.text_input(t("موضوع الفيديو","Video Topic"),key="tiktok_topic")

    if st.button(t("تحليل","Analyze"),key="tiktok_btn"):

        st.write(ai_generate(
        f"Analyze TikTok viral strategy for topic {topic}",
        "tiktok"
        ))

# =========================
# ADS GENERATOR
# =========================

elif page=="Ads Generator":

    st.title(t("مولد الإعلانات","Ads Generator"))

    product=st.text_input(t("المنتج","Product"),key="ads_product")

    platform=st.selectbox(
        t("المنصة","Platform"),
        ["Facebook","TikTok","Google"],
        key="ads_platform"
    )

    if st.button(t("إنشاء إعلان","Generate Ad"),key="ads_btn"):

        st.write(ai_generate(
        f"Create high converting {platform} ad copy for {product}",
        "ads"
        ))

# =========================
# LANDING PAGE BUILDER
# =========================

elif page=="Landing Page Builder":

    st.title(t("منشئ صفحات الهبوط","Landing Page Builder"))

    product=st.text_input(t("المنتج","Product"),key="landing_product")

    if st.button(t("إنشاء الصفحة","Generate Page"),key="landing_btn"):

        st.write(ai_generate(
        f"Create high converting landing page for {product}",
        "landing"
        ))

# =========================
# VIRAL CONTENT
# =========================

elif page=="Viral Content Engine":

    st.title(t("محرك المحتوى الفيروسي","Viral Content Engine"))

    niche=st.text_input(t("المجال","Niche"),key="viral_niche")

    if st.button(t("توليد أفكار","Generate Ideas"),key="viral_btn"):

        st.write(ai_generate(
        f"Generate 20 viral social media ideas for niche {niche}",
        "viral"
        ))

# =========================
# AI MARKETING BRAIN
# =========================

elif page=="AI Marketing Brain":

    st.title(t("العقل التسويقي","AI Marketing Brain"))

    business=st.text_input(t("نوع النشاط","Business Type"),key="brain_business")

    if st.button(t("تحليل","Analyze"),key="brain_btn"):

        st.write(ai_generate(
        f"Create full marketing strategy for business {business}",
        "brain"
        ))

# =========================
# AUTO MARKETING SYSTEM
# =========================

elif page=="Auto Marketing System":

    st.title(t("النظام التسويقي الآلي","Auto Marketing System"))

    product=st.text_input(t("المنتج","Product"),key="auto_product")

    if st.button(t("إنشاء النظام","Generate System"),key="auto_btn"):

        st.write(ai_generate(
        f"Create automated marketing funnel for product {product}",
        "automation"
        ))

# =========================
# REVENUE DASHBOARD
# =========================

elif page=="Revenue Dashboard":

    st.title(t("لوحة الأرباح","Revenue Dashboard"))

    users=pd.read_sql("SELECT * FROM users",conn)

    pro_users=len(users[users["plan"]=="pro"])

    revenue=pro_users*20

    col1,col2=st.columns(2)

    col1.metric(t("المستخدمين المدفوعين","Pro Users"),pro_users)

    col2.metric(t("الإيرادات المتوقعة","Estimated Revenue"),revenue)

# =========================
# ADMIN
# =========================

elif page=="Admin Panel":

    st.title(t("لوحة المدير","Admin Panel"))

    st.dataframe(pd.read_sql("SELECT * FROM users",conn))

    st.subheader("AI Logs")

    st.dataframe(pd.read_sql("SELECT * FROM ai_logs",conn))