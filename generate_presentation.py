import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# Initialize Presentation with 16:9 Widescreen
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

# Premium Theme Colors
COLOR_BG = RGBColor(10, 20, 14)          # Very Dark Forest Green (#0A140E)
COLOR_CARD_BG = RGBColor(19, 36, 26)     # Dark Slate Emerald (#13241A)
COLOR_CARD_BORDER = RGBColor(34, 66, 47) # Subdued Border Green (#22422F)
COLOR_PRIMARY = RGBColor(16, 185, 129)   # Emerald Bright (#10B981)
COLOR_ACCENT = RGBColor(245, 158, 11)    # Harvest Gold (#F59E0B)
COLOR_WHITE = RGBColor(248, 250, 252)    # Crisp White (#F8FAFC)
COLOR_MUTED = RGBColor(167, 186, 173)    # Muted Sage (#A7BAAD)
COLOR_HIGHLIGHT = RGBColor(52, 211, 153) # Light Mint (#34D399)
COLOR_DARK_TEXT = RGBColor(15, 23, 42)

ASSETS_DIR = r"c:\Users\rishi\Downloads\Cotton-20261003T053350Z-1-001\presentation_assets"
OUTPUT_PPTX = r"c:\Users\rishi\Downloads\Cotton-20261003T053350Z-1-001\Cotton_Farm_Intelligence_Presentation.pptx"

def create_slide_background(slide):
    """Fills slide background with dark forest green."""
    bg_shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), prs.slide_width, prs.slide_height
    )
    bg_shape.fill.solid()
    bg_shape.fill.fore_color.rgb = COLOR_BG
    bg_shape.line.fill.background()
    return bg_shape

def add_header(slide, tag_text, title_text, subtitle_text=""):
    """Adds standard header with badge, title, and Marathi/English subtitle."""
    # Tag Badge
    badge_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(4.5), Inches(0.35))
    tf_b = badge_box.text_frame
    tf_b.word_wrap = True
    tf_b.margin_left = tf_b.margin_top = tf_b.margin_right = tf_b.margin_bottom = 0
    p_b = tf_b.paragraphs[0]
    p_b.text = f"●  {tag_text.upper()}"
    p_b.font.size = Pt(10)
    p_b.font.bold = True
    p_b.font.color.rgb = COLOR_PRIMARY
    
    # Title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.72), Inches(11.5), Inches(0.55))
    tf_t = title_box.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = tf_t.margin_top = tf_t.margin_right = tf_t.margin_bottom = 0
    p_t = tf_t.paragraphs[0]
    p_t.text = title_text
    p_t.font.size = Pt(22)
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_WHITE
    
    # Subtitle
    if subtitle_text:
        sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.5), Inches(0.35))
        tf_s = sub_box.text_frame
        tf_s.word_wrap = True
        tf_s.margin_left = tf_s.margin_top = tf_s.margin_right = tf_s.margin_bottom = 0
        p_s = tf_s.paragraphs[0]
        p_s.text = subtitle_text
        p_s.font.size = Pt(12)
        p_s.font.color.rgb = COLOR_MUTED

def add_footer(slide, current_idx, total_slides=13):
    """Adds bottom brand bar and slide index."""
    footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.05), Inches(11.733), Inches(0.3))
    tf = footer_box.text_frame
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.text = f"Khandesh Cotton Farm Intelligence & Disease Diagnostic System  |  Dhule District, Maharashtra  |  Slide {current_idx} of {total_slides}"
    p.font.size = Pt(9)
    p.font.color.rgb = RGBColor(90, 115, 100)

def add_card(slide, left, top, width, height, title=None, fill_color=COLOR_CARD_BG, border_color=COLOR_CARD_BORDER):
    """Draws a themed card container."""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = fill_color
    card.line.color.rgb = border_color
    card.line.width = Pt(1.2)
    
    if title:
        title_box = slide.shapes.add_textbox(left + Inches(0.25), top + Inches(0.18), width - Inches(0.5), Inches(0.35))
        tf = title_box.text_frame
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = COLOR_HIGHLIGHT
    return card

# ==============================================================================
# SLIDE 1: Title Slide (Grand Hero)
# ==============================================================================
slide1 = prs.slides.add_slide(blank_layout)
create_slide_background(slide1)

# Subtle background decorative card
hero_card = add_card(slide1, Inches(0.8), Inches(0.8), Inches(11.733), Inches(5.9), fill_color=RGBColor(14, 28, 20), border_color=RGBColor(26, 56, 38))

# Title & Marathi Subtitle
tb = slide1.shapes.add_textbox(Inches(1.3), Inches(1.3), Inches(10.7), Inches(2.2))
tf = tb.text_frame
tf.word_wrap = True

p0 = tf.paragraphs[0]
p0.text = "🌾 KHANDESH AGRO-INTELLIGENCE"
p0.font.size = Pt(13)
p0.font.bold = True
p0.font.color.rgb = COLOR_PRIMARY
p0.space_after = Pt(10)

p1 = tf.add_paragraph()
p1.text = "Cotton Farm Intelligence & Leaf Disease Diagnostic System"
p1.font.size = Pt(32)
p1.font.bold = True
p1.font.color.rgb = COLOR_WHITE
p1.space_after = Pt(8)

p2 = tf.add_paragraph()
p2.text = "धुळे कापूस कृषी बुद्धिमत्ता — Deep Learning Diagnostics & Agro-Climatic Intelligence for Dhule District, Maharashtra"
p2.font.size = Pt(15)
p2.font.color.rgb = COLOR_ACCENT

# 4 Metric Highlights across bottom of hero card
highlights = [
    ("89.90%", "Untouched Test Accuracy", "Rigorous evaluation on 871 test leaves"),
    ("5,852", "DSU Leaf Clusters", "14,955 images forensic leakage audited"),
    ("1.87 L Ha", "Dhule Cotton Acreage", "Dhule, Shirpur, Sindkheda & Sakri"),
    ("9 Classes", "Foliar Pathologies", "MobileNetV2 Transfer Learning Baseline"),
]

card_w = Inches(2.5)
card_gap = Inches(0.2)
start_x = Inches(1.3)

for i, (val, label, sub) in enumerate(highlights):
    cx = start_x + i * (card_w + card_gap)
    c_box = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cx, Inches(3.7), card_w, Inches(1.7))
    c_box.fill.solid()
    c_box.fill.fore_color.rgb = RGBColor(20, 42, 30)
    c_box.line.color.rgb = RGBColor(34, 76, 52)
    
    c_tf = c_box.text_frame
    c_tf.word_wrap = True
    c_tf.margin_left = c_tf.margin_right = Inches(0.15)
    c_tf.margin_top = Inches(0.15)
    
    p_val = c_tf.paragraphs[0]
    p_val.text = val
    p_val.font.size = Pt(22)
    p_val.font.bold = True
    p_val.font.color.rgb = COLOR_PRIMARY
    
    p_lbl = c_tf.add_paragraph()
    p_lbl.text = label
    p_lbl.font.size = Pt(11)
    p_lbl.font.bold = True
    p_lbl.font.color.rgb = COLOR_WHITE
    p_lbl.space_before = Pt(3)
    
    p_sub = c_tf.add_paragraph()
    p_sub.text = sub
    p_sub.font.size = Pt(9)
    p_sub.font.color.rgb = COLOR_MUTED
    p_sub.space_before = Pt(2)

# Author & Academic info box
auth_box = slide1.shapes.add_textbox(Inches(1.3), Inches(5.6), Inches(10.7), Inches(0.8))
tf_a = auth_box.text_frame
p_a = tf_a.paragraphs[0]
p_a.text = "B.Tech Information Technology Capstone Project  •  Phase 1 Baseline & Web Deployment Platform  •  October 2026"
p_a.font.size = Pt(11)
p_a.font.color.rgb = COLOR_MUTED

add_footer(slide1, 1)

# ==============================================================================
# SLIDE 2: Regional Agro-Climatic Context (Dhule & Khandesh)
# ==============================================================================
slide2 = prs.slides.add_slide(blank_layout)
create_slide_background(slide2)
add_header(slide2, "Regional Geography & Agronomy", "Dhule District: The Khandesh 'White Gold' Cotton Belt", "धुळे जिल्हा - खान्देश पांढरे सोने कृषी पर्यावरण (Agro-Ecosystem Context)")

# 3 Column Layout: Agro-climate, Soil, Talukas
col_w = Inches(3.64)
col_top = Inches(1.8)
col_h = Inches(4.9)

# Col 1: Regional Agronomy
add_card(slide2, Inches(0.8), col_top, col_w, col_h, "🌾 Agronomic Profile")
tb = slide2.shapes.add_textbox(Inches(1.05), col_top + Inches(0.65), col_w - Inches(0.5), col_h - Inches(0.8))
tf = tb.text_frame
tf.word_wrap = True
bullets1 = [
    ("Khandesh Commodity Hub: ", "Cotton is the primary cash crop of North Maharashtra, known regionally as 'पांढरे सोने' (White Gold)."),
    ("Total Cultivation Area: ", "Over 1,87,000 Hectares (1.87 L Ha) dedicated to cotton across Dhule district during the Kharif season."),
    ("Rainfed Vulnerability: ", "Approximately 68% of cotton tracts are dependent on rainfed semi-arid monsoon precipitation (650–750 mm annually)."),
    ("Climatic Pressures: ", "High ambient irradiance, prolonged dry spells, followed by sudden October humidity spikes triggering fungal and bacterial spore explosions."),
]
for bold_prefix, text in bullets1:
    p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
    p.space_after = Pt(10)
    r1 = p.add_run()
    r1.text = bold_prefix
    r1.font.bold = True
    r1.font.size = Pt(11)
    r1.font.color.rgb = COLOR_HIGHLIGHT
    r2 = p.add_run()
    r2.text = text
    r2.font.size = Pt(10.5)
    r2.font.color.rgb = COLOR_WHITE

# Col 2: Black Cotton Soil (Regur / Vertisols)
add_card(slide2, Inches(4.84), col_top, col_w, col_h, "🌱 Black Soil & Edaphic Dynamics")
tb = slide2.shapes.add_textbox(Inches(5.09), col_top + Inches(0.65), col_w - Inches(0.5), col_h - Inches(0.8))
tf = tb.text_frame
tf.word_wrap = True
bullets2 = [
    ("Deep Regur (Vertisols): ", "Dhule soils exhibit high clay fractions (>50%), formed from weathering of Deccan basalt trap rock."),
    ("High Moisture Retention: ", "High swell-shrink montmorillonite clay provides moisture during dry spells, but causes severe drainage impediments when waterlogged."),
    ("Sub-Surface Anaerobiosis: ", "Continuous monsoon waterlogging in low-lying fields induces root suffocation and predisposes crops to Fusarium Wilt and Root Rot."),
    ("Alkaline Soil pH: ", "Observed soil pH of 7.8–8.2 creates optimal nutrient conditions but demands strict micro-nutrient management (Zinc, Iron)."),
]
for bold_prefix, text in bullets2:
    p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
    p.space_after = Pt(10)
    r1 = p.add_run()
    r1.text = bold_prefix
    r1.font.bold = True
    r1.font.size = Pt(11)
    r1.font.color.rgb = COLOR_ACCENT
    r2 = p.add_run()
    r2.text = text
    r2.font.size = Pt(10.5)
    r2.font.color.rgb = COLOR_WHITE

# Col 3: Taluka Breakdown
add_card(slide2, Inches(8.88), col_top, col_w, col_h, "📍 Taluka Cotton Belts")
tb = slide2.shapes.add_textbox(Inches(9.13), col_top + Inches(0.65), col_w - Inches(0.5), col_h - Inches(0.8))
tf = tb.text_frame
tf.word_wrap = True
talukas = [
    ("Dhule (धुळे) - 88% Suitability", "Prime Black Soil Belt (1,874 sq km). Dominant in Bt Hybrid, Long Staple cotton. APMC Dhule is the central market."),
    ("Shirpur (शिरपूर) - 85% Suitability", "Tapi River Basin Fertile Plain (1,692 sq km). High-yielding Sankar Bt Cotton with canal & lift irrigation."),
    ("Sindkheda (शिंदखेडा) - 83% Suitability", "Alluvial Medium-Heavy Soil (1,562 sq km). Productive Bt Cotton plains with extensive drip fertigation adoption."),
    ("Sakri (साक्री) - 80% Suitability", "Western Ghats fringe & hilly terrain (2,007 sq km). Rainfed black-loam soil; mix of Desi and hardy Bt varieties."),
]
for title, desc in talukas:
    p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
    p.space_after = Pt(8)
    r1 = p.add_run()
    r1.text = f"● {title}\n"
    r1.font.bold = True
    r1.font.size = Pt(11)
    r1.font.color.rgb = COLOR_PRIMARY
    r2 = p.add_run()
    r2.text = desc
    r2.font.size = Pt(9.5)
    r2.font.color.rgb = COLOR_WHITE

add_footer(slide2, 2)

# ==============================================================================
# SLIDE 3: Problem Statement: Yield Losses & Flaws in Naive AI
# ==============================================================================
slide3 = prs.slides.add_slide(blank_layout)
create_slide_background(slide3)
add_header(slide3, "Challenges & Problem Statement", "Agricultural Crisis: Foliar Pathologies & Broken AI Benchmarks", "Why conventional academic models fail smallholder farmers in actual field conditions")

# 2 Large Column Comparison
col_w = Inches(5.66)
col_top = Inches(1.8)
col_h = Inches(4.9)

# Box 1: Real-World Agronomic Crisis
add_card(slide3, Inches(0.8), col_top, col_w, col_h, "⚠️ The Field Problem: Crop Loss & Late Diagnostics")
tb1 = slide3.shapes.add_textbox(Inches(1.05), col_top + Inches(0.65), col_w - Inches(0.5), col_h - Inches(0.8))
tf1 = tb1.text_frame
tf1.word_wrap = True
pts1 = [
    ("30% - 45% Yield Penalties: ", "Foliar diseases (Bacterial Blight, Alternaria, Powdery Mildew, Target Spot) and sucking pests (Aphids, Armyworm) cause catastrophic yield losses annually in Dhule."),
    ("Retrospective Treatment: ", "Farmers diagnose diseases retrospectively after necrotic lesions cover >20% of leaf area. Chemical sprays at this stage are inefficient and cost-prohibitive."),
    ("Indiscriminate Agrochemical Overuse: ", "Lack of accurate point-of-care diagnosis leads to excessive broad-spectrum pesticide spraying, damaging beneficial predator insects (Ladybird beetles) and raising production costs."),
    ("Market Exploitation: ", "Smallholder farmers lack real-time visibility into mandi benchmark auction prices, resulting in distress selling below Fair Average Quality (FAQ) rates."),
]
for bold_p, text in pts1:
    p = tf1.add_paragraph() if tf1.paragraphs[0].text else tf1.paragraphs[0]
    p.space_after = Pt(10)
    r1 = p.add_run()
    r1.text = bold_p
    r1.font.bold = True
    r1.font.size = Pt(11.5)
    r1.font.color.rgb = RGBColor(239, 68, 68)  # Red warning
    r2 = p.add_run()
    r2.text = text
    r2.font.size = Pt(10.5)
    r2.font.color.rgb = COLOR_WHITE

# Box 2: The Academic AI Trap (Data Leakage)
add_card(slide3, Inches(6.86), col_top, col_w, col_h, "🔬 The Research Trap: 70%+ Literature Data Leakage")
tb2 = slide3.shapes.add_textbox(Inches(7.11), col_top + Inches(0.65), col_w - Inches(0.5), col_h - Inches(0.8))
tf2 = tb2.text_frame
tf2.word_wrap = True
pts2 = [
    ("Pre-Augmented Duplicate Clumping: ", "Public benchmark datasets (Kaggle, Mendeley) contain raw archives pre-augmented with rotations, flips, and crops BEFORE splitting. A single leaf exists in 30-40 transformed copies."),
    ("Catastrophic Evaluation Leakage: ", "When researchers apply random 80/20 train/test splits, transformed copies of the same physical leaf land in both partitions!"),
    ("Artificially Inflated 'Lab' Accuracy: ", "Neural networks memorize unique leaf contours, camera noise, and backgrounds rather than pathological lesions—generating 99%+ reported lab accuracy but crashing to <50% in real fields."),
    ("Class-Label Contradictions: ", "Audits revealed identical cryptographic image hashes tagged as different diseases across contradictory folder directories."),
]
for bold_p, text in pts2:
    p = tf2.add_paragraph() if tf2.paragraphs[0].text else tf2.paragraphs[0]
    p.space_after = Pt(10)
    r1 = p.add_run()
    r1.text = bold_p
    r1.font.bold = True
    r1.font.size = Pt(11.5)
    r1.font.color.rgb = COLOR_ACCENT
    r2 = p.add_run()
    r2.text = text
    r2.font.size = Pt(10.5)
    r2.font.color.rgb = COLOR_WHITE

add_footer(slide3, 3)

# ==============================================================================
# SLIDE 4: Scientific Innovation: Forensic Audit & DSU Leaf Clustering
# ==============================================================================
slide4 = prs.slides.add_slide(blank_layout)
create_slide_background(slide4)
add_header(slide4, "Methodological Rigor", "Forensic Dataset Audit & Disjoint Set Union (DSU) Clustering", "Guaranteeing zero cross-split data leakage across 14,955 images")

# 4 Pipeline Stage Cards Horizontally
step_w = Inches(2.78)
step_gap = Inches(0.2)
step_top = Inches(1.8)
step_h = Inches(4.9)
start_x = Inches(0.8)

steps_data = [
    ("Stage 1: Cryptographic Audit", "14,955 Files Audited", [
        ("MD5 Hash Extraction: ", "Computed cryptographic digests for every file across Original and Augmented directories."),
        ("OS Artifacts Purged: ", "4 macOS '.DS_Store' metadata files detected and safely eliminated."),
        ("Cross-Class Clashes: ", "14 images with identical cryptographic hashes had contradictory disease labels and were permanently purged."),
    ], COLOR_PRIMARY),
    
    ("Stage 2: DSU Connected Clustering", "5,852 Physical Leaf Clusters", [
        ("Disjoint Set Union (DSU): ", "Engineered a graph clustering algorithm linking pre-augmented variants back to root base leaf identities."),
        ("Heuristic & Path Grouping: ", "Parsed prefix patterns (rotation_, contrast_, flip_, crop_) to group all derived synthetic variants."),
        ("Isolated Identities: ", "Formed 5,852 strictly disjoint physical leaf clusters containing 14,923 verified valid images."),
    ], COLOR_HIGHLIGHT),
    
    ("Stage 3: Stratified Group Partition", "Zero Overlap (|Train ∩ Test| = 0)", [
        ("Cluster-Level Splitting: ", "All images of a leaf cluster were assigned EN BLOC to either Train, Val, or Test."),
        ("Train Set (~70%): ", "10,418 images (only set subjected to on-the-fly augmentation)."),
        ("Validation Set (~15%): ", "887 images (strictly unaugmented physical leaves for model selection)."),
        ("Untouched Test Set (~15%): ", "872 images (100% clean benchmark for final unbiased evaluation)."),
    ], COLOR_ACCENT),
    
    ("Stage 4: Mathematical Verification", "Cryptographic Proof of Purity", [
        ("Intersection Verification: ", "Automated MD5 intersection script proved $|Train \\cap Test| = 0$."),
        ("Generalization Proof: ", "Validation accuracy (90.4%) closely mirrored untouched test accuracy (89.9%), proving genuine feature learning without memorization."),
        ("Benchmark Foundation: ", "Provides a trustworthy reference for regional deployment in Dhule."),
    ], RGBColor(56, 189, 248)),
]

for i, (title, sub, bullets, color) in enumerate(steps_data):
    cx = start_x + i * (step_w + step_gap)
    add_card(slide4, cx, step_top, step_w, step_h, None, fill_color=RGBColor(16, 32, 24), border_color=color)
    
    # Title box
    tb = slide4.shapes.add_textbox(cx + Inches(0.15), step_top + Inches(0.18), step_w - Inches(0.3), Inches(0.75))
    tf = tb.text_frame
    tf.word_wrap = True
    p0 = tf.paragraphs[0]
    p0.text = title
    p0.font.size = Pt(12)
    p0.font.bold = True
    p0.font.color.rgb = color
    
    p1 = tf.add_paragraph()
    p1.text = sub
    p1.font.size = Pt(10)
    p1.font.color.rgb = COLOR_WHITE
    p1.space_before = Pt(2)
    
    # Bullets
    tb_b = slide4.shapes.add_textbox(cx + Inches(0.15), step_top + Inches(1.0), step_w - Inches(0.3), step_h - Inches(1.15))
    tf_b = tb_b.text_frame
    tf_b.word_wrap = True
    for bp, txt in bullets:
        p = tf_b.add_paragraph() if tf_b.paragraphs[0].text else tf_b.paragraphs[0]
        p.space_after = Pt(8)
        r1 = p.add_run()
        r1.text = bp
        r1.font.bold = True
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = COLOR_HIGHLIGHT
        r2 = p.add_run()
        r2.text = txt
        r2.font.size = Pt(9)
        r2.font.color.rgb = COLOR_WHITE

add_footer(slide4, 4)

# ==============================================================================
# SLIDE 5: Deep Learning Model Architecture & Performance
# ==============================================================================
slide5 = prs.slides.add_slide(blank_layout)
create_slide_background(slide5)
add_header(slide5, "Machine Learning Architecture", "MobileNetV2 Transfer Learning Benchmark & Test Results", "Rigorous evaluation across 871 untouched test leaves (9 pathology classes)")

# Left Box: Model Specs & Overall Metrics
add_card(slide5, Inches(0.8), Inches(1.8), Inches(5.66), Inches(4.9), "🧠 MobileNetV2 Architecture & Hyperparameters")
tb = slide5.shapes.add_textbox(Inches(1.05), Inches(2.45), Inches(5.16), Inches(4.1))
tf = tb.text_frame
tf.word_wrap = True

specs = [
    ("Backbone Network: ", "MobileNetV2 (Sandler et al., CVPR 2018) with depthwise separable convolutions and inverted residual bottlenecks."),
    ("Pretrained Representations: ", "ImageNet-1k initialized feature extractor with frozen base layers for stable foliar feature transfer."),
    ("Edge Inference Latency: ", "~45 ms inference latency on standard mobile/server hardware (~3.5 Million parameters). Ideal for rural deployment."),
    ("Balanced Cross-Entropy Loss: ", "Inverse class frequency weighting: W_c = N_total / (K * N_c) to eliminate majority class bias."),
    ("Key Overall Performance Metrics (Untouched Test Leaves):", ""),
    ("   ● Overall Test Accuracy: ", "89.90% (783 of 871 correctly diagnosed)"),
    ("   ● Macro F1-Score: ", "0.8741 (rigorous unweighted class balance)"),
    ("   ● Weighted F1-Score: ", "0.8966 | Macro Precision: 0.8660 | Macro Recall: 0.8905"),
    ("   ● Total Misclassifications: ", "Only 88 images across all 9 test categories (10.10%)"),
]
for bp, txt in specs:
    p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
    p.space_after = Pt(4)
    r1 = p.add_run()
    r1.text = bp
    r1.font.bold = True
    r1.font.size = Pt(10)
    r1.font.color.rgb = COLOR_HIGHLIGHT if "●" in bp else COLOR_WHITE
    if txt:
        r2 = p.add_run()
        r2.text = txt
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = COLOR_ACCENT if "%" in txt else COLOR_WHITE

# Right Box: Quantitative Table on Untouched Test Partition
add_card(slide5, Inches(6.86), Inches(1.8), Inches(5.66), Inches(4.9), "📊 Class-Wise Performance on Untouched Test Leaves")

# Create Table
rows = 10
cols = 5
left = Inches(7.06)
top = Inches(2.45)
width = Inches(5.26)
height = Inches(4.0)

table_shape = slide5.shapes.add_table(rows, cols, left, top, width, height)
table = table_shape.table

# Set Column Widths
table.columns[0].width = Inches(1.7)
table.columns[1].width = Inches(0.85)
table.columns[2].width = Inches(0.85)
table.columns[3].width = Inches(0.86)
table.columns[4].width = Inches(1.0)

table_data = [
    ["Disease Class", "Precision", "Recall", "F1-Score", "Test Leaves"],
    ["Alternaria Leaf", "0.915", "0.946", "0.930", "148"],
    ["Aphids (मावा)", "0.808", "0.913", "0.857", "23"],
    ["Army Worm (अळी)", "0.895", "0.850", "0.872", "20"],
    ["Bacterial Blight", "0.968", "0.697", "0.811", "175"],
    ["Fusarium Wilt (मर)", "0.865", "0.944", "0.902", "142"],
    ["Healthy Leaf", "0.977", "0.994", "0.986", "174"],
    ["Powdery Mildew", "0.783", "0.900", "0.837", "20"],
    ["Target Spot", "0.750", "0.818", "0.783", "22"],
    ["Verticillium Wilt", "0.833", "0.952", "0.889", "147"],
]

for r_idx, row in enumerate(table_data):
    for c_idx, val in enumerate(row):
        cell = table.cell(r_idx, c_idx)
        cell.text = val
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = cell.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER if c_idx > 0 else PP_ALIGN.LEFT
        p.font.size = Pt(9 if r_idx > 0 else 9.5)
        p.font.bold = (r_idx == 0 or c_idx == 0)
        p.font.color.rgb = COLOR_HIGHLIGHT if r_idx == 0 else COLOR_WHITE

add_footer(slide5, 5)

# ==============================================================================
# SLIDE 6: System Architecture & Full-Stack Implementation
# ==============================================================================
slide6 = prs.slides.add_slide(blank_layout)
create_slide_background(slide6)
add_header(slide6, "Full-Stack System Architecture", "End-to-End Khandesh Cotton Farm Intelligence Platform", "Asynchronous FastAPI microservices, Leaflet GIS, and responsive React frontend")

# 3 Horizontal Tier Cards
tier_w = Inches(3.64)
tier_top = Inches(1.8)
tier_h = Inches(4.9)

# Tier 1: Frontend Layer
add_card(slide6, Inches(0.8), tier_top, tier_w, tier_h, "💻 Client Layer (React & Vite)")
tb = slide6.shapes.add_textbox(Inches(1.05), tier_top + Inches(0.65), tier_w - Inches(0.5), tier_h - Inches(0.8))
tf = tb.text_frame
tf.word_wrap = True
t1_pts = [
    ("React 18 & TypeScript: ", "Type-safe, component-driven reactive single-page architecture built with Vite bundler for sub-second hot reload."),
    ("Leaflet Interactive GIS: ", "Multi-layer tile switching: Google Road Map, Google Satellite (Farmlands), Google Terrain, and OpenStreetMap."),
    ("Dynamic Agronomic Charts: ", "Recharts SVG visualizations for APMC Mandi price trajectories, moisture metrics, and factor breakdown bars."),
    ("Bilingual UI: ", "Integrated Marathi (मराठी) and English terminology for native Khandesh farmer accessibility."),
]
for bp, txt in t1_pts:
    p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
    p.space_after = Pt(10)
    r1 = p.add_run()
    r1.text = bp
    r1.font.bold = True
    r1.font.size = Pt(10.5)
    r1.font.color.rgb = COLOR_PRIMARY
    r2 = p.add_run()
    r2.text = txt
    r2.font.size = Pt(9.5)
    r2.font.color.rgb = COLOR_WHITE

# Tier 2: Backend API Layer
add_card(slide6, Inches(4.84), tier_top, tier_w, tier_h, "⚡ Backend API (FastAPI)")
tb = slide6.shapes.add_textbox(Inches(5.09), tier_top + Inches(0.65), tier_w - Inches(0.5), tier_h - Inches(0.8))
tf = tb.text_frame
tf.word_wrap = True
t2_pts = [
    ("High-Throughput ASGI: ", "FastAPI asynchronous runtime powered by Uvicorn on port 8000 with auto-generated OpenAPI/Swagger interactive docs."),
    ("PyTorch Inference Engine: ", "In-memory singleton model service executing MobileNetV2 forward pass in ~45ms per image."),
    ("Multi-Factor Suitability: ", "Heuristic agronomic engine assessing Open-Meteo ambient temp, soil pH, clay fraction, and irrigation access."),
    ("SQLite Persistence: ", "Lightweight relational database logging user farm coordinates, historical diagnoses, and agronomic audit records."),
]
for bp, txt in t2_pts:
    p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
    p.space_after = Pt(10)
    r1 = p.add_run()
    r1.text = bp
    r1.font.bold = True
    r1.font.size = Pt(10.5)
    r1.font.color.rgb = COLOR_HIGHLIGHT
    r2 = p.add_run()
    r2.text = txt
    r2.font.size = Pt(9.5)
    r2.font.color.rgb = COLOR_WHITE

# Tier 3: External Services & Data
add_card(slide6, Inches(8.88), tier_top, tier_w, tier_h, "🌐 Agronomic & Weather Data")
tb = slide6.shapes.add_textbox(Inches(9.13), tier_top + Inches(0.65), tier_w - Inches(0.5), tier_h - Inches(0.8))
tf = tb.text_frame
tf.word_wrap = True
t3_pts = [
    ("Open-Meteo Meteorology: ", "Real-time agro-meteorological API fetching live ambient temperature and rainfall projections for Dhule district."),
    ("NBSS&LUP Soil Baselines: ", "ICAR National Bureau of Soil Survey Vertisol data baselines for clay percentage, organic carbon, and cation exchange."),
    ("APMC & Agmarknet Feeds: ", "Daily auction rate integration across Dhule, Shirpur, Jalgaon, Akola, Malegaon, and Chopda agricultural market yards."),
    ("Institutional Advisory: ", "Prescriptions aligned with Krishi Vigyan Kendra (KVK Dhule) and MPKV Rahuri cotton management protocols."),
]
for bp, txt in t3_pts:
    p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
    p.space_after = Pt(10)
    r1 = p.add_run()
    r1.text = bp
    r1.font.bold = True
    r1.font.size = Pt(10.5)
    r1.font.color.rgb = COLOR_ACCENT
    r2 = p.add_run()
    r2.text = txt
    r2.font.size = Pt(9.5)
    r2.font.color.rgb = COLOR_WHITE

add_footer(slide6, 6)

# ==============================================================================
# SLIDE 7: Dashboard Tour - Executive Overview (WITH SCREENSHOT 1)
# ==============================================================================
slide7 = prs.slides.add_slide(blank_layout)
create_slide_background(slide7)
add_header(slide7, "Dashboard Tour • Module 1", "Executive Farm Overview: Crop Progress & Regional Metrics", "धुळे कापूस कृषी केंद्र — Macro-level situational awareness for farmers and agricultural officers")

# Left: Explanatory Card with Features
add_card(slide7, Inches(0.8), Inches(1.8), Inches(4.5), Inches(4.9), "🌾 Overview Features & Agronomic KPIs")
tb = slide7.shapes.add_textbox(Inches(1.05), Inches(2.45), Inches(4.0), Inches(4.1))
tf = tb.text_frame
tf.word_wrap = True
ov_pts = [
    ("Kharif Crop Stage Timeline: ", "Visual 5-stage tracker (Sowing → Vegetative → Flowering → Boll Stage → Picking) identifying active physiological risks."),
    ("Cultivation Acreage KPI: ", "Monitors 1.87 Lakh Hectares under cotton across Dhule, Shirpur, Sindkheda, and Sakri."),
    ("Live Mandi Benchmark: ", "Displays current Dhule APMC rate (₹7,250/Qtl, +₹120) alongside Government MSP (₹7,121/Qtl)."),
    ("Historical Price Trajectory: ", "Interactive SVG area chart tracking April to October price evolution across Khandesh market yards."),
    ("Taluka Suitability Index: ", "Interactive progress bars ranking all 4 talukas with soil type, area, and dominant cotton hybrid recommendations."),
]
for bp, txt in ov_pts:
    p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
    p.space_after = Pt(8)
    r1 = p.add_run()
    r1.text = bp
    r1.font.bold = True
    r1.font.size = Pt(10)
    r1.font.color.rgb = COLOR_PRIMARY
    r2 = p.add_run()
    r2.text = txt
    r2.font.size = Pt(9)
    r2.font.color.rgb = COLOR_WHITE

# Right: High-Res Screenshot 1
img_path1 = os.path.join(ASSETS_DIR, "01_dashboard_overview.png")
if os.path.exists(img_path1):
    slide7.shapes.add_picture(img_path1, Inches(5.5), Inches(1.8), width=Inches(7.03))

add_footer(slide7, 7)

# ==============================================================================
# SLIDE 8: Dashboard Tour - Google GIS Suitability Map (WITH SCREENSHOT 2)
# ==============================================================================
slide8 = prs.slides.add_slide(blank_layout)
create_slide_background(slide8)
add_header(slide8, "Dashboard Tour • Module 2", "Agro-Ecological GIS Map & Soil Suitability Engine", "धुळे जमीन व हवामान उपयुक्तता नकाशा — Georeferenced agronomic assessment for precision planting")

# Left: Explanatory Card
add_card(slide8, Inches(0.8), Inches(1.8), Inches(4.5), Inches(4.9), "🗺️ GIS Mapping & Suitability Features")
tb = slide8.shapes.add_textbox(Inches(1.05), Inches(2.45), Inches(4.0), Inches(4.1))
tf = tb.text_frame
tf.word_wrap = True
map_pts = [
    ("Interactive Google Layers: ", "Switch dynamically between Google Road Network, Google Satellite Farmland Imagery, Google Terrain, and OpenStreetMap."),
    ("Color-Coded Taluka Belts: ", "GIS circle overlays mapping regional suitability buffers: Dhule Central (88%), Shirpur Tapi Basin (85%), Sindkheda (83%), Sakri (80%)."),
    ("One-Click Field Geocoding: ", "Farmers can tap any field on the map to auto-populate exact GPS coordinates for micro-climatic evaluation."),
    ("Multi-Factor Factor Analysis: ", "Evaluates live ambient temperature (Open-Meteo), soil pH (8.1 Vertisol baseline), clay fraction (>50%), and supplemental irrigation support."),
    ("Agronomic Advisory Output: ", "Generates tailored recommendations, moisture risk warnings, and soil testing reminders for KVK Dhule."),
]
for bp, txt in map_pts:
    p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
    p.space_after = Pt(8)
    r1 = p.add_run()
    r1.text = bp
    r1.font.bold = True
    r1.font.size = Pt(10)
    r1.font.color.rgb = COLOR_HIGHLIGHT
    r2 = p.add_run()
    r2.text = txt
    r2.font.size = Pt(9)
    r2.font.color.rgb = COLOR_WHITE

# Right: High-Res Screenshot 2
img_path2 = os.path.join(ASSETS_DIR, "02_dashboard_suitability_map.png")
if os.path.exists(img_path2):
    slide8.shapes.add_picture(img_path2, Inches(5.5), Inches(1.8), width=Inches(7.03))

add_footer(slide8, 8)

# ==============================================================================
# SLIDE 9: Dashboard Tour - AI Leaf Disease Diagnosis (WITH SCREENSHOT 3)
# ==============================================================================
slide9 = prs.slides.add_slide(blank_layout)
create_slide_background(slide9)
add_header(slide9, "Dashboard Tour • Module 3", "AI Point-of-Care Leaf Health Diagnostic Engine", "कापूस पान रोग निदान — MobileNetV2 computer vision inference with localized chemical prescriptions")

# Left: Explanatory Card
add_card(slide9, Inches(0.8), Inches(1.8), Inches(4.5), Inches(4.9), "🌿 AI Diagnostic Workflow & Prescriptions")
tb = slide9.shapes.add_textbox(Inches(1.05), Inches(2.45), Inches(4.0), Inches(4.1))
tf = tb.text_frame
tf.word_wrap = True
diag_pts = [
    ("Instant Foliar Diagnosis: ", "Farmers upload leaf closeup photos via drag-and-drop or smartphone camera; processed in ~45ms."),
    ("9 Pathology Detectors: ", "Detects Alternaria Leaf Spot, Aphids, Armyworm, Bacterial Blight, Curl Virus, Fusarium Wilt, Healthy Leaf, Powdery Mildew, and Target Spot."),
    ("Softmax Confidence & Top-3 Probabilities: ", "Displays classification confidence alongside ranking of top 3 probable diseases to support nuanced agronomic judgment."),
    ("Actionable Chemical Advisory: ", "Provides exact fungicide/insecticide names, spray dosage (e.g., Mancozeb 75 WP @ 2.5 g/L, Streptocycline @ 0.5 g/L), and water dilution rates."),
    ("Prophylactic Measures: ", "Outlines biological pest control (ladybird beetles, pheromone traps) and 3-year crop rotation schedules."),
]
for bp, txt in diag_pts:
    p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
    p.space_after = Pt(8)
    r1 = p.add_run()
    r1.text = bp
    r1.font.bold = True
    r1.font.size = Pt(10)
    r1.font.color.rgb = COLOR_PRIMARY
    r2 = p.add_run()
    r2.text = txt
    r2.font.size = Pt(9)
    r2.font.color.rgb = COLOR_WHITE

# Right: High-Res Screenshot 3
img_path3 = os.path.join(ASSETS_DIR, "03_dashboard_leaf_health_ai.png")
if os.path.exists(img_path3):
    slide9.shapes.add_picture(img_path3, Inches(5.5), Inches(1.8), width=Inches(7.03))

add_footer(slide9, 9)

# ==============================================================================
# SLIDE 10: Dashboard Tour - APMC Mandi Intelligence (WITH SCREENSHOT 4)
# ==============================================================================
slide10 = prs.slides.add_slide(blank_layout)
create_slide_background(slide10)
add_header(slide10, "Dashboard Tour • Module 4", "Mandi Market Intelligence & APMC Price Optimization", "कापूस बाजारभाव — Real-time price transparency across Dhule, Shirpur, Jalgaon, and Akola")

# Left: Explanatory Card
add_card(slide10, Inches(0.8), Inches(1.8), Inches(4.5), Inches(4.9), "💰 Market Intelligence & Farmer Advisory")
tb = slide10.shapes.add_textbox(Inches(1.05), Inches(2.45), Inches(4.0), Inches(4.1))
tf = tb.text_frame
tf.word_wrap = True
mandi_pts = [
    ("Live Mandi Price Feeds: ", "Real-time APMC auction rates for Dhule APMC (₹7,250), Shirpur APMC (₹7,180), Jalgaon (₹7,320), and Akola White Gold (₹7,400)."),
    ("Market vs. MSP Indicator: ", "Automated comparative tracker highlighting price advantage over Government Minimum Support Price (₹7,121 for Long Staple)."),
    ("Moisture Premium Guidance: ", "Advises farmers on sun-drying practices to maintain moisture below 8%, unlocking ₹150–250/Qtl quality premiums at auction."),
    ("Cross-Mandi Arbitrage: ", "Visual bar chart allows farmers to evaluate transportation costs vs. higher price spreads in neighboring APMCs (e.g. Jalgaon vs Dhule)."),
    ("e-NAM Integration: ", "Encourages registration on the National Agriculture Market for transparent electronic bidding without intermediary brokerage."),
]
for bp, txt in mandi_pts:
    p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
    p.space_after = Pt(8)
    r1 = p.add_run()
    r1.text = bp
    r1.font.bold = True
    r1.font.size = Pt(10)
    r1.font.color.rgb = COLOR_ACCENT
    r2 = p.add_run()
    r2.text = txt
    r2.font.size = Pt(9)
    r2.font.color.rgb = COLOR_WHITE

# Right: High-Res Screenshot 4
img_path4 = os.path.join(ASSETS_DIR, "04_dashboard_mandi_prices.png")
if os.path.exists(img_path4):
    slide10.shapes.add_picture(img_path4, Inches(5.5), Inches(1.8), width=Inches(7.03))

add_footer(slide10, 10)

# ==============================================================================
# SLIDE 11: Real-World Agronomic Impact & Farmer Benefits
# ==============================================================================
slide11 = prs.slides.add_slide(blank_layout)
create_slide_background(slide11)
add_header(slide11, "Socio-Economic & Agronomic Value", "Tangible Impacts for Smallholder Farmers in Dhule", "Transforming agricultural productivity, chemical safety, and market bargaining power")

# 4 Value Pillars (2x2 Grid)
grid_w = Inches(5.66)
grid_h = Inches(2.35)

pillars = [
    ("🌱 Targeted Disease Interventions & Cost Savings", [
        "Eliminates blind broad-spectrum pesticide applications, saving ₹2,500–₹4,000 per acre in unnecessary chemical expenses.",
        "Prevents epidemic crop failure through early detection at the initial lesion stage before pathogen spores spread across canopy.",
    ], Inches(0.8), Inches(1.8), COLOR_PRIMARY),
    
    ("📈 Market Price Bargaining & Income Enhancement", [
        "Eliminates middleman price asymmetry by equipping farmers with live daily APMC auction benchmarks.",
        "Moisture management guidance prevents unfair commercial deductions of 5%–10% at private ginning mills.",
    ], Inches(6.86), Inches(1.8), COLOR_ACCENT),
    
    ("🏛️ Institutional Knowledge Bridging", [
        "Connects ICAR, MPKV Rahuri, and Krishi Vigyan Kendra (KVK Dhule) research advisories directly to smallholder fields.",
        "Provides direct hotline contact to District Agricultural Officer (DAO) and APMC main yard.",
    ], Inches(0.8), Inches(4.35), COLOR_HIGHLIGHT),
    
    ("🌾 Environmental & Soil Health Sustainability", [
        "Reduced chemical spraying preserves beneficial pollinator insects and soil microbiological health in Vertisols.",
        "Encourages integrated pest management (IPM), neem formulations, and bio-fertilizer usage.",
    ], Inches(6.86), Inches(4.35), RGBColor(56, 189, 248)),
]

for title, bullets, gx, gy, col in pillars:
    add_card(slide11, gx, gy, grid_w, grid_h, title, fill_color=RGBColor(16, 32, 24), border_color=col)
    tb = slide11.shapes.add_textbox(gx + Inches(0.25), gy + Inches(0.6), grid_w - Inches(0.5), grid_h - Inches(0.7))
    tf = tb.text_frame
    tf.word_wrap = True
    for b in bullets:
        p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
        p.space_after = Pt(6)
        r = p.add_run()
        r.text = f"● {b}"
        r.font.size = Pt(10)
        r.font.color.rgb = COLOR_WHITE

add_footer(slide11, 11)

# ==============================================================================
# SLIDE 12: Project Roadmap & Academic Evaluation
# ==============================================================================
slide12 = prs.slides.add_slide(blank_layout)
create_slide_background(slide12)
add_header(slide12, "Phase 2 Roadmap & Future Scope", "From Phase 1 Baseline to Field Deployment in Dhule", "Bridging laboratory benchmark models into resilient rural point-of-care tools")

col_w = Inches(3.64)
col_top = Inches(1.8)
col_h = Inches(4.9)

# Col 1: Phase 1 Achievements
add_card(slide12, Inches(0.8), col_top, col_w, col_h, "✅ Phase 1 Achievements")
tb = slide12.shapes.add_textbox(Inches(1.05), col_top + Inches(0.65), col_w - Inches(0.5), col_h - Inches(0.8))
tf = tb.text_frame
tf.word_wrap = True
p1_done = [
    ("Forensic Leakage Audit: ", "Successfully purged 14 conflicting hashes and isolated 5,852 physical leaf clusters via DSU clustering."),
    ("Clean Transfer Learning: ", "MobileNetV2 achieved 89.90% accuracy and 0.8741 Macro-F1 on strictly untouched test leaf clusters."),
    ("Operational Web Platform: ", "Production-grade FastAPI backend + React Vite Leaflet frontend running locally with sub-second response times."),
    ("Agro-Climatic Integration: ", "Real-time Open-Meteo weather and NBSS&LUP soil baselines active."),
]
for bp, txt in p1_done:
    p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
    p.space_after = Pt(8)
    r1 = p.add_run()
    r1.text = bp
    r1.font.bold = True
    r1.font.size = Pt(10.5)
    r1.font.color.rgb = COLOR_PRIMARY
    r2 = p.add_run()
    r2.text = txt
    r2.font.size = Pt(9.5)
    r2.font.color.rgb = COLOR_WHITE

# Col 2: Phase 2 In-Situ Field Work
add_card(slide12, Inches(4.84), col_top, col_w, col_h, "🚀 Phase 2 Field Deployment")
tb = slide12.shapes.add_textbox(Inches(5.09), col_top + Inches(0.65), col_w - Inches(0.5), col_h - Inches(0.8))
tf = tb.text_frame
tf.word_wrap = True
p2_plan = [
    ("On-Site Leaf Acquisition: ", "Partner with College of Agriculture, Dhule (MPKV Rahuri) and KVK Dhule to collect in-situ field leaf images."),
    ("Domain Shift Benchmarking: ", "Quantify out-of-distribution performance drops caused by ambient dust, direct sunlight glare, and soil splash."),
    ("Few-Shot Prototypical Nets: ", "Train metric-learning episodic models capable of recognizing new disease variants with <10 field examples."),
    ("Lightweight Edge Quantization: ", "Quantize PyTorch model to INT8 ONNX / TFLite for zero-latency execution on budget Android smartphones."),
]
for bp, txt in p2_plan:
    p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
    p.space_after = Pt(8)
    r1 = p.add_run()
    r1.text = bp
    r1.font.bold = True
    r1.font.size = Pt(10.5)
    r1.font.color.rgb = COLOR_HIGHLIGHT
    r2 = p.add_run()
    r2.text = txt
    r2.font.size = Pt(9.5)
    r2.font.color.rgb = COLOR_WHITE

# Col 3: Product Extension
add_card(slide12, Inches(8.88), col_top, col_w, col_h, "📱 Product & Rural Scaling")
tb = slide12.shapes.add_textbox(Inches(9.13), col_top + Inches(0.65), col_w - Inches(0.5), col_h - Inches(0.8))
tf = tb.text_frame
tf.word_wrap = True
p3_prod = [
    ("Offline-First Android App: ", "Progressive Web App (PWA) / native Android APK with local SQLite caching for internet-deprived farm pockets."),
    ("Voice Advisory in Khandeshi: ", "Integrate text-to-speech audio guidance in local Khandeshi and Marathi dialects for illiterate farmers."),
    ("Satellite Drone Integration: ", "Incorporate multi-spectral NDVI drone imagery to detect canopy stress zones prior to visible leaf necrosis."),
    ("SMS & WhatsApp Bot: ", "Daily automated Mandi price alerts and weather warnings sent directly to registered farmer mobile numbers."),
]
for bp, txt in p3_prod:
    p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
    p.space_after = Pt(8)
    r1 = p.add_run()
    r1.text = bp
    r1.font.bold = True
    r1.font.size = Pt(10.5)
    r1.font.color.rgb = COLOR_ACCENT
    r2 = p.add_run()
    r2.text = txt
    r2.font.size = Pt(9.5)
    r2.font.color.rgb = COLOR_WHITE

add_footer(slide12, 12)

# ==============================================================================
# SLIDE 13: Summary & Conclusion / Q&A Slide
# ==============================================================================
slide13 = prs.slides.add_slide(blank_layout)
create_slide_background(slide13)

hero_card13 = add_card(slide13, Inches(0.8), Inches(0.8), Inches(11.733), Inches(5.9), fill_color=RGBColor(14, 28, 20), border_color=RGBColor(26, 56, 38))

tb = slide13.shapes.add_textbox(Inches(1.3), Inches(1.3), Inches(10.7), Inches(2.2))
tf = tb.text_frame
tf.word_wrap = True

p0 = tf.paragraphs[0]
p0.text = "🌾 CONCLUSION & PROJECT IMPACT"
p0.font.size = Pt(13)
p0.font.bold = True
p0.font.color.rgb = COLOR_PRIMARY
p0.space_after = Pt(8)

p1 = tf.add_paragraph()
p1.text = "Scientific Rigor Meets Smallholder Farmer Empowerment"
p1.font.size = Pt(30)
p1.font.bold = True
p1.font.color.rgb = COLOR_WHITE
p1.space_after = Pt(8)

p2 = tf.add_paragraph()
p2.text = "A scientifically verified, leakage-proof computer vision pipeline and production-grade agro-intelligence hub for Khandesh cotton farmers."
p2.font.size = Pt(14)
p2.font.color.rgb = COLOR_ACCENT

# 3 Summary Pillar Cards
pillars13 = [
    ("🔬 Methodological Rigor", "Proved and solved benchmark dataset leakage using cryptographic hashing and DSU cluster partitioning across 14,955 images."),
    ("🧠 89.90% Test Accuracy", "Delivered lightweight MobileNetV2 transfer learning baseline with class-balanced weighting on strictly untouched test leaves."),
    ("🚜 Practical Rural Utility", "Full-stack GIS map, instant leaf diagnosis, live APMC Mandi prices, and Marathi farmer advisory running in real time."),
]

card_w13 = Inches(3.4)
card_gap13 = Inches(0.25)
start_x13 = Inches(1.3)

for i, (title, desc) in enumerate(pillars13):
    cx = start_x13 + i * (card_w13 + card_gap13)
    c_box = slide13.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cx, Inches(3.6), card_w13, Inches(1.8))
    c_box.fill.solid()
    c_box.fill.fore_color.rgb = RGBColor(20, 42, 30)
    c_box.line.color.rgb = RGBColor(34, 76, 52)
    
    c_tf = c_box.text_frame
    c_tf.word_wrap = True
    c_tf.margin_left = c_tf.margin_right = Inches(0.2)
    c_tf.margin_top = Inches(0.2)
    
    p_t = c_tf.paragraphs[0]
    p_t.text = title
    p_t.font.size = Pt(14)
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_HIGHLIGHT
    
    p_d = c_tf.add_paragraph()
    p_d.text = desc
    p_d.font.size = Pt(10)
    p_d.font.color.rgb = COLOR_WHITE
    p_d.space_before = Pt(6)

# Q&A Footer Box
qa_box = slide13.shapes.add_textbox(Inches(1.3), Inches(5.6), Inches(10.7), Inches(0.8))
tf_qa = qa_box.text_frame
p_qa = tf_qa.paragraphs[0]
p_qa.text = "Thank You! Questions & Discussion Welcomed  •  FastAPI Docs: http://localhost:8000/docs  •  Frontend: http://localhost:5173"
p_qa.font.size = Pt(12)
p_qa.font.bold = True
p_qa.font.color.rgb = COLOR_PRIMARY

add_footer(slide13, 13)

# Save Presentation
prs.save(OUTPUT_PPTX)
print(f"Presentation successfully generated and saved to: {OUTPUT_PPTX}")
