"""
Script to generate the official 12-slide presentation for EduSearch AI.
Adheres strictly to the 12-slide structure, design guidelines, and frontend architecture.
"""

import sys
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# -----------------------------------------------------------------------------
# PRESENTATION SETUP & PALETTE CONFIGURATION
# -----------------------------------------------------------------------------
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# Color Palette (Modern AI / Tech / Education theme matching Streamlit UI)
BG_DARK = RGBColor(11, 17, 32)        # Deep Obsidian Navy #0B1120
CARD_BG = RGBColor(19, 29, 54)        # Midnight Slate #131D36
CARD_BG_LIGHT = RGBColor(27, 40, 72)  # Elevated Slate #1B2848
CARD_BORDER = RGBColor(40, 60, 102)   # Subtle Border #283C66

# Neon / High-Tech Accents
ACCENT_TEAL = RGBColor(0, 229, 163)   # Signature Vibrant Teal #00E5A3
ACCENT_CYAN = RGBColor(56, 189, 248)  # Electric Cyan #38BDF8
ACCENT_PURPLE = RGBColor(139, 92, 246) # Vivid Violet #8B5CF6
ACCENT_INDIGO = RGBColor(99, 102, 241) # Indigo #6366F1
ACCENT_AMBER = RGBColor(245, 158, 11) # Warm Amber #F59E0B
ACCENT_ROSE = RGBColor(244, 63, 94)   # Rose Red #F43F5E

# Typography Colors
TEXT_WHITE = RGBColor(255, 255, 255)
TEXT_LIGHT = RGBColor(226, 232, 240)  # Slate 200 #E2E8F0
TEXT_MUTED = RGBColor(148, 163, 184)  # Slate 400 #94A3B8
TEXT_DARK = RGBColor(15, 23, 42)

FONT_HEADING = "Segoe UI"
FONT_BODY = "Segoe UI"

blank_slide_layout = prs.slide_layouts[6]

# -----------------------------------------------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------------------------------------------
def set_slide_background(slide, color=BG_DARK):
    bg_shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg_shape.fill.solid()
    bg_shape.fill.fore_color.rgb = color
    bg_shape.line.fill.background()
    return bg_shape

def add_header(slide, kicker: str, title: str, subtitle: str, slide_num: int):
    """Creates a consistent, sleek top banner with kicker, title, subtitle, and slide counter."""
    # Kicker Pill
    pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.4), Inches(2.2), Inches(0.32))
    pill.fill.solid()
    pill.fill.fore_color.rgb = CARD_BG_LIGHT
    pill.line.color.rgb = ACCENT_TEAL
    pill.line.width = Pt(1)
    tf_pill = pill.text_frame
    tf_pill.word_wrap = True
    tf_pill.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_pill = tf_pill.paragraphs[0]
    p_pill.text = kicker.upper()
    p_pill.alignment = PP_ALIGN.CENTER
    p_pill.font.name = FONT_HEADING
    p_pill.font.size = Pt(9.5)
    p_pill.font.bold = True
    p_pill.font.color.rgb = ACCENT_TEAL

    # Slide Counter
    counter = slide.shapes.add_textbox(Inches(11.2), Inches(0.35), Inches(1.333), Inches(0.4))
    tf_c = counter.text_frame
    p_c = tf_c.paragraphs[0]
    p_c.text = f"{slide_num:02d} / 12"
    p_c.alignment = PP_ALIGN.RIGHT
    p_c.font.name = FONT_HEADING
    p_c.font.size = Pt(12)
    p_c.font.bold = True
    p_c.font.color.rgb = ACCENT_CYAN

    # Main Title
    t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(10.5), Inches(0.65))
    tf_t = t_box.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = tf_t.margin_top = tf_t.margin_right = tf_t.margin_bottom = 0
    p_t = tf_t.paragraphs[0]
    p_t.text = title
    p_t.font.name = FONT_HEADING
    p_t.font.size = Pt(22)
    p_t.font.bold = True
    p_t.font.color.rgb = TEXT_WHITE

    # Subtitle
    s_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.38), Inches(11.5), Inches(0.45))
    tf_s = s_box.text_frame
    tf_s.word_wrap = True
    tf_s.margin_left = tf_s.margin_top = tf_s.margin_right = tf_s.margin_bottom = 0
    p_s = tf_s.paragraphs[0]
    p_s.text = subtitle
    p_s.font.name = FONT_BODY
    p_s.font.size = Pt(11.5)
    p_s.font.color.rgb = TEXT_MUTED

def create_card(slide, left, top, width, height, bg_color=CARD_BG, border_color=CARD_BORDER, border_width=1.0):
    """Draws a rounded card box with border."""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    if border_color:
        card.line.color.rgb = border_color
        card.line.width = Pt(border_width)
    else:
        card.line.fill.background()
    return card

# =============================================================================
# SLIDE 1 — EduSearch AI (Title Slide)
# =============================================================================
slide1 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide1)

# Subtle decorative background grid/glow card
glow_card = create_card(slide1, Inches(0.8), Inches(0.7), Inches(11.733), Inches(6.1), CARD_BG, CARD_BORDER, 1.5)

# Brand Kicker Badge
badge = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.3), Inches(1.15), Inches(3.2), Inches(0.4))
badge.fill.solid()
badge.fill.fore_color.rgb = CARD_BG_LIGHT
badge.line.color.rgb = ACCENT_TEAL
badge.line.width = Pt(1.5)
tf_b = badge.text_frame
tf_b.vertical_anchor = MSO_ANCHOR.MIDDLE
p_b = tf_b.paragraphs[0]
p_b.text = "✦ AI-POWERED ACADEMIC ECOSYSTEM"
p_b.font.name = FONT_HEADING
p_b.font.size = Pt(10.5)
p_b.font.bold = True
p_b.font.color.rgb = ACCENT_TEAL
p_b.alignment = PP_ALIGN.CENTER

# Main Title
title_box = slide1.shapes.add_textbox(Inches(1.25), Inches(1.65), Inches(7.5), Inches(1.1))
tf = title_box.text_frame
tf.word_wrap = True
tf.margin_left = tf.margin_top = 0
p = tf.paragraphs[0]
p.text = "EduSearch AI"
p.font.name = FONT_HEADING
p.font.size = Pt(46)
p.font.bold = True
p.font.color.rgb = TEXT_WHITE

# Subtitle
sub_box = slide1.shapes.add_textbox(Inches(1.25), Inches(2.75), Inches(7.5), Inches(0.6))
tf_sub = sub_box.text_frame
tf_sub.word_wrap = True
tf_sub.margin_left = tf_sub.margin_top = 0
p_sub = tf_sub.paragraphs[0]
p_sub.text = "AI-Powered Smart Learning & Productivity Platform"
p_sub.font.name = FONT_HEADING
p_sub.font.size = Pt(19)
p_sub.font.bold = True
p_sub.font.color.rgb = ACCENT_CYAN

# One-line description
desc_box = slide1.shapes.add_textbox(Inches(1.25), Inches(3.45), Inches(7.2), Inches(0.8))
tf_d = desc_box.text_frame
tf_d.word_wrap = True
tf_d.margin_left = tf_d.margin_top = 0
p_d = tf_d.paragraphs[0]
p_d.text = "A unified student workspace integrating intelligent question paper analysis, Gemini-driven tutoring, adaptive focus scheduling, and daily achievement tracking."
p_d.font.name = FONT_BODY
p_d.font.size = Pt(13)
p_d.font.color.rgb = TEXT_LIGHT

# Feature Highlight Chips
chips = ["Gemini 3.6 Multimodal AI", "Automated Paper Parsing", "Smart Timetable & Timer", "Session Analytics"]
chip_left = Inches(1.25)
for c_text in chips:
    chip = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, chip_left, Inches(4.35), Inches(1.68), Inches(0.35))
    chip.fill.solid()
    chip.fill.fore_color.rgb = CARD_BG_LIGHT
    chip.line.color.rgb = ACCENT_INDIGO
    chip.line.width = Pt(1)
    tf_c = chip.text_frame
    tf_c.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_c = tf_c.paragraphs[0]
    p_c.text = c_text
    p_c.font.name = FONT_BODY
    p_c.font.size = Pt(8.5)
    p_c.font.bold = True
    p_c.font.color.rgb = TEXT_LIGHT
    p_c.alignment = PP_ALIGN.CENTER
    chip_left += Inches(1.78)

# Right Side Tech Visual Card
tech_card = create_card(slide1, Inches(8.9), Inches(1.15), Inches(3.2), Inches(5.15), CARD_BG_LIGHT, ACCENT_CYAN, 1.5)
# Title inside card
tc_box = slide1.shapes.add_textbox(Inches(9.1), Inches(1.35), Inches(2.8), Inches(0.4))
tf_tc = tc_box.text_frame
p_tc = tf_tc.paragraphs[0]
p_tc.text = "PROJECT METRICS & TECH"
p_tc.font.name = FONT_HEADING
p_tc.font.size = Pt(11)
p_tc.font.bold = True
p_tc.font.color.rgb = ACCENT_CYAN

tech_items = [
    ("Core Framework", "Streamlit Multi-Page Architecture"),
    ("Intelligence Engine", "Google Gemini 3.6 Flash LLM"),
    ("Document Processing", "PyPDF Text & Regex Tokenizer"),
    ("Persistence Layer", "SQLite Databases (auth & chats)"),
    ("Design Philosophy", "Card-Based Dark/Teal UI System"),
    ("Security Model", "SHA-256 Auth & Session Tokens"),
]
t_top = Inches(1.85)
for label, val in tech_items:
    t_box = slide1.shapes.add_textbox(Inches(9.1), t_top, Inches(2.8), Inches(0.5))
    tf_t = t_box.text_frame
    tf_t.word_wrap = True
    tf_t.margin_top = tf_t.margin_left = tf_t.margin_bottom = 0
    p1 = tf_t.paragraphs[0]
    p1.text = label
    p1.font.name = FONT_BODY
    p1.font.size = Pt(9)
    p1.font.color.rgb = TEXT_MUTED
    p2 = tf_t.add_paragraph()
    p2.text = val
    p2.font.name = FONT_HEADING
    p2.font.size = Pt(10.5)
    p2.font.bold = True
    p2.font.color.rgb = TEXT_WHITE
    t_top += Inches(0.7)

# Bottom Presentation Placeholders Card
p_card = create_card(slide1, Inches(1.25), Inches(4.95), Inches(7.35), Inches(1.35), CARD_BG_LIGHT, CARD_BORDER, 1.0)

# 3 Placeholder columns
p_col1 = slide1.shapes.add_textbox(Inches(1.4), Inches(5.05), Inches(2.2), Inches(1.15))
tf1 = p_col1.text_frame
tf1.word_wrap = True
p1_h = tf1.paragraphs[0]
p1_h.text = "PRESENTED BY"
p1_h.font.name = FONT_HEADING
p1_h.font.size = Pt(9)
p1_h.font.bold = True
p1_h.font.color.rgb = ACCENT_TEAL
p1_v = tf1.add_paragraph()
p1_v.text = "[Student Name / Lead]\nRoll No: [XXXXXX]"
p1_v.font.name = FONT_BODY
p1_v.font.size = Pt(10)
p1_v.font.color.rgb = TEXT_WHITE

p_col2 = slide1.shapes.add_textbox(Inches(3.8), Inches(5.05), Inches(2.3), Inches(1.15))
tf2 = p_col2.text_frame
tf2.word_wrap = True
p2_h = tf2.paragraphs[0]
p2_h.text = "TEAM MEMBERS"
p2_h.font.name = FONT_HEADING
p2_h.font.size = Pt(9)
p2_h.font.bold = True
p2_h.font.color.rgb = ACCENT_PURPLE
p2_v = tf2.add_paragraph()
p2_v.text = "• [Member 1 - Full Stack]\n• [Member 2 - AI Integration]\n• [Member 3 - UI/UX Design]"
p2_v.font.name = FONT_BODY
p2_v.font.size = Pt(9.5)
p2_v.font.color.rgb = TEXT_WHITE

p_col3 = slide1.shapes.add_textbox(Inches(6.3), Inches(5.05), Inches(2.2), Inches(1.15))
tf3 = p_col3.text_frame
tf3.word_wrap = True
p3_h = tf3.paragraphs[0]
p3_h.text = "COLLEGE / INSTITUTION"
p3_h.font.name = FONT_HEADING
p3_h.font.size = Pt(9)
p3_h.font.bold = True
p3_h.font.color.rgb = ACCENT_CYAN
p3_v = tf3.add_paragraph()
p3_v.text = "[Department of Computer Science]\n[Institution / University Name]\nAcademic Year 2025-2026"
p3_v.font.name = FONT_BODY
p3_v.font.size = Pt(9.5)
p3_v.font.color.rgb = TEXT_WHITE


# =============================================================================
# SLIDE 2 — Introduction
# =============================================================================
slide2 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide2)
add_header(slide2, "Platform Overview", "Introduction to EduSearch AI",
           "Next-generation academic workspace unifying AI assistance with student workflow management", 2)

intro_cards = [
    {
        "kicker": "CORE PURPOSE",
        "title": "AI-Powered Learning Platform",
        "desc": "Built to empower students through cutting-edge artificial intelligence, transforming unstructured study materials into high-yield learning pathways.",
        "badge": "Generative Tutoring",
        "color": ACCENT_TEAL
    },
    {
        "kicker": "UNIFIED WORKFLOW",
        "title": "Integrated Study Management",
        "desc": "Seamlessly fuses active AI assistance with study schedule generation, focused timing blocks, and automated daily progress monitoring.",
        "badge": "Study Sync",
        "color": ACCENT_CYAN
    },
    {
        "kicker": "CENTRALIZED SUITE",
        "title": "All-in-One Educational Suite",
        "desc": "Eliminates tool fragmentation by centralizing question paper analysis, document-grounded Q&A, and milestone tracking into a single interface.",
        "badge": "No Tool Hopping",
        "color": ACCENT_PURPLE
    },
    {
        "kicker": "PROVEN OUTCOMES",
        "title": "Organized, Interactive & Efficient",
        "desc": "Converts passive reading into active, data-driven revision, enhancing exam preparedness and study habit consistency.",
        "badge": "Smart Results",
        "color": ACCENT_AMBER
    }
]

left_start = Inches(0.8)
card_w = Inches(2.78)
for i, item in enumerate(intro_cards):
    cur_left = left_start + i * Inches(2.98)
    card = create_card(slide2, cur_left, Inches(2.0), card_w, Inches(3.9), CARD_BG, item["color"], 1.5)
    
    # Pill inside card
    pill = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left + Inches(0.2), Inches(2.25), Inches(1.4), Inches(0.28))
    pill.fill.solid()
    pill.fill.fore_color.rgb = CARD_BG_LIGHT
    pill.line.color.rgb = item["color"]
    pill.line.width = Pt(1)
    tf_p = pill.text_frame
    tf_p.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_p = tf_p.paragraphs[0]
    p_p.text = item["kicker"]
    p_p.font.name = FONT_HEADING
    p_p.font.size = Pt(8.5)
    p_p.font.bold = True
    p_p.font.color.rgb = item["color"]
    p_p.alignment = PP_ALIGN.CENTER

    # Title
    t_box = slide2.shapes.add_textbox(cur_left + Inches(0.2), Inches(2.68), card_w - Inches(0.4), Inches(0.8))
    tf_t = t_box.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = tf_t.margin_top = 0
    p_t = tf_t.paragraphs[0]
    p_t.text = item["title"]
    p_t.font.name = FONT_HEADING
    p_t.font.size = Pt(14)
    p_t.font.bold = True
    p_t.font.color.rgb = TEXT_WHITE

    # Description
    d_box = slide2.shapes.add_textbox(cur_left + Inches(0.2), Inches(3.55), card_w - Inches(0.4), Inches(1.5))
    tf_d = d_box.text_frame
    tf_d.word_wrap = True
    tf_d.margin_left = tf_d.margin_top = 0
    p_d = tf_d.paragraphs[0]
    p_d.text = item["desc"]
    p_d.font.name = FONT_BODY
    p_d.font.size = Pt(10.5)
    p_d.font.color.rgb = TEXT_LIGHT

    # Bottom Badge
    b_box = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left + Inches(0.2), Inches(5.35), card_w - Inches(0.4), Inches(0.35))
    b_box.fill.solid()
    b_box.fill.fore_color.rgb = CARD_BG_LIGHT
    b_box.line.fill.background()
    tf_b = b_box.text_frame
    tf_b.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_b = tf_b.paragraphs[0]
    p_b.text = f"★ {item['badge']}"
    p_b.font.name = FONT_HEADING
    p_b.font.size = Pt(9.5)
    p_b.font.bold = True
    p_b.font.color.rgb = item["color"]
    p_b.alignment = PP_ALIGN.CENTER

# Summary Bottom Banner
bot_banner = create_card(slide2, Inches(0.8), Inches(6.15), Inches(11.733), Inches(0.85), CARD_BG_LIGHT, CARD_BORDER, 1.0)
bb_box = slide2.shapes.add_textbox(Inches(1.0), Inches(6.25), Inches(11.333), Inches(0.65))
tf_bb = bb_box.text_frame
tf_bb.word_wrap = True
p_bb = tf_bb.paragraphs[0]
p_bb.text = "ARCHITECTURE HIGHLIGHT: Engineered as a modular Streamlit multi-page platform backed by local SQLite persistence and Google Gemini 3.6 Flash for responsive student interactions."
p_bb.font.name = FONT_BODY
p_bb.font.size = Pt(10.5)
p_bb.font.color.rgb = TEXT_LIGHT


# =============================================================================
# SLIDE 3 — Problem Statement
# =============================================================================
slide3 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide3)
add_header(slide3, "Market Need & Pain Points", "Problem Statement: Challenges Faced by Students",
           "Current study workflows are fragmented, inefficient, and lack intelligent automation", 3)

problems = [
    {
        "tag": "PAIN POINT 01",
        "title": "Difficulty Managing Study Time",
        "desc": "Students struggle to allocate focused time blocks across extensive syllabi, leading to severe last-minute cramming and academic stress.",
        "icon": "⏱"
    },
    {
        "tag": "PAIN POINT 02",
        "title": "Lack of Centralized Tools",
        "desc": "Students constantly juggle between multiple disparate applications for notes, timers, question papers, and query resolution.",
        "icon": "🧩"
    },
    {
        "tag": "PAIN POINT 03",
        "title": "Tedious Question Paper Analysis",
        "desc": "Manual cross-referencing of previous examination papers is time-consuming and often fails to identify recurring high-yield question patterns.",
        "icon": "📄"
    },
    {
        "tag": "PAIN POINT 04",
        "title": "No Daily Achievement Tracking",
        "desc": "Absence of structured micro-goal tracking causes loss of daily study momentum and reduces student accountability over time.",
        "icon": "🎯"
    },
    {
        "tag": "PAIN POINT 05",
        "title": "Lack of Long-Term Progress History",
        "desc": "Students cannot easily review historical queries, previous exam breakdowns, or track study improvements across semesters.",
        "icon": "📊"
    },
    {
        "tag": "PAIN POINT 06",
        "title": "Need for Context-Aware AI Tutor",
        "desc": "Generic search engines fail to provide structured, curriculum-grounded explanations specifically tailored to syllabus documents.",
        "icon": "🤖"
    }
]

# 2 rows x 3 columns grid
row_h = Inches(1.85)
col_w = Inches(3.78)
left_positions = [Inches(0.8), Inches(4.78), Inches(8.75)]
top_positions = [Inches(2.0), Inches(4.05)]

for idx, p_item in enumerate(problems):
    row_idx = idx // 3
    col_idx = idx % 3
    c_left = left_positions[col_idx]
    c_top = top_positions[row_idx]

    card = create_card(slide3, c_left, c_top, col_w, row_h, CARD_BG, ACCENT_ROSE, 1.2)

    # Icon + Tag
    tag_box = slide3.shapes.add_textbox(c_left + Inches(0.18), c_top + Inches(0.12), col_w - Inches(0.36), Inches(0.3))
    tf_tag = tag_box.text_frame
    tf_tag.margin_top = tf_tag.margin_left = 0
    p_tag = tf_tag.paragraphs[0]
    p_tag.text = f"{p_item['icon']}  {p_item['tag']}"
    p_tag.font.name = FONT_HEADING
    p_tag.font.size = Pt(9.5)
    p_tag.font.bold = True
    p_tag.font.color.rgb = ACCENT_ROSE

    # Title
    title_box = slide3.shapes.add_textbox(c_left + Inches(0.18), c_top + Inches(0.42), col_w - Inches(0.36), Inches(0.4))
    tf_t = title_box.text_frame
    tf_t.word_wrap = True
    tf_t.margin_top = tf_t.margin_left = 0
    p_t = tf_t.paragraphs[0]
    p_t.text = p_item["title"]
    p_t.font.name = FONT_HEADING
    p_t.font.size = Pt(12)
    p_t.font.bold = True
    p_t.font.color.rgb = TEXT_WHITE

    # Desc
    d_box = slide3.shapes.add_textbox(c_left + Inches(0.18), c_top + Inches(0.85), col_w - Inches(0.36), Inches(0.9))
    tf_d = d_box.text_frame
    tf_d.word_wrap = True
    tf_d.margin_top = tf_d.margin_left = 0
    p_d = tf_d.paragraphs[0]
    p_d.text = p_item["desc"]
    p_d.font.name = FONT_BODY
    p_d.font.size = Pt(9.5)
    p_d.font.color.rgb = TEXT_MUTED

# Bottom Impact Strip
impact_strip = create_card(slide3, Inches(0.8), Inches(6.15), Inches(11.733), Inches(0.85), CARD_BG_LIGHT, ACCENT_AMBER, 1.2)
is_box = slide3.shapes.add_textbox(Inches(1.0), Inches(6.25), Inches(11.333), Inches(0.65))
tf_is = is_box.text_frame
tf_is.word_wrap = True
p_is = tf_is.paragraphs[0]
p_is.text = "CORE PROBLEM IMPACT: Disconnected study tools and manual paper analysis cause significant study fatigue, inefficient preparation, and missed academic targets."
p_is.font.name = FONT_HEADING
p_is.font.size = Pt(10.5)
p_is.font.bold = True
p_is.font.color.rgb = ACCENT_AMBER


# =============================================================================
# SLIDE 4 — Proposed Solution: EduSearch AI
# =============================================================================
slide4 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide4)
add_header(slide4, "End-to-End Architecture", "Proposed Solution: The EduSearch AI Workflow",
           "An integrated pipeline connecting user authentication to continuous learning analytics", 4)

workflow_steps = [
    ("01", "Login", "Secure SHA-256 Auth & User Isolation", ACCENT_TEAL),
    ("02", "Dashboard", "Central Command Center & Analytics", ACCENT_CYAN),
    ("03", "AI Assistant", "Document-Grounded Gemini 3.6 Tutoring", ACCENT_PURPLE),
    ("04", "Analyzer", "PDF Question Parsing & Pattern Detection", ACCENT_ROSE),
    ("05", "Study Timer", "AI Timetable Generation & Focus Blocks", ACCENT_AMBER),
    ("06", "Achievement", "Daily Goal Logging & Streaks", ACCENT_TEAL),
    ("07", "History", "Persistent SQLite Session Audit Trail", ACCENT_CYAN),
]

wf_left = Inches(0.8)
node_w = Inches(1.48)
gap = Inches(0.22)

for i, (num, name, desc, color) in enumerate(workflow_steps):
    card = create_card(slide4, wf_left, Inches(2.1), node_w, Inches(2.5), CARD_BG, color, 1.5)

    # Step Number Circle / Pill
    num_pill = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, wf_left + Inches(0.15), Inches(2.25), Inches(0.55), Inches(0.32))
    num_pill.fill.solid()
    num_pill.fill.fore_color.rgb = CARD_BG_LIGHT
    num_pill.line.color.rgb = color
    num_pill.line.width = Pt(1)
    tf_np = num_pill.text_frame
    tf_np.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_np = tf_np.paragraphs[0]
    p_np.text = num
    p_np.font.name = FONT_HEADING
    p_np.font.size = Pt(9.5)
    p_np.font.bold = True
    p_np.font.color.rgb = color
    p_np.alignment = PP_ALIGN.CENTER

    # Step Name
    n_box = slide4.shapes.add_textbox(wf_left + Inches(0.12), Inches(2.7), node_w - Inches(0.24), Inches(0.5))
    tf_n = n_box.text_frame
    tf_n.word_wrap = True
    tf_n.margin_top = tf_n.margin_left = 0
    p_n = tf_n.paragraphs[0]
    p_n.text = name
    p_n.font.name = FONT_HEADING
    p_n.font.size = Pt(11.5)
    p_n.font.bold = True
    p_n.font.color.rgb = TEXT_WHITE

    # Step Desc
    d_box = slide4.shapes.add_textbox(wf_left + Inches(0.12), Inches(3.25), node_w - Inches(0.24), Inches(1.2))
    tf_d = d_box.text_frame
    tf_d.word_wrap = True
    tf_d.margin_top = tf_d.margin_left = 0
    p_d = tf_d.paragraphs[0]
    p_d.text = desc
    p_d.font.name = FONT_BODY
    p_d.font.size = Pt(9)
    p_d.font.color.rgb = TEXT_MUTED

    # Arrow connector (except last)
    if i < len(workflow_steps) - 1:
        arr_box = slide4.shapes.add_textbox(wf_left + node_w, Inches(2.8), gap, Inches(0.5))
        tf_a = arr_box.text_frame
        tf_a.margin_top = tf_a.margin_left = 0
        p_a = tf_a.paragraphs[0]
        p_a.text = "→"
        p_a.alignment = PP_ALIGN.CENTER
        p_a.font.name = FONT_HEADING
        p_a.font.size = Pt(14)
        p_a.font.bold = True
        p_a.font.color.rgb = ACCENT_CYAN

    wf_left += node_w + gap

# Bottom Architectural Synergy Detail Box
syn_card = create_card(slide4, Inches(0.8), Inches(4.9), Inches(11.733), Inches(2.1), CARD_BG_LIGHT, CARD_BORDER, 1.2)

syn_title = slide4.shapes.add_textbox(Inches(1.1), Inches(5.05), Inches(11.0), Inches(0.35))
tf_st = syn_title.text_frame
p_st = tf_st.paragraphs[0]
p_st.text = "HOW THESE FEATURES WORK TOGETHER AS AN INTEGRATED SYSTEM"
p_st.font.name = FONT_HEADING
p_st.font.size = Pt(11.5)
p_st.font.bold = True
p_st.font.color.rgb = ACCENT_TEAL

synergy_points = [
    ("Unified Data Loop", "Extracted questions and analyzed exam topics directly inform the AI Timetable generator to prioritize high-weightage topics."),
    ("Context-Aware Tutoring", "Students encountering difficult questions in analyzer or timetable can send them directly to the AI Assistant with 1-click."),
    ("Accountability Engine", "Focus timer sessions automatically record into Today's Achievements, updating daily streaks and historical progress.")
]

s_top = Inches(5.45)
for s_title, s_desc in synergy_points:
    sb = slide4.shapes.add_textbox(Inches(1.1), s_top, Inches(11.0), Inches(0.4))
    tf_s = sb.text_frame
    tf_s.word_wrap = True
    tf_s.margin_top = tf_s.margin_left = 0
    ps1 = tf_s.paragraphs[0]
    ps1.text = f"✔  {s_title}: "
    ps1.font.name = FONT_HEADING
    ps1.font.size = Pt(10.5)
    ps1.font.bold = True
    ps1.font.color.rgb = TEXT_WHITE
    run = ps1.add_run()
    run.text = s_desc
    run.font.bold = False
    run.font.color.rgb = TEXT_LIGHT
    s_top += Inches(0.45)


# =============================================================================
# SLIDE 5 — Dashboard
# =============================================================================
slide5 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide5)
add_header(slide5, "Command Center", "EduSearch AI Dashboard: Student Hub",
           "Centralized overview providing single-click navigation, live metrics, and study readiness", 5)

# Left Column: Dashboard Capabilities
left_col_card = create_card(slide5, Inches(0.8), Inches(2.0), Inches(4.5), Inches(5.0), CARD_BG, CARD_BORDER, 1.2)

lc_header = slide5.shapes.add_textbox(Inches(1.05), Inches(2.2), Inches(4.0), Inches(0.4))
tf_lch = lc_header.text_frame
p_lch = tf_lch.paragraphs[0]
p_lch.text = "CENTRALIZED DASHBOARD HIGHLIGHTS"
p_lch.font.name = FONT_HEADING
p_lch.font.size = Pt(12)
p_lch.font.bold = True
p_lch.font.color.rgb = ACCENT_CYAN

dash_features = [
    ("Consolidated Activity Overview", "Displays real-time counts of papers analyzed, questions discovered, and core topics mapped."),
    ("Instant Quick Access Hub", "Streamlined 1-click routing to Today's Achievements, AI Assistant, Question Analyzer, and History."),
    ("Personalized Student Greeting", "Dynamic user-tailored session greeting pulling from active authentication state."),
    ("System Readiness Status", "Visual status pill confirming database availability and AI service readiness.")
]

d_top = Inches(2.7)
for d_title, d_desc in dash_features:
    dfb = slide5.shapes.add_textbox(Inches(1.05), d_top, Inches(4.0), Inches(0.9))
    tf_df = dfb.text_frame
    tf_df.word_wrap = True
    tf_df.margin_top = tf_df.margin_left = 0
    p1 = tf_df.paragraphs[0]
    p1.text = f"▸ {d_title}"
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(11)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_WHITE
    p2 = tf_df.add_paragraph()
    p2.text = d_desc
    p2.font.name = FONT_BODY
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = TEXT_MUTED
    d_top += Inches(1.05)

# Right Column: UI Mockup representation matching dash.py
ui_frame = create_card(slide5, Inches(5.6), Inches(2.0), Inches(6.933), Inches(5.0), RGBColor(15, 23, 42), ACCENT_TEAL, 1.5)

# Window Bar
win_bar = slide5.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(5.6), Inches(2.0), Inches(6.933), Inches(0.38))
win_bar.fill.solid()
win_bar.fill.fore_color.rgb = CARD_BG_LIGHT
win_bar.line.fill.background()
tf_wb = win_bar.text_frame
tf_wb.vertical_anchor = MSO_ANCHOR.MIDDLE
p_wb = tf_wb.paragraphs[0]
p_wb.text = "  ● ● ●   EduSearch AI — Dashboard Workspace  (dash.py)"
p_wb.font.name = FONT_BODY
p_wb.font.size = Pt(8.5)
p_wb.font.color.rgb = TEXT_MUTED

# Inside UI: Sidebar Strip + Hero Panel
sb_strip = slide5.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(5.6), Inches(2.38), Inches(1.8), Inches(4.62))
sb_strip.fill.solid()
sb_strip.fill.fore_color.rgb = RGBColor(12, 20, 38)
sb_strip.line.fill.background()

sb_box = slide5.shapes.add_textbox(Inches(5.7), Inches(2.5), Inches(1.6), Inches(4.3))
tf_sb = sb_box.text_frame
tf_sb.word_wrap = True
tf_sb.margin_left = tf_sb.margin_top = 0
p_sbt = tf_sb.paragraphs[0]
p_sbt.text = "EDUSEARCH AI\nSmart Practice."
p_sbt.font.name = FONT_HEADING
p_sbt.font.size = Pt(9)
p_sbt.font.bold = True
p_sbt.font.color.rgb = ACCENT_TEAL

nav_items = ["\n⊞ Dashboard", "📄 Question Analyzer", "🤖 AI Assistant", "📅 Timetable Maker", "🏆 Today Achievement", "🕒 History"]
for nav in nav_items:
    pn = tf_sb.add_paragraph()
    pn.text = nav
    pn.font.name = FONT_BODY
    pn.font.size = Pt(8.5)
    pn.font.color.rgb = TEXT_LIGHT if "Dashboard" in nav else TEXT_MUTED

# Inside UI: Main Content Area
# Hero Panel Mockup
hero_mock = create_card(slide5, Inches(7.55), Inches(2.55), Inches(4.8), Inches(1.2), CARD_BG, CARD_BORDER, 1.0)
hm_box = slide5.shapes.add_textbox(Inches(7.7), Inches(2.65), Inches(4.5), Inches(1.0))
tf_hm = hm_box.text_frame
tf_hm.word_wrap = True
tf_hm.margin_top = tf_hm.margin_left = 0
p_hm1 = tf_hm.paragraphs[0]
p_hm1.text = "✦ YOUR STUDY COMMAND CENTER"
p_hm1.font.name = FONT_HEADING
p_hm1.font.size = Pt(8)
p_hm1.font.bold = True
p_hm1.font.color.rgb = ACCENT_TEAL

p_hm2 = tf_hm.add_paragraph()
p_hm2.text = "EduSearch AI Dashboard"
p_hm2.font.name = FONT_HEADING
p_hm2.font.size = Pt(14)
p_hm2.font.bold = True
p_hm2.font.color.rgb = TEXT_WHITE

p_hm3 = tf_hm.add_paragraph()
p_hm3.text = "Turn question papers into a sharper, more confident study plan."
p_hm3.font.name = FONT_BODY
p_hm3.font.size = Pt(8.5)
p_hm3.font.color.rgb = TEXT_MUTED

# 4 Metric Cards Mockup
metric_data = [("Papers Analyzed", "12"), ("Questions Found", "148"), ("Topics Detected", "26"), ("Study Streak", "Ready")]
m_left = Inches(7.55)
for m_label, m_val in metric_data:
    mc = create_card(slide5, m_left, Inches(3.9), Inches(1.13), Inches(0.85), CARD_BG_LIGHT, CARD_BORDER, 1.0)
    m_box = slide5.shapes.add_textbox(m_left + Inches(0.08), Inches(3.95), Inches(0.97), Inches(0.75))
    tf_m = m_box.text_frame
    tf_m.word_wrap = True
    tf_m.margin_top = tf_m.margin_left = 0
    pm1 = tf_m.paragraphs[0]
    pm1.text = m_val
    pm1.font.name = FONT_HEADING
    pm1.font.size = Pt(13)
    pm1.font.bold = True
    pm1.font.color.rgb = ACCENT_CYAN
    pm2 = tf_m.add_paragraph()
    pm2.text = m_label
    pm2.font.name = FONT_BODY
    pm2.font.size = Pt(7.5)
    pm2.font.color.rgb = TEXT_LIGHT
    m_left += Inches(1.22)

# Quick Access Cards Mockup
qa_data = [
    ("Today's Achievement", "Track 148 questions", ACCENT_TEAL),
    ("AI Assistant", "Ask, explore & study", ACCENT_PURPLE),
    ("History", "Review past 12 papers", ACCENT_CYAN)
]
qa_left = Inches(7.55)
for q_title, q_sub, q_color in qa_data:
    qac = create_card(slide5, qa_left, Inches(4.9), Inches(1.54), Inches(0.95), CARD_BG, q_color, 1.2)
    q_box = slide5.shapes.add_textbox(qa_left + Inches(0.1), Inches(4.98), Inches(1.34), Inches(0.8))
    tf_q = q_box.text_frame
    tf_q.word_wrap = True
    tf_q.margin_top = tf_q.margin_left = 0
    pq1 = tf_q.paragraphs[0]
    pq1.text = q_title
    pq1.font.name = FONT_HEADING
    pq1.font.size = Pt(9.5)
    pq1.font.bold = True
    pq1.font.color.rgb = TEXT_WHITE
    pq2 = tf_q.add_paragraph()
    pq2.text = q_sub
    pq2.font.name = FONT_BODY
    pq2.font.size = Pt(7.5)
    pq2.font.color.rgb = TEXT_MUTED
    qa_left += Inches(1.63)

# UI footer note
ui_note = slide5.shapes.add_textbox(Inches(7.55), Inches(6.05), Inches(4.8), Inches(0.8))
tf_un = ui_note.text_frame
tf_un.word_wrap = True
tf_un.margin_top = tf_un.margin_left = 0
p_un = tf_un.paragraphs[0]
p_un.text = "⚡ Real-time Streamlit session state links dashboard actions directly with local SQLite databases for instant page switches and data consistency."
p_un.font.name = FONT_BODY
p_un.font.size = Pt(8.5)
p_un.font.color.rgb = ACCENT_TEAL


# =============================================================================
# SLIDE 6 — AI Assistant
# =============================================================================
slide6 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide6)
add_header(slide6, "Intelligence Engine", "AI Assistant: Context-Aware Academic Tutor",
           "Powered by Google Gemini 3.6 Flash with document grounding and multi-key resilience", 6)

# Left Column: Architectural Features
left_card = create_card(slide6, Inches(0.8), Inches(2.0), Inches(5.2), Inches(5.0), CARD_BG, CARD_BORDER, 1.2)

ai_title = slide6.shapes.add_textbox(Inches(1.05), Inches(2.2), Inches(4.7), Inches(0.4))
tf_at = ai_title.text_frame
p_at = tf_at.paragraphs[0]
p_at.text = "KEY CAPABILITIES & ARCHITECTURE"
p_at.font.name = FONT_HEADING
p_at.font.size = Pt(12)
p_at.font.bold = True
p_at.font.color.rgb = ACCENT_PURPLE

ai_features = [
    ("Multimodal Document Grounding", "Students upload PDF notes or exam guidelines; Gemini analyzes the file directly as primary evidence, preventing hallucinations."),
    ("Interactive Concept Explanation", "Breaks down difficult theorems, code, and definitions into bulleted, digestible steps with academic rigor."),
    ("Multi-Key API Key Rotation", "Implements automatic key rotation across backup API keys (GEMINI_API_KEY_1 to 10) for continuous high availability."),
    ("Persistent SQLite Chat Archival", "Automatically records questions, answers, dates, and timestamps into chat_history.db for later revision."),
    ("Personalized Study Prompting", "Employs strict academic tutor system instructions ensuring college-level pedagogical precision.")
]

a_top = Inches(2.65)
for af_title, af_desc in ai_features:
    afb = slide6.shapes.add_textbox(Inches(1.05), a_top, Inches(4.7), Inches(0.75))
    tf_af = afb.text_frame
    tf_af.word_wrap = True
    tf_af.margin_top = tf_af.margin_left = 0
    p1 = tf_af.paragraphs[0]
    p1.text = f"✔  {af_title}"
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(10.5)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_WHITE
    p2 = tf_af.add_paragraph()
    p2.text = af_desc
    p2.font.name = FONT_BODY
    p2.font.size = Pt(9)
    p2.font.color.rgb = TEXT_MUTED
    a_top += Inches(0.82)

# Right Column: Simulated Chatbot Interface UI Mockup
chat_frame = create_card(slide6, Inches(6.3), Inches(2.0), Inches(6.233), Inches(5.0), RGBColor(15, 23, 42), ACCENT_PURPLE, 1.5)

# Chat Header
ch_bar = slide6.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.3), Inches(2.0), Inches(6.233), Inches(0.6))
ch_bar.fill.solid()
ch_bar.fill.fore_color.rgb = CARD_BG_LIGHT
ch_bar.line.fill.background()
tf_chb = ch_bar.text_frame
tf_chb.vertical_anchor = MSO_ANCHOR.MIDDLE
p_chb = tf_chb.paragraphs[0]
p_chb.text = "   🤖  EduSearch AI Tutor  •  Active Model: Gemini 3.6 Flash  •  Status: Online"
p_chb.font.name = FONT_HEADING
p_chb.font.size = Pt(9.5)
p_chb.font.bold = True
p_chb.font.color.rgb = ACCENT_TEAL

# User Bubble
user_bubble = create_card(slide6, Inches(7.4), Inches(2.8), Inches(4.9), Inches(0.85), CARD_BG, ACCENT_CYAN, 1.0)
ub_box = slide6.shapes.add_textbox(Inches(7.55), Inches(2.85), Inches(4.6), Inches(0.75))
tf_ub = ub_box.text_frame
tf_ub.word_wrap = True
tf_ub.margin_top = tf_ub.margin_left = 0
pub1 = tf_ub.paragraphs[0]
pub1.text = "📎 Attached: Data_Structures_Unit3.pdf"
pub1.font.name = FONT_HEADING
pub1.font.size = Pt(8.5)
pub1.font.bold = True
pub1.font.color.rgb = ACCENT_CYAN
pub2 = tf_ub.add_paragraph()
pub2.text = "Can you explain Dijkstra's algorithm from this PDF and list common exam traps?"
pub2.font.name = FONT_BODY
pub2.font.size = Pt(9.5)
pub2.font.color.rgb = TEXT_WHITE

# Assistant Bubble
asst_bubble = create_card(slide6, Inches(6.55), Inches(3.8), Inches(5.75), Inches(2.2), CARD_BG_LIGHT, ACCENT_PURPLE, 1.0)
ab_box = slide6.shapes.add_textbox(Inches(6.75), Inches(3.9), Inches(5.35), Inches(2.0))
tf_ab = ab_box.text_frame
tf_ab.word_wrap = True
tf_ab.margin_top = tf_ab.margin_left = 0
pab1 = tf_ab.paragraphs[0]
pab1.text = "EduSearch Academic Tutor (Grounding Source: Unit3.pdf)"
pab1.font.name = FONT_HEADING
pab1.font.size = Pt(9.5)
pab1.font.bold = True
pab1.font.color.rgb = ACCENT_PURPLE

response_bullets = [
    "Core Concept: Greedy shortest-path algorithm for weighted graphs with non-negative edges.",
    "Data Structure: Utilizes a Min-Priority Queue yielding O((V + E) log V) time complexity.",
    "Exam Trap #1: Does NOT support negative edge weights (requires Bellman-Ford instead).",
    "Exam Trap #2: Forgetting to mark nodes as visited leads to redundant relaxation steps."
]
for rb in response_bullets:
    prb = tf_ab.add_paragraph()
    prb.text = f"• {rb}"
    prb.font.name = FONT_BODY
    prb.font.size = Pt(8.8)
    prb.font.color.rgb = TEXT_LIGHT

# Chat Input bar mockup
in_bar = create_card(slide6, Inches(6.55), Inches(6.2), Inches(5.75), Inches(0.6), CARD_BG, CARD_BORDER, 1.0)
ib_box = slide6.shapes.add_textbox(Inches(6.75), Inches(6.28), Inches(5.35), Inches(0.45))
tf_ib = ib_box.text_frame
tf_ib.margin_top = tf_ib.margin_left = 0
p_ib = tf_ib.paragraphs[0]
p_ib.text = "Ask a follow-up question or upload another syllabus note...             [Send ➔]"
p_ib.font.name = FONT_BODY
p_ib.font.size = Pt(9)
p_ib.font.color.rgb = TEXT_MUTED


# =============================================================================
# SLIDE 7 — Speech & Paper Analyzer
# =============================================================================
slide7 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide7)
add_header(slide7, "Document & Audio Intelligence", "Speech & Paper Analyzer: Exam Pattern Detection",
           "Automating previous-year question paper parsing to uncover high-weightage topics", 7)

# 4-Stage Visual Workflow Across Top
steps_analyzer = [
    ("Stage 1", "Input Ingestion", "Upload multiple PDF question papers or speech/audio lecture transcripts.", ACCENT_TEAL),
    ("Stage 2", "AI Text Extraction", "PyPDF layout-aware text extraction & regex question segmentation.", ACCENT_CYAN),
    ("Stage 3", "Pattern Analysis", "Question frequency matching & topic normalization across papers.", ACCENT_PURPLE),
    ("Stage 4", "Targeted Insights", "Ranked high-yield question groups & frequency distribution report.", ACCENT_AMBER),
]

sa_left = Inches(0.8)
sa_w = Inches(2.78)
for idx, (stg, stitle, sdesc, scolor) in enumerate(steps_analyzer):
    scard = create_card(slide7, sa_left, Inches(2.0), sa_w, Inches(2.1), CARD_BG, scolor, 1.5)

    pill = slide7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, sa_left + Inches(0.15), Inches(2.15), Inches(1.1), Inches(0.28))
    pill.fill.solid()
    pill.fill.fore_color.rgb = CARD_BG_LIGHT
    pill.line.color.rgb = scolor
    pill.line.width = Pt(1)
    tf_p = pill.text_frame
    tf_p.vertical_anchor = MSO_ANCHOR.MIDDLE
    pp = tf_p.paragraphs[0]
    pp.text = stg.upper()
    pp.font.name = FONT_HEADING
    pp.font.size = Pt(8.5)
    pp.font.bold = True
    pp.font.color.rgb = scolor
    pp.alignment = PP_ALIGN.CENTER

    t_box = slide7.shapes.add_textbox(sa_left + Inches(0.15), Inches(2.55), sa_w - Inches(0.3), Inches(0.4))
    tf_t = t_box.text_frame
    tf_t.word_wrap = True
    tf_t.margin_top = tf_t.margin_left = 0
    pt = tf_t.paragraphs[0]
    pt.text = stitle
    pt.font.name = FONT_HEADING
    pt.font.size = Pt(12)
    pt.font.bold = True
    pt.font.color.rgb = TEXT_WHITE

    d_box = slide7.shapes.add_textbox(sa_left + Inches(0.15), Inches(3.0), sa_w - Inches(0.3), Inches(0.95))
    tf_d = d_box.text_frame
    tf_d.word_wrap = True
    tf_d.margin_top = tf_d.margin_left = 0
    pd = tf_d.paragraphs[0]
    pd.text = sdesc
    pd.font.name = FONT_BODY
    pd.font.size = Pt(9.5)
    pd.font.color.rgb = TEXT_MUTED

    sa_left += Inches(2.98)

# Lower Split: Left = Key Benefits, Right = Analyzer Output Mockup
# Left: Key Benefits
ben_card = create_card(slide7, Inches(0.8), Inches(4.35), Inches(5.4), Inches(2.65), CARD_BG_LIGHT, CARD_BORDER, 1.2)
bc_title = slide7.shapes.add_textbox(Inches(1.05), Inches(4.45), Inches(4.9), Inches(0.35))
tf_bc = bc_title.text_frame
p_bc = tf_bc.paragraphs[0]
p_bc.text = "CORE ADVANTAGES OVER MANUAL ANALYSIS"
p_bc.font.name = FONT_HEADING
p_bc.font.size = Pt(11)
p_bc.font.bold = True
p_bc.font.color.rgb = ACCENT_TEAL

benefits = [
    ("Saves 80%+ Preparation Time", "Eliminates hours spent manually cross-checking physical papers across exam years."),
    ("Detects Exact & Near-Matches", "Regex normalizer catches recurring questions even when wording differs slightly."),
    ("Scanned PDF OCR Alert", "Intelligently flags scanned or password-protected PDFs that require OCR preprocessing."),
    ("Direct Timetable Export", "Frequency scores feed directly into the AI Timetable maker for targeted study.")
]
b_top = Inches(4.85)
for b_h, b_d in benefits:
    bb = slide7.shapes.add_textbox(Inches(1.05), b_top, Inches(4.9), Inches(0.45))
    tf_b = bb.text_frame
    tf_b.word_wrap = True
    tf_b.margin_top = tf_b.margin_left = 0
    pb1 = tf_b.paragraphs[0]
    pb1.text = f"✔ {b_h}: "
    pb1.font.name = FONT_HEADING
    pb1.font.size = Pt(9.5)
    pb1.font.bold = True
    pb1.font.color.rgb = TEXT_WHITE
    r = pb1.add_run()
    r.text = b_d
    r.font.bold = False
    r.font.color.rgb = TEXT_LIGHT
    b_top += Inches(0.48)

# Right: Dataframe / Table Mockup
table_card = create_card(slide7, Inches(6.5), Inches(4.35), Inches(6.033), Inches(2.65), RGBColor(15, 23, 42), ACCENT_CYAN, 1.2)
tc_title = slide7.shapes.add_textbox(Inches(6.75), Inches(4.45), Inches(5.5), Inches(0.35))
tf_tc = tc_title.text_frame
p_tc = tf_tc.paragraphs[0]
p_tc.text = "LIVE ANALYZER OUTPUT PREVIEW (pages/que.py)"
p_tc.font.name = FONT_HEADING
p_tc.font.size = Pt(10.5)
p_tc.font.bold = True
p_tc.font.color.rgb = ACCENT_CYAN

# Table Rows Mockup
headers = [("Question Excerpt", Inches(6.75), Inches(2.8)), ("Occurrences", Inches(9.6), Inches(1.1)), ("Repeated", Inches(10.8), Inches(0.85)), ("Priority", Inches(11.75), Inches(0.65))]
for h_name, h_pos, h_w in headers:
    hb = slide7.shapes.add_textbox(h_pos, Inches(4.85), h_w, Inches(0.3))
    tf_hb = hb.text_frame
    tf_hb.margin_top = tf_hb.margin_left = 0
    phb = tf_hb.paragraphs[0]
    phb.text = h_name
    phb.font.name = FONT_HEADING
    phb.font.size = Pt(8.5)
    phb.font.bold = True
    phb.font.color.rgb = TEXT_MUTED

sample_rows = [
    ("Explain AVL Tree rotations with insertion examples", "4 Times", "YES", "HIGH", ACCENT_ROSE),
    ("Differentiate DFS and BFS traversal with complexity", "3 Times", "YES", "HIGH", ACCENT_ROSE),
    ("Derive Master Theorem cases for recursive recurrence", "2 Times", "YES", "MED", ACCENT_AMBER),
    ("Define B-Trees and state minimum degree properties", "1 Time", "NO", "NORM", ACCENT_TEAL),
]

row_top = Inches(5.2)
for q_text, occ, rep, pri, pcol in sample_rows:
    r1 = slide7.shapes.add_textbox(Inches(6.75), row_top, Inches(2.8), Inches(0.3))
    r1.text_frame.margin_top = r1.text_frame.margin_left = 0
    pr1 = r1.text_frame.paragraphs[0]
    pr1.text = q_text
    pr1.font.name = FONT_BODY
    pr1.font.size = Pt(8.5)
    pr1.font.color.rgb = TEXT_WHITE

    r2 = slide7.shapes.add_textbox(Inches(9.6), row_top, Inches(1.1), Inches(0.3))
    r2.text_frame.margin_top = r2.text_frame.margin_left = 0
    pr2 = r2.text_frame.paragraphs[0]
    pr2.text = occ
    pr2.font.name = FONT_BODY
    pr2.font.size = Pt(8.5)
    pr2.font.color.rgb = TEXT_LIGHT

    r3 = slide7.shapes.add_textbox(Inches(10.8), row_top, Inches(0.85), Inches(0.3))
    r3.text_frame.margin_top = r3.text_frame.margin_left = 0
    pr3 = r3.text_frame.paragraphs[0]
    pr3.text = rep
    pr3.font.name = FONT_BODY
    pr3.font.size = Pt(8.5)
    pr3.font.bold = True
    pr3.font.color.rgb = pcol

    r4 = slide7.shapes.add_textbox(Inches(11.75), row_top, Inches(0.65), Inches(0.3))
    r4.text_frame.margin_top = r4.text_frame.margin_left = 0
    pr4 = r4.text_frame.paragraphs[0]
    pr4.text = pri
    pr4.font.name = FONT_HEADING
    pr4.font.size = Pt(8.5)
    pr4.font.bold = True
    pr4.font.color.rgb = pcol

    row_top += Inches(0.4)


# =============================================================================
# SLIDE 8 — Today's Achievement
# =============================================================================
slide8 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide8)
add_header(slide8, "Gamified Consistency", "Today's Achievement: Daily Milestone Tracking",
           "Encouraging consistent study habits through micro-goals, badges, and progress logging", 8)

# Left Column: Features & Psychological Benefits
left_card8 = create_card(slide8, Inches(0.8), Inches(2.0), Inches(5.2), Inches(5.0), CARD_BG, CARD_BORDER, 1.2)

tda_title = slide8.shapes.add_textbox(Inches(1.05), Inches(2.2), Inches(4.7), Inches(0.4))
tf_tdat = tda_title.text_frame
p_tdat = tf_tdat.paragraphs[0]
p_tdat.text = "MILESTONE TRACKER HIGHLIGHTS"
p_tdat.font.name = FONT_HEADING
p_tdat.font.size = Pt(12)
p_tdat.font.bold = True
p_tdat.font.color.rgb = ACCENT_TEAL

tda_points = [
    ("Daily Accomplishment Logging", "Provides dedicated forms to record completed study goals, finished chapters, and problem sets."),
    ("Multi-Category Tagging", "Organizes entries across categories: Study, Coding, Revision, Project, and Personal Development."),
    ("Instant Status Management", "Tracks completion status (Completed, In Progress, Review Needed) to prevent unfinished tasks."),
    ("Persistent CSV & DB Storage", "Maintains local achievements.csv ensuring zero progress loss between browser sessions."),
    ("Positive Reinforcement", "Features 'Level Up' badges and visual momentum cards to sustain high student morale.")
]

t_top8 = Inches(2.7)
for tp_title, tp_desc in tda_points:
    tpb = slide8.shapes.add_textbox(Inches(1.05), t_top8, Inches(4.7), Inches(0.75))
    tf_tp = tpb.text_frame
    tf_tp.word_wrap = True
    tf_tp.margin_top = tf_tp.margin_left = 0
    p1 = tf_tp.paragraphs[0]
    p1.text = f"★  {tp_title}"
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(10.5)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_WHITE
    p2 = tf_tp.add_paragraph()
    p2.text = tp_desc
    p2.font.name = FONT_BODY
    p2.font.size = Pt(9)
    p2.font.color.rgb = TEXT_MUTED
    t_top8 += Inches(0.82)

# Right Column: Visual UI Mockup of Achievement Cards & Badges
right_card8 = create_card(slide8, Inches(6.3), Inches(2.0), Inches(6.233), Inches(5.0), RGBColor(15, 23, 42), ACCENT_TEAL, 1.5)

# Banner Badge in mockup
ach_banner = create_card(slide8, Inches(6.55), Inches(2.2), Inches(5.733), Inches(1.05), CARD_BG, ACCENT_AMBER, 1.2)
ab_box = slide8.shapes.add_textbox(Inches(6.75), Inches(2.3), Inches(5.3), Inches(0.85))
tf_ab = ab_box.text_frame
tf_ab.word_wrap = True
tf_ab.margin_top = tf_ab.margin_left = 0
pab1 = tf_ab.paragraphs[0]
pab1.text = "⚡ LEVEL UP: 5-DAY STUDY STREAK ACTIVE!"
pab1.font.name = FONT_HEADING
pab1.font.size = Pt(11)
pab1.font.bold = True
pab1.font.color.rgb = ACCENT_AMBER
pab2 = tf_ab.add_paragraph()
pab2.text = "You have completed 18 study milestones this week. Consistency rating: 94%"
pab2.font.name = FONT_BODY
pab2.font.size = Pt(9)
pab2.font.color.rgb = TEXT_LIGHT

# 3 Achievement Cards Mockup
sample_achievements = [
    ("Completed 4 Previous Exam Question Papers", "Category: Question Analyzer", "STATUS: COMPLETED", ACCENT_TEAL),
    ("Mastered Dynamic Programming Memoization", "Category: AI Assistant Tutoring", "STATUS: COMPLETED", ACCENT_TEAL),
    ("3-Hour Focused Timetable Study Session", "Category: Timetable Maker", "STATUS: IN PROGRESS", ACCENT_CYAN),
]

ach_top = Inches(3.45)
for a_title, a_cat, a_stat, a_col in sample_achievements:
    ac = create_card(slide8, Inches(6.55), ach_top, Inches(5.733), Inches(0.95), CARD_BG_LIGHT, a_col, 1.0)
    ac_box = slide8.shapes.add_textbox(Inches(6.75), ach_top + Inches(0.08), Inches(5.3), Inches(0.8))
    tf_ac = ac_box.text_frame
    tf_ac.word_wrap = True
    tf_ac.margin_top = tf_ac.margin_left = 0
    pa1 = tf_ac.paragraphs[0]
    pa1.text = a_title
    pa1.font.name = FONT_HEADING
    pa1.font.size = Pt(10)
    pa1.font.bold = True
    pa1.font.color.rgb = TEXT_WHITE
    pa2 = tf_ac.add_paragraph()
    pa2.text = f"{a_cat}   •   {a_stat}"
    pa2.font.name = FONT_BODY
    pa2.font.size = Pt(8.5)
    pa2.font.color.rgb = a_col
    ach_top += Inches(1.1)


# =============================================================================
# SLIDE 9 — Study Timer
# =============================================================================
slide9 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide9)
add_header(slide9, "Focus & Time Management", "Study Timer & Timetable Maker: Smart Scheduling",
           "Balancing available study hours with curriculum syllabus using AI-driven allocation", 9)

# Left Column: Features
left_card9 = create_card(slide9, Inches(0.8), Inches(2.0), Inches(5.2), Inches(5.0), CARD_BG, CARD_BORDER, 1.2)

timer_title = slide9.shapes.add_textbox(Inches(1.05), Inches(2.2), Inches(4.7), Inches(0.4))
tf_tt = timer_title.text_frame
p_tt = tf_tt.paragraphs[0]
p_tt.text = "SMART FOCUS & TIMETABLE CAPABILITIES"
p_tt.font.name = FONT_HEADING
p_tt.font.size = Pt(12)
p_tt.font.bold = True
p_tt.font.color.rgb = ACCENT_CYAN

timer_features = [
    ("AI-Powered Study Schedule Generation", "Takes student available hours (e.g. 2.5 hrs) and syllabus PDF, synthesizing an optimized timetable."),
    ("Strict Syllabus Alignment", "Enforces strict constraints: zero hallucinated topics; every block maps directly to the uploaded course document."),
    ("Granular Block Allocation", "Divides large topics into structured 30-45 minute focus intervals separated by cognitive rest breaks."),
    ("Chat Database Integration", "Automatically saves generated study timetables into chat_history.db for quick recall and daily tracking."),
    ("Focus Duration Accountability", "Encourages deep work sessions, significantly reducing student multitasking and distraction.")
]

tt_top = Inches(2.7)
for tf_title, tf_desc in timer_features:
    tfb = slide9.shapes.add_textbox(Inches(1.05), tt_top, Inches(4.7), Inches(0.75))
    tf_tf = tfb.text_frame
    tf_tf.word_wrap = True
    tf_tf.margin_top = tf_tf.margin_left = 0
    p1 = tf_tf.paragraphs[0]
    p1.text = f"⏱  {tf_title}"
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(10.5)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_WHITE
    p2 = tf_tf.add_paragraph()
    p2.text = tf_desc
    p2.font.name = FONT_BODY
    p2.font.size = Pt(9)
    p2.font.color.rgb = TEXT_MUTED
    tt_top += Inches(0.82)

# Right Column: Visual UI Mockup of Timer & Generated Timetable
right_card9 = create_card(slide9, Inches(6.3), Inches(2.0), Inches(6.233), Inches(5.0), RGBColor(15, 23, 42), ACCENT_CYAN, 1.5)

# Timer Focus Widget
t_widget = create_card(slide9, Inches(6.55), Inches(2.2), Inches(5.733), Inches(1.35), CARD_BG, ACCENT_TEAL, 1.2)
tw_box = slide9.shapes.add_textbox(Inches(6.75), Inches(2.3), Inches(5.3), Inches(1.15))
tf_tw = tw_box.text_frame
tf_tw.word_wrap = True
tf_tw.margin_top = tf_tw.margin_left = 0
ptw1 = tf_tw.paragraphs[0]
ptw1.text = "FOCUS SESSION IN PROGRESS  •  AVAILABLE TIME: 2 HRS 30 MIN"
ptw1.font.name = FONT_HEADING
ptw1.font.size = Pt(9)
ptw1.font.bold = True
ptw1.font.color.rgb = ACCENT_TEAL
ptw2 = tf_tw.add_paragraph()
ptw2.text = "01 : 45 : 00"
ptw2.font.name = FONT_HEADING
ptw2.font.size = Pt(28)
ptw2.font.bold = True
ptw2.font.color.rgb = TEXT_WHITE
ptw3 = tf_tw.add_paragraph()
ptw3.text = "Active Block: Module 2 — Binary Search Trees & Balanced Trees (45 min remaining)"
ptw3.font.name = FONT_BODY
ptw3.font.size = Pt(8.5)
ptw3.font.color.rgb = ACCENT_CYAN

# Timetable Blocks Mockup
tb_title = slide9.shapes.add_textbox(Inches(6.55), Inches(3.7), Inches(5.5), Inches(0.3))
tf_tbt = tb_title.text_frame
p_tbt = tf_tbt.paragraphs[0]
p_tbt.text = "GENERATED TIMETABLE (pages/timetable.py)"
p_tbt.font.name = FONT_HEADING
p_tbt.font.size = Pt(10)
p_tbt.font.bold = True
p_tbt.font.color.rgb = TEXT_LIGHT

blocks = [
    ("Block 1 (45 Min)", "Array & Linked List Traversal Analysis", "COMPLETED", ACCENT_TEAL),
    ("Block 2 (45 Min)", "Binary Search Trees & Balancing (Active)", "IN PROGRESS", ACCENT_CYAN),
    ("Break (15 Min)", "Cognitive Rest & Hydration", "UPCOMING", TEXT_MUTED),
    ("Block 3 (45 Min)", "Graph Representation: Matrix vs Adjacency", "SCHEDULED", ACCENT_PURPLE),
]

b_top9 = Inches(4.05)
for b_num, b_topic, b_st, b_col in blocks:
    bc = create_card(slide9, Inches(6.55), b_top9, Inches(5.733), Inches(0.62), CARD_BG_LIGHT, b_col, 1.0)
    bc_box = slide9.shapes.add_textbox(Inches(6.75), b_top9 + Inches(0.08), Inches(5.3), Inches(0.5))
    tf_bc = bc_box.text_frame
    tf_bc.word_wrap = True
    tf_bc.margin_top = tf_bc.margin_left = 0
    pbc1 = tf_bc.paragraphs[0]
    pbc1.text = f"{b_num} — {b_topic}"
    pbc1.font.name = FONT_HEADING
    pbc1.font.size = Pt(9.5)
    pbc1.font.bold = True
    pbc1.font.color.rgb = TEXT_WHITE
    pbc2 = tf_bc.add_paragraph()
    pbc2.text = f"Status: {b_st}"
    pbc2.font.name = FONT_BODY
    pbc2.font.size = Pt(8)
    pbc2.font.color.rgb = b_col
    b_top9 += Inches(0.68)


# =============================================================================
# SLIDE 10 — History & Progress Tracking
# =============================================================================
slide10 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide10)
add_header(slide10, "Audit Trail & Retention", "History & Progress Tracking: Long-Term Visibility",
           "Complete archival of AI interactions, analyzed papers, and timetables in local SQLite", 10)

# Left Column: Capabilities
left_card10 = create_card(slide10, Inches(0.8), Inches(2.0), Inches(5.2), Inches(5.0), CARD_BG, CARD_BORDER, 1.2)

his_title = slide10.shapes.add_textbox(Inches(1.05), Inches(2.2), Inches(4.7), Inches(0.4))
tf_ht = his_title.text_frame
p_ht = tf_ht.paragraphs[0]
p_ht.text = "HISTORY & AUDIT CAPABILITIES"
p_ht.font.name = FONT_HEADING
p_ht.font.size = Pt(12)
p_ht.font.bold = True
p_ht.font.color.rgb = ACCENT_PURPLE

his_points = [
    ("Centralized SQLite Persistence", "Stores all user queries, model responses, timestamps, and dates in chat_history.db."),
    ("User-Isolated Query History", "Enforces foreign-key user_id mapping so each student only accesses their own study records."),
    ("Search, Filter & Review", "Allows instant searching by keyword, paper title, or session date to revisit past study solutions."),
    ("Soft Deletion Management", "Includes safe deletion protocols (deleted flag) maintaining audit integrity while decluttering views."),
    ("Long-Term Study Habit Analytics", "Provides historical visibility into study consistency, helping students identify academic improvement trends.")
]

h_top = Inches(2.7)
for hp_title, hp_desc in his_points:
    hpb = slide10.shapes.add_textbox(Inches(1.05), h_top, Inches(4.7), Inches(0.75))
    tf_hp = hpb.text_frame
    tf_hp.word_wrap = True
    tf_hp.margin_top = tf_hp.margin_left = 0
    p1 = tf_hp.paragraphs[0]
    p1.text = f"📊  {hp_title}"
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(10.5)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_WHITE
    p2 = tf_hp.add_paragraph()
    p2.text = hp_desc
    p2.font.name = FONT_BODY
    p2.font.size = Pt(9)
    p2.font.color.rgb = TEXT_MUTED
    h_top += Inches(0.82)

# Right Column: Visual Timeline / Activity Log Mockup
right_card10 = create_card(slide10, Inches(6.3), Inches(2.0), Inches(6.233), Inches(5.0), RGBColor(15, 23, 42), ACCENT_PURPLE, 1.5)

log_title = slide10.shapes.add_textbox(Inches(6.55), Inches(2.2), Inches(5.5), Inches(0.35))
tf_lt = log_title.text_frame
p_lt = tf_lt.paragraphs[0]
p_lt.text = "ACTIVITY LOG & CHAT HISTORY PREVIEW (pages/his.py)"
p_lt.font.name = FONT_HEADING
p_lt.font.size = Pt(10.5)
p_lt.font.bold = True
p_lt.font.color.rgb = ACCENT_PURPLE

sample_logs = [
    ("Timetable: Operating_Systems_Final.pdf (3 Hours)", "Date: 23-09-2025 | 10:45 AM", "Generated 4-stage study plan for memory management & scheduling.", ACCENT_CYAN),
    ("AI Q&A: Explain Semaphore vs Mutex with code examples", "Date: 22-09-2025 | 04:15 PM", "Gemini 3.6 Flash returned 3 comparison points & synchronization demo.", ACCENT_PURPLE),
    ("Question Paper Analysis: 5 Previous Year Papers (DSA)", "Date: 21-09-2025 | 02:30 PM", "Extracted 148 questions; flagged 26 recurring exam questions.", ACCENT_TEAL),
    ("Milestone Logged: Completed Unit 4 Dynamic Programming", "Date: 20-09-2025 | 08:20 PM", "Recorded into achievements.csv with status: COMPLETED.", ACCENT_AMBER),
]

l_top = Inches(2.65)
for l_title, l_meta, l_desc, l_col in sample_logs:
    lc = create_card(slide10, Inches(6.55), l_top, Inches(5.733), Inches(0.95), CARD_BG_LIGHT, l_col, 1.0)
    lc_box = slide10.shapes.add_textbox(Inches(6.75), l_top + Inches(0.08), Inches(5.3), Inches(0.8))
    tf_lc = lc_box.text_frame
    tf_lc.word_wrap = True
    tf_lc.margin_top = tf_lc.margin_left = 0
    pl1 = tf_lc.paragraphs[0]
    pl1.text = l_title
    pl1.font.name = FONT_HEADING
    pl1.font.size = Pt(9.5)
    pl1.font.bold = True
    pl1.font.color.rgb = TEXT_WHITE
    pl2 = tf_lc.add_paragraph()
    pl2.text = f"{l_meta}  •  {l_desc}"
    pl2.font.name = FONT_BODY
    pl2.font.size = Pt(8.2)
    pl2.font.color.rgb = TEXT_MUTED
    l_top += Inches(1.05)


# =============================================================================
# SLIDE 11 — Login & User Experience
# =============================================================================
slide11 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide11)
add_header(slide11, "Authentication & UX", "Login & User Experience: Secure & Personalized",
           "Robust session management, SHA-256 data isolation, and cohesive aesthetic architecture", 11)

# Left Column: Auth Details & Security
left_card11 = create_card(slide11, Inches(0.8), Inches(2.0), Inches(5.2), Inches(5.0), CARD_BG, CARD_BORDER, 1.2)

auth_title = slide11.shapes.add_textbox(Inches(1.05), Inches(2.2), Inches(4.7), Inches(0.4))
tf_aut = auth_title.text_frame
p_aut = tf_aut.paragraphs[0]
p_aut.text = "SECURITY ARCHITECTURE & USER EXPERIENCE"
p_aut.font.name = FONT_HEADING
p_aut.font.size = Pt(12)
p_aut.font.bold = True
p_aut.font.color.rgb = ACCENT_TEAL

auth_points = [
    ("SHA-256 Cryptographic Hashing", "Zero plain-text password storage; all student credentials securely salted and hashed in auth.db."),
    ("Strict User Data Isolation", "Every user session is assigned a unique token; history, achievements, and papers remain completely private."),
    ("Automated Auth Gate (auth_gate())", "Unauthenticated visitors are automatically intercepted and routed to the sign-in modal across all pages."),
    ("Streamlined Sign In / Sign Up", "Features clean tabbed authentication with email verification, validation checks, and error toasts."),
    ("Cohesive Design Language", "Modern CSS system with Material Symbols Outlined, dark navy surfaces, and vibrant teal/cyan accents.")
]

au_top = Inches(2.7)
for aup_title, aup_desc in auth_points:
    aupb = slide11.shapes.add_textbox(Inches(1.05), au_top, Inches(4.7), Inches(0.75))
    tf_aup = aupb.text_frame
    tf_aup.word_wrap = True
    tf_aup.margin_top = tf_aup.margin_left = 0
    p1 = tf_aup.paragraphs[0]
    p1.text = f"🔒  {aup_title}"
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(10.5)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_WHITE
    p2 = tf_aup.add_paragraph()
    p2.text = aup_desc
    p2.font.name = FONT_BODY
    p2.font.size = Pt(9)
    p2.font.color.rgb = TEXT_MUTED
    au_top += Inches(0.82)

# Right Column: Visual Mockup connecting Login Screen to Personalized Dashboard
right_card11 = create_card(slide11, Inches(6.3), Inches(2.0), Inches(6.233), Inches(5.0), RGBColor(15, 23, 42), ACCENT_TEAL, 1.5)

# Left sub-box: Login Card Mockup
login_box = create_card(slide11, Inches(6.55), Inches(2.3), Inches(2.6), Inches(4.3), CARD_BG, ACCENT_TEAL, 1.2)
l_box_tb = slide11.shapes.add_textbox(Inches(6.7), Inches(2.45), Inches(2.3), Inches(3.9))
tf_ltb = l_box_tb.text_frame
tf_ltb.word_wrap = True
tf_ltb.margin_top = tf_ltb.margin_left = 0
plt1 = tf_ltb.paragraphs[0]
plt1.text = "SIGN IN TO EDUSEARCH"
plt1.font.name = FONT_HEADING
plt1.font.size = Pt(9)
plt1.font.bold = True
plt1.font.color.rgb = ACCENT_TEAL

login_fields = [
    ("\nUsername / Email:", "student@university.edu"),
    ("Password:", "••••••••••••"),
    ("Security:", "SHA-256 Verified"),
]
for f_label, f_val in login_fields:
    pf = tf_ltb.add_paragraph()
    pf.text = f"{f_label}\n[{f_val}]"
    pf.font.name = FONT_BODY
    pf.font.size = Pt(8.2)
    pf.font.color.rgb = TEXT_LIGHT

btn_p = tf_ltb.add_paragraph()
btn_p.text = "\n[ ➔  Sign In Button ]"
btn_p.font.name = FONT_HEADING
btn_p.font.size = Pt(9)
btn_p.font.bold = True
btn_p.font.color.rgb = ACCENT_TEAL

# Arrow between Login and Dashboard
flow_arr = slide11.shapes.add_textbox(Inches(9.2), Inches(4.0), Inches(0.5), Inches(0.5))
tf_fa = flow_arr.text_frame
p_fa = tf_fa.paragraphs[0]
p_fa.text = "➔"
p_fa.alignment = PP_ALIGN.CENTER
p_fa.font.name = FONT_HEADING
p_fa.font.size = Pt(20)
p_fa.font.bold = True
p_fa.font.color.rgb = ACCENT_CYAN

# Right sub-box: Personalized Dashboard State Mockup
dash_mock = create_card(slide11, Inches(9.75), Inches(2.3), Inches(2.55), Inches(4.3), CARD_BG_LIGHT, ACCENT_CYAN, 1.2)
dm_tb = slide11.shapes.add_textbox(Inches(9.9), Inches(2.45), Inches(2.25), Inches(3.9))
tf_dm = dm_tb.text_frame
tf_dm.word_wrap = True
tf_dm.margin_top = tf_dm.margin_left = 0
pdm1 = tf_dm.paragraphs[0]
pdm1.text = "PERSONALIZED WORKSPACE"
pdm1.font.name = FONT_HEADING
pdm1.font.size = Pt(9)
pdm1.font.bold = True
pdm1.font.color.rgb = ACCENT_CYAN

dash_states = [
    ("\nActive User:", "Welcome, Alex [ID: #104]"),
    ("Personalized Data:", "• 12 Papers Analyzed\n• 48 Chat Sessions\n• 5 Active Goals"),
    ("Auth Token:", "Session Active (auth_sessions)"),
    ("Logout Action:", "[Sign Out Button]"),
]
for ds_label, ds_val in dash_states:
    pds = tf_dm.add_paragraph()
    pds.text = f"{ds_label}\n{ds_val}"
    pds.font.name = FONT_BODY
    pds.font.size = Pt(8.2)
    pds.font.color.rgb = TEXT_LIGHT


# =============================================================================
# SLIDE 12 — Conclusion & Future Scope
# =============================================================================
slide12 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide12)
add_header(slide12, "Summary & Vision", "Conclusion & Future Scope",
           "Transforming student productivity today while engineering the future of education", 12)

# Left Column: Project Conclusion
left_card12 = create_card(slide12, Inches(0.8), Inches(2.0), Inches(5.6), Inches(4.2), CARD_BG, ACCENT_TEAL, 1.5)

conc_title = slide12.shapes.add_textbox(Inches(1.05), Inches(2.2), Inches(5.1), Inches(0.35))
tf_ct = conc_title.text_frame
p_ct = tf_ct.paragraphs[0]
p_ct.text = "PROJECT CONCLUSION"
p_ct.font.name = FONT_HEADING
p_ct.font.size = Pt(13)
p_ct.font.bold = True
p_ct.font.color.rgb = ACCENT_TEAL

conclusion_points = [
    ("Integrated All-in-One Platform", "Successfully unifies exam question paper analysis, AI academic tutoring, focus scheduling, and achievement tracking in one cohesive environment."),
    ("Eliminates Fragmented Workflows", "Replaces scattered apps with a centralized student command center, saving significant study time and mental bandwidth."),
    ("Measurable Academic Productivity", "Transforms passive document reading into structured, question-driven study sessions with clear daily milestones."),
    ("Robust & Resilient Architecture", "Combines local SQLite privacy with Google Gemini 3.6 Flash and multi-key failover for reliable academic tutoring.")
]

c_top = Inches(2.65)
for cp_title, cp_desc in conclusion_points:
    cpb = slide12.shapes.add_textbox(Inches(1.05), c_top, Inches(5.1), Inches(0.7))
    tf_cp = cpb.text_frame
    tf_cp.word_wrap = True
    tf_cp.margin_top = tf_cp.margin_left = 0
    p1 = tf_cp.paragraphs[0]
    p1.text = f"✔  {cp_title}"
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(10.5)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_WHITE
    p2 = tf_cp.add_paragraph()
    p2.text = cp_desc
    p2.font.name = FONT_BODY
    p2.font.size = Pt(9)
    p2.font.color.rgb = TEXT_MUTED
    c_top += Inches(0.82)

# Right Column: Future Scope
right_card12 = create_card(slide12, Inches(6.8), Inches(2.0), Inches(5.733), Inches(4.2), CARD_BG, ACCENT_PURPLE, 1.5)

fs_title = slide12.shapes.add_textbox(Inches(7.05), Inches(2.2), Inches(5.2), Inches(0.35))
tf_fst = fs_title.text_frame
p_fst = tf_fst.paragraphs[0]
p_fst.text = "FUTURE ROADMAP & SCOPE"
p_fst.font.name = FONT_HEADING
p_fst.font.size = Pt(13)
p_fst.font.bold = True
p_fst.font.color.rgb = ACCENT_PURPLE

future_points = [
    ("Advanced AI Personalization", "Adaptive difficulty tuning, weak-topic diagnostics, and automated exam probability scoring."),
    ("Voice-Based Learning Assistant", "Full conversational voice Q&A and real-time lecture speech-to-text live summarization."),
    ("Deep Academic Analytics", "Predictive learning velocity curves, subject mastery heatmaps, and revision reminders."),
    ("Additional Educational Tools", "Interactive flashcard generator, mock quiz engine, and LaTeX formula solver."),
    ("Mobile Application Integration", "Cross-platform Flutter/React Native companion apps with push alerts and offline synchronization.")
]

f_top = Inches(2.65)
for fp_title, fp_desc in future_points:
    fpb = slide12.shapes.add_textbox(Inches(7.05), f_top, Inches(5.2), Inches(0.65))
    tf_fp = fpb.text_frame
    tf_fp.word_wrap = True
    tf_fp.margin_top = tf_fp.margin_left = 0
    p1 = tf_fp.paragraphs[0]
    p1.text = f"🚀  {fp_title}"
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(10)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_WHITE
    p2 = tf_fp.add_paragraph()
    p2.text = fp_desc
    p2.font.name = FONT_BODY
    p2.font.size = Pt(8.8)
    p2.font.color.rgb = TEXT_MUTED
    f_top += Inches(0.68)

# Bottom Prominent Tagline Banner
tagline_card = create_card(slide12, Inches(0.8), Inches(6.35), Inches(11.733), Inches(0.75), CARD_BG_LIGHT, ACCENT_CYAN, 1.5)
tlb_box = slide12.shapes.add_textbox(Inches(1.0), Inches(6.45), Inches(11.333), Inches(0.55))
tf_tlb = tlb_box.text_frame
tf_tlb.word_wrap = True
tf_tlb.vertical_anchor = MSO_ANCHOR.MIDDLE
p_tagline = tf_tlb.paragraphs[0]
p_tagline.text = "“ EduSearch AI — Learn Smarter. Study Better. Achieve More. ”"
p_tagline.alignment = PP_ALIGN.CENTER
p_tagline.font.name = FONT_HEADING
p_tagline.font.size = Pt(14)
p_tagline.font.bold = True
p_tagline.font.color.rgb = ACCENT_CYAN

# -----------------------------------------------------------------------------
# SAVE PRESENTATION
# -----------------------------------------------------------------------------
output_path = Path("EduSearch_AI_Presentation.pptx").resolve()
prs.save(str(output_path))
print(f"SUCCESS: EduSearch AI Presentation generated with EXACTLY {len(prs.slides)} slides at: {output_path}")
